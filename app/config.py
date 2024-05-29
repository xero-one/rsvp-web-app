import os
from typing import Any
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates as fastapi_templates
from jinja2 import ( 
    Environment, 
    PackageLoader
)
from args import env




ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_WORKSPACE_NAME="backend"
load_dotenv()

# fastAPI specific template path
HTML_PAGES = os.path.join("src/page_templates")
EMAIL_HTML = "email_templates"
# FastAPI customized jinja templates specifically for server html rendering
html_page_templates = fastapi_templates(directory=HTML_PAGES)
html_page_templates.env.globals["env"] = env

email_templates = Environment(
    loader=PackageLoader(
        package_name="src", 
        package_path=EMAIL_HTML
    )
)

abs_images_path =  os.path.join(ROOT_DIR, "src", "assets", "img")


DEV_PORT = os.getenv("DEV_PORT")
DEV_HOST = os.getenv("DEV_HOST")

PROD_HOST = os.getenv("PROD_HOST")
PROD_PORT = os.getenv("PROD_PORT")
DOMAIN = os.getenv("DOMAIN")


origins = [
    f"http://localhost:{DEV_PORT}",
    f"http://localhost:{PROD_PORT}"
]


# Customize FastAPI's default logger dictionary can also be used in python "logger" module
FASTAPI_LOG_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "[%(asctime)s] %(levelname)s in %(module)s | %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "app": { 
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn": {
            "handlers": ["default"], 
            "level": "INFO", 
            "propagate": False
        },
        "uvicorn.error": {
            "level": "INFO"
        },
        "uvicorn.access": {
            "handlers": ["access"], 
            "level": "INFO", 
            "propagate": False
        }
    },
} 


# RSVP APP CONFIG SETTINGS
RSVP_EVENT_MODERATOR_CONTACT = "chadgresham@ymail.com"
"""
There is a time 'parse_date' algorithim in the sr.utils.lib that 
is set to read/parse the 'EVENT_DATE'. When setting the event date 
please be mindful of this and about the string date's format. Acceptable
dates are full month day, year time and 12 hour time denoted by PM.
The daetime format for this is '%B %d, %Y %I:%M %p'. Please be 
mindful of this when changing the format. You can refer to 
https://datatest.readthedocs.io/en/stable/how-to/date-time-str.html
for acceptable datetiem formats.
"""
RSVP_EVENT_DATE = "June 1, 2024 2:00 PM"
# RSVP_EVENT_DATE = "May 17, 2024 12:00 AM" 
RSVP_DATETIME_FORMAT = "%B %d, %Y %I:%M %p"
RSVP_EVENT_TIME_ZONE = "Eastern Time (US and Canada)"
RSVP_LIMIT = 100     # limit the amout RSVP attendees (negative numbers (depending on 'rsvp_count') and None disable the feature )


# EMAIL CONFIGS
SMTP_GMAIL_HOST = os.getenv("SMTP_GMAIL_HOST")
SMTP_GMAIL_PORT = os.getenv("SMTP_GMAIL_PORT")
RSVP_GMAIL = os.getenv("RSVP_GMAIL")
RSVP_GMAIL_APP_PASSWORD = os.getenv("RSVP_GMAIL_APP_PASSWORD")

# GMAIL SMTP CONFIG
gmail_server_login_config = {
    "host": SMTP_GMAIL_HOST,
    "port": SMTP_GMAIL_PORT,
    "username": RSVP_GMAIL,
    "password": RSVP_GMAIL_APP_PASSWORD
}

# AWS SETTINGS
class DDB_Config:
    DDB_REGION_NAME = os.getenv("AWS_DEFAULT_REGION")
    DDB_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    DDB_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

