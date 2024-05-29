from src.logging.logging_handlers import (
    config_logging_instance,
    handle_info_msg,
    handle_warn_msg,
    handle_error_msg
)




log = config_logging_instance("app")


def generate_tables(ddb):
    tb_attendees = "Attendees"
    current_table_names = [table.name for table in ddb.tables.all()]

    if tb_attendees not in current_table_names:
        print(f"'{tb_attendees}' not found. Creating it.")
        handle_info_msg(logging=log, msg=f"'{tb_attendees}' not found. Creating it.")
        try:
            ddb.create_table(
                TableName=tb_attendees,                
                AttributeDefinitions=[
                    {
                        "AttributeName": "email", 
                        "AttributeType": "S"       
                    },
                    {
                        "AttributeName": "last_name", 
                        "AttributeType": "S"       
                    }
                ],
                KeySchema=[
                    {
                        "AttributeName": "email",
                        "KeyType": "HASH"
                    },
                    {
                        "AttributeName": "last_name",
                        "KeyType": "RANGE"
                    }
                ],
                ProvisionedThroughput={             # specying read and write capacity units
                    "ReadCapacityUnits": 10,        # these two values really depend on the app's traffic
                    "WriteCapacityUnits": 10
                }
            )
            handle_info_msg(logging=log, msg=f"'{tb_attendees}' table created successfully.")
        except Exception as e:
            handle_error_msg(logging=log, msg=f"Failed to create '{tb_attendees}' table -- {e}")
    else:
        print(f"No need to init db tables exist.")
        handle_info_msg(logging=log, msg=f"No need to init db tables exist.")

