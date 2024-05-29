import os
from typing import Union
from datetime import datetime
import urllib.parse
from src.logging.logging_handlers import (
    handle_info_msg,
    handle_warn_msg,
    handle_error_msg
)
from config import ( 
    email_templates,
    RSVP_DATETIME_FORMAT
)




class Data_Response:
    statuses = ( "OK", "NOT OK" )
   
    def _parse_response(
        self, 
        data,
        status_code, 
        error_msg
    ):
        res = [
            self.statuses[0], 
            {
                "status_code": 0,
                "data": None,
                "error_msg": ""
            }
        ]
        if error_msg:
            # NOT OK
            res[0] = self.statuses[1]
            res[1]["status_code"] = status_code if status_code else 1
            res[1]["error_msg"] = error_msg
        if data:
            # OK
            res[1]["data"] = data
        return tuple(res)

    def __call__(
        self,
        data = None, 
        status_code: int = 0,  
        error_msg: str = ""
     ):
        return self._parse_response(
            data=data, 
            status_code=status_code, 
            error_msg=error_msg
        )


# Image Parsing
class ImageMeta:
    from PIL import Image
    def __init__(self, filepath):
        if os.path.exists(filepath):
            self.img = self.Image.open(filepath) if os.path.splitext(filepath)[-1] != ".svg" else None
            self.width = self.img.width if self.img != None else None
            self.height = self.img.height if self.img != None else None
            self.base64 = base64Image(filepath=filepath)
            self.data = self.data()
        else:
            self.img = None
            self.width = None
            self.height = None
            self.base64 = None
            self.data = self.data()
        
    def data(self):
        return {
            "img": self.img,
            "width": self.width,
            "height": self.height,
            "base64": self. base64
        }


######### Image Helpers ###########
def base64Image(filepath: str) -> Union[str, None]:
    from base64 import b64encode
    # Status messages
    WARN_MSG=""
    ERROR_MSG=""

    if os.path.exists(filepath):
        binary_res = open(filepath, 'rb').read()
        base64_utf8_str = b64encode(binary_res).decode("utf-8")
        # File components
        ext = os.path.splitext(filepath)[-1][1:]
        return f"data:image/{ext};base64,{base64_utf8_str}"
    else:
        WARN_MSG = f"Could not convert image at '{filepath}' because it is not a valid path."
        handle_warn_msg(WARN_MSG)
        return None


######### FastAPI Helpers #########
# jinja Template handler #
def select_email_template(logging, template_name: str, context: dict={}):
    try:
        return email_templates.get_template(template_name).render(**context)
    except Exception as e:
        handle_error_msg(logging=logging, msg=e)


def base_url(url, with_path=False):
    parsed = urllib.parse.urlparse(url)
    path   = '/'.join(parsed.path.split('/')[:-1]) if with_path else ''
    parsed = parsed._replace(path=path)
    parsed = parsed._replace(params='')
    parsed = parsed._replace(query='')
    parsed = parsed._replace(fragment='')
    return parsed.geturl()


######### Datetime Helpers ########
parse_rsvp_date = lambda date_str: datetime.strptime(date_str, RSVP_DATETIME_FORMAT)
