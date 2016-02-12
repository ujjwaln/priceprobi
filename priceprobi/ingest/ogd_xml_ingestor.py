__author__ = 'ujjwal'
import os
import requests
import xmltodict
from datetime import datetime
from priceprobi.config import OGD, data_dir, get_config
from priceprobi.utils import get_env
from priceprobi.db.mongo_helper import MongoHelper
from priceprobi import logger


def download_file():
    dl_url = OGD["mandi_prices_xml_url"]
    try:
        req = requests.get(dl_url)
    except:
        logger.critical("Error while downloading %s" % dl_url)
        raise

    dl_file_name = os.path.join(data_dir,
            "%s_%s.xml" % (os.path.splitext(os.path.basename(dl_url))[0], datetime.now().strftime("%y-%m-%d")))
    if os.path.exists(dl_file_name):
        logger.debug("Deleted existing file %s" % dl_file_name)
        return False

    with open(dl_file_name, "w") as dlf:
        dlf.write(req.text)

    return dl_file_name


def run_ingest(config, xmlfile):

    with open(xmlfile, 'rb') as f:
        xmlstr = f.read()

    xmldict = xmltodict.parse(xmlstr)
    tables = xmldict["soap:Envelope"]["soap:Body"]["showResponse"]["showResult"]["diffgr:diffgram"]["NewDataSet"]["Table"]
    data = []
    for t in tables:
        obj = {
            "arrival_date": t["Arrival_Date"],
            "district": t["District"],
            "market": t["Market"],
            "max_price": t["Max_x0020_Price"],
            "min_price": t["Min_x0020_Price"],
            "modal_price": t["Modal_x0020_Price"],
            "state": t["State"],
            "variety": t["Variety"]
        }

        if "Commodity" in t:
            obj["commodity"] = t["Commodity"]
        elif "Column1" in t:
            obj["commodity"] = t["Column1"]
        else:
            logger.warn("Commodity not found in %s" % t["@diffgr:id"])
            continue

        logger.debug("Inserted %s %s %s" % (obj["commodity"], obj["market"], obj["arrival_date"]))
        data.append(obj)

    mongo_helper = MongoHelper(config)
    mongo_helper.rename_collection("mandi_prices")
    mongo_helper.save("mandi_prices", docs=data)


if __name__ == "__main__":
    config = get_config(env=get_env())
    xmlfile = download_file()
    if xmlfile:
        logger.info("Downloaded %s" % xmlfile)
        run_ingest(config, xmlfile)
    else:
        logger.warn("Latest file %s already ingested" % xmlfile)