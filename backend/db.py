from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
import logging
from dotenv import load_dotenv
logger = logging.getLogger(__name__)
load_dotenv()

def connect_to_qdrant():
    qdrant_client = QdrantClient(
        location=os.getenv('DATABASE_URL'),
        api_key=os.getenv('API_KEY'),
    )
    return qdrant_client
def create_collection(collection_name,qdrant_client):
    logging.basicConfig(
        level=logging.INFO,  
        format="%(asctime)s - %(levelname)s - %(message)s"  
    )
    qdrant_client.create_collection(
        collection_name=os.getenv('COLLECTION_NAME'),
        vectors_config=VectorParams(size=2048, distance=Distance.COSINE),
    )
    logger.info(f"Collection {collection_name} created successfully")
def insert_data(qdrant_client, data):
    logging.basicConfig(
        level=logging.INFO,  
        format="%(asctime)s - %(levelname)s - %(message)s"  
    )
    try:
        qdrant_client.upsert(
            collection_name=os.getenv('COLLECTION_NAME'),
            points=data,
        )
        logger.info(f"Point with ID {data[0].id} inserted into collection successfully")
    except Exception as e:
        logger.error(f"Error inserting data: {e}")