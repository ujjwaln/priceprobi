# priceprobi
Agricultural Commodity prices monitoring app

angularjs client:
consists of ppapp which is a angular-material based client that uses leaflet directive for mapping. see src/js/controller.js
and src/js/app.js


python backend:
priceprobi/ingest folder contains python code for downloading commodity prices from data.gov.in using its
 1. api endpoint: see ingest/ogd_api_ingestor.py (api doesn't seem to be returning more than 100 commodity prices
 2. raw xml file: see ingest/ogd_xml_ingestor.py (xml endpoint seems to have all the commodities)

 both ingestors download and parse data and save to mongodb

priceprobi/geocoding/geocoder.py has code for geocoding commodity mandi (godown) addresses using
nominatim http://open.mapquestapi.com/nominatim/v1/search.php
and CICS http://india.csis.u-tokyo.ac.jp/geocode-cgi/census_ajax_json.cgi

priceprobi/api/pp_api.py contains the Eve REST api application.