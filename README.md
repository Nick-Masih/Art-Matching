# ART MATCHING

Utilized resnset50 and met muesuem dataset to create a vector embedding of paintings.

The embeddings were then uploaded to qdrant cloud and a basic search function was implemented to search for paintings based on the query embedding.

The search function was then integrated with a basic next.js frontend that allows for a user to upload an image and get back a list of 5 paintings from the database that are most similar to the uploaded image.

## **How To Run the App**
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

*New Terminal*

cd frontend 
npm run dev