from models.inference import get_device,get_preprocess
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image
from PIL import Image
import torchvision.transforms as T
import cv2
import io
import numpy as np
import logging

logger = logging.getLogger(__name__)

def generate_heatmap(image_bytes, model, target_layer, pred_class_idx, device=None, original_size=None):
    """
    Generate Grad-CAM heatmap for the given image and prediction class.
    
    Args:
        image_bytes: Raw image bytes
        model: Loaded PyTorch model
        target_layer: Target layer for Grad-CAM
        pred_class_idx: Index of the predicted class to visualize
        device: Device to run on
        original_size: Tuple (width, height) for output heatmap size. If None, uses original image size.
    
    Returns:
        dict: Contains heatmap_overlay (PIL Image), heatmap_array (numpy array), and metadata
    """
    device = device or get_device()
    
    try:
        logger.info("generating heatmap")
        # Load original image
        original_pil = Image.open(io.BytesIO(image_bytes))
        if original_pil.mode != 'L':
            original_pil = original_pil.convert('L')
        
        # Get original dimensions if not provided
        if original_size is None:
            original_size = original_pil.size  # (width, height)
        
        logger.info("preprocessing image")
        # Preprocess image for model
        preprocess = get_preprocess()
        tensor_img = preprocess(original_pil).to(device)
        
        # Set up Grad-CAM
        cam = GradCAM(
            model=model,
            target_layers=[target_layer],
        )
        
        # Generate heatmap for specific class
        targets = [ClassifierOutputTarget(pred_class_idx)]
        grayscale_cam = cam(input_tensor=tensor_img, targets=targets)[0]  # Shape: (224, 224)
        
        # Resize heatmap to original image size
        heatmap_resized = cv2.resize(grayscale_cam, original_size, interpolation=cv2.INTER_CUBIC)
        
        # Prepare original image for overlay (resize to match heatmap and convert to RGB)
        original_resized = original_pil.resize(original_size, Image.LANCZOS)
        rgb_img = np.array(original_resized.convert("RGB")).astype(np.float32) / 255.0
        
        logger.info("creating heatmap overlay")
        # Create heatmap overlay
        heatmap_overlay = show_cam_on_image(rgb_img, heatmap_resized, use_rgb=True)
        
        # Convert to PIL Image
        overlay_pil = Image.fromarray(heatmap_overlay)
        
        logger.info("heatmap generated and saved")
        
        return {
            "heatmap_overlay": overlay_pil,
            "heatmap_array": heatmap_resized,
            "original_size": original_size,
            "model_input_size": (224, 224),
            "success": True,
            "error": None
        }
        
    except Exception as e:
        return {
            "heatmap_overlay": None,
            "heatmap_array": None,
            "original_size": original_size,
            "model_input_size": (224, 224),
            "success": False,
            "error": str(e)
        }
