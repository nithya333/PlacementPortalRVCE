from pymongo import MongoClient
import os

# Singleton MongoDB client
class MongoDBClient:
    _client = None

    @staticmethod
    def get_client():
        if MongoDBClient._client is None:
            # Initialize MongoDB client if not created already
            # uri = os.getenv('MONGO_URI', 'mongodb+srv://?retryWrites=true&w=majority&appName=Cluster0Charitham')  # Use your MongoDB URI here
            uri = 'mongodb+srv://nithya3169:MTUsn5fNh1xOurY5@cluster0charitham.hdany.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0Charitham'  
            
            MongoDBClient._client = MongoClient(uri)
        return MongoDBClient._client


# Utility function to get database
def get_db():
    client = MongoDBClient.get_client()
    return client['Placement']
