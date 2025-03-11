import aiohttp
import logging
import torchvision.transforms as transforms
from PIL import Image
from io import BytesIO
import torch
import torchvision.models as models
import asyncio

logger = logging.getLogger(__name__)

class ImageData:
    def __init__(self, image_bytes, metadata):
        self.image_bytes = image_bytes
        self.metadata = metadata

class ImageProcessor:
    def __init__(self):
        self.model = self.load_model()
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])
        self.session = aiohttp.ClientSession()
        
    def load_model(self):
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        model = torch.nn.Sequential(*list(model.children())[:-1])
        model.eval()
        logging.info('Model Loaded')
        return model

    async def get_image_data(self, object_id):
        met_api_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
        logger.debug(f"Attempting to get image {object_id} from {met_api_url}")
        
        try:
            async with self.session.get(met_api_url) as response:
                response.raise_for_status()  # Raise an error for bad responses
                data = await response.json()  # Ensure you are getting JSON data
                
                image_url = data.get('primaryImage')
                
                if not image_url:
                    return None
                
                async with self.session.get(image_url) as image_response:
                    image_response.raise_for_status()
                    image_bytes = await image_response.read()  # Return the image bytes
                    
                    if image_bytes is None or len(image_bytes) == 0:
                        logger.warning(f"Image bytes are None or empty for {object_id}, skipping.")
                        return None

                    logger.debug(f"Fetched image bytes of size: {len(image_bytes)} for {object_id}")
                    return image_bytes  # Return the image bytes
            
        except (aiohttp.ClientError, ValueError, KeyError) as e:
            logger.warning(f"Could not process image {object_id}. Error {str(e)}")
            return None

    async def get_batch_images(self, object_ids):
        """Process multiple images concurrently"""
        logger.info("Getting images for batch")
        tasks = [self.get_image_data(obj_id) for obj_id in object_ids]
        return await asyncio.gather(*tasks)

    def transform_image_bytes_to_vectors(self, image_bytes_list):
        """Transform single or multiple images to vectors."""
        try:
            if not isinstance(image_bytes_list, list):
                image_bytes_list = [image_bytes_list]
                
            images = []
            for img_bytes in image_bytes_list:
                if img_bytes is not None:
                    image = Image.open(BytesIO(img_bytes)).convert('RGB')
                    image = self.transform(image)
                    images.append(image)
                    
            if not images:
                logger.warning("No valid images to transform, returning None.")
                return None
                
            images = torch.stack(images)
            
            with torch.no_grad():
                features = self.model(images)
                vectors = features.squeeze().numpy()
                
            if len(vectors.shape) == 1:
                return [vectors.tolist()]
            else:
                return [v.tolist() for v in vectors]
                
        except Exception as e:
            logger.error(f"Error transforming images to vectors: {e}")
            return None

    async def close(self):
        await self.session.close()