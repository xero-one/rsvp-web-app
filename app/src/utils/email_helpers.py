import smtplib
from email.utils import formataddr
from email.message import (
    Message,
    EmailMessage 
)
from starlette.datastructures import UploadFile
from src.logging.logging_handlers import (
    config_logging_instance,
    handle_info_msg,
    handle_warn_msg,
    handle_error_msg
)
from src.utils.lib import ( 
    Data_Response,
    select_email_template 
)




log = config_logging_instance("app")


def SMTP_Service(
    host: str, 
    port: int,
    username: str,
    password: str,
    useSSL = False
) -> dict:
    # Status messages
    INFO_MSG = ""
    WARN_MSG = ""
    ERROR_MSG = ""

    # Inits
    server_conn_data = None
    res = Data_Response()
    
    if useSSL:
        server = smtplib.SMTP_SSL(host=host, port=port)
    else:
        server = smtplib.SMTP(host=host, port=port)
        # server.ehlo(name=host)
        server.starttls()
    server_conn_data = server

    # Generic SMTP server login. Useful for non-commercial or personal servers
    if all((host, port, username, password)):
        if server:
            try:
                server.login(user=username, password=password)
                server_conn_data = ( "GENERIC SMTP", server )
            except Exception:
                handle_error_msg(logging=log, msg=ERROR_MSG)
    else:  
        ERROR_MSG = "No smtp host settings detected. Please enter credentials to use smtp."
        handle_error_msg(logging=log,msg=ERROR_MSG)

    return res(data=server_conn_data, error_msg=ERROR_MSG)


def PrepEmail(email_dict: dict):
    # Status messages
    INFO_MSG=""
    WARN_MSG=""
    ERROR_MSG=""

    if type(email_dict) != dict:
        INFO_MSG = "No email dict detected"
        handle_info_msg(logging=log, msg=INFO_MSG)
        return None

    # Inits

    INFO_MSG = f"Preping to send email.........................."
    handle_info_msg(logging=log, msg=INFO_MSG)
    email_msg = EmailMessage()

    From = email_dict.get("Sender")
    TO = email_dict.get("TO")
    CC = email_dict.get("CC")
    Subject = email_dict.get("Subject")
    Body = email_dict.get("Body")
    Template = email_dict.get("Template")
    Attachments = email_dict.get("Attachments")
    type_of_email = email_dict.get("email_type")
    
    # From (Can only be a string)
    if type(From) == str and From:
        email_msg["From"] = From
    elif type(From) == tuple and From:
        email_msg["From"] = formataddr(From)
    else:
        WARN_MSG = f"No Sender explicitly set..."
        handle_warn_msg(logging=log, msg=WARN_MSG)

    # TO
    if type(TO) == str and TO:
        email_msg["To"] = TO
    elif any(( type(TO) == tuple, type(TO) == list )):
        if len(TO) > 0:
            email_msg["To"] = ', '.join(TO)
        else:
            ERROR_MSG = f"NO RECIPIENT LIST DETECTED ('TO') please enter an email(s) to send email to."
            handle_error_msg(logging=log, msg=ERROR_MSG)
            return
    else:
        ERROR_MSG = f"NO RECIPIENT LIST DETECTED ('TO') please enter an email(s) to send email to."
        handle_error_msg(logging=log, msg=ERROR_MSG)

     # CC
    if type(CC) == str and CC:
        email_msg["Cc"] = CC
    elif any(( type(CC) == tuple, type(CC) == list )):
        if len(CC) > 0:
            email_msg["Cc"] = ', '.join(CC)

    # Set subject
    email_msg["Subject"] = Subject
  
    # Set Body
    if Body:
        if Template is None:
            email_msg.set_content(Body)
        else:  
            content_keys = [
                "to", 
                "subject", 
                "attachments"
            ]
            content = [ 
                TO, 
                Subject,  
                Attachments
            ]
            content = dict(zip(content_keys, content))
            if type(Body) in (list, tuple):
                Body = { f"var_{idx+1}":x for idx, x in enumerate(content["Body"]) }
            content.update(Body)
            email_msg.add_alternative(
                select_email_template(
                    logging=log,
                    template_name=Template,
                    context=content
                ),
                subtype = "html"
            )
    ### ToDo Add attachments algorithim
    if Attachments:
        if type(Attachments) != list:
            Attachments =  [Attachments] 
        for attachment in Attachments:
            if isinstance(attachment, UploadFile):
                filename = attachment.filename
                content_type = attachment.content_type
                mimetype = f".{content_type.split('/')[-1]}" if type(content_type)==str and "/" in content_type else None
                bytes_data = attachment.file.read()
                email_msg.add_attachment(
                    bytes_data,
                    maintype=content_type,
                    subtype=mimetype,
                    filename=filename
                )
    return email_msg


