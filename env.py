from tinydb import TinyDB, Query
from dotenv import load_dotenv
import os

load_dotenv()
db = TinyDB(os.getenv('DB_PATH'))
