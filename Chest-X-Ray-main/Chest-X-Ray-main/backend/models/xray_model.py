import numpy as np
from PIL import Image
import torchxrayvision as xrv
import torch
from skimage import exposure

def get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def load_model(device=None):
    device = device or get_device()
    model = xrv.models.DenseNet(weights="densenet121-res224-all").to(device)
    model.eval()
    labels = model.pathologies
    return model, labels

def normalize_xray(img):
    """Normalize an X-ray image to the expected range [-1024, 1024]."""
    img = img.astype(np.float32)
    # Normalize to [0, 1] first
    img = exposure.rescale_intensity(img, out_range=(0, 1))
    # Then scale to [-1024, 1024] as expected by torchxrayvision
    img = img * 2048 - 1024
    return img



def get_preprocess():
    """Custom preprocessing for torchxrayvision models."""
    def preprocess_fn(pil_image):
        # Convert to grayscale if needed
        if pil_image.mode != 'L':
            pil_image = pil_image.convert('L')
        
        # Resize to 224x224
        pil_image = pil_image.resize((224, 224), Image.LANCZOS)
        
        # Convert to numpy and normalize for xray vision
        np_img = np.array(pil_image)
        np_img = normalize_xray(np_img)
        
        # Convert to tensor and add batch dimension
        tensor = torch.from_numpy(np_img).unsqueeze(0).unsqueeze(0)  # [1, 1, 224, 224]
        return tensor.float()
    
    return preprocess_fn


def get_last_conv_layer(model):
    """Get the last convolutional layer for GradCAM."""
    # For DenseNet-121 in torchxrayvision, the last conv layer is typically:
    # model.features.denseblock4.denselayer16.conv2
    try:
        return model.features.denseblock4.denselayer16.conv2
    except AttributeError:
        # Fallback: find the last Conv2d layer
        last_conv = None
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Conv2d):
                last_conv = module
        return last_conv