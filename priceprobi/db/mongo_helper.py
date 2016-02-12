__author__ = 'ujjwal'

import pymongo
import time


class MongoHelper():
    def __init__(self, config, db_name=None):
        host = config["MONGO_HOST"]
        port = config["MONGO_PORT"]
        if db_name:
            ogd_db = db_name
        else:
            ogd_db = config["MONGO_DBNAME"]

        client = pymongo.MongoClient(host=host, port=port)
        self.db = client[ogd_db]

    def save(self, collection_name, docs):
        for doc in docs:
            self.db[collection_name].insert(doc)

    def rename_collection(self, old_name, new_name=None):
        for coll_name in self.db.collection_names(include_system_collections=False):
            if coll_name == old_name:
                if new_name is None:
                    new_name = "%s_%s" % (coll_name, str(long(time.time())))
                self.db[old_name].rename(new_name)

