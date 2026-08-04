import streamlit as st
import Complementos as comp

st.set_page_config(page_title="Face-Guest", page_icon=":smiley:", layout="wide")

# Inicio, Menu, Tirar Foto, Gerar Hash, Comparar Hash

# Aqui iniciamosa st.session_state tela caso não exista, e definimos a tela inicial como "inicio"
if "tela" not in st.session_state:
    st.session_state.tela = "inicio"

# Aqui há uma breve apresentação ao usuário e um botão que o leva ao menu do Face-Guest.
if st.session_state.tela == "inicio":

    st.markdown("<h1 style='text-align: center; color: #1F77B4;'>📷 FACE-GUEST</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Iniciar", use_container_width=True):

            st.session_state.tela = "menu"
            st.rerun()

# Aqui é o Menu que leva aos outros três módulos do Face-Guest.
if st.session_state.tela != "inicio":

    # Barra lateral do Menu
    with st.sidebar:
        st.sidebar.header("Escolha um dos módulos do Face-Guest!")
        escolha = st.radio("Choose an option:", ["Tirar foto", "Gerar hash facial", "Comparar hashes faciais"], index=None)
    
        if escolha == "Tirar foto":
            st.session_state.tela = "tirar_foto"
        if escolha == "Gerar hash facial":
            st.session_state.tela = "gerar_hash"
        if escolha == "Comparar hashes faciais":
            st.session_state.tela = "comparar_hashes"

# Módulo #1
if st.session_state.tela == "tirar_foto":

    # upcol1, upcol2, upcol3 = st.columns([2, 2, 2])

    midcol1, midcol2, midcol3 = st.columns([1, 2, 1])
    container = st.container

    with midcol2:
        st.markdown("<h1 style='text-align: center; color: #1F77B4;'>Capture sua imagem:</h1>", unsafe_allow_html=True)

        estilo_camera = """
<style>
    /* Pega os botões dentro do widget de câmera e zera a fonte original */
    div[data-testid="stCameraInput"] button {
        font-size: 0 !important;
    }
    
    /* Adiciona o texto novo em português */
    div[data-testid="stCameraInput"] button::after {
        content: '📸 Tirar Foto';
        font-size: 16px !important;
        font-weight: 600;
        visibility: visible !important;
        display: block;
    }
</style>
"""
        st.markdown(estilo_camera, unsafe_allow_html=True)
        face = st.camera_input("📷 Capture sua imagem", key="camera_input", label_visibility="hidden", )

# Módulo #2
elif st.session_state.tela == "gerar_hash":
    st.write("Opção selecionada: Gerar hash facial")
    
# Módulo #3
elif st.session_state.tela == "comparar_hashes":
    st.write("Opção selecionada: Comparar hashes faciais")