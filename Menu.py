import streamlit as st
import Complementos as comp
import Facial as face

st.set_page_config(page_title="Face-Guest", page_icon=":smiley:", layout="centered")

# Aqui iniciamos a st.session_state tela caso não exista, e definimos a tela inicial como "inicio"
if "tela" not in st.session_state:
    st.session_state.tela = "inicio"

# Módulo #1
if st.session_state.tela == "inicio":

    #Prints de tela atual vão existir por todo o código, para facilitar a visualização de qual tela está ativa no momento
    print(f"Tela atual: {st.session_state.tela}")

    #Isso aqui é pra foto ficar no meio KKKK
    midcol1, midcol2, midcol3 = st.columns([1, 2, 1])
    container = st.container

    with midcol2:
        face = st.camera_input("Capture sua foto para gerar o hash facial", key="camera_input")

        if face is not None:

            #Geração de nome e caminho
            nome_face = comp.data() + ".jpg"
            caminho_face = f"./Faciais/{nome_face}"
            print(f"Nome da Facial: {nome_face}")

            #Caminho é salvo na sessão
            st.session_state["caminho_face"] = caminho_face

            #Salvando o arquivo
            with open(f"./Faciais/{nome_face}", "wb") as arquivo:
                arquivo.write(face.getbuffer())
                print(f"Facial salva em: {caminho_face}")

            #Mostra sucesso e espera um tempo de 2 segundos, depois vai para a sessão de geração de hash
            st.success("Foto salva!")
            comp.wait(2)

            st.session_state.tela = "gerar_hash"
            st.rerun()

if st.session_state.tela == "gerar_hash":

    print(f"Tela atual: {st.session_state.tela}")

    st.write("Tela de Gerar Hash")

    resultado = face.gerar_hash(caminho=st.session_state["caminho_face"])

    if resultado:
        st.success("Hash gerado com sucesso!")

        comp.wait(2)

        st.session_state.tela = "inicio"
        st.rerun()

    else:
        st.error("Nenhum rosto detectado na imagem. Por favor, tente novamente.")

        comp.wait(2)

        st.session_state.tela = "inicio"
        st.rerun()