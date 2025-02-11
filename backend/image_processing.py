import requests
import logging
import torchvision.transforms as transforms
from PIL import Image
from io import BytesIO
import torch
import torchvision.models as models
logger = logging.getLogger(__name__)

def get_image_data(object_id) -> str:
    logger.info("inside get_image_data")
    met_api_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    logger.info(f"Attemping to get image {object_id} from {met_api_url}")
    
    try:
        response = requests.get(met_api_url)
        if not response:
            logger.warning(f"Failed to make request for {met_api_url}")
            return None
            
        image_url = response.json()['primaryImage']
        
        if not image_url:
            logger.warning(f"No image URL found for {object_id}")
            return None
            
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        return image_response.content
        
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        logger.error(f"Error processing {object_id}: {str(e)}")
        return None

def transform_image(image_bytes):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])

    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    image = transform(image)
    image = image.unsqueeze(0)

    return image

def load_model():
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model = torch.nn.Sequential(*list(model.children())[:-1])
    model.eval()
    return model


def transform_image_to_vector(image_bytes,model):
    image = transform_image(image_bytes)
    with torch.no_grad():
        features = model(image)
        vector = features.squeeze().numpy()
    return vector