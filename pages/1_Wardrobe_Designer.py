import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Wardrobe Designer",
    layout="wide"
)

st.title("Wardrobe Designer (2D Elevation)")

# ----------------------------
# Inputs
# ----------------------------
with st.sidebar:
    st.header("Wardrobe Inputs")

    total_width = st.number_input(
        "Total Width (mm)",
        min_value=600,
        max_value=6000,
        value=2400,
        step=100,
    )

    height = st.number_input(
        "Height (mm)",
        min_value=1800,
        max_value=3000,
        value=2400,
        step=50,
    )

    depth = st.number_input(
        "Depth (mm)",
        min_value=400,
        max_value=700,
        value=600,
        step=25,
    )

    bays = st.number_input(
        "Number of Bays",
        min_value=1,
        max_value=8,
        value=4,
        step=1,
    )

# ----------------------------
# Calculations
# ----------------------------
bay_width = total_width / bays
bay_widths = [bay_width] * bays

# ----------------------------
# Drawing function
# ----------------------------
def draw_wardrobe(bay_widths, height):
    fig, ax = plt.subplots(figsize=(total_width / 400, height / 400))

    x = 0
    for i, w in enumerate(bay_widths):
        # Outer bay
        ax.add_patch(
            plt.Rectangle(
                (x, 0),
                w,
                height,
                fill=False,
                linewidth=2
            )
        )

        # Centre hanging rail (visual only)
        rail_y = height * 0.75
        ax.plot(
            [x + 40, x + w - 40],
            [rail_y, rail_y],
            linewidth=2
        )

        # Label
        ax.text(
            x + w / 2,
            -80,
            f"Bay {i + 1}\n{int(w)}mm",
            ha="center",
            va="top",
            fontsize=9
        )

        x += w

    # Outer frame
    ax.add_patch(
        plt.Rectangle(
            (0, 0),
            sum(bay_widths),
            height,
            fill=False,
            linewidth=3
        )
    )

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(0, sum(bay_widths))
    ax.set_ylim(-150, height + 50)

    return fig

# ----------------------------
# Layout
# ----------------------------
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Summary")
    st.write(f"**Total width:** {int(total_width)} mm")
    st.write(f"**Height:** {int(height)} mm")
    st.write(f"**Depth:** {int(depth)} mm")
    st.write(f"**Bays:** {bays}")
    st.write(f"**Bay width:** {int(bay_width)} mm")

with col2:
    st.subheader("Wardrobe Elevation")
    fig = draw_wardrobe(bay_widths, height)
    st.pyplot(fig, use_container_width=True)
