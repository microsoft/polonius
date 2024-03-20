"""Module configuring development environment."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

load_dotenv(override=True)

# dbuser = os.environ["MONGODB_USERNAME"]
# dbpass = os.environ["MONGODB_PASSWORD"]
# dbhost = os.environ["MONGODB_HOST"]
# dbname = os.environ["MONGODB_DATABASE"]
# DATABASE_URI = f"mongodb://{dbuser}:{dbpass}@{dbhost}/{dbname}?authSource=admin"
DATABASE_URI = os.environ["AZURE_COSMOS_CONNECTION_STRING"]
TIME_ZONE = "UTC"
