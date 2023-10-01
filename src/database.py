import logging
from collections import namedtuple

import pymongo

logger = logging.getLogger("database")


Collection = namedtuple("Collection", ["unique_key", "db_collection"])


class Database:
    def __init__(self, config):
        self._config = config
        self._client = pymongo.MongoClient(self._config["connection_string"])

        self._check_connection()

        logger.info("Using database: %s", self._config["db_name"])
        self._db = self._client[self._config["db_name"]]
        self.items = Collection("id", self._db.items)
        self.users = Collection("id", self._db.users)

    def _check_connection(self):
        logger.info("Checking connection to the database")
        try:
            self._client.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            logger.error("Couldn't connect to the database")
            raise ConnectionError
        except pymongo.errors.OperationFailure:
            logger.error("Couldn't authenticate to the database")
            raise ConnectionError
        logger.info("Successfully connected to the database")

    def insert(self, data, collection):
        logger.debug("Inserting document into the database: %s", data)
        if self.exists(data, collection):
            logger.debug("Document already exists in the database")
            logger.debug("Updating document")
            self.update(data, collection)
        else:
            logger.debug("Document doesn't exist in the database")
            logger.debug("Inserting document")
            collection[1].insert_one(data)

    def exists(self, data, collection: Collection):
        logger.debug(f"Checking if document exists in the database: {data}")
        return collection.db_collection.find_one({collection.unique_key: data[collection.unique_key]})

    def update(self, data, collection):
        logger.debug(f"Updating document in the database: {data}")
        collection.db_collection.update_one(
            {collection.unique_key: data[collection.unique_key]}, {"$set": data}, upsert=True
        )

    def reset(self):
        logger.debug("Resetting database")
        self.items.db_collection.drop()
        self.users.db_collection.drop()

    def get_no_dupes(self, collection, ids):
        no_dupes = []
        for id in ids:
            db_item = collection.db_collection.find_one({"id": id})
            if not db_item:
                no_dupes.append(id)
        return no_dupes
