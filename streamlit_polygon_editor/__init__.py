import io
import base64
import os
import hashlib
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

_COMPONENT_PATH = os.path.join(os.path.dirname(__file__), "frontend")
_polygon_editor_func = components.declare_component("polygon_editor", path=_COMPONENT_PATH)

def length_of_line(line):
    "Calculate the length of a piecewise linear line."
    total_length = 0
    for i in range(len(line) - 1):
        x1, y1 = line[i]
        x2, y2 = line[i + 1]
        total_length += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return total_length


@st.cache_data(show_spinner=False)
def _prepare_image_payload(_image: Image.Image, _cache_key: str) -> tuple[str, str]:
    """PNG/base64-encode the image and hash it, cached by image content.

    Streamlit re-runs the whole script on every interaction, which
    previously re-encoded the (potentially large) image to PNG/base64 every
    single time even though it rarely changes. Caching this avoids that
    repeated work.

    Streamlit's own cache hasher cannot hash a PIL Image (it raises
    UnhashableParamError), so the image itself is passed as `_image` - the
    leading underscore tells Streamlit not to hash it - and a cheap,
    already-hashable fingerprint (`_cache_key`, computed by the caller from
    the raw pixel bytes) is used as the actual cache key instead.
    """
    buffered = io.BytesIO()
    _image.save(buffered, format="PNG")
    raw = buffered.getvalue()
    image_data_url = f"data:image/png;base64,{base64.b64encode(raw).decode()}"
    image_token = hashlib.sha256(raw).hexdigest()
    return image_data_url, image_token


def _image_cache_key(image: Image.Image) -> str:
    """Cheap, hashable fingerprint of an image's content (no PNG compression)."""
    return f"{image.size}:{image.mode}:{hashlib.sha256(image.tobytes()).hexdigest()}"


