import streamlit as st

st.set_page_config(
    page_title="BizCardX: Business Card Data with OCR",
    page_icon=" ⌨",
)
st.write("# Welcome to BizCardX: Business Card Data with OCR!  ⌨")

st.title("By Geetha Sukumar")



st.markdown(
    """
    BizCardX - A Streamlit Application that allows users to
    upload an image of a business card and extract relevant information from it using
    easyOCR.
    
    - The extracted information can be edited for its correctness and saved to MySQL Databases.
    - All the Business card details with a preview of the uploaded card is available for the user to View and Delete it as required.
"""
)
