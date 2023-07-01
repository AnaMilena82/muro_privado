

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
        self.reciever_id = db_data['reciever_id']
        self.message_created_at = db_data['message_created_at']
        self.message_updated_at = db_data['message_updated_at']

    @classmethod
    def get_user_messages(cls,user_id):

        # Fetch the user to associate with all the message objects
        reciever = User.get_user_by_id(user_id)

        # Query for all messages, with the sender's user data
        query = """SELECT messages.*,
                first_name, last_name, email
                FROM messages
                JOIN users on messages.sender_id = users.id
                WHERE receiver_id =  %(id)s"""
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
                "created_at": message["message_created_at"],
                "updated_at": message["message_updated_at"],
            }
            sender = User(sender_data)

            # Make the message object
            message = {
                "id": message["id"],
                "content": message["content"],
                "sender": sender,
                "reciever": reciever,
                "created_at": message["message_created_at"],
                "updated_at": message["message_updated_at"],
            }
            messages.append( cls(message) )

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
        delta = now - self.created_at
        
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif (math.floor(delta.total_seconds() / 60)) >= 60:
            return f"{math.floor(math.floor(delta.total_seconds() / 60)/60)} hours ago"
        elif delta.total_seconds() >= 60:
            return f"{math.floor(delta.total_seconds() / 60)} minutes ago"
        else:
            return f"{math.floor(delta.total_seconds())} seconds ago"