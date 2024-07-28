from dotenv import load_dotenv
import os

load_dotenv()

APPID = os.getenv("APPID")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")
account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
weatherAPI_endpoint = os.getenv("weatherAPI_endpoint")
geocoder_endpoint = os.getenv("geocoder_endpoint")
target_number = os.getenv("target_number")
base_number = os.getenv("base_number")


weatherAPI_params={
    "lat" : "44.42",
    "lon" : "26.10",
    "cnt" : "4",
    "appid" : APPID
}

connection_params = {
    "database" : DB_NAME,
    "user" : DB_USER,
    "password" : DB_PASS,
    "host" : DB_HOST,
    "port" : "5432"
}