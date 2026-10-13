# Face-Guest

Middleware para gerenciar a rede de visitantes (Wi-Fi guest) usando reconhecimento facial.

## Funcionalidades

- Cadastro de visitantes com captura de foto
- Reconhecimento facial para liberar o acesso à rede
- Controle do tempo de acesso (data e hora de início e expiração)
- Interface web feita com Streamlit

## Requisitos

- Python 3.10
- Windows: [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) com a carga de trabalho **"Desenvolvimento para desktop com C++"** (necessário para compilar o `dlib`)
- CMake (`pip install cmake`), caso o `dlib` reclame da ausência dele

## Instalação

```bash
# 1. Clone o repositório
git clone <URL_DO_REPOSITORIO>
cd Face-Guest

# 2. Crie e ative um ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 3. Instale as dependências
pip install -r requirements.txt
```

Conteúdo sugerido para o `requirements.txt`:

```text
streamlit
setuptools
dlib
face_recognition
```

> Instale o Visual Studio Build Tools **antes** do passo 3, senão o `dlib` falha ao compilar.

## Configuração

O arquivo `config.json` fica apenas no servidor da empresa e **não é versionado** (está no `.gitignore`).
Depois de clonar, crie o seu a partir do modelo:

```bash
cp config.example.json config.json      # Linux/macOS
copy config.example.json config.json    # Windows (cmd)
```

Em seguida, edite o `config.json` com os valores do seu ambiente.

## Como executar

```bash
streamlit run app.py
```

(Troque `app.py` pelo nome do arquivo principal do projeto.)

## Bibliotecas utilizadas

| Biblioteca | Uso |
|---|---|
| `face_recognition` / `dlib` | Detecção e comparação de rostos |
| `streamlit` | Interface web |
| `os`, `datetime`, `time` | Biblioteca padrão do Python (arquivos, datas e controle de tempo) |

## Privacidade e segurança

Imagens de rosto e dados biométricos são dados pessoais sensíveis (LGPD). Guarde-os com acesso restrito, defina um prazo de retenção e apague os dados dos visitantes quando o acesso expirar.