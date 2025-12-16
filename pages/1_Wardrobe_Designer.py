import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

st.set_page_config(page_title="Wardrobe Designer", layout="wide")
st.title("Wardrobe Designer (Option 1)")

# ----------------------------
# Helpers
# ----------------------------
def mm_to_m(x_mm: float) -> float:
    return x_mm / 1000.0

def clamp_int(x, lo, hi):
    return max(lo, min(hi, int(x)))

def ensure_state(num_bays: int):
    if "bay_types" not in st.session_state or len(st.session_state["bay_types"]) != num_bays:
        st.session_state["bay_types"] = ["Single"] * num_bays

    if "bay_widths" not in st.session_state or len(st.session_state["bay_widths"]) != num_bays:
        st.session_state["bay_widths"] = None  # means "auto"

def split_widths(total_w_mm: int, num_bays: int, custom: list[int] | None):
    if custom and len(custom) == num_bays and sum(custom) > 0:
        # Scale to exactly total width, preserving proportions
        scaled = np.array(custom, dtype=float)
        scaled = scaled / scaled.sum() * total_w_mm
        rounded = np.floor(scaled).astype(int)
        diff = total_w_mm - int(rounded.sum())
        # distribute remainder
        for i in range(abs(diff)):
            rounded[i % num_bays] += 1 if diff > 0 else -1
        return rounded.tolist()

    # Auto: equal widths
    base = total_w_mm // num_bays
    widths = [base] * num_bays
    rem = total_w_mm - base * num_bays
    for i in range(rem):
        widths[i] += 1
    return widths

def draw_elevation(total_w_mm, total_h_mm, bay_widths_mm, bay_types, view_mode, show_dims):
    W = mm_to_m(total_w_mm)
    H = mm_to_m(total_h_mm)

    fig, ax = plt.subplots(figsize=(min(14, max(8, W * 4.0)), min(8, max(4.5, H * 2.0))))
    ax.set_aspect("equal")
    ax.axis("off")

    # Outer carcass
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, linewidth=2))

    # Bay lines + internals
    x = 0.0
    for idx, (bw_mm, btype) in enumerate(zip(bay_widths_mm, bay_types), start=1):
        bw = mm_to_m(bw_mm)

        # Vertical bay boundary (except at far left which is outer frame)
        if x > 0:
            ax.plot([x, x], [0, H], linewidth=1.5)

        # Internals (no text labels for hanging)
        # Use simple visual cues:
        # - Single: one rail line
        # - Double: two rail lines
        # - Drawer Tower: drawer fronts as horizontal lines

        pad = 0.03 * min(bw, H)  # visual padding
        left = x + pad
        right = x + bw - pad

        if btype == "Single":
            # one rail line near upper third
            rail_y = H * 0.72
            ax.plot([left, right], [rail_y, rail_y], linewidth=2)

        elif btype == "Double":
            # two rails
            rail_y1 = H * 0.72
            rail_y2 = H * 0.45
            ax.plot([left, right], [rail_y1, rail_y1], linewidth=2)
            ax.plot([left, right], [rail_y2, rail_y2], linewidth=2)

        elif btype == "Drawer Tower":
            # stack of drawers from lower section up to mid
            bottom = H * 0.05
            top = H * 0.75
            # outer drawer "box"
            ax.add_patch(Rectangle((x + pad, bottom), bw - 2 * pad, top - bottom, fill=False, linewidth=1.5))
            # drawer lines
            n_drawers = 5 if view_mode == "Customer view" else 6
            ys = np.linspace(bottom, top, n_drawers + 1)
            for y in ys[1:-1]:
                ax.plot([x + pad, x + bw - pad], [y, y], linewidth=1)

        # Installer view: subtle bay index markers (optional)
        if view_mode == "Installer view":
            ax.text(x + bw / 2, H + (H * 0.02), f"Bay {idx}", ha="center", va="bottom", fontsize=10)

        # Dimensions labels (optional)
        if show_dims:
            ax.text(x + bw / 2, -H * 0.04, f"{bw_mm}mm", ha="center", va="top", fontsize=9)

        x += bw

    # last right boundary line is outer frame already

    # Overall dims (optional)
    if show_dims:
        ax.text(W / 2, H + H * 0.06, f"Overall: {total_w_mm}mm x {total_h_mm}mm", ha="center", va="bottom", fontsize=10)

    ax.set_xlim(-W * 0.03, W * 1.03)
    ax.set_ylim(-H * 0.10, H * 1.12)
    return fig

