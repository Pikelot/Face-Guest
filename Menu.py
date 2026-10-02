import streamlit as st
import Complementos as comp
import Controladora as ctrl
import Facial as face

st.set_page_config(page_title="Face-Guest", page_icon=":smiley:", layout="centered")

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

    resultado = face.gerar_encoding(caminho=st.session_state["caminho_face"], ação=0)

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

#Session 3 - Gera os Vouchers e retorna para o inicio

if st.session_state.tela == "gerar_voucher":

    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    voucher = ctrl.Gerar_voucher()

    st.write("")

    col1, col2, col3 = st.columns([1, 20, 1])

    with col2:
        st.title(voucher)
        st.subheader("Seu Código de Acesso Único")

    comp.wait(10)

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

    resultado = face.gerar_encoding(caminho=st.session_state["caminho_face"], ação=1)
    
    if resultado[0]:
        st.success("Encoding gerado com sucesso!")
        st.session_state.camera_key += 1

        st.session_state["caminho_encoding"] = resultado[1]

        st.session_state.tela = "comparar_encoding"

        comp.wait(2)
        st.rerun()

    else:
        st.error("Nenhum rosto detectado na imagem. Por favor, tente novamente.")
        st.session_state.camera_key += 1
        st.session_state.tela = "inicio_verififcar_face"

        comp.wait(2)
        st.rerun()

#Session 6 - Compara os encodings e retorna o resultado para o usuário depois retorna para o inicio WIP
if st.session_state.tela == "comparar_encoding":

    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    resultado = face.comparar_encodings(st.session_state["caminho_encoding"])

    st.success(resultado)

    comp.wait(5)

    st.session_state.tela = "inicio_verificar_face"
    st.rerun()