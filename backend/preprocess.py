import pandas as pd
from qdrant_client.models import PointStruct
import pandas as pd
from tqdm import tqdm
import db
import logging
import image_processing
logger = logging.getLogger(__name__)

def process_paintings_to_qdrant(csv_path):
    logging.basicConfig(
        level=logging.INFO,  
        format="%(asctime)s - %(levelname)s - %(message)s"  
    )
    
    try:
        client = db.connect_to_qdrant()
    except Exception as e:
        logger.error(f"Error connecting to Qdrant: {e}")
        return
    
    # Load model
    try:
        model = image_processing.load_model()
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return
    logger.info(f"Model loaded successfully")

    
    # Process CSV in chunks
    chunk_size = 1000
    for chunk in tqdm(pd.read_csv(csv_path, 
                            usecols=['Object ID', 'Title', 'Artist Display Name', 'Object Date', 'Classification', 'Link Resource'],
                            dtype={
                                'Object ID': 'int32',
                                'Title': 'string',
                                'Artist Display Name': 'string',
                                'Object Date': 'string',
                                'Classification': 'string',
                                'Link Resource': 'string'
                            },
                            chunksize=chunk_size)):
        
        # Filter dataset for paintings only
        paintings = chunk[chunk['Classification'].str.contains('Paintings', na=False)]
        
        for _, row in paintings.iterrows():
            try:
                # Get image bytes
                image_bytes = image_processing.get_image_data(row['Object ID'])
                if not image_bytes:
                    continue
                
                # Get vector from model
                vector = image_processing.transform_image_to_vector(image_bytes,model)
                logger.info(f"image {row['Object ID']} processed through model")
                
                # Create point for Qdrant
                point = PointStruct(
                    id=row['Object ID'],
                    vector=vector.tolist(),
                    payload={
                        'title': row['Title'] if pd.notna(row['Title']) else '',
                        'artist': row['Artist Display Name'] if pd.notna(row['Artist Display Name']) else '',
                        'date': row['Object Date'] if pd.notna(row['Object Date']) else '',
                        'met_url': row['Link Resource'] if pd.notna(row['Link Resource']) else ''
                    }
                )
                db.insert_data(client,[point])
            except Exception as e:
                logger.error(f"Image {row['Object ID']}: Error processing: {e}")
                continue

# Usage
process_paintings_to_qdrant(
    csv_path='MetObjects.csv',
)