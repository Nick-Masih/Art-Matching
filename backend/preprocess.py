from huggingface_hub import create_collection
import pandas as pd
from qdrant_client.models import PointStruct
import pandas as pd
from tqdm import tqdm
import db
import logging
from image_processing import ImageData, ImageProcessor
from dotenv import load_dotenv
from time import sleep
import asyncio
logger = logging.getLogger(__name__)

async def process_paintings_to_qdrant(csv_path, batch_size=128):
    logging.basicConfig(
        level=logging.INFO,  
        format="%(levelname)s - %(message)s"  
    )
    
    db_manager = db.DatabaseManager()
    image_processor = ImageProcessor()
    logger.info("Model loaded successfully")
    points_batch = []
    
    try:
        # Process CSV in chunks
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
                                chunksize=1000)):
            
            # Process images in batches
            for i in range(0, len(chunk), batch_size):
                batch = chunk.iloc[i:i + batch_size]
                batch_image_data = []
                object_ids = batch['Object ID'].tolist()

                image_bytes_list = await image_processor.get_batch_images(object_ids)
                # Collect batch data
                for index, (idx, row) in enumerate(batch.iterrows()):  # Unpack correctly
                    image_bytes = image_bytes_list[index]  # Get corresponding image bytes
                    try:
                        if image_bytes:
                            metadata = {
                                'id': row['Object ID'],  # Accessing the Series correctly
                                'title': row['Title'] if pd.notna(row['Title']) else '',
                                'artist': row['Artist Display Name'] if pd.notna(row['Artist Display Name']) else '',
                                'date': row['Object Date'] if pd.notna(row['Object Date']) else '',
                                'met_url': row['Link Resource'] if pd.notna(row['Link Resource']) else ''
                            }
                            # Create an ImageData object
                            image_data = ImageData(image_bytes, metadata)
                            batch_image_data.append(image_data)  # Store the ImageData object
                        else:
                            logger.warning(f"No image found for {row['Object ID']}")
                    except Exception as e:
                        logger.error(f"Error processing image for Object ID {row['Object ID']}: {e}")

                if batch_image_data:
                    # Get just image bytes from ImageData objects
                    image_bytes_list = []
                    for image_data in batch_image_data:
                        image_bytes_list.append(image_data.image_bytes)
                    logger.info(f"Image bytes list of size {len(image_bytes_list)} created successfully")

                    # Process batch through model
                    vectors = image_processor.transform_image_bytes_to_vectors(image_bytes_list)
                    logger.info(f"Vectors created successfully, attempting to insert {len(vectors)} images/vectors into db")

                    # Create points and insert
                    for vector, image_data in zip(vectors, batch_image_data):
                        point = PointStruct(
                            id=image_data.metadata['id'],
                            vector=vector, 
                            payload=image_data.metadata
                        )
                        points_batch.append(point)
                    
                    # Insert points into qdrant
                    try:
                        db_manager.insert_data(points_batch)
                    except Exception as e:
                        logger.error(f"Failed to insert data: {e}")
                        continue
                    
                    points_batch = []  
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
    finally:
        await image_processor.close()  # Ensure the session is closed
        logger.info('Completed Processing and Inserting Images')

def create_paintings_csv(original_csv_path, output_csv_path):
    # Read the original CSV
    all_data = pd.read_csv(original_csv_path)

    # Filter for paintings
    paintings = all_data[all_data['Classification'].str.contains('Paintings', na=False)]

    # Save the filtered DataFrame to a new CSV
    paintings.to_csv(output_csv_path, index=False)
    print(f"Paintings data saved to {output_csv_path}")

# create_paintings_csv(
#     original_csv_path='MetObjects.csv',
#     output_csv_path='paintings.csv'
# )

if __name__ == "__main__":
    # db = db.DatabaseManager()
    # db.create_collection()
    asyncio.run(process_paintings_to_qdrant(
        csv_path='paintings.csv',
    ))