import streamlit as st
from pathlib import Path
import Complementos as comp
import Controladora as ctrl
import Facial as face
import DB_SQL as sql

st.set_page_config(page_title="Face-Guest", page_icon=":smiley:", layout="centered")

# ---------- ESTILO VISUAL (definido em estilo.css) ----------
css = Path(__file__).with_name("estilo.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

sql.criar_tabela()

# Aqui iniciamos a st.session_state tela caso não exista, e definimos a tela inicial como "inicio"
if "tela" not in st.session_state:
    st.session_state.tela = "inicio"

if "controladora" not in st.session_state:
    st.session_state.controladora = ctrl.Conectar()
    print(f"Menu.py - Conectado a controladora.")

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

    if "voucher" not in st.session_state:
        st.session_state["voucher"] = ctrl.Gerar_voucher(st.session_state.controladora, st.session_state["id"])[0]

    st.write("")

    col1, col2, col3 = st.columns([1, 20, 1])

    with col2:
        st.title(st.session_state["voucher"])
        st.subheader("Seu Código de Acesso Único")

    registrada = False
    for tentativa in range(12):
        print(f"Menu.py - Tentativa {tentativa + 1}/12 para localizar o dispositivo...")
        st.info(f"Procurando o dispositivo... tentativa {tentativa + 1} de 12")

        try:
            dispositivo = ctrl.IP(
                st.session_state.controladora,
                st.session_state["voucher"],
            )

            if dispositivo:
                ip, hostname, mac = dispositivo
                sql.registrar_conexao(
                    st.session_state["id"],
                    ip,
                    st.session_state["voucher"],
                    hostname,
                    mac,
                )
                print(
                    f"Menu.py - Conexão registrada: ID={st.session_state['id']}, "
                    f"Voucher={st.session_state['voucher']}, IP={ip}, "
                    f"Hostname={hostname}, MAC={mac}"
                )
                st.success(f"Conexão detectada e registrada! IP: {ip}")
                registrada = True
                break

            print("Menu.py - IP ainda não disponível; aguardando 5 segundos...")
        except Exception as e:
            print(f"Menu.py - Erro ao consultar ou registrar conexão: {e}")
            st.error("Falha ao consultar ou registrar. Consulte o terminal para ver o erro.")

        if tentativa < 11:
            comp.wait(5)

    if not registrada:
        st.warning(
            "O voucher foi emitido, mas a controladora não informou o IP "
            "dentro de 60 segundos. Tente verificar o histórico novamente em instantes."
        )

    st.session_state.pop("voucher", None)
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
