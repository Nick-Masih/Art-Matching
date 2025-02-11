import logging
import db
import image_processing 
import os
from dotenv import load_dotenv
logger = logging.getLogger(__name__)
load_dotenv()
def search_similar_paintings(image_bytes, top_k=5):
    logging.basicConfig(
        level=logging.INFO,  
        format="%(asctime)s - %(levelname)s - %(message)s"  
    )
    try:
        logger.info("Loading model")
        model = image_processing.load_model()
        
        # Transform uploaded image to vector
        vector = image_processing.transform_image_to_vector(image_bytes, model)
        logger.info(f"Vector created successfully")
        
        # Connect to Qdrant
        logger.info("Connecting to Qdrant")
        qdrant_client = db.connect_to_qdrant()
        
        # Search for similar vectors
        logger.info("Searching for similar paintings")
        search_result = qdrant_client.search(
            collection_name=os.getenv('COLLECTION_NAME'),
            query_vector=vector.tolist(),
            limit=top_k
        )

        similar_paintings = []
        for result in search_result:
            similar_paintings.append({
                'id': result.id,
                'score': result.score,
                'title': result.payload.get('title', ''),
                'artist': result.payload.get('artist', ''),
                'date': result.payload.get('date', ''),
                'met_url': result.payload.get('met_url', '')
            })
            
        return similar_paintings
        
    except Exception as e:
        logger.error(f"Error searching similar paintings: {e}")
        return None
