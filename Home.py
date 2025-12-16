import streamlit as st

st.set_page_config(
    page_title="Wardrobe Designer",
    layout="wide"
)

st.title("Wardrobe Designer")
st.markdown("""
Welcome.

Use the menu on the left to open the **Wardrobe Designer**.

This tool generates a **scaled 2D wardrobe elevation**
based on your inputs — no pricing, no CAD, just design.
""")

st.info("On mobile, tap ☰ (top left) to open the menu.")
