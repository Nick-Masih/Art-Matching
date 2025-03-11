# ART MATCHING

Utilized resnet50 and the [met museum dataset](https://github.com/metmuseum/openaccess/blob/master/MetObjects.csv) to create vector embedding of the paintings in the dataset.    
The vectors were then uploaded to qdrant cloud and a basic search function was implemented to search for paintings based on similar vectors.  
The search function was then integrated with a basic next.js frontend that allows users to upload an image and get back 5 paintings from the database that are most similar to the uploaded image.

## **How To Run the App**
**Step 1:**  
Create a .env file with these values  
API_KEY=\<your qdrant api key\>  
DATABASE_URL=\<your qdrant db url\>  
COLLECTION_NAME=\<whatever you want to call the collection\>  

**Step 2:**  
cd backend  
uvicorn app:app --host 0.0.0.0 --port 8000 --reload  

**Step 3:**  
*New Terminal*  
cd frontend  
npm run dev