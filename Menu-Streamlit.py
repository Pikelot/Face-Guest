import streamlit as st
import Complementos as comp

st.set_page_config(page_title="Face-Guest", page_icon=":smiley:", layout="wide")

# Inicio, Menu, Tirar Foto, Gerar Hash, Comparar Hash

# Aqui iniciamos a st.session_state tela caso não exista, e definimos a tela inicial como "inicio"
if "tela" not in st.session_state:
    st.session_state.tela = "inicio"

# Módulo #1
if st.session_state.tela == "inicio":

    # upcol1, upcol2, upcol3 = st.columns([2, 2, 2])

    midcol1, midcol2, midcol3 = st.columns([1, 2, 1])
    container = st.container

    with midcol2:
        face = st.camera_input("Capture sua foto para gerar o hash facial", key="camera_input")