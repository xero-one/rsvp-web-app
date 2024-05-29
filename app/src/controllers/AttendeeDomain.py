from uuid import uuid4
from pydantic import Field
from decimal import Decimal
from pydantic import BaseModel
from pydantic.types import UUID4
from typing import List, Optional, Literal
from src.repository.attendees import AttendeesRepository




class AttendeeModel(BaseModel):
    email: str = Field(..., example="don@mafia.com")
    first_name: str = Field(..., examples="John")
    last_name: str = Field(..., example="Doe")
    virtual_attendance_option: str = Literal["by phone call", "by computer"]


class AttendeeDomainController():
    def __init__(self, repository: AttendeesRepository) -> None:
        self.__repository = repository

    def get_all(self):
        return self.__repository.get_all()
    
    def find_attendee(self, email: str):
        return self.__repository.find_attendee(email=email)
    
    def get_attendee(self, email: str, last_name: str):
        return self.__repository.get_attendee(email=email, last_name=last_name)

    def add_attendee(self, attendee: AttendeeModel):
        return self.__repository.add_attendee(attendee=attendee)

    def update_attendee(self, attendee: AttendeeModel):
        return self.__repository.update_attendee(attendee=attendee)

    def delete_attendee(self, email: str):
        return self.__repository.delete_recipe(email=email)
    
