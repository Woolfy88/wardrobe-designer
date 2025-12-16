import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from dataclasses import dataclass
from typing import List

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Wardrobe Designer", layout="wide")

# ----------------------------
# Data model
# ----------------------------
@dataclass
class Bay:
    width_mm: int
    layout: str  # "Single" | "Drawer tower" | "Double"

# ----------------------------
# Session state helpers (robust)
# ----------------------------
def _is_int_list(x, n=None) -> bool:
    if not isinstance(x, list):
        return False
    if n is not None and len(x) != n:
        return False
    return all(isinstance(v, int) for v in x)

def _is_str_list(x, n=None) -> bool:
    if not isinstance(x, list):
        return False
    if n is not None and len(x) != n:
        return False
    return all(isinstance(v, str) for v in x)

def ensure_state(num_bays: int, default_width: int):
    # Ensure bay widths list is valid
    bw = st.session_state.get("bay_widths")
    if not _is_int_list(bw, n=num_bays):
        st.session_state["bay_widths"] = [default_width] * num_bays

    # Ensure bay layouts list is valid
    bl = st.session_state.get("bay_layouts")
    if not _is_str_list(bl, n=num_bays):
        st.session_state["bay_layouts"] = ["Single"] * num_bays

def build_bays() -> List[Bay]:
    return [Bay(width_mm=w, layout=layout)
            for w, layout in zip(st.session_state["bay_widths"], st.session_state["bay_layouts"])]

# ----------------------------
# Drawing utilities
# ----------------------------
def draw_elevation(bays: List[Bay], height_mm: int, depth_mm: int, customer_view: bool):
    """
    2D front elevation: bays drawn left-to-right with internals indicated.
    customer_view=True removes "technical" lines and keeps it cleaner.
    """
    total_width = sum(b.width_mm for b in bays)
    # Scale figure size based on wardrobe size (inches-ish)
    fig_w = max(6.5, min(16.0, total_width / 250))
    fig_h = max(4.0, min(10.0, height_mm / 300))

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # Outer carcass
    ax.add_patch(Rectangle((0, 0), total_width, height_mm, fill=False, linewidth=2))

    # Vertical bay dividers + internals
    x = 0
    for idx, bay in enumerate(bays):
        # Bay outline (optional inner box)
        ax.add_patch(Rectangle((x, 0), bay.width_mm, height_mm, fill=False, linewidth=1.5))

        # Divider line at right edge (except last)
        if idx < len(bays) - 1:
            ax.plot([x + bay.width_mm, x + bay.width_mm], [0, height_mm], linewidth=2)

        # Internals
        if bay.layout == "Drawer tower":
            # Drawer tower centered, with drawers stacked
            tower_w = int(bay.width_mm * 0.55)
            tower_x = x + (bay.width_mm - tower_w) / 2
            base_y = 0
            tower_h = int(height_mm * 0.60)

            ax.add_patch(Rectangle((tower_x, base_y), tower_w, tower_h, fill=False, linewidth=1.5))

            # Draw 4-5 drawer fronts
            drawer_count = 5
            step = tower_h / drawer_count
            for d in range(1, drawer_count):
                y = base_y + d * step
                ax.plot([tower_x, tower_x + tower_w], [y, y], linewidth=1)

            # Optional top shelf line above tower
            if not customer_view:
                shelf_y = tower_h + int(height_mm * 0.05)
                ax.plot([x + 40, x + bay.width_mm - 40], [shelf_y, shelf_y], linewidth=1)

        elif bay.layout == "Double":
            # Two hanging zones (no labels per request)
            top_y = int(height_mm * 0.58)
            mid_y = int(height_mm * 0.12)

            # Suggest rails as thin lines
            ax.plot([x + 40, x + bay.width_mm - 40], [top_y, top_y], linewidth=1.5)
            ax.plot([x + 40, x + bay.width_mm - 40], [mid_y + int(height_mm * 0.20), mid_y + int(height_mm * 0.20)], linewidth=1.5)

            # Optional small shelf line between zones (installer-ish)
            if not customer_view:
                split_y = int(height_mm * 0.50)
                ax.plot([x + 40, x + bay.width_mm - 40], [split_y, split_y], linewidth=1)

        else:
            # "Single" (plain): just one rail line (no label)
            rail_y = int(height_mm * 0.62)
            ax.plot([x + 40, x + bay.width_mm - 40], [rail_y, rail_y], linewidth=1.5)

            # Optional: a top shelf line for installer view
            if not customer_view:
                shelf_y = int(height_mm * 0.85)
                ax.plot([x + 40, x + bay.width_mm - 40], [shelf_y, shelf_y], linewidth=1)

        # Bay width annotation (installer view only)
        if not customer_view:
            ax.text(x + bay.width_mm / 2, -height_mm * 0.035, f"{bay.width_mm}mm",
                    ha="center", va="top", fontsize=10)

        x += bay.width_mm

    # Customer view: remove axes, keep clean
    ax.set_xlim(0, total_width)
    ax.set_ylim(-height_mm * 0.08, height_mm)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    title = "Wardrobe (Customer View)" if customer_view else "Wardrobe (Installer View)"
    ax.set_title(title, fontsize=14, pad=12)

    return fig