def custom_polygon_editor(
    bg_image: Image.Image,
    initial_polygons: list[list[list[float]]] = None,
    initial_lines: list[list[list[float]]] = None,
    active_tool: str = "polygon", # "polygon" nebo "line"
    poly_view_mode: str = "all",
    line_view_mode: str = "all",
    max_height: int = 550, 
    key: str = "polygon_editor",
    confirm_mode: bool = False,
):
    """
    confirm_mode:
        False (výchozí) - každá úprava (kreslení, přesun bodu, smazání,
            přepnutí nástroje/pohledu, undo, ...) se ihned pošle do Pythonu
            a vyvolá rerun skriptu.
        True - úpravy se hromadí jen lokálně v prohlížeči. Do Pythonu se
            odešlou až po kliknutí na tlačítko "✅ Confirm" na liště nástrojů.
    """
    width, height = bg_image.size
    image_data_url, image_token = _prepare_image_payload(bg_image, _image_cache_key(bg_image))

    default_polygons = initial_polygons if initial_polygons is not None else []
    default_lines = initial_lines if initial_lines is not None else []

    default_val = {
        "active_tool": active_tool,
        "active_polygon_index": 0,
        "active_line_index": 0,
        "poly_view_mode": poly_view_mode,
        "line_view_mode": line_view_mode,
        "polygons": default_polygons,
        "lines": default_lines,
        "image_token": image_token,
    }

    component_value = _polygon_editor_func(
        image_data_url=image_data_url,
        width=width,
        height=height,
        max_height=max_height,
        initial_polygons=default_polygons,
        initial_lines=default_lines,
        active_tool=active_tool,
        poly_view_mode=poly_view_mode,
        line_view_mode=line_view_mode,
        image_token=image_token,
        confirm_mode=confirm_mode,
        key=key,
        default=default_val
    )

    if not isinstance(component_value, dict):
        return default_val
    # If the frontend is still holding data from a previous (different)
    # image - e.g. right after bg_image was swapped, before the iframe has
    # caught up - discard it instead of handing back geometry drawn on a
    # different picture.
    if component_value.get("image_token") != image_token:
        return default_val
    return component_value


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.title("Interactive Multi-Polygon & Distance Measurement Editor")

    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        img_name = uploaded_file.name
    else:
        img = Image.new('RGB', (800, 500), color=(240, 240, 245))
        img_name = "default_canvas"

    w, h = img.size

    default_polygons = [
        [
            [int(w * 0.15), int(h * 0.15)],
            [int(w * 0.45), int(h * 0.15)],
            [int(w * 0.45), int(h * 0.55)],
            [int(w * 0.15), int(h * 0.55)]
        ]
    ]

    default_lines = [
        [
            [int(w * 0.15), int(h * 0.8)],
            [int(w * 0.55), int(h * 0.8)]
        ]
    ]

    confirm_mode = st.sidebar.checkbox(
        "Confirm Mode",
        value=False,
        help="When enabled, changes are only sent to Python after clicking the ✅ Confirm button in the toolbar. Otherwise, every change is sent immediately.",
    )

    c1, c2 = st.columns([5, 2])
    with c1:
        st.subheader("Canvas")
        with st.container(border=True):
            editor_result = custom_polygon_editor(
                bg_image=img,
                initial_polygons=default_polygons,
                initial_lines=default_lines,
                key=f"editor_{img_name}", 
                max_height=600,
                confirm_mode=confirm_mode,
            )

    with c2:

        st.subheader("Scale & Lines")


        st.write(f"Active Tool: **{editor_result.get('active_tool')}**")
        # You can also read the active tool: editor_result.get("active_tool")
        real_scale_length = st.number_input("Reference line #1 length (in meters)", value=1.0, step=0.1)
        
        lines_coords = editor_result.get("lines", [])
        polygons_coords = editor_result.get("polygons", [])
        active_poly_idx = editor_result.get("active_polygon_index", 0)
        active_line_idx = editor_result.get("active_line_index", 0)

        px_per_unit = 0.0
        if lines_coords and len(lines_coords[0]) >= 2:
            px_dist = length_of_line(lines_coords[0])
            if px_dist > 0 and real_scale_length > 0:
                px_per_unit = px_dist / real_scale_length
                st.info(f"Scale from line #1: {px_per_unit:.2f} px / m")

        st.markdown("#### Measured Lines")
        if lines_coords:
            for idx, line in enumerate(lines_coords):
                if len(line) >= 2:
                    dist_px = length_of_line(line)
                    is_active = (idx == active_line_idx and editor_result.get("active_tool") == "line")
                    label = f"**Line #{idx + 1}** {'(Selected)' if is_active else ''}"
                    st.write(label)
                    st.write(f"- Length: `{dist_px:.2f} px`")
                    if px_per_unit > 0:
                        st.write(f"- Actual Length: `{dist_px / px_per_unit:.2f} m`")
        else:
            st.write("No lines.")

        st.markdown("---")
        st.subheader("Polygons & Geometry")
        if polygons_coords:
            st.write(f"Total polygons: **{len(polygons_coords)}**")
            
            for idx, poly in enumerate(polygons_coords):
                if len(poly) >= 3:
                    area = 0.0
                    perimeter = 0.0
                    n = len(poly)
                    for i in range(n):
                        x1, y1 = poly[i]
                        x2, y2 = poly[(i + 1) % n]
                        area += (x1 * y2 - x2 * y1)
                        perimeter += ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
                    area = abs(area) / 2.0

                    is_act = (idx == active_poly_idx and editor_result.get("active_tool") == "polygon")
                    st.markdown(f"**Polygon #{idx + 1}** {'⭐' if is_act else ''}")
                    st.write(f"- Perimeter: `{perimeter:.2f} px`" + (f" (`{perimeter / px_per_unit:.2f} m`)" if px_per_unit > 0 else ""))
                    st.write(f"- Area: `{area:.2f} px²`" + (f" (`{area / (px_per_unit**2):.4f} m²`)" if px_per_unit > 0 else ""))
        else:
            st.warning("No polygons.")