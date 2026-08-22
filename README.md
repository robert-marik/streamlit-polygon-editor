# Streamlit Polygon & Scale Editor

An interactive, bidirectional Streamlit custom component built on top of OpenLayers. It enables users to draw or edit polygon coordinates and optionally define a scale line on any background image.

---

## 📖 User Guide

### Installation

#### Install directly from GitHub via `pip`:
```bash
pip install git+[https://github.com/robert-marik/streamlit-polygon-editor.git](https://github.com/robert-marik/streamlit-polygon-editor.git)

```

#### Install locally:

Clone the repository and run:

```bash
pip install .

```

---

### Usage Examples

#### Mode 1: Polygon Only (`enable_scale_line=False`)

```python
import streamlit as st
from PIL import Image
from streamlit_polygon_editor import custom_polygon_editor

img = Image.open("your_image.png")

# Returns a list of coordinates: [[x1, y1], [x2, y2], ...]
polygon_coords = custom_polygon_editor(
    bg_image=img,
    initial_coords=[[100, 100], [400, 100], [400, 300], [100, 300]],
    enable_scale_line=False,
    key="editor_polygon_only"
)

st.write("Polygon Coordinates:", polygon_coords)

```

#### Mode 2: Polygon + Scale Line (`enable_scale_line=True`)

```python
import streamlit as st
from PIL import Image
from streamlit_polygon_editor import custom_polygon_editor

img = Image.open("your_image.png")

# Returns a dict: {"polygon": [[x1, y1], ...], "scale_line": [[x1, y1], [x2, y2]]}
result = custom_polygon_editor(
    bg_image=img,
    initial_coords=[[100, 100], [400, 100], [400, 300], [100, 300]],
    initial_scale_line=[[50, 400], [350, 400]],
    enable_scale_line=True,
    key="editor_with_scale"
)

st.write("Polygon Coordinates:", result["polygon"])
st.write("Scale Line Coordinates:", result["scale_line"])

```

### API Reference

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `bg_image` | `PIL.Image.Image` | *Required* | Pillow Image object used as canvas background. |
| `initial_coords` | `list[list[float]]` | `None` | Initial vertices for the polygon `[[x1, y1], ...]`. |
| `initial_scale_line` | `list[list[float]]` | `None` | Initial endpoints for the scale line `[[x1, y1], [x2, y2]]`. |
| `enable_scale_line` | `bool` | `True` | If `True`, enables scale segment and returns a `dict`. If `False`, disables scale segment and returns a `list`. |
| `key` | `str` | `"polygon_editor"` | Unique key identifier for Streamlit state tracking. |

---

## 🛠️ Developer Guide

### Project Structure

```text
streamlit-polygon-editor/
├── MANIFEST.in
├── README.md
├── pyproject.toml
├── setup.py
└── streamlit_polygon_editor/
    ├── __init__.py
    └── frontend/
        ├── index.html
        └── static/
            ├── ol.css
            └── ol.js

```

### Development Setup

1. **Clone Repository:**
```bash
git clone [https://github.com/robert-marik/streamlit-polygon-editor.git](https://github.com/robert-marik/streamlit-polygon-editor.git)
cd streamlit-polygon-editor

```


2. **Install in Editable Mode:**
```bash
pip install -e .

```


*Changes made to Python or HTML files will automatically reflect in your test app without reinstallation.*
3. **Run Demo App:**
```bash
streamlit run streamlit_polygon_editor/__init__.py

```



### Building & Distribution

1. **Build Distribution Packages:**
```bash
pip install build twine
python -m build

```


2. **Upload to PyPI:**
```bash
python -m twine upload dist/*

```