def draw_isometric(bays: List[Bay], height_mm: int, depth_mm: int, customer_view: bool):
    """
    Fake-3D isometric: front face + top/depth offset.
    Still matplotlib, so it stays simple and fast.
    """
    total_width = sum(b.width_mm for b in bays)

    # Isometric offsets (in mm units for drawing)
    dx = int(depth_mm * 0.55)
    dy = int(depth_mm * 0.30)

    fig_w = max(7.0, min(16.0, (total_width + dx) / 260))
    fig_h = max(4.5, min(10.0, (height_mm + dy) / 320))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # Front rectangle
    ax.add_patch(Rectangle((0, 0), total_width, height_mm, fill=False, linewidth=2))

    # "Top" outline (shifted)
    ax.plot([0, dx, total_width + dx, total_width, 0],
            [height_mm, height_mm + dy, height_mm + dy, height_mm, height_mm],
            linewidth=2)

    # Side outline
    ax.plot([total_width, total_width + dx],
            [0, dy],
            linewidth=2)
    ax.plot([total_width + dx, total_width + dx],
            [dy, height_mm + dy],
            linewidth=2)

    # Bay dividers on front + top
    x = 0
    for i, bay in enumerate(bays[:-1]):
        x += bay.width_mm
        ax.plot([x, x], [0, height_mm], linewidth=1.5)
        ax.plot([x, x + dx], [height_mm, height_mm + dy], linewidth=1.5)

    # Light internal hints (customer view = less busy)
    if not customer_view:
        x = 0
        for bay in bays:
            # show one internal line per bay
            ax.plot([x + 40, x + bay.width_mm - 40], [int(height_mm * 0.75), int(height_mm * 0.75)], linewidth=1)
            x += bay.width_mm

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    title = "Isometric (Customer View)" if customer_view else "Isometric (Installer View)"
    ax.set_title(title, fontsize=14, pad=12)

    ax.set_xlim(-depth_mm * 0.1, total_width + dx + depth_mm * 0.2)
    ax.set_ylim(-height_mm * 0.05, height_mm + dy + height_mm * 0.1)

    return fig

# ----------------------------
# UI
# ----------------------------
st.title("Wardrobe Designer")

with st.sidebar:
    st.header("Wardrobe")
    total_height = st.number_input("Height (mm)", min_value=1800, max_value=3000, value=2400, step=10)
    depth = st.number_input("Depth (mm)", min_value=400, max_value=800, value=600, step=10)

    st.divider()
    num_bays = st.number_input("Number of bays", min_value=1, max_value=8, value=4, step=1)

    st.divider()
    view_mode = st.radio("View mode", ["Customer view", "Installer view"], index=0)
    customer_view = (view_mode == "Customer view")

    show_isometric = st.checkbox("Show fake-3D isometric", value=False)

    st.divider()
    equal_widths = st.checkbox("Keep bays equal width", value=True)

# Setup state safely
default_bay_width = 600
ensure_state(int(num_bays), default_bay_width)

# Layout editors
st.subheader("Bay setup")

# If equal widths, expose one control and apply to all
if equal_widths:
    w = st.number_input("Bay width (mm)", min_value=300, max_value=1200,
                        value=int(st.session_state["bay_widths"][0]), step=10)
    st.session_state["bay_widths"] = [int(w)] * int(num_bays)

cols = st.columns(int(num_bays))
layouts = ["Single", "Drawer tower", "Double"]

for i in range(int(num_bays)):
    with cols[i]:
        st.markdown(f"**Bay {i+1}**")
        if not equal_widths:
            st.session_state["bay_widths"][i] = int(st.number_input(
                "Width (mm)", min_value=300, max_value=1200,
                value=int(st.session_state["bay_widths"][i]), step=10, key=f"w_{i}"
            ))
        st.session_state["bay_layouts"][i] = st.selectbox(
            "Internal", layouts,
            index=layouts.index(st.session_state["bay_layouts"][i]) if st.session_state["bay_layouts"][i] in layouts else 0,
            key=f"layout_{i}"
        )

bays = build_bays()

# Render outputs
st.divider()
left, right = st.columns([2, 1], vertical_alignment="top")

with left:
    st.subheader("Design preview")
    fig = draw_elevation(bays=bays, height_mm=int(total_height), depth_mm=int(depth), customer_view=customer_view)
    st.pyplot(fig, clear_figure=True)

    if show_isometric:
        fig_iso = draw_isometric(bays=bays, height_mm=int(total_height), depth_mm=int(depth), customer_view=customer_view)
        st.pyplot(fig_iso, clear_figure=True)

with right:
    st.subheader("Summary")
    st.write(f"**Total width:** {sum(b.width_mm for b in bays)} mm")
    st.write(f"**Height:** {int(total_height)} mm")
    st.write(f"**Depth:** {int(depth)} mm")

    st.divider()
    st.write("**Bays:**")
    for idx, bay in enumerate(bays, start=1):
        st.write(f"- Bay {idx}: {bay.width_mm} mm — {bay.layout}")

    st.divider()
    if st.button("Reset designer"):
        # Clear only our keys
        for k in ["bay_widths", "bay_layouts"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()