def draw_isometric(total_w_mm, total_h_mm, depth_mm, bay_widths_mm, bay_types, view_mode):
    # Fake 3D: draw front face + a shifted "top" and "side" to imply depth
    W = mm_to_m(total_w_mm)
    H = mm_to_m(total_h_mm)
    D = mm_to_m(depth_mm)

    # isometric offset (tweakable)
    ox = D * 0.55
    oy = D * 0.35

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_aspect("equal")
    ax.axis("off")

    # Front face rectangle
    front = Rectangle((0, 0), W, H, fill=False, linewidth=2)
    ax.add_patch(front)

    # Top face polygon
    top = Polygon([(0, H), (W, H), (W + ox, H + oy), (0 + ox, H + oy)], closed=True, fill=False, linewidth=1.5)
    ax.add_patch(top)

    # Side face polygon
    side = Polygon([(W, 0), (W, H), (W + ox, H + oy), (W + ox, 0 + oy)], closed=True, fill=False, linewidth=1.5)
    ax.add_patch(side)

    # Bay lines on front + echoed on top
    x = 0.0
    for idx, (bw_mm, btype) in enumerate(zip(bay_widths_mm, bay_types), start=1):
        bw = mm_to_m(bw_mm)
        if x > 0:
            ax.plot([x, x], [0, H], linewidth=1.2)
            ax.plot([x, x + ox], [H, H + oy], linewidth=1.0)

        # internal cues on the front (still no text labels)
        pad = 0.03 * min(bw, H)
        left = x + pad
        right = x + bw - pad

        if btype == "Single":
            rail_y = H * 0.72
            ax.plot([left, right], [rail_y, rail_y], linewidth=2)
        elif btype == "Double":
            rail_y1 = H * 0.72
            rail_y2 = H * 0.45
            ax.plot([left, right], [rail_y1, rail_y1], linewidth=2)
            ax.plot([left, right], [rail_y2, rail_y2], linewidth=2)
        elif btype == "Drawer Tower":
            bottom = H * 0.05
            top_y = H * 0.75
            ax.add_patch(Rectangle((x + pad, bottom), bw - 2 * pad, top_y - bottom, fill=False, linewidth=1.2))
            n_drawers = 5 if view_mode == "Customer view" else 6
            ys = np.linspace(bottom, top_y, n_drawers + 1)
            for y in ys[1:-1]:
                ax.plot([x + pad, x + bw - pad], [y, y], linewidth=0.9)

        # Installer view: bay id above
        if view_mode == "Installer view":
            ax.text(x + bw / 2, H + oy + (H * 0.03), f"Bay {idx}", ha="center", va="bottom", fontsize=9)

        x += bw

    ax.set_xlim(-W * 0.05, W + ox + W * 0.10)
    ax.set_ylim(-H * 0.05, H + oy + H * 0.15)
    return fig

# ----------------------------
# Sidebar controls
# ----------------------------
st.sidebar.header("Wardrobe Setup")

view_mode = st.sidebar.radio("View mode", ["Customer view", "Installer view"], horizontal=False)
render_mode = st.sidebar.radio("Render", ["2D elevation", "Isometric (fake 3D)"], horizontal=False)

total_w_mm = st.sidebar.number_input("Overall width (mm)", min_value=600, max_value=6000, value=2400, step=10)
total_h_mm = st.sidebar.number_input("Overall height (mm)", min_value=1800, max_value=3000, value=2400, step=10)
depth_mm = st.sidebar.number_input("Depth (mm)", min_value=300, max_value=800, value=600, step=10)

num_bays = clamp_int(st.sidebar.number_input("Number of bays", min_value=1, max_value=8, value=4, step=1), 1, 8)
ensure_state(num_bays)

st.sidebar.divider()
st.sidebar.subheader("Bays")

# Bay options per bay
bay_types = []
for i in range(num_bays):
    bay_types.append(
        st.sidebar.selectbox(
            f"Bay {i+1} type",
            ["Single", "Double", "Drawer Tower"],
            index=["Single", "Double", "Drawer Tower"].index(st.session_state["bay_types"][i]),
            key=f"bay_type_{i}",
        )
    )

# Persist
st.session_state["bay_types"] = bay_types

custom_widths_toggle = st.sidebar.checkbox("Custom bay widths", value=False)
custom_widths = None
if custom_widths_toggle:
    custom_widths = []
    st.sidebar.caption("Enter bay widths in mm (they will scale to fit overall width).")
    for i in range(num_bays):
        custom_widths.append(
            st.sidebar.number_input(f"Bay {i+1} width (mm)", min_value=200, max_value=3000, value=total_w_mm // num_bays, step=10, key=f"bay_w_{i}")
        )

show_dims = False
if view_mode == "Installer view":
    show_dims = st.sidebar.checkbox("Show dimensions", value=True)

# Compute bay widths
bay_widths_mm = split_widths(int(total_w_mm), num_bays, custom_widths)

# ----------------------------
# Main layout
# ----------------------------
colA, colB = st.columns([2, 1], gap="large")

with colA:
    st.subheader("Preview")

    if render_mode == "2D elevation":
        fig = draw_elevation(int(total_w_mm), int(total_h_mm), bay_widths_mm, bay_types, view_mode, show_dims)
        st.pyplot(fig, use_container_width=True)
    else:
        fig = draw_isometric(int(total_w_mm), int(total_h_mm), int(depth_mm), bay_widths_mm, bay_types, view_mode)
        st.pyplot(fig, use_container_width=True)

with colB:
    st.subheader("Summary")

    st.write(f"**Overall:** {int(total_w_mm)}mm (W) × {int(total_h_mm)}mm (H) × {int(depth_mm)}mm (D)")
    st.write(f"**Bays:** {num_bays}")

    for i, (w, t) in enumerate(zip(bay_widths_mm, bay_types), start=1):
        st.write(f"- Bay {i}: {w}mm — {t}")

    st.divider()
    st.info("No pricing included. This is purely a layout/design visual tied to your inputs.")
