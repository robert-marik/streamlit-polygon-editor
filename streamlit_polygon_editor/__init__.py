import io
import base64
import os
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

_COMPONENT_PATH = os.path.join(os.path.dirname(__file__), "frontend")
_polygon_editor_func = components.declare_component("polygon_editor", path=_COMPONENT_PATH)

def custom_polygon_editor(
    bg_image: Image.Image,
    initial_coords: list[list[float]] = None,
    initial_scale_line: list[list[float]] = None,
    enable_scale_line: bool = True,
    key: str = "polygon_editor"
):
    """
    Bidirectional Streamlit polygon editor component with optional scale line measurement.
    
    If enable_scale_line == True, returns dict:
        {"polygon": [[x, y], ...], "scale_line": [[x1, y1], [x2, y2]]}
    
    If enable_scale_line == False, returns list:
        [[x, y], ...]
    """
    width, height = bg_image.size

    buffered = io.BytesIO()
    bg_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    image_data_url = f"data:image/png;base64,{img_str}"

    default_polygon = initial_coords if initial_coords else []
    
    if enable_scale_line and initial_scale_line is None:
        initial_scale_line = [
            [int(width * 0.2), int(height * 0.9)],
            [int(width * 0.5), int(height * 0.9)]
        ]

    default_val = {
        "polygon": default_polygon,
        "scale_line": initial_scale_line if enable_scale_line else []
    }

    component_value = _polygon_editor_func(
        image_data_url=image_data_url,
        width=width,
        height=height,
        initial_coords=default_polygon,
        initial_scale_line=initial_scale_line if enable_scale_line else [],
        enable_scale_line=enable_scale_line,
        key=key,
        default=default_val if enable_scale_line else default_polygon
    )

    if not enable_scale_line:
        if isinstance(component_value, dict):
            return component_value.get("polygon", [])
        return component_value if isinstance(component_value, list) else default_polygon
    
    return component_value if isinstance(component_value, dict) else default_val


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.title("Interactive Polygon & Scale Editor Demo")

    st.sidebar.header("Settings")
    use_scale = st.sidebar.checkbox("Enable Scale Line", value=True)
    uploaded_file = st.sidebar.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        img_name = uploaded_file.name
    else:
        img = Image.new('RGB', (700, 450), color=(240, 240, 245))
        img_name = "default_canvas"

    w, h = img.size

    default_polygon = [
        [int(w * 0.2), int(h * 0.2)],
        [int(w * 0.8), int(h * 0.2)],
        [int(w * 0.8), int(h * 0.7)],
        [int(w * 0.2), int(h * 0.7)]
    ]

    default_scale = [
        [int(w * 0.2), int(h * 0.85)],
        [int(w * 0.6), int(h * 0.85)]
    ]

    real_scale_length = 1.0
    if use_scale:
        real_scale_length = st.sidebar.number_input("Real Scale Length (e.g., meters)", value=1.0, step=0.1)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Canvas")
        editor_result = custom_polygon_editor(
            bg_image=img,
            initial_coords=default_polygon,
            initial_scale_line=default_scale,
            enable_scale_line=use_scale,
            key=f"editor_{img_name}_{use_scale}"
        )

    with col2:
        if use_scale:
            st.subheader("📏 Scale Info")
            polygon_coords = editor_result.get("polygon", [])
            scale_line = editor_result.get("scale_line", [])

            if len(scale_line) == 2:
                p1, p2 = scale_line[0], scale_line[1]
                px_distance = ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2) ** 0.5
                st.write(f"**Segment length:** {px_distance:.2f} px")
                if px_distance > 0 and real_scale_length > 0:
                    px_per_unit = px_distance / real_scale_length
                    st.metric("Scale Ratio", f"{px_per_unit:.2f} px / unit")
            st.markdown("---")
        else:
            polygon_coords = editor_result

        st.subheader("📍 Polygon Coordinates")
        if polygon_coords:
            st.success(f"Vertices count: {len(polygon_coords)}")
            st.dataframe(
                [{"Vertex": i + 1, "X (px)": pt[0], "Y (px)": pt[1]} for i, pt in enumerate(polygon_coords)],
                use_container_width=True
            )
        else:
            st.warning("Polygon is empty.")
