__author__ = "ujjwal"
import os
import json
import requests
import urllib
import xmltodict
from priceprobi.utils import get_env
from priceprobi.config import get_config
from priceprobi.db.mongo_helper import MongoHelper
from priceprobi.config import NOMINATIM, CSIS
from priceprobi import logger


def scrape_cics_data():
    states_url = "http://india.csis.u-tokyo.ac.jp/api/getStateList"
    st_req = requests.get(states_url)
    states = json.loads(st_req.text)
    data = []

    for s in states:
        districts_url = "http://india.csis.u-tokyo.ac.jp/api/getDistrictList?p=%s" % s['id']
        dis_req = requests.get(districts_url)
        districts = json.loads(dis_req.text)
        s["districts"] = []

        for d in districts:
            subdistricts_url = "http://india.csis.u-tokyo.ac.jp/api/getSubDistrictList?p=%s" % d['id']
            subdis_req = requests.get(subdistricts_url)
            sub_districts = json.loads(subdis_req.text)
            d["sub_districts"] = sub_districts
            s["districts"].append(d)

        data.append(s)

    with open(CSIS["scraped_file_name"], 'w') as of:
        of.write(json.dumps(data))


class Geocoder(object):

    def __init__(self, config):
        self.mongo_helper = MongoHelper(config=config)
        if not os.path.exists(CSIS["scraped_file_name"]):
            scrape_cics_data()

        if os.path.exists(CSIS["scraped_file_name"]):
            with open(CSIS["scraped_file_name"], 'r') as sf:
                data = sf.read()
                self.states = json.loads(data)
        else:
            raise Exception("Could not download CSIS file")

    def __nominatim_geocode(self, state, district, market):
        query = "%s, %s, %s" % (market, district, state)
        params = {
            "format": "json",
            "q": query
        }
        req = requests.get(NOMINATIM["api_url"], params=params)
        logger.debug("nm request for %s %s %s" % (state, district, market))

        resp = req.json()
        return resp

    def __cics_geocode(self, state, district, market):
        f_str_state = ""
        f_str_district = ""
        for st in self.states:
            if st['name'].lower() == state.lower():
                state_id = st['id']
                f_str_state = '"state":"' + state_id + '"'
                for di in st['districts']:
                    if di['name'].lower() == district.lower():
                        district_id = di['id']
                        f_str_district = ', "district":"' + district_id + '"'
                        break

        f_param = "{" + f_str_state + f_str_district + "}"
        data = urllib.urlencode({"q": market, "f": f_param})
        req = requests.post("http://india.csis.u-tokyo.ac.jp/geocode-cgi/census_ajax_json.cgi", data=data)
        logger.debug("cics request for %s %s %s" % (state, district, market))

        xmldict = xmltodict.parse(req.text)
        if "markers" in xmldict:
            results = xmldict["markers"]
            if results and "marker" in results:
                return results["marker"]
        return None

    def check_mandi_locations(self):
        logger.debug("Check mandi locations")
        mandi_prices = self.mongo_helper.db["mandi_prices"]
        mandi_locations = self.mongo_helper.db["mandi_locations"]

        cursor = mandi_prices.find()
        for mp in cursor:
            state = (mp["state"]).lower()
            district = (mp["district"]).lower()
            market = (mp["market"]).lower()

            query = {"state": state, "district": district, "market": market}
            doc = mandi_locations.find_one(query)

            if doc is None:
                doc = {
                    "state": state, "district": district, "market": market
                }
                doc["_id"] = mandi_locations.insert(doc)

            if not "cics_geocode" in doc:
                cics_data = self.__cics_geocode(state, district, market)
                if cics_data and len(cics_data) > 0:
                    mandi_locations.update({"_id": doc["_id"]}, {"$set": {"cics_geocode": cics_data}})

            if not "nm_geocode" in doc:
                nm_data = self.__nominatim_geocode(state, district, market)
                if nm_data and len(nm_data) > 0:
                    mandi_locations.update({"_id": doc["_id"]}, {"$set": {"nm_geocode": nm_data}})

            logger.debug("Inserted new mandi location for %s %s %s" % (state, district, market))

    def create_batch_geocodes(self):
        mandi_prices = self.mongo_helper.db["mandi_prices"]
        mandi_locations = self.mongo_helper.db["mandi_locations"]
        cursor = mandi_prices.find()

        for mp in cursor:
            state = (mp["state"]).lower()
            district = (mp["district"]).lower()
            market = (mp["market"]).lower()
            query = {"state": state, "district": district, "market": market}

            logger.info("geocoding mandi %s" % mp["_id"])
            ml = mandi_locations.find_one(query)

            if ml is None:
                logger.warn("no mandi location for mandi %s, %s, %s, %s" %
                            (mp["_id"], state, district, market))
            else:
                #if not "cics_loc" in mp:
                if "cics_geocode" in ml:
                    if isinstance(ml["cics_geocode"], list):
                        score = -1
                        nm_max = None
                        for cg in ml["cics_geocode"]:
                            if int(cg["@score"]) > score:
                                nm_max = cg
                                score = int(cg["@score"])

                        if nm_max:
                            cics_loc = {
                                "type": "Point",
                                "coordinates": [float(nm_max["@lng"]), float(nm_max["@lat"])]
                            }
                            mandi_prices.update({"_id": mp["_id"]}, {"$set": {"cics_loc": cics_loc}})

                    if isinstance(ml["cics_geocode"], dict):
                        cics_loc = {
                            "type": "Point",
                            "coordinates": [float(ml["cics_geocode"]["@lng"]), float(ml["cics_geocode"]["@lat"])]
                        }
                        mandi_prices.update({"_id": mp["_id"]}, {"$set": {"cics_loc": cics_loc}})

                #if not "nm_loc" in mp:
                if "nm_geocode" in ml:
                    score = -1
                    nm_max = None
                    for nm in ml["nm_geocode"]:
                        if ("importance" in nm) and (float(nm["importance"]) > score):
                            nm_max = nm
                            score = float(nm["importance"])

                    if nm_max:
                        nm_loc = {
                            "type": "Point",
                            "coordinates": [nm_max["lon"], nm_max["lat"]]
                        }
                        mandi_prices.update({"_id": mp["_id"]}, {"$set": {"nm_loc": nm_loc}})

if __name__ == "__main__":
    config = get_config(get_env())
    geocoder = Geocoder(config=config)
    geocoder.check_mandi_locations()
    geocoder.create_batch_geocodes()
