import streamlit as st
import Complementos as comp
import Controladora as ctrl
import Facial as face
import DB_SQL as sql

st.set_page_config(page_title="Face-Guest", page_icon=":smiley:", layout="centered")

# ---------- ESTILO VISUAL (somente aparência) ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
}

/* Fundo com gradiente suave */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 55%, #312e81 100%);
    color: #e2e8f0;
}

/* Esconde elementos padrão do Streamlit */
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }

/* Container principal */
.block-container {
    padding-top: 3rem;
    max-width: 760px;
}

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(148, 163, 184, 0.15);
}
[data-testid="stSidebar"] [role="radiogroup"] { gap: 0.5rem; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 12px;
    padding: 0.7rem 0.9rem;
    transition: all 0.2s ease;
    width: 100%;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(99, 102, 241, 0.18);
    border-color: rgba(129, 140, 248, 0.6);
    transform: translateX(3px);
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, rgba(99,102,241,0.35), rgba(139,92,246,0.35));
    border-color: #818cf8;
}

/* ---------- CÂMERA ---------- */
[data-testid="stCameraInput"] {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 1rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
}
[data-testid="stCameraInput"] label p {
    font-weight: 600;
    font-size: 1rem;
    text-align: center;
    color: #c7d2fe;
}
[data-testid="stCameraInput"] video,
[data-testid="stCameraInput"] img {
    border-radius: 14px;
}

/* ---------- BOTÕES ---------- */
.stButton > button,
[data-testid="stCameraInput"] button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.45);
}
.stButton > button:hover,
[data-testid="stCameraInput"] button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(99, 102, 241, 0.6);
    color: #fff;
}

/* ---------- ALERTAS (sucesso / erro) ---------- */
[data-testid="stAlert"] {
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(8px);
    animation: surgir 0.4s ease;
}

/* ---------- TELA DO VOUCHER ---------- */
h1 {
    font-family: 'JetBrains Mono', monospace !important;
    text-align: center;
    font-size: 3rem !important;
    letter-spacing: 0.25rem;
    color: #fff;
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.25));
    border: 2px dashed #818cf8;
    border-radius: 20px;
    padding: 1.5rem 1rem !important;
    margin-top: 1rem;
    text-shadow: 0 0 20px rgba(129, 140, 248, 0.8);
    animation: surgir 0.6s ease, brilho 2.5s ease-in-out infinite;
}
h3 {
    text-align: center;
    color: #a5b4fc;
    font-weight: 500;
}

/* ---------- TELA DE HISTÓRICO ---------- */
[data-testid="stMarkdownContainer"] p {
    line-height: 1.6;
}

