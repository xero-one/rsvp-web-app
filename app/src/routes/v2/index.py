from fastapi import (
    APIRouter, 
    Request, 
    Response, 
    status,
    Form
)
from src.globals.project_wide_constants import (
    EVENT_TITLE,
    EVENT_DESCRIPTION,
    EVENT_INVITE_TYPE,
    INVITE_A,
    INVITE_B,
    INVITE_FULL
)
from fastapi.responses import HTMLResponse, JSONResponse
from settings import limiter
from db.context import ddb
from src.utils.email_helpers import SendEmail
from src.repository.attendees import AttendeesRepository
from src.controllers.AttendeeDomain import AttendeeDomainController
from src.utils.lib import base_url
from config import (
    RSVP_EVENT_DATE,
    RSVP_EVENT_TIME_ZONE,
    RSVP_GMAIL,
    RSVP_EVENT_MODERATOR_CONTACT,
    gmail_server_login_config
)
from src.logging.logging_handlers import (
    config_logging_instance,
    handle_info_msg,
    handle_warn_msg,
    handle_error_msg
)




log = config_logging_instance("app")
v2_router = APIRouter(prefix="/v2")


@v2_router.post("/rsvp", response_class=HTMLResponse, status_code=200)
@limiter.limit("50/minute")
def get_rsvp_data(
    request: Request,
    first_name: str = Form(min_length=1, max_length=250),
    last_name: str = Form(min_length=1, max_length=250),
    email: str = Form(min_length=1, max_length=250),
    virtual_attendance_option: str = Form(max_length=250)
):
    # Status messages
    INFO_MSG = ""
    WARN_MSG = ""
    ERROR_MSG = ""

    # Request constants
    client_host = request.client.host
    req_path = str(request.url)
    attendance_choices = [ "by phone call", "by computer" ]

    # VALIDATE
    # If no email is provided
    if not email:
       ERROR_MSG = "No email provided. Please provide an email to send invite to."
    if virtual_attendance_option.strip() not in attendance_choices:
        ERROR_MSG = "Invalid choices for virtual attendance field."
    if ERROR_MSG:
        return JSONResponse(
            status_code=400,
            content={
                "code": status.HTTP_400_BAD_REQUEST,
                "ok": False,
                "message": ERROR_MSG,
                "data": None,
                "url": req_path
            }
        )
    
    # Establish db context with controlled methods to add to db
    conn_context = AttendeesRepository(db=ddb())
    domain_ctrl = AttendeeDomainController(repository=conn_context)

    # Check if user exists
    find_email = domain_ctrl.find_attendee(email=email.lower())
    if len(find_email) > 0:
        ERROR_MSG = "An attendee with that email already exists. Please try again."
        return JSONResponse(
                status_code=400,
                content={
                    "code": status.HTTP_400_BAD_REQUEST,
                    "ok": False,
                    "message": ERROR_MSG,
                    "data": None,
                    "url": req_path
                }
            )
    domain_ctrl.add_attendee(attendee={
        "email": email.lower(),
        "first_name": first_name.lower(),
        "last_name": last_name.lower(),
        "virtual_attendance_option": virtual_attendance_option
    })


    # BEGIN PROCESSING
    try:
        event_title =  EVENT_TITLE
        event_description = EVENT_DESCRIPTION
        event_date = " ".join([ RSVP_EVENT_DATE.strip(), RSVP_EVENT_TIME_ZONE.strip() ])
        event_invite_type = EVENT_INVITE_TYPE
        by_phone_instructions = INVITE_A
        by_computer_instructions = INVITE_B
        full_rsvp_invite_data = INVITE_FULL

        client_rsvp_invite = {
            "Sender": ( 'RSVP MEMORIAL', RSVP_GMAIL ),
            "TO": email,
            "Subject": f"{event_title} {event_invite_type}",
            "Template": "RSVP_ZOOM_INVITE.HTML",
            "Body": { 
                "event_img": base_url(req_path) + "/assets/img/person/chip-decrative-piece-LIGHT-BACKGROUND.png",
                "event_title": event_title,
                "type_invite": event_invite_type,
                "event_date": event_date,
                "attendance_type": virtual_attendance_option,
                "first_name": first_name,
                "last_name": last_name,
                "instructions": by_phone_instructions if virtual_attendance_option == attendance_choices[0] else by_computer_instructions,
                "full_invite": full_rsvp_invite_data,
                "event_moderator_email_contact": RSVP_EVENT_MODERATOR_CONTACT,
                "home_url": base_url(req_path)
            }
        }
        email_to_client = SendEmail(
            SMTP_config=gmail_server_login_config,
            email_dict= client_rsvp_invite
        )

        # Fake object
        # res_status, res_data = ( "OK", {"data": "Looks good"})
        res_status, res_data = email_to_client

        if res_status == "OK":
            return JSONResponse(
                status_code=200,
                content={
                    "code": status.HTTP_200_OK,
                    "ok": True,
                    "message": "",
                    "data": None, 
                    "url": req_path
                }
            )
        else:
            # Is "res_data" a dictionary response
            if type(res_data) == dict and res_data.get("error_msg"):
                ERROR_MSG = res_data.get("error_msg")
            handle_error_msg(logging=log, msg=ERROR_MSG)
            
            return JSONResponse(
                status_code=500,
                content={
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "ok": False,
                    "message": ERROR_MSG,
                    "data": None,
                    "url": req_path
                }
            )
    except Exception as e:
        ERROR_MSG = e
        handle_error_msg(logging=log, msg=ERROR_MSG)
        return JSONResponse(
            status_code=500,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "ok": False,
                "message": ERROR_MSG,
                "data": None,
                "url": req_path
            }
        )
    