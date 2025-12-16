import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Wardrobe Designer", layout="wide")
st.title("Wardrobe Designer")

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("Wardrobe Settings")

total_width = st.sidebar.number_input(
    "Total Width (mm)", min_value=1200, max_value=6000, value=2400, step=100
)

height = st.sidebar.number_input(
    "Height (mm)", min_value=1800, max_value=3000, value=2400, step=50
)

num_bays = st.sidebar.number_input(
    "Number of Bays", min_value=1, max_value=6, value=4, step=1
)

st.sidebar.divider()
st.sidebar.subheader("Bay Types")

bay_types = []
for i in range(num_bays):
    bay_type = st.sidebar.selectbox(
        f"Bay {i + 1}",
        ["Single Hanging", "Double Hanging", "Drawer Tower"],
        key=f"bay_{i}",
    )
    bay_types.append(bay_type)

# -----------------------------
# Drawing Function
# -----------------------------
def draw_wardrobe(total_width, height, bay_types):
    bay_width = total_width / len(bay_types)

    fig, ax = plt.subplots(figsize=(total_width / 400, height / 400))

    x = 0
    for bay_type in bay_types:
        # Outer bay
        ax.add_patch(
            plt.Rectangle((x, 0), bay_width, height, fill=False, linewidth=2)
        )

        # Internal layout
        if bay_type == "Single Hanging":
            # Shelf at top
            ax.plot([x, x + bay_width], [height * 0.85, height * 0.85], linewidth=2)
            # Hanging rail
            ax.plot(
                [x + bay_width * 0.15, x + bay_width * 0.85],
                [height * 0.75, height * 0.75],
                linewidth=2,
            )

        elif bay_type == "Double Hanging":
            # Top shelf
            ax.plot([x, x + bay_width], [height * 0.9, height * 0.9], linewidth=2)
            # Upper rail
            ax.plot(
                [x + bay_width * 0.15, x + bay_width * 0.85],
                [height * 0.7, height * 0.7],
                linewidth=2,
            )
            # Lower rail
            ax.plot(
                [x + bay_width * 0.15, x + bay_width * 0.85],
                [height * 0.4, height * 0.4],
                linewidth=2,
            )

        elif bay_type == "Drawer Tower":
            drawer_count = 4
            drawer_height = (height * 0.6) / drawer_count
            y = 0

            for _ in range(drawer_count):
                ax.add_patch(
                    plt.Rectangle(
                        (x, y),
                        bay_width,
                        drawer_height,
                        fill=False,
                        linewidth=1.5,
                    )
                )
                y += drawer_height

            # Shelf above drawers
            ax.plot([x, x + bay_width], [height * 0.65, height * 0.65], linewidth=2)

        x += bay_width

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(0, total_width)
    ax.set_ylim(0, height)

    return fig

# -----------------------------
# Render
# -----------------------------
st.subheader("Wardrobe Elevation")

fig = draw_wardrobe(total_width, height, bay_types)
st.pyplot(fig)

st.info(
    "This is a scaled elevation view. Dimensions and internals are generated directly from your inputs."
)

