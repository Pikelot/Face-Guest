import streamlit as st
import Complementos as comp

st.title("FACE-GUEST")

# Cria um widget que abre a câmera no navegador
foto_tirada = st.camera_input("Tire uma foto")

if foto_tirada is not None:
    # Exibe a foto na tela
    st.image(foto_tirada, caption="Sua foto")
    
    # Salva o arquivo localmente
    with open(f"{comp.data()}.jpg", "wb") as arquivo:
        arquivo.write(foto_tirada.getbuffer())
        
    st.success("Foto salva no servidor!")