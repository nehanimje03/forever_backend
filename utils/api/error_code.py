# Standard Library Imports
import json

# Third-Party Imports
from dotenv import load_dotenv
from decouple import config

load_dotenv()

# -------- Load JSON Configs -------- #
OWN_ERROR_CODE = json.loads(config("OWN_ERROR_CODE"))
OWN_SUCCESS_CODE = json.loads(config("OWN_SUCCESS_CODE"))

THIRD_SUCCESS_CODE = json.loads(config("THIRD_SUCCESS_CODE"))
THIRD_ERROR_CODE = json.loads(config("THIRD_ERROR_CODE"))

# -------- Commonly Used Codes -------- #
SUCCESS = OWN_SUCCESS_CODE.get("200")
CREATED = OWN_SUCCESS_CODE.get("201")

BAD_REQUEST = OWN_ERROR_CODE.get("400")
UNAUTHORIZED = OWN_ERROR_CODE.get("401")
NOT_FOUND = OWN_ERROR_CODE.get("404")
INTERNAL_SERVER_ERROR = OWN_ERROR_CODE.get("500")
