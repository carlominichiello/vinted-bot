import logging

import pymongo

logger = logging.getLogger("database")


class Database:
    def __init__(self, config):
        self._config = config
        self._client = pymongo.MongoClient(self._config["connection_string"])

        self._check_connection()

        logger.info("Using database: %s", self._config["db_name"])
        self._db = self._client[self._config["db_name"]]
        self.items = ("id", self._db.items)
        self.users = ("id", self._db.users)

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

    def exists(self, data, collection):
        unique_key = collection[0]
        db_collection = collection[1]

        logger.debug(f"Checking if document exists in the database: {data}")
        return db_collection.find_one({unique_key: data[unique_key]}) is not None

    def update(self, data, collection):
        unique_key = collection[0]
        db_collection = collection[1]

        logger.debug(f"Updating document in the database: {data}")
        db_collection.update_one({unique_key: data[unique_key]}, {"$set": data})

    def reset(self):
        logger.debug("Resetting database")
        self._db.items.drop()
        self._db.users.drop()

    def get_no_dupes(self, collection, ids):
        no_dupes = []
        for id in ids:
            db_item = collection[1].find_one({"id": id})
            if not db_item:
                no_dupes.append(id)
        return no_dupes