/* ---------- ANIMAÇÕES ---------- */
@keyframes surgir {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes brilho {
    0%, 100% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.3); }
    50%      { box-shadow: 0 0 35px rgba(139, 92, 246, 0.7); }
}
</style>
""", unsafe_allow_html=True)
# ---------- FIM DO ESTILO ----------

sql.criar_tabela()

# Aqui iniciamos a st.session_state tela caso não exista, e definimos a tela inicial como "inicio"
if "tela" not in st.session_state:
    st.session_state.tela = "inicio"

opcoes = {
    "Autenticar e gerar Voucher": "inicio",
    "Verificar histórico facial": "inicio_verificar_face"
}

selecao = st.sidebar.radio("Menu", list(opcoes.keys()))

if st.session_state.tela in ["inicio", "inicio_verificar_face"]:
    st.session_state.tela = opcoes[selecao]

if "camera_key" not in st.session_state:
    st.session_state.camera_key = 0

# PROCESSO DE AUTENTICAÇÃO

#Session 1 - Captura a face e envia para a geração de enconding
if st.session_state.tela == "inicio":

    #Prints de tela atual vão existir por todo o código, para facilitar a visualização de qual tela está ativa no momento
    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    #Isso aqui é pra foto ficar no meio KKKK
    midcol1, midcol2, midcol3 = st.columns([1, 2, 1])
    container = st.container

    with midcol2:

        face = st.camera_input("Capture sua foto para gerar o encoding facial", key=f"camera_input_{st.session_state.camera_key}")

        if face is not None:

            #Geração de nome e caminho
            nome_face = comp.data() + ".jpg"
            caminho_face = f"./Faciais/{nome_face}"
            print(f"Menu.py - Nome da Facial: {nome_face}")

            #Caminho é salvo na sessão
            st.session_state["caminho_face"] = caminho_face

            #Salvando o arquivo
            with open(f"./Faciais/{nome_face}", "wb") as arquivo:
                arquivo.write(face.getbuffer())
                print(f"Menu.py - Facial salva em: {caminho_face}")

            #Mostra sucesso e espera um tempo de 2 segundos, depois vai para a sessão de geração do encoding
            st.success("Foto salva!")
            comp.wait(2)

            face = ""

            st.session_state.tela = "gerar_encoding"
            st.rerun()

#Session 2 - Gera os encodings e redireciona para a geração de Vouchers ou retorna para o inicio se erro
if st.session_state.tela == "gerar_encoding":

    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    resultado = face.gerar_encoding(caminho=st.session_state["caminho_face"])
    st.session_state["id"] = resultado[1]

    if resultado[0]:
        st.success("Encoding gerado com sucesso!")
        st.session_state.camera_key += 1
        st.session_state.tela = "gerar_voucher"

        comp.wait(2)
        st.rerun()

    else:
        st.error("Nenhum rosto detectado na imagem. Por favor, tente novamente.")
        st.session_state.camera_key += 1
        st.session_state.tela = "inicio"

        comp.wait(2)
        st.rerun()

#Session 3 - Gera os Vouchers e manda conexão para o banco de dados, depois retorna para o inicio

if st.session_state.tela == "gerar_voucher":

    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    voucher = ctrl.Gerar_voucher()
    ip = ctrl.IP()

    st.write("")

    col1, col2, col3 = st.columns([1, 20, 1])

    with col2:
        st.title(voucher)
        st.subheader("Seu Código de Acesso Único")

    comp.wait(10)

    sql.registrar_conexao(st.session_state["id"], ip, voucher)
    print(f"Menu.py - Conexão registrada no banco de dados com ID: {st.session_state['id']}, Voucher: {voucher}, IP: {ip}")

    st.session_state.tela = "inicio"
    st.rerun()

# PROCESSO DE VERIFICAÇÃO

#Session 4 - Captura a face e envia para a geração de encodings
if st.session_state.tela == "inicio_verificar_face":

    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    #Basicamente a mesma coisa da tela de autenticação

    midcol1, midcol2, midcol3 = st.columns([1, 2, 1])
    container = st.container

    with midcol2:

        face = st.camera_input("Capture a foto para verificar a facial", key=f"camera_input_{st.session_state.camera_key}")

        if face is not None:

            #Geração de nome e caminho
            nome_face = comp.data() + ".jpg"
            caminho_face = f"./Faciais/{nome_face}"
            print(f"Menu.py - Nome da Facial: {nome_face}")

            #Caminho é salvo na sessão
            st.session_state["caminho_face"] = caminho_face

            #Salvando o arquivo
            with open(f"./Faciais/{nome_face}", "wb") as arquivo:
                arquivo.write(face.getbuffer())
                print(f"Menu.py - Facial salva em: {caminho_face}")

            #Mostra sucesso e espera um tempo de 2 segundos, depois vai para a sessão de geração de encoding
            st.success("Foto salva!")
            comp.wait(2)

            face = ""

            #Aqui vamos para a session de número #4
            st.session_state.tela = "verificar_gerar_encoding"
            st.rerun()

#Session 5 - Gera os encodings e redireciona para a comparação dos encodings ou retorna para o inicio se erro
if st.session_state.tela == "verificar_gerar_encoding":

    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    #Gera o resultado da comparação entre os dois encodings, [0] é o booleano e [1] é o ID da pessoa encontrada no banco de dados

    resultado = face.gerar_encoding_comparação(caminho=st.session_state["caminho_face"])
    
    if resultado[0]:

        st.success("Encoding gerado com sucesso e Facial encontrada!")
        st.session_state.camera_key += 1

        st.session_state["id"] = resultado[1]

        st.session_state.tela = "retornar_encoding"

        comp.wait(2)
        st.rerun()

    else:
        st.error("Nenhum rosto detectado na imagem. Por favor, tente novamente.")
        st.session_state.camera_key += 1
        st.session_state.tela = "inicio_verificar_face"

        comp.wait(2)
        st.rerun()

#Session 6 - retorna o resultado para o usuário depois retorna para o inicio WIP
#Session 6 - retorna o resultado para o usuário depois retorna para o inicio
if st.session_state.tela == "retornar_encoding":

    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    resultado = sql.buscar_conexoes(st.session_state["id"])

    print(f"Menu.py - Resultado: {resultado}")

    if resultado:

        st.success("Facial encontrada!")

        st.metric("Usuário ID", st.session_state["id"])
        st.metric("Conexões registradas", len(resultado))

        # Tabela com todas as conexões de uma vez
        import pandas as pd
        df = pd.DataFrame(resultado, columns=["IP", "Voucher", "Data"])

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "IP": st.column_config.TextColumn("🌐 IP"),
                "Voucher": st.column_config.TextColumn("🎟️ Voucher"),
                "Data": st.column_config.TextColumn("📅 Data"),
            },
        )

        st.write("")

        if st.button("🔄 Nova verificação", use_container_width=True):
            st.session_state.tela = "inicio_verificar_face"
            st.rerun()

    else:

        st.warning("Facial encontrada, mas nenhuma conexão foi registrada para esta pessoa.")

        comp.wait(3)

        st.session_state.tela = "inicio_verificar_face"
        st.rerun()