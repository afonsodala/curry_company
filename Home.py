import streamlit as st
from PIL import Image

st.set_page_config(
        page_title ='Home',
        page_icon ='🎲'
)



#image_path = r'\Users\Afonso Dala\Documents\repos\ftc_programacao_python\ciclo06'

image = Image.open ('pic.jpg')
st.sidebar.image (image, width=120)

st.sidebar.markdown('### Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write ('## Curry Conmpany Growth Dashboard')

