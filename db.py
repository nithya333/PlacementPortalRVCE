from pymongo import MongoClient
import os

# Singleton MongoDB client
class MongoDBClient:
    _client = None

    @staticmethod
    def get_client():
        if MongoDBClient._client is None:
            # Initialize MongoDB client if not created already 
            uri = 'mongodb+srv://?retryWrites=true&w=majority&appName=cluster_name'  # Use your MongoDB URI here
            
            MongoDBClient._client = MongoClient(uri)
        return MongoDBClient._client


# Utility function to get database
def get_db():
    client = MongoDBClient.get_client()
    return client['Placement']
