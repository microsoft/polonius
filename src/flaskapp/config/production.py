import os

import pymongo

# Create a mongoDB Connection
client = pymongo.MongoClient("DATABASE_CONNECTION_STRING")
DEBUG = False


if "WEBSITE_HOSTNAME" in os.environ:
    ALLOWED_HOSTS = [os.environ["WEBSITE_HOSTNAME"]]
else:
    ALLOWED_HOSTS = []


DATABASE_URI = os.environ["AZURE_COSMOS_CONNECTION_STRING"]
