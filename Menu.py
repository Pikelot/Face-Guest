import streamlit as st
import base64
from pathlib import Path
import Complementos as comp
import Controladora as ctrl
import Facial as face
import DB_SQL as sql

st.set_page_config(page_title="Face-Guest", page_icon=":smiley:", layout="centered")

# ---------- ESTILO VISUAL (definido em estilo.css) ----------
css = Path(__file__).with_name("estilo.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Imagem opcional, exibida em todas as telas quando o arquivo estiver presente.
caminho_imagem_canto = Path(__file__).parent / "assets" / "rodape.png"
if caminho_imagem_canto.exists():
    imagem_base64 = base64.b64encode(caminho_imagem_canto.read_bytes()).decode("ascii")
    st.markdown(
        f'<img class="imagem-canto" src="data:image/png;base64,{imagem_base64}" alt="">',
        unsafe_allow_html=True,
    )

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

#Session 0 - Tela de inicio
if st.session_state.tela == "inicio":
    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    st.markdown(
        """
        <section class="welcome-card">
            <div class="welcome-eyebrow">FACE GUEST · ACESSO DE VISITANTES</div>
            <div class="welcome-title">Bem-vindo!</div>
            <p class="welcome-description">
                Faça sua autenticação facial para receber um voucher individual
                de acesso à rede Wi-Fi para visitantes.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-label'>Como funciona</div>", unsafe_allow_html=True)
    etapa1, etapa2, etapa3 = st.columns(3)
    etapas = [
        (etapa1, "01", "Consentimento", "Leia o termo e confirme que concorda."),
        (etapa2, "02", "Identificação", "Informe seu CPF para continuar."),
        (etapa3, "03", "Autenticação", "Capture seu rosto e receba o voucher."),
    ]
    for coluna, numero, titulo, descricao in etapas:
        with coluna:
            st.markdown(
                f"""
                <div class="step-card">
                    <span class="step-number">{numero}</span>
                    <div class="step-title">{titulo}</div>
                    <div class="step-description">{descricao}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    _, botao_coluna, _ = st.columns([1, 2, 1])
    with botao_coluna:
        if st.button("Iniciar autenticação", use_container_width=True, type="primary"):
            st.session_state.tela = "termo_de_consentimento"
            st.rerun()

#Session 0.25 - Termo de Consentimento
if st.session_state.tela == "termo_de_consentimento":
    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    #Aqui exibimos o termo de consentimento para o usuário, e ele precisa aceitar para continuar
    st.markdown(
        """
        <section class="consent-card">
            <div class="welcome-eyebrow">ANTES DE CONTINUAR</div>
            <div class="consent-title">Termo de consentimento</div>
            <p class="consent-copy">
                Ao utilizar este sistema, você concorda com a coleta e uso de suas
                informações faciais para fins de autenticação e registro de conexões.
                Seus dados serão armazenados de forma segura e não serão compartilhados
                com terceiros sem o seu consentimento.
            </p>
            <div class="consent-purpose">
                <strong>Finalidade</strong>
                <span>Autenticação facial e registro de conexões.</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    #Checkbox para o usuário aceitar o termo de consentimento
    aceitou_termo = st.checkbox(
        "Li e concordo com o termo de consentimento.",
        key="aceitou_termo_consentimento",
    )

    #Divisão de botões para voltar ou aceitar e continuar, dependendo do estado do checkbox, utiliza o st.columns para criar duas colunas, uma para cada botão.
    voltar_coluna, aceitar_coluna = st.columns(2)
    with voltar_coluna:
        if st.button("Voltar", use_container_width=True):
            st.session_state.tela = "inicio"
            st.rerun()
    with aceitar_coluna:
        if st.button(
            "Aceitar e continuar",
            use_container_width=True,
            type="primary",
            disabled=not aceitou_termo,
        ):
            st.session_state.tela = "registrar_cpf"
            st.rerun()

#Session 0.5 - Registro do CPF do usuário
if st.session_state.tela == "registrar_cpf":
    print(f"Menu.py - Tela atual: {st.session_state.tela}")

    st.markdown(
        """
        <section class="cpf-card">
            <div class="welcome-eyebrow">ETAPA 2 DE 3 · IDENTIFICAÇÃO</div>
            <div class="cpf-progress"><span></span></div>
            <div class="cpf-title">Informe seu CPF</div>
            <p class="cpf-description">
                Usaremos essa informação para identificar seu registro e associá-lo
                à conexão de visitante.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    _, formulario_coluna, _ = st.columns([1, 2, 1])
    with formulario_coluna:
        cpf = st.text_input(
            "CPF",
            placeholder="Somente os 11 números",
            max_chars=11,
            key="cpf_input",
            help="Digite o CPF sem pontos ou traço.",
        )
        st.caption("Não inclua pontos, espaços ou traço.")

    voltar_coluna, continuar_coluna = st.columns(2)
    with voltar_coluna:
        if st.button("Voltar", use_container_width=True):
            st.session_state.tela = "termo_de_consentimento"
            st.rerun()

    with continuar_coluna:
        continuar = st.button(
            "Continuar",
            use_container_width=True,
            type="primary",
        )

    if continuar:
        if len(cpf) == 11 and cpf.isdigit():
            st.session_state["cpf"] = cpf
            st.success("CPF registrado com sucesso!")
            comp.wait(2)
            st.session_state.tela = "capturar_face"
            st.rerun()
        else:
            st.error("CPF inválido. Certifique-se de digitar 11 números.")

#Session 1 - Captura a face e envia para a geração de enconding
if st.session_state.tela == "capturar_face":

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
        st.session_state.tela = "capturar_face"

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
                    st.session_state["cpf"],
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
    st.session_state.tela = "capturar_face"
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
