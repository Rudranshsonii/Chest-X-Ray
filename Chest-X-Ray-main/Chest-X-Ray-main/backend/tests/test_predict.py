import pytest
import io
import torch
import numpy as np
from PIL import Image, UnidentifiedImageError
from unittest.mock import MagicMock
from models.inference import predict


@pytest.fixture
def dummy_image_bytes():
    """Create a valid grayscale PNG image as bytes."""
    img = Image.new("L", (64, 64), color=128)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_predict_success(dummy_image_bytes):
    """Test predict returns sorted predictions with mocked model + preprocess."""
    labels = ["disease_A", "disease_B", "disease_C"]

    # Mock preprocess → returns tensor [1, 3, 224, 224]
    def mock_preprocess(img):
        return torch.ones((1, 3, 224, 224))

    # Mock model → returns fixed logits
    mock_model = MagicMock()
    mock_model.return_value = torch.tensor([[0.2, 2.0, -1.0]])

    result = predict(
        image_bytes=dummy_image_bytes,
        model=mock_model,
        labels=labels,
        preprocess=mock_preprocess,
        target_layer=None,
        device="cpu"
    )

    assert "predictions" in result
    assert len(result["predictions"]) == 3
    assert result["predictions"][0]["label"] == "disease_B"  # highest score
    assert result["top_label"] == "disease_B"
    assert isinstance(result["original_size"], tuple)


def test_predict_invalid_image():
    """Test predict raises error when given invalid image bytes."""
    labels = ["a", "b", "c"]

    def mock_preprocess(img):
        return torch.ones((1, 3, 224, 224))

    mock_model = MagicMock()

    with pytest.raises(UnidentifiedImageError):
        predict(
            image_bytes=b"not-an-image",
            model=mock_model,
            labels=labels,
            preprocess=mock_preprocess,
            target_layer=None,
            device="cpu"
        )
