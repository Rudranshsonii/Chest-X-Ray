from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import asyncio
from typing import Dict, Any
import logging

from models.inference import predict
from models.explain import generate_heatmap
from models.xray_model import get_device, get_last_conv_layer, get_preprocess,load_model
from utils import file_manager, image_to_base64, create_error_response, create_success_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chest-xray"])

model = None
labels = None
preprocess = None
target_layer = None
device = None

async def initialize_model():
    """Initialize the model and related components."""
    global model, labels, preprocess, target_layer, device
    
    try:
        logger.info("Initializing model...")
        device = get_device()
        model, labels = load_model(device)
        preprocess = get_preprocess()
        target_layer = get_last_conv_layer(model)
        logger.info(f"Model initialized successfully on device: {device}")
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        raise e


@router.post("/predict")
async def predict_disease(file: UploadFile = File(...)) -> JSONResponse:
    """
    Predict top-5 diseases from chest X-ray image.
    
    Args:
        file: Uploaded chest X-ray image (PNG/JPG)
        
    Returns:
        JSON response with top-5 predictions and probabilities
    """
    file_path = None
    
    try:
        if model is None:
            await initialize_model()
        
        file_path, file_bytes = file_manager.save_uploaded_file(file)
        logger.info(f"Processing prediction for file: {file.filename}")
        
        pred_results = predict(image_bytes=file_bytes,model=model,labels=labels,preprocess=preprocess,target_layer=target_layer,device=device)  
      
        response_data = {
            "filename": file.filename,
            "predictions": pred_results["predictions"][:5], 
            "top_prediction": {
                "label": pred_results["top_label"],
                "probability": pred_results["top_probability"]
            }
        }
        
        return JSONResponse(
            content=create_success_response(response_data),
            status_code=200
        )
        
    except HTTPException as e:
        logger.error(f"HTTP error in predict: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in predict: {e}")
        return JSONResponse(
            content=create_error_response(f"Prediction failed: {str(e)}"),
            status_code=500
        )
    finally:
        if file_path:
            file_manager.cleanup_file(file_path)


@router.post("/explain")
async def explain_prediction(file: UploadFile = File(...)) -> JSONResponse:
    """
    Generate Grad-CAM heatmap explanation for chest X-ray image.
    
    Args:
        file: Uploaded chest X-ray image (PNG/JPG)
        
    Returns:
        JSON response with base64 encoded heatmap overlay
    """
    file_path = None
    
    try:
        if model is None:
            await initialize_model()
        
        file_path, file_bytes = file_manager.save_uploaded_file(file)
        logger.info(f"Processing explanation for file: {file.filename}")
        
        pred_results = predict(image_bytes=file_bytes,model=model,labels=labels,preprocess=preprocess,target_layer=target_layer,device=device)
        
        heatmap_results = generate_heatmap(image_bytes=file_bytes,model=model,target_layer=target_layer,pred_class_idx=pred_results["top_class_index"],device=device,original_size=pred_results["original_size"])   
        
        if not heatmap_results["success"]:
            raise Exception(heatmap_results["error"])
        
        heatmap_base64 = image_to_base64(heatmap_results["heatmap_overlay"])
        
        response_data = {
            "filename": file.filename,
            "heatmap_image": heatmap_base64,
            "explained_prediction": {
                "label": pred_results["top_label"],
                "probability": pred_results["top_probability"],
                "class_index": pred_results["top_class_index"]
            },
            "image_info": {
                "original_size": heatmap_results["original_size"],
                "model_input_size": heatmap_results["model_input_size"]
            }
        }
        return JSONResponse(
            content=create_success_response(response_data),
            status_code=200
        )
        
    except HTTPException as e:
        logger.error(f"HTTP error in explain: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in explain: {e}")
        return JSONResponse(
            content=create_error_response(f"Explanation failed: {str(e)}"),
            status_code=500
        )
    finally:
        if file_path:
            logger.info("removing the image")
            file_manager.cleanup_file(file_path)


# Startup event to initialize model
@router.on_event("startup")
async def startup_event():
    """Initialize model on startup."""
    await initialize_model()
