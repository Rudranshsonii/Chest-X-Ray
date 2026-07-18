import pytest
import io
import numpy as np
from PIL import Image
from unittest.mock import MagicMock, patch
from models.explain import generate_heatmap  # ensure this path is correct


@pytest.fixture
def dummy_image_bytes():
    """Return a small valid grayscale PNG image in bytes."""
    img = Image.fromarray(np.uint8(np.ones((100, 100)) * 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_generate_heatmap_success(dummy_image_bytes):
    """Test heatmap generation with a valid image and mocked GradCAM."""
    from unittest.mock import MagicMock, patch
    import torch
    import numpy as np
    from models.explain import generate_heatmap

    mock_model = MagicMock()
    mock_layer = MagicMock()

    with patch("models.explain.GradCAM") as MockGradCAM, \
         patch("models.explain.get_preprocess") as mock_get_preprocess, \
         patch("models.explain.show_cam_on_image") as mock_show_cam:

        # Make the GradCAM instance itself callable
        instance = MockGradCAM.return_value
        instance.return_value = np.ones((1, 224, 224), dtype=np.float32)  # shape (1,H,W)
        instance.__call__ = instance  # make instance callable

        # Mock preprocess → dummy PyTorch tensor
        mock_get_preprocess.return_value = lambda img: torch.ones((1, 3, 224, 224), dtype=torch.float32)

        # Mock show_cam_on_image → return dummy RGB image
        mock_show_cam.return_value = np.ones((100, 100, 3), dtype=np.uint8)

        result = generate_heatmap(
            image_bytes=dummy_image_bytes,
            model=mock_model,
            target_layer=mock_layer,
            pred_class_idx=0,
            device="cpu"
        )

    assert result["success"] is True
    assert result["heatmap_overlay"] is not None
    assert result["heatmap_array"].shape == (100, 100)


def test_generate_heatmap_invalid_image():
    """Test error handling when invalid image bytes are provided."""
    mock_model = MagicMock()
    mock_layer = MagicMock()

    # Provide invalid bytes
    bad_bytes = b"not-an-image"

    result = generate_heatmap(
        image_bytes=bad_bytes,
        model=mock_model,
        target_layer=mock_layer,
        pred_class_idx=0
    )

    assert result["success"] is False
    assert result["heatmap_overlay"] is None
    assert "cannot identify image file" in result["error"].lower()
