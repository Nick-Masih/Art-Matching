from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
import logging
from dotenv import load_dotenv

load_dotenv()
class DatabaseManager:
    def __init__(self):
        self.client = QdrantClient(
            location=os.getenv('DATABASE_URL'),
            api_key=os.getenv('API_KEY'),
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Connected to Qdrant")

    def create_collection(self):
        """Create a collection based on env var name in Qdrant."""
        try:
            self.client.create_collection(
                collection_name=os.getenv('COLLECTION_NAME'),
                vectors_config=VectorParams(size=2048, distance=Distance.COSINE),
            )
            self.logger.info(f"Collection {os.getenv('COLLECTION_NAME')} created successfully")
        except Exception as e:
            self.logger.error(f"Error creating collection: {e}")
            raise

    def insert_data(self, data):
        """Insert data into Qdrant in batches."""
        try:
                self.client.upsert(
                    collection_name=os.getenv('COLLECTION_NAME'),
                    points=data
                )
                self.logger.info(f"Inserted batch of {len(data)} points")
        except Exception as e:
            self.logger.error(f"Error inserting data: {e}")
            raise

    def search(self, vector, limit):
        """Search for similar vector data."""
        try:
            return self.client.search(
                collection_name=os.getenv('COLLECTION_NAME'),
                query_vector=vector,
                limit=limit
            )
        except Exception as e:
            self.logger.error(f"Error searching: {e}")
            raise
