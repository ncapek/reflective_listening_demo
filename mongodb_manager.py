from datetime import datetime

from pymongo import MongoClient


class MongoPersistence:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client[
            "chatbot_database"
        ]  # Change 'chatbot_database' to your database name
        self.conversations = self.db[
            "conversations"
        ]  # Change 'conversations' to your collection name

    def save_conversation(self, conversation):
        """Saves the conversation to MongoDB."""
        conversation_data = {
            "conversation": conversation.to_dict(),
            "timestamp": datetime.now(),
        }
        self.conversations.insert_one(conversation_data)
        print("Conversation saved to MongoDB.")
