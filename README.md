# Face Guest

Aplicação web feita com Streamlit para cadastrar visitantes, emitir vouchers de acesso Wi-Fi pela controladora UniFi e consultar o histórico de conexões associado ao cadastro facial.

## Como funciona

1. O visitante lê e aceita o termo de consentimento.
2. Informa o CPF e captura uma foto pela câmera do dispositivo.
3. O sistema compara o rosto com os registros existentes ou cria um novo cadastro.
4. A tela orienta o visitante a se conectar à rede `desenvolvern.visitantes` e emitir um voucher.
5. O visitante informa o voucher no portal UniFi. A aplicação aguarda a conexão e, quando encontra os dados do dispositivo, registra IP, hostname, MAC, voucher, CPF e horário.
6. Pela opção de verificação facial, é possível consultar o histórico de conexões relacionado ao cadastro encontrado.

Os vouchers são solicitados à controladora com validade de 60 minutos e limite de um uso, conforme a implementação atual em `Controladora.py`.

## Requisitos

- Python instalado no computador que executará a aplicação.
- Acesso de rede desse computador à controladora UniFi.
- Uma conta da controladora com permissão para criar vouchers e consultar clientes convidados.
- Câmera e permissão do navegador para capturar a imagem. Em acesso remoto, a câmera normalmente exige que o site seja servido por HTTPS.
- Dependências Python: Streamlit, face_recognition, dlib, ChromaDB, Flask e pyunifi.

O `face_recognition` depende do `dlib`; a instalação pode exigir ferramentas de compilação C++ e CMake, dependendo da versão do Python e do sistema operacional. Use uma versão de Python compatível com as versões dessas bibliotecas disponíveis para seu sistema.

## Instalação

Abra um terminal na pasta do projeto e crie um ambiente virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install --upgrade pip
python -m pip install streamlit face-recognition chromadb Flask pyunifi
```

Se a instalação do `dlib` falhar no Windows, instale as ferramentas de compilação C++ da Microsoft e o CMake, ou use uma versão de Python para a qual haja uma distribuição compatível do `dlib`.

## Configurar a controladora

O arquivo `Controladora.py` lê `config.json` na raiz do projeto. Existe um modelo chamado `config_base.json`; copie-o e preencha os valores do seu ambiente:

```powershell
Copy-Item config_base.json config.json
```

Edite `config.json` com os dados de acesso à controladora. O arquivo deve conter estas chaves:

```json
{
  "servidor": "IP ou nome DNS da controladora, sem protocolo e sem porta",
  "porta": 11443,
  "usuario": "USUARIO_DA_CONTROLADORA",
  "senha": "SENHA_DA_CONTROLADORA",
  "version": "VERSAO_DA_API_CONFIGURADA_NO_PYUNIFI",
  "site_id": "ID_DO_SITE",
  "ssl_verify": false
}
```

Use os valores correspondentes à sua instalação UniFi e à versão do pacote `pyunifi`. A porta precisa ser a mesma usada para acessar o serviço de gerenciamento/API da controladora. Não inclua `https://` nem a porta no campo `servidor`, pois a porta tem seu próprio campo. Se a controladora usar certificado confiável, configure `ssl_verify` conforme necessário para validá-lo.

`config.json` contém credenciais e não deve ser enviado ao Git. O repositório inclui essa regra no `.gitignore`; confira também se o arquivo não foi adicionado ao Git anteriormente.

## Executar

Com o ambiente virtual ativo e `config.json` preenchido, execute na raiz do projeto:

```powershell
python -m streamlit run Menu.py
```

O Streamlit mostrará o endereço local para abrir no navegador. Para disponibilizar a aplicação a outros dispositivos, configure a rede e o HTTPS adequadamente, além das permissões de câmera.

## Arquivos e dados locais

| Arquivo ou pasta | Finalidade |
|---|---|
| `Menu.py` | Interface e fluxo principal do aplicativo. |
| `Controladora.py` | Conexão com a UniFi, emissão de voucher e consulta de dispositivos. |
| `DB_SQL.py` | Cadastro e histórico de conexões em SQLite. |
| `DB_Chroma.py` | Armazenamento e busca dos vetores faciais no ChromaDB. |
| `Facial.py` | Captura/processamento e comparação facial. |
| `Complementos.py` | Funções auxiliares. |
| `estilo.css` | Estilos da interface. |
| `.streamlit/config.toml` | Tema do Streamlit. |
| `Assets/rodape.png` | Imagem opcional exibida no rodapé da interface. |
| `face_guest.db` | Banco SQLite criado/atualizado pela aplicação. |
| `chroma_db/` | Dados persistentes do ChromaDB, incluindo os vetores faciais. |
| `Faciais/` | Arquivos de imagem facial usados pelo fluxo da aplicação. |

Os bancos, imagens e vetores faciais são dados locais da aplicação. Faça backups e controle o acesso a eles de acordo com as regras da organização. Para apagar os dados, encerre o Streamlit antes de remover os arquivos correspondentes.

## Privacidade

CPF e dados biométricos faciais são dados pessoais, e biometria é dado pessoal sensível segundo a LGPD. Informe claramente a finalidade do tratamento, limite o acesso, defina prazo de retenção e procedimento de exclusão, e proteja os arquivos e credenciais. Este README não substitui a avaliação jurídica ou as políticas de privacidade da organização.
