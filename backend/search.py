import logging
import db
import image_processing 
from dotenv import load_dotenv
logger = logging.getLogger(__name__)
load_dotenv()

async def search_similar_paintings(image_bytes, top_k=5):
    logging.basicConfig(
        level=logging.INFO,  
        format="%(levelname)s - %(message)s"  
    )
    image_processor = image_processing.ImageProcessor() 
    try:        
        # Transform uploaded image to vector
        vector = image_processor.transform_image_bytes_to_vectors(image_bytes)
        if vector is None:
            return None
        logger.info(f"Vector created successfully")

        # Ensure vector is in the correct format (flatten if necessary)
        if isinstance(vector, list) and isinstance(vector[0], list):
            vector = vector[0]  # Flatten the vector if it's a list of lists

        # Connect to Qdrant
        db_manager = db.DatabaseManager()
        
        # Search for similar vectors
        logger.info("Searching for similar paintings")
        search_result = db_manager.search(vector, top_k)
        logger.debug(f"Search result: {search_result}")
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
    finally:
        await image_processor.close()  # Await the close method
    