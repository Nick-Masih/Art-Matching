from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from search import search_similar_paintings
import image_processing

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/image/{object_id}")
async def get_image(object_id: int):
    try:
        image_data = image_processing.get_image_data(object_id)
        if not image_data:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=image_data, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get image")

@app.post("/search")
async def search(image: UploadFile = File(...)):
    try:
        image_bytes = await image.read()
        results = search_similar_paintings(image_bytes)
        
        if not results:
            raise HTTPException(status_code=500, detail="Search failed")
            
        # Add image
        for result in results:
            result['image_url'] = f"http://localhost:8000/image/{result['id']}"
            
        return {"results": results}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "An error occurred while processing your request"}
        ) 