def SendEmail(
    SMTP_config: dict,
    email_dict: dict,
) -> None:
    # Status messages
    INFO_MSG = ""
    WARN_MSG = ""
    ERROR_MSG = ""
    # Inits
    server_conn_data = None
    res = Data_Response()

    # Check SMTP_config
    if type(SMTP_config) != dict:
        ERROR_MSG = "No SMTP Service connection data detected, aborting..."
    if bool(SMTP_config.get("username") == False):
        ERROR_MSG += "Username required to connect to SMTP service."
    if bool(SMTP_config.get("password") == False):
        ERROR_MSG += "Password required to connect to SMTP service."
    
    if ERROR_MSG:
        return res(data=None, error_msg=ERROR_MSG) 
    
    # Check email_dict
    if type(email_dict) != dict:
        ERROR_MSG = "No email data (dictionary) detected aborting, nothing to send."
    if bool(email_dict.get("Sender")) == False:
        ERROR_MSG += "No 'Sender' for email object. Please provide a Sender for this email."
    if bool(email_dict.get("TO")) == False:
        ERROR_MSG += "No 'recipient' (To) set to receive email object. Please provide a 'recipient' to send email object to." 
   
    email_msg = PrepEmail(email_dict=email_dict)
    if not email_msg:
        ERROR_MSG += "Failed to parse email data (dictionary). Please make sure you set mandatory 'Sender', 'To', and 'Template' fields for parsing."
   
    if ERROR_MSG:
        return res(data=None, error_msg=ERROR_MSG) 
    
    def smtp_operations():
        # SMTP lib operations...
        smtp_status, smtp_res = SMTP_Service(
            host=SMTP_config.get("host"),
            port=SMTP_config.get("port"),
            username=SMTP_config.get("username"),
            password=SMTP_config.get("password")
        )
        if smtp_status == "OK":
            service, smtp_server = smtp_res["data"]
            # Gnereic SMTP service
            if service == "GENERIC SMTP":
                try:
                    smtp_server.send_message(
                        from_addr=email_dict.get("From"),
                        to_addrs=email_dict.get("To"),
                        msg=email_msg
                    )
                    smtp_server.quit()
                    INFO_MSG = f"Email sent successfully"
                    handle_info_msg(logging=log, msg=INFO_MSG)
                    return res(data=None, error_msg=None)
                except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, IOError):
                    smtp_operations()
                    INFO_MSG = "Connection is broken. Restablishing a new connection :) "
                    handle_info_msg(logging=log, msg=INFO_MSG)
            # ADD MORE SMTP SERVICES HERE IF THERE ARE ANY SPECIALIZED ONES
            else:
                ERROR_MSG = "No known service detected in data response object."
                handle_error_msg(logging=log, msg=ERROR_MSG)
                return res(data=None, error_msg=ERROR_MSG)
    
        elif smtp_status == "NOT OK":
            # return what went wrong to t
            ERROR_MSG = smtp_res["error_msg"]
            return res(data=None, error_msg=ERROR_MSG)  

    INFO_MSG = f"Beginning to send '{email_dict.get('Subject') if email_dict.get('Subject') else 'message'}'..."
    handle_info_msg(logging=log, msg=INFO_MSG)
        
    return smtp_operations()
    
