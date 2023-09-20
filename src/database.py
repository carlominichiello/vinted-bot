import logging

import pymongo

logger = logging.getLogger("database")


class Database:
    def __init__(self, config):
        self.config = config
        self.client = pymongo.MongoClient(self.config["connection_string"])

        self.check_connection()

        logger.info("Using database: %s", self.config["db_name"])
        self.db = self.client[self.config["db_name"]]
        self.items = ("vinted_id", self.db.items)
        self.users = ("vinted_id", self.db.users)

    def check_connection(self):
        logger.info("Checking connection to the database")
        try:
            self.client.server_info()
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
        self.db.items.drop()
        self.db.users.drop()
