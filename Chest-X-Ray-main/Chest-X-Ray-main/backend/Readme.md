# features

1. Predicted disease probabilities using a pretrained model that we specify.
2. A heatmap overlay (visual explanation) showing which regions of the image were most important for the model.

# Grad-CAM Workflow
Input Image (Chest X-ray)
          │
          ▼
   ┌─────────────┐
   │ Convolution │  ← Early conv layers: detect edges, textures
   └─────────────┘
          │
          ▼
   ┌─────────────┐
   │  Conv Layers│  ← Intermediate layers: detect patterns, shapes
   └─────────────┘
          │
          ▼
   ┌─────────────────────────┐
   │ Last Conv Layer (target)│  ← Captures high-level features
   └─────────────────────────┘
          │
          ▼
Gradients w.r.t target class
          │
          ▼
  Weighted feature maps
          │
          ▼
   ┌───────────────┐
   │  Heatmap Overlay│  ← Shows which regions contributed most
   └───────────────┘
          │
          ▼
  Output: Heatmap highlighting disease regions



python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
uv pip sync requirements.txt

uvicorn app:app --host 0.0.0.0 --port 8007 --timeout-keep-alive 1800 --reload

# Run tests from backed 

```
PYTHONPATH=. pytest -v
```