from botocore.exceptions import ClientError
from boto3.resources.base import ServiceResource
from boto3.dynamodb.conditions import Key




class AttendeesRepository:
    def __init__(self, db: ServiceResource) -> None:
        self.__db = db

    def get_all(self):
        table = self.__db.Table("Attendees")
        response = table.scan()
        return response.get("Items", [])

    def find_attendee(self, email: str):
        try:
            table = self.__db.Table("Attendees")
            response = table.query(KeyConditionExpression=Key("email").eq(email))
            return response.get("Items")
        except ClientError as e:
            raise ValueError(e.response["Error"]["Message"])

    def get_attendee(self, email: str, last_name: str):
        try:
            table = self.__db.Table("Attendees")
            response = table.get_item(Key={"email": email, "last_name": last_name})
            print("HERE IS RESPONSE: ", response)
            return response.get("Items")
        except ClientError as e:
            raise ValueError(e.response["Error"]["Message"])

    def add_attendee(self, attendee: dict):
        table = self.__db.Table("Attendees")
        response = table.put_item(Item=attendee)
        return response

    def update_attendee(self, attendee: dict):
        table = self.__db.Table("Attendees")
        response = table.update_item(
            Key={"uid": attendee.get("email")},
            UpdateExpression="""
                set
                    email=:email,
                    first_name=:first_name,
                    last_name=:last_name,
                    virtual_attendance_option=:virtual_attendance_option
            """,
            ExpressionAttributeValues={
                ":email": attendee.get("email"),
                ":first_name": attendee.get("first_name"),
                ":last_name": attendee.get("last_name"),
                ":virtual_attendance_option": attendee.get("virtual_attendance_option")
            },
            ReturnValues="UPDATED_NEW"
        )
        return response

    def delete_attendee(self, email: str):
        table = self.__db.Table("Attendees")
        response = table.delete_item(
            Key={"email": email}
        )
        return response
    
