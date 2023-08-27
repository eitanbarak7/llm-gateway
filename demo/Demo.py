import streamlit as st
from PIL import Image
image = Image.open('./demo/pages/acmelogo.jpeg')

st.set_page_config(
    page_title="Hello",
    page_icon=image,
)

st.write("# Welcome to the LLM Chat! 👋")
logo = Image.open('./demo/pages/acme.jpeg')
st.sidebar.image(logo, width=300)
st.sidebar.success("Select a chat above.")



st.markdown(
    """
    This is the LLM Chat Service. \n
    Currently it provides the following capabilities:
    - Regular LLM chat with OpenAI
    - Specialized assistant for the "Why Students Should Eat Breakfast Every Day" essay.
    
    **👈 Start by selecting a chat on the left.**

"""
)
