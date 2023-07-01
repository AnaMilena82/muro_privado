

from app_private_wall.config.mysqlconnection import connectToMySQL
from datetime import datetime
from app_private_wall.models.model_users import User
from app_private_wall import app,BASE_DE_DATOS
import math

class Message:
    def __init__(self,db_data):
        self.id = db_data['id']
        self.content = db_data['content']
        self.sender_id = db_data['sender_id']
        self.receiver_id = db_data['receiver_id']
        self.message_created_at = db_data['message_created_at']
        self.message_updated_at = db_data['message_updated_at']

    @classmethod
    def get_user_messages(cls,user_id):

        # Fetch the user to associate with all the message objects
        receiver = User.get_user_by_id(user_id)

        # Query for all messages, with the sender's user data
        query = """
        SELECT messages.*,
            users.id AS sender_id,
            users.first_name,
            users.last_name,
            users.email,
            users.password,
            users.fech_nac,
            users.country_nac,
            users.created_at AS user_created_at,
            users.updated_at AS user_updated_at
        FROM messages
        JOIN users ON messages.sender_id = users.id
        WHERE receiver_id = %(id)s
        """
        results = connectToMySQL(BASE_DE_DATOS).query_db(query,{"id": user_id})

        # Create and populate a list of message objects
        messages = []

        for message in results:
            # Make the sender object
            sender_data = {
                "id": message["sender_id"],
                "first_name": message["first_name"],
                "last_name": message["last_name"],
                "email": message["email"],
                "password": message["password"],
                "fech_nac": message["fech_nac"],
                "country_nac": message["country_nac"],
                "created_at": message["user_created_at"],
                "updated_at": message["user_updated_at"],
            }
            sender = User(sender_data)

            # Make the message object
            message_data  = {
                "id": message["id"],
                "content": message["content"],
                "sender_id": sender,
                "receiver_id": receiver,
                "message_created_at": message["message_created_at"],
                "message_updated_at": message["message_updated_at"],
                "sender_first_name": message["first_name"], 
            }
            messages.append( cls(message_data) )

        return messages

    @classmethod
    def new_message(cls,data):
        query = "INSERT INTO messages (content,sender_id,receiver_id) VALUES (%(content)s,%(sender_id)s,%(receiver_id)s);"
        return connectToMySQL(BASE_DE_DATOS).query_db(query,data)

    @classmethod
    def delete_message(cls, message_id):
        query = "DELETE FROM messages WHERE messages.id = %(id)s;"
        return connectToMySQL(BASE_DE_DATOS).query_db(query,{"id": message_id})

    def time_span(self):
        now = datetime.now()
        delta = now - self.message_created_at
        
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif (math.floor(delta.total_seconds() / 60)) >= 60:
            return f"{math.floor(math.floor(delta.total_seconds() / 60)/60)} hours ago"
        elif delta.total_seconds() >= 60:
            return f"{math.floor(delta.total_seconds() / 60)} minutes ago"
        else:
            return f"{math.floor(delta.total_seconds())} seconds ago"
        
 