import streamlit as st
import Complementos as comp

st.set_page_config(page_title="Face-Guest", page_icon=":smiley:", layout="wide")

# [ESTÉTICA] Substituição do st.title padrão por um HTML customizado para centralizar e dar cor
st.markdown("<h1 style='text-align: center; color: #1F77B4;'>📷 FACE-GUEST</h1>", unsafe_allow_html=True)

# [ESTÉTICA] Linha divisória horizontal para separar o título do resto da página
st.divider()

if "tela" not in st.session_state:
    st.session_state.tela = "inicio"

if st.session_state.tela == "inicio":
    # [ESTÉTICA] Centralização do subtítulo e mudança de cor para um tom mais suave
    st.markdown("<h3 style='text-align: center; color: gray;'>Seja bem-vindo ao sistema de reconhecimento</h3>", unsafe_allow_html=True)
    
    # [ESTÉTICA] Quebras de linha (espaços vazios) para o botão não ficar colado no texto
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # [ESTÉTICA] Adição de ícone no texto. 
        # type="primary" deixa o botão em destaque com a cor principal do tema.
        # use_container_width=True faz o botão esticar e preencher toda a coluna central.
        if st.button("🚀 Iniciar Sistema", type="primary", use_container_width=True):
            st.session_state.tela = "menu"
            st.rerun()

if st.session_state.tela != "inicio":
    with st.sidebar:
        # [ESTÉTICA] Adição de emojis e mudança para subheader para não ficar muito grande
        st.subheader("⚙️ Menu de Navegação")
        st.write("Selecione um módulo:")
        
        # [ESTÉTICA] Linha divisória na barra lateral para organizar a leitura
        st.divider()
        
        # [ESTÉTICA] Emojis adicionados diretamente nos rótulos das opções
        escolha = st.radio(
            "Opções", 
            ["📸 Tirar foto", "🔐 Gerar hash facial", "⚖️ Comparar hashes faciais"], 
            index=None,
            # [ESTÉTICA] label_visibility="collapsed" esconde o título "Opções" do radio, deixando mais clean
            label_visibility="collapsed"
        )
    
        if escolha == "📸 Tirar foto":
            st.session_state.tela = "tirar_foto"
        if escolha == "🔐 Gerar hash facial":
            st.session_state.tela = "gerar_hash"
        if escolha == "⚖️ Comparar hashes faciais":
            st.session_state.tela = "comparar_hashes"

# Módulo #1
if st.session_state.tela == "tirar_foto":
    # [ESTÉTICA] st.subheader e st.info criam um visual mais hierárquico e corporativo
    st.subheader("📸 Captura de Imagem")
    st.info("Centralize o rosto na câmera para iniciar.")
    
    col1, col2 = st.columns(2)
    with col1:
        # [ESTÉTICA] Movemos o widget da câmera para dentro da Coluna 1
        foto_tirada = st.camera_input("Tire uma foto")
        
    with col2:
        # [ESTÉTICA] st.container(border=True) cria uma "caixa" bonitinha ao redor do resultado
        with st.container(border=True):
            st.markdown("#### 📋 Resultado da Captura")
            
            # [ESTÉTICA] Feedback visual dinâmico com cores dependendo se a foto foi tirada ou não
            if foto_tirada:
                st.success("Foto capturada com sucesso!")
            else:
                st.warning("Aguardando captura da câmera...")

# Módulo #2
elif st.session_state.tela == "gerar_hash":
    # [ESTÉTICA] Padronização dos cabeçalhos dos módulos
    st.subheader("🔐 Geração de Hash Facial")
    st.info("O sistema está pronto para processar a biometria.")
    
# Módulo #3
elif st.session_state.tela == "comparar_hashes":
    # [ESTÉTICA] Padronização dos cabeçalhos dos módulos
    st.subheader("⚖️ Comparação de Hashes")
    st.info("O sistema está pronto para realizar a validação.")