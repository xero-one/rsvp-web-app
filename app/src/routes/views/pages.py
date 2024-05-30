from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from db.context import ddb
from src.repository.attendees import AttendeesRepository
from src.controllers.AttendeeDomain import AttendeeDomainController
from config import ( 
    html_page_templates,
    PAGE_RATE_LIMIT,
    RSVP_EVENT_DATE,
    RSVP_LIMIT,
    RSVP_EVENT_TIME_ZONE
)
from src.utils.lib import parse_rsvp_date
from settings import limiter




router = APIRouter(tags=["views"])


# Home page
@router.get("/", response_class=HTMLResponse)
@limiter.limit(limit_value=f"{PAGE_RATE_LIMIT}/minute")
def home_page(request: Request) -> HTMLResponse:
    detailed_event_date = " ".join([ RSVP_EVENT_DATE.strip(), RSVP_EVENT_TIME_ZONE.strip() ])
    rsvp_end_date = parse_rsvp_date(date_str=RSVP_EVENT_DATE) if RSVP_EVENT_DATE else RSVP_EVENT_DATE
    todays_date = datetime.now()
    rsvp_count = None
    rsvp_enabled = True

    if type(rsvp_end_date) == datetime and todays_date < rsvp_end_date:
        conn_context = AttendeesRepository(db=ddb())
        domain_ctrl = AttendeeDomainController(repository=conn_context)

        all_attendees = domain_ctrl.get_all()
        rsvp_count = len(all_attendees)
    else:
        rsvp_enabled = False

    return html_page_templates.TemplateResponse(
        "home.html", 
        {
            "request": request,
            "event_date": detailed_event_date,
            "rsvp_enabled": rsvp_enabled,
            "rsvp_count": rsvp_count, 
            "rsvp_limit": RSVP_LIMIT
        })

