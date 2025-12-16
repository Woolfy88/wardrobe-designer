import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

st.set_page_config(page_title="Wardrobe Designer", layout="wide")
st.title("Wardrobe Designer (Option 1 – 2D Elevation)")

st.caption("Build a simple wardrobe elevation by bays. Choose Single Hanging / Double Hanging / Drawer Tower per bay.")

# ----------------------------
# Helpers
# ----------------------------
def mm(val) -> float:
    """Force float in mm units."""
    return float(val)

def ensure_session_defaults(num_bays: int):
    if "bay_configs" not in st.session_state:
        st.session_state.bay_configs = []

    # Expand / shrink list to match num_bays
    current = len(st.session_state.bay_configs)
    if current < num_bays:
        for _ in range(num_bays - current):
            st.session_state.bay_configs.append({
                "type": "Single Hanging",
                "drawer_count": 4,
                "tower_height": 900,   # mm
                "rail_height": 1700,   # mm (single hanging)
                "mid_rail_height": 950 # mm (double hanging split line)
            })
    elif current > num_bays:
        st.session_state.bay_configs = st.session_state.bay_configs[:num_bays]

def draw_wardrobe(total_width, total_height, plinth_height, bay_widths, bay_configs):
    """
    Draw 2D elevation:
    - Outer carcass box
    - Vertical bay divisions
    - Plinth
    - Internals per bay:
        - Single Hanging: rail line at rail_height
        - Double Hanging: split line at mid_rail_height and rail lines above/below
        - Drawer Tower: drawers stacked in a tower at bottom
    """
    W = mm(total_width)
    H = mm(total_height)
    P = mm(plinth_height)

    fig_w = max(7, W / 300)  # scale figure size
    fig_h = max(4, H / 450)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # Outer wardrobe
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, linewidth=2))

    # Plinth
    if P > 0:
        ax.add_patch(Rectangle((0, 0), W, P, fill=False, linewidth=1))
        ax.text(W * 0.5, P * 0.5, f"Plinth {int(P)}mm", ha="center", va="center", fontsize=9)

    # Bay divisions + content
    x = 0.0
    for i, (bw, cfg) in enumerate(zip(bay_widths, bay_configs), start=1):
        bw = mm(bw)
        # vertical division line except first (x==0)
        if x > 0:
            ax.plot([x, x], [0, H], linewidth=2)

        # bay label
        ax.text(x + bw / 2, H + (H * 0.02), f"Bay {i}\n{int(bw)}mm", ha="center", va="bottom", fontsize=10)

        bay_bottom = P
        bay_top = H

        bay_type = cfg["type"]

        # Draw internals
        if bay_type == "Single Hanging":
            rail_h = mm(cfg["rail_height"])
            rail_h = np.clip(rail_h, bay_bottom + 200, bay_top - 100)
            # rail line
            ax.plot([x + bw * 0.15, x + bw * 0.85], [rail_h, rail_h], linewidth=2)
            ax.text(x + bw * 0.5, rail_h + 35, "Hanging Rail", ha="center", va="bottom", fontsize=9)

        elif bay_type == "Double Hanging":
            mid = mm(cfg["mid_rail_height"])
            mid = np.clip(mid, bay_bottom + 300, bay_top - 300)

            # split shelf/rail line
            ax.plot([x, x + bw], [mid, mid], linewidth=1.5)

            # top rail
            top_rail = np.clip(mid + 550, mid + 300, bay_top - 100)
            ax.plot([x + bw * 0.15, x + bw * 0.85], [top_rail, top_rail], linewidth=2)
            ax.text(x + bw * 0.5, top_rail + 35, "Top Rail", ha="center", va="bottom", fontsize=9)

            # bottom rail
            bot_rail = np.clip(bay_bottom + 550, bay_bottom + 250, mid - 100)
            ax.plot([x + bw * 0.15, x + bw * 0.85], [bot_rail, bot_rail], linewidth=2)
            ax.text(x + bw * 0.5, bot_rail + 35, "Bottom Rail", ha="center", va="bottom", fontsize=9)

            ax.text(x + bw * 0.5, mid + 10, "Mid Divider", ha="center", va="bottom", fontsize=8)

        elif bay_type == "Drawer Tower":
            drawer_count = int(cfg["drawer_count"])
            tower_h = mm(cfg["tower_height"])
            tower_h = np.clip(tower_h, 400, bay_top - bay_bottom - 100)

            # Tower outline (bottom-aligned above plinth)
            tower_y = bay_bottom
            ax.add_patch(Rectangle((x + bw * 0.12, tower_y), bw * 0.76, tower_h, fill=False, linewidth=1.5))
            ax.text(x + bw * 0.5, tower_y + tower_h + 35, f"Drawer Tower ({drawer_count})", ha="center", va="bottom", fontsize=9)

            # Drawer lines
            drawer_count = max(1, drawer_count)
            drawer_h = tower_h / drawer_count
            for d in range(1, drawer_count):
                y = tower_y + d * drawer_h
                ax.plot([x + bw * 0.12, x + bw * 0.88], [y, y], linewidth=1)

            # Optional rail above tower (visual)
            rail_h = min(bay_top - 120, tower_y + tower_h + 650)
            if rail_h > tower_y + tower_h + 150:
                ax.plot([x + bw * 0.15, x + bw * 0.85], [rail_h, rail_h], linewidth=2)
                ax.text(x + bw * 0.5, rail_h + 35, "Hanging Rail", ha="center", va="bottom", fontsize=9)

        # bay type label inside
        ax.text(x + bw * 0.5, bay_top - 80, bay_type, ha="center", va="top", fontsize=10)

        x += bw

    # Axes styling
    ax.set_xlim(-50, W + 50)
    ax.set_ylim(0, H + (H * 0.12))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    return fig


