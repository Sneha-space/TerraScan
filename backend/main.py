# import cv2
# from src.ml.image_enhancer import CVProcessor
# from src.services.pdf_to_img import extract_images_from_pdf

# # Initialize the processor (it automatically loads the AI model)
# processor = CVProcessor(use_enhancement=True)

# if __name__ == "__main__":
#     # 1. Convert PDF pages to image bytes
#     image_bytes = extract_images_from_pdf(r"c:\Users\sneha\Downloads\pgms vs nns-Sneha Biswas.pdf")
    
#     # 2. Decode bytes into OpenCV images
#     images = processor.process_bytes(image_bytes)
    
#     # 3. Run Preprocessing + AI Enhancement
#     enhanced_images = processor.process(images)
    
#     # 4. Display the resulting enhanced images
#     for idx, image in enumerate(enhanced_images):
#         cv2.imshow(f"Enhanced Page {idx+1}", image)
#         cv2.waitKey(0)
#     cv2.destroyAllWindows()

"""TerraScan API entry point.

Creates the app and mounts routers. Business logic belongs in
src/services/, not here.

Run from backend/:  uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import CORS_ORIGINS

from src.api.routes import documents, dashboard, records

from src.db.base import Base
from src.db.session import engine
import src.models  # noqa: F401, registers models with Base



Base.metadata.create_all(bind=engine)


app = FastAPI(title="TerraScan API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(dashboard.router)
app.include_router(records.router)

@app.get("/health")
def health():
    """Liveness check. Used to confirm the server is up."""
    return {"status": "ok"}