# ----------------------------
# UI
# ----------------------------
with st.sidebar:
    st.header("Wardrobe Settings")

    total_width = st.number_input("Total width (mm)", min_value=600, max_value=12000, value=2400, step=50)
    total_height = st.number_input("Total height (mm)", min_value=1800, max_value=3000, value=2400, step=50)
    plinth_height = st.number_input("Plinth (mm)", min_value=0, max_value=200, value=80, step=10)

    num_bays = st.slider("Number of bays", min_value=1, max_value=8, value=4)

    st.divider()
    width_mode = st.radio("Bay widths", ["Equal widths", "Custom widths"], index=0)

ensure_session_defaults(num_bays)

# Bay widths
if width_mode == "Equal widths":
    bay_widths = [total_width / num_bays] * num_bays
else:
    st.subheader("Bay widths (mm)")
    st.caption("Tip: make them add up to the total. If not, we’ll auto-scale to fit.")
    cols = st.columns(min(4, num_bays))
    raw = []
    for i in range(num_bays):
        with cols[i % len(cols)]:
            raw.append(st.number_input(f"Bay {i+1} width", min_value=200, max_value=4000, value=int(total_width / num_bays), step=50))
    s = sum(raw)
    if s <= 0:
        bay_widths = [total_width / num_bays] * num_bays
    else:
        # Auto-scale widths to total
        bay_widths = [w * (total_width / s) for w in raw]

st.divider()
st.subheader("Bay internals")

for i in range(num_bays):
    cfg = st.session_state.bay_configs[i]
    with st.expander(f"Bay {i+1} options", expanded=(i == 0)):
        cfg["type"] = st.selectbox(
            "Bay type",
            ["Single Hanging", "Double Hanging", "Drawer Tower"],
            index=["Single Hanging", "Double Hanging", "Drawer Tower"].index(cfg["type"]),
            key=f"bay_type_{i}"
        )

        if cfg["type"] == "Single Hanging":
            cfg["rail_height"] = st.number_input(
                "Rail height (mm)",
                min_value=400, max_value=int(total_height),
                value=int(cfg["rail_height"]), step=25,
                key=f"rail_{i}"
            )

        elif cfg["type"] == "Double Hanging":
            cfg["mid_rail_height"] = st.number_input(
                "Mid divider height (mm)",
                min_value=400, max_value=int(total_height - 400),
                value=int(cfg["mid_rail_height"]), step=25,
                key=f"mid_{i}"
            )

        elif cfg["type"] == "Drawer Tower":
            cfg["drawer_count"] = st.slider(
                "Number of drawers", min_value=1, max_value=8,
                value=int(cfg["drawer_count"]),
                key=f"drawers_{i}"
            )
            cfg["tower_height"] = st.number_input(
                "Tower height (mm)",
                min_value=400, max_value=int(total_height),
                value=int(cfg["tower_height"]), step=50,
                key=f"tower_{i}"
            )

    st.session_state.bay_configs[i] = cfg

# ----------------------------
# Render
# ----------------------------
st.subheader("Wardrobe elevation preview")

fig = draw_wardrobe(
    total_width=total_width,
    total_height=total_height,
    plinth_height=plinth_height,
    bay_widths=bay_widths,
    bay_configs=st.session_state.bay_configs
)
st.pyplot(fig, use_container_width=True)

# Optional: download image
st.divider()
st.subheader("Download")
import io
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
st.download_button(
    "Download PNG",
    data=buf.getvalue(),
    file_name="wardrobe_elevation.png",
    mime="image/png"
)
