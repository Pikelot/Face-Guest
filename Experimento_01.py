"""
Experimento 1 - Face-Guest: calibração do limiar e taxa de acerto (identificação 1:N)

Estrutura de pastas esperada dentro de --pasta:

    cadastro/        P01_01.jpg, P02_01.jpg, ...        (fotos de cadastro; 1 por pessoa)
    teste_cad/       P01_02.jpg ... P01_11.jpg, ...     (OUTRAS fotos das cadastradas)
    teste_nao_cad/   P11_01.jpg ... P11_10.jpg, ...     (pessoas que NÃO estão na base)

Regras:
  - O nome antes do último "_número" é a identidade real (P01_05.jpg -> P01).
  - A RODADA não vem mais do número do arquivo: é a ordem das fotos de cada pessoa
    (1a foto de cada pessoa = rodada 1, 2a = rodada 2, ...). Assim a numeração dos
    arquivos pode ter "buracos" (_02 a _11) sem desalinhar as rodadas.
  - Fotos idênticas (mesmo conteúdo) são ignoradas, inclusive entre cadastro e teste.

Uso:
    python experimento1.py --pasta "C:\\caminho\\da\\pasta"
    python experimento1.py --pasta "..." --limiares 0.4 0.45 0.5 --limiar-ref 0.5
    python experimento1.py --pasta "..." --excluir-sem-rosto

Saída (pasta --pasta/resultados/<data-hora>/):
    relatorio.txt, consultas.csv, limiares_rodadas.csv, limiares_agregado.csv,
    por_pessoa.csv, distancias.png, far_frr.png (gráficos exigem matplotlib).
"""

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import time
import uuid
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import chromadb
import numpy as np
import face_recognition

EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
LIMIARES_PADRAO = [0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]
SUFIXO_NUM = re.compile(r"^(?P<nome>.+?)_(?P<num>\d+)$")
LIMIAR_FOTO_REPETIDA = 0.05   # distância abaixo disso entre fotos "diferentes" é suspeita

DEC = ","        # separador decimal usado na tela e nos CSV (ver --decimal-ponto)
LINHAS = []      # tudo o que for impresso também vai para o relatorio.txt


# ------------------------------------------------------------------ saída/formatos

def p(texto=""):
    print(texto)
    LINHAS.append(str(texto))


def n(x, casas=1):
    """Formata número com o separador decimal escolhido; None vira '-'."""
    if x is None:
        return "-"
    return f"{x:.{casas}f}".replace(".", DEC)


def n_csv(x, casas=2):
    return "" if x is None else n(x, casas)


def imprimir_tabela(cabecalho, linhas):
    colunas = zip(cabecalho, *linhas)
    larguras = [max(len(str(c)) for c in col) for col in colunas]
    fmt = " | ".join(f"{{:>{w}}}" for w in larguras)
    p(fmt.format(*cabecalho))
    p("-+-".join("-" * w for w in larguras))
    for linha in linhas:
        p(fmt.format(*[str(c) for c in linha]))


def salvar_csv(caminho, cabecalho, linhas):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cabecalho)
        w.writerows(linhas)


# --------------------------------------------------------------------- arquivos

def nome_pessoa(arquivo: Path):
    m = SUFIXO_NUM.match(arquivo.stem)
    return m["nome"] if m else arquivo.stem


def chave_natural(arquivo: Path):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", arquivo.name)]


def hash_arquivo(arquivo: Path):
    return hashlib.sha1(arquivo.read_bytes()).hexdigest()


def coletar(pasta: Path, tipo: str, vistos: dict):
    """Lista as imagens da pasta, ignora duplicatas e atribui a rodada por ordem."""
    if not pasta.is_dir():
        raise SystemExit(f"ERRO: pasta não encontrada: {pasta}")

    arquivos = sorted(
        (a for a in pasta.iterdir() if a.is_file() and a.suffix.lower() in EXTENSOES),
        key=chave_natural,
    )
    por_pessoa = defaultdict(list)
    for a in arquivos:
        h = hash_arquivo(a)
        if h in vistos:
            p(f"AVISO: {pasta.name}/{a.name} é idêntica a {vistos[h]}; ignorada.")
            continue
        vistos[h] = f"{pasta.name}/{a.name}"
        por_pessoa[nome_pessoa(a)].append(a)

    itens = []
    for pessoa, lista in por_pessoa.items():
        for rodada, a in enumerate(lista, start=1):
            itens.append({"arquivo": a, "pessoa": pessoa, "rodada": rodada})
    itens.sort(key=lambda it: chave_natural(it["arquivo"]))

    if tipo != "cadastro":
        contagem = Counter(it["pessoa"] for it in itens)
        if len(set(contagem.values())) > 1:
            maximo = max(contagem.values())
            faltando = {k: v for k, v in sorted(contagem.items()) if v != maximo}
            p(f"AVISO: {pasta.name}/ tem número desigual de fotos por pessoa "
              f"(esperado {maximo}): {faltando}")
    return itens


# ------------------------------------------------------------ encoding + cache

class Cache:
    """Guarda encodings em disco para não recalcular tudo a cada execução."""

    def __init__(self, caminho: Path, ativo: bool):
        self.caminho = caminho
        self.ativo = ativo
        self.dados = {}
        if ativo and caminho.exists():
            try:
                self.dados = json.loads(caminho.read_text(encoding="utf-8"))
            except Exception:
                self.dados = {}

    @staticmethod
    def chave(arquivo, upsample, max_lado):
        st = arquivo.stat()
        return f"{arquivo.resolve()}|{st.st_size}|{st.st_mtime_ns}|{upsample}|{max_lado}"

    def obter(self, arquivo, upsample, max_lado):
        return self.dados.get(self.chave(arquivo, upsample, max_lado)) if self.ativo else None

    def guardar(self, arquivo, upsample, max_lado, item):
        if self.ativo:
            self.dados[self.chave(arquivo, upsample, max_lado)] = item

    def salvar(self):
        if self.ativo:
            self.caminho.write_text(json.dumps(self.dados), encoding="utf-8")


def carregar_imagem(arquivo: Path, max_lado: int):
    if not max_lado:
        return face_recognition.load_image_file(str(arquivo))
    from PIL import Image
    img = Image.open(arquivo).convert("RGB")
    if max(img.size) > max_lado:
        img.thumbnail((max_lado, max_lado))
    return np.array(img)


def extrair(arquivo: Path, upsample: int, max_lado: int):
    """Única função que usa o face_recognition. Retorna (encoding | None, n_rostos).
    Com upsample=1 e max_lado=0 o resultado é o mesmo de face_encodings(imagem)."""
    imagem = carregar_imagem(arquivo, max_lado)
    locais = face_recognition.face_locations(imagem, number_of_times_to_upsample=upsample)
    if not locais:
        return None, 0
    encodings = face_recognition.face_encodings(imagem, known_face_locations=locais)
    return encodings[0].tolist(), len(locais)   # primeiro rosto, como no sistema


def obter_encoding(arquivo, cache, upsample, max_lado):
    item = cache.obter(arquivo, upsample, max_lado)
    if item is None:
        inicio = time.perf_counter()
        enc, n_rostos = extrair(arquivo, upsample, max_lado)
        item = {"enc": enc, "n_rostos": n_rostos, "tempo_enc": time.perf_counter() - inicio}
        cache.guardar(arquivo, upsample, max_lado, item)
    return item


# ----------------------------------------------------------------- base e consultas

def montar_base(itens, cache, upsample, max_lado):
    client = chromadb.Client()   # em memória, descartada ao fim do programa
    colecao = client.create_collection(
        name=f"base_{uuid.uuid4().hex[:8]}",
        metadata={"hnsw:space": "l2"},
    )
    cadastradas = set()
    for it in itens:
        d = obter_encoding(it["arquivo"], cache, upsample, max_lado)
        if d["enc"] is None:
            p(f"AVISO: sem rosto no cadastro de {it['arquivo'].name}; ignorada.")
            continue
        if d["n_rostos"] > 1:
            p(f"AVISO: {it['arquivo'].name} tem {d['n_rostos']} rostos; usando o primeiro.")
        colecao.add(
            ids=[it["arquivo"].name],
            embeddings=[d["enc"]],
            metadatas=[{"pessoa": it["pessoa"]}],
        )
        cadastradas.add(it["pessoa"])
        p(f"Cadastrada: {it['pessoa']} ({it['arquivo'].name})")
    if not cadastradas:
        raise SystemExit("ERRO: nenhuma pessoa cadastrada com sucesso.")
    return colecao, cadastradas


def consultar(colecao, itens, tipo, cadastradas, cache, upsample, max_lado):
    registros = []
    total = len(itens)
    for i, it in enumerate(itens, start=1):
        a, pessoa = it["arquivo"], it["pessoa"]
        if tipo == "cadastrada" and pessoa not in cadastradas:
            p(f"AVISO: {a.name} está em teste_cad/ mas '{pessoa}' não está na base.")
        if tipo == "nao_cadastrada" and pessoa in cadastradas:
            p(f"AVISO: {a.name} está em teste_nao_cad/ mas '{pessoa}' está cadastrada!")

        d = obter_encoding(a, cache, upsample, max_lado)
        achado, dist, t_busca = None, None, 0.0
        if d["enc"] is None:
            p(f"SEM ROSTO: {tipo}/{a.name}")
        else:
            if d["n_rostos"] > 1:
                p(f"AVISO: {a.name} tem {d['n_rostos']} rostos; usando o primeiro.")
            inicio = time.perf_counter()
            r = colecao.query(query_embeddings=[d["enc"]], n_results=1,
                              include=["distances", "metadatas"])
            t_busca = time.perf_counter() - inicio
            achado = r["metadatas"][0][0]["pessoa"]
            # Chroma (l2) devolve a distância ao QUADRADO -> raiz = euclidiana normal
            dist = math.sqrt(max(r["distances"][0][0], 0.0))

        registros.append({
            "arquivo": a.name, "tipo": tipo, "pessoa": pessoa, "rodada": it["rodada"],
            "achado": achado, "dist": dist, "n_rostos": d["n_rostos"],
            "tempo_enc": d["tempo_enc"], "tempo_busca": t_busca,
        })
        if i % 20 == 0 or i == total:
            print(f"  [{tipo}] {i}/{total}")
    return registros


# --------------------------------------------------------------------- métricas

def pct(parte, total):
    return None if total == 0 else 100.0 * parte / total


def wilson(k, total, z=1.96):
    """Intervalo de confiança de 95% (Wilson) para uma proporção, em %."""
    if total == 0:
        return None, None
    prop = k / total
    den = 1 + z * z / total
    centro = (prop + z * z / (2 * total)) / den
    margem = z * math.sqrt(prop * (1 - prop) / total + z * z / (4 * total * total)) / den
    return 100 * (centro - margem), 100 * (centro + margem)


def contar(regs, limiar, excluir_sem_rosto=False):
    if excluir_sem_rosto:
        regs = [r for r in regs if r["dist"] is not None]
    cad = [r for r in regs if r["tipo"] == "cadastrada"]
    nao = [r for r in regs if r["tipo"] == "nao_cadastrada"]

    def aceita(r):
        return r["dist"] is not None and r["dist"] <= limiar   # sem rosto nunca é aceita

    acertos = sum(1 for r in cad if aceita(r) and r["achado"] == r["pessoa"])
    id_errado = sum(1 for r in cad if aceita(r) and r["achado"] != r["pessoa"])
    fa = sum(1 for r in nao if aceita(r))
    return {
        "n_cad": len(cad), "n_nao": len(nao),
        "acertos": acertos, "id_errado": id_errado,
        "fr": len(cad) - acertos - id_errado,
        "fa": fa, "rc": len(nao) - fa,
    }


def taxas(c):
    return {
        "TAR": pct(c["acertos"], c["n_cad"]),
        "FRR": pct(c["fr"], c["n_cad"]),
        "ID_ERRADO": pct(c["id_errado"], c["n_cad"]),
        "FAR": pct(c["fa"], c["n_nao"]),
        "ACURACIA": pct(c["acertos"] + c["rc"], c["n_cad"] + c["n_nao"]),
    }


def media_dp(valores):
    valores = [v for v in valores if v is not None]
    if not valores:
        return None, None
    return statistics.mean(valores), (statistics.stdev(valores) if len(valores) > 1 else 0.0)


def curva(registros, excluir, passo=0.005):
    """FAR e (100-TAR) para limiares de 0 a 1; usada no EER e no gráfico."""
    pontos = []
    for t in np.arange(0.0, 1.0 + passo / 2, passo):
        tx = taxas(contar(registros, float(t), excluir))
        if tx["FAR"] is None or tx["TAR"] is None:
            return []
        pontos.append((float(t), tx["FAR"], 100.0 - tx["TAR"]))
    return pontos


def calcular_eer(pontos):
    if not pontos:
        return None
    t, far, frr = min(pontos, key=lambda x: abs(x[1] - x[2]))
    return {"limiar": t, "far": far, "frr": frr, "eer": (far + frr) / 2}


# ------------------------------------------------------------------- relatórios

def secao_resumo(registros, cadastradas):
    sem_rosto = [r for r in registros if r["dist"] is None]
    multi = [r for r in registros if r["n_rostos"] > 1]
    cad = [r for r in registros if r["tipo"] == "cadastrada"]
    nao = [r for r in registros if r["tipo"] == "nao_cadastrada"]
    rodadas = sorted({r["rodada"] for r in registros})

    p("\n=== Resumo ===")
    p(f"Pessoas na base: {len(cadastradas)}")
    p(f"Consultas: {len(registros)} (cadastradas: {len(cad)}, não cadastradas: {len(nao)}) | "
      f"Rodadas: {len(rodadas)}")
    p(f"Sem rosto detectado: {len(sem_rosto)} "
      f"(cadastradas: {sum(r['tipo'] == 'cadastrada' for r in sem_rosto)}, "
      f"não cadastradas: {sum(r['tipo'] == 'nao_cadastrada' for r in sem_rosto)})")
    if multi:
        p(f"Fotos com mais de um rosto: {len(multi)} -> " + ", ".join(r["arquivo"] for r in multi))
    t_enc = [r["tempo_enc"] for r in registros if r["dist"] is not None]
    t_busca = [r["tempo_busca"] for r in registros if r["dist"] is not None]
    if t_enc:
        p(f"Tempo médio: encoding {n(statistics.mean(t_enc), 2)} s + busca no Chroma "
          f"{n(statistics.mean(t_busca) * 1000, 1)} ms por foto")

    suspeitas = [r for r in cad if r["dist"] is not None and r["achado"] == r["pessoa"]
                 and r["dist"] < LIMIAR_FOTO_REPETIDA]
    if suspeitas:
        p(f"\nATENÇÃO: {len(suspeitas)} foto(s) de teste quase idêntica(s) ao cadastro "
          f"(distância < {n(LIMIAR_FOTO_REPETIDA, 2)}); podem ser a mesma foto recortada:")
        for r in suspeitas:
            p(f"   {r['arquivo']}  dist={n(r['dist'], 4)}")


def secao_rodadas(registros, limiares, excluir):
    rodadas = sorted({r["rodada"] for r in registros})
    linhas, linhas_csv = [], []
    for lim in limiares:
        acum = defaultdict(list)
        for rd in rodadas:
            regs = [r for r in registros if r["rodada"] == rd]
            for k, v in taxas(contar(regs, lim, excluir)).items():
                acum[k].append(v)
        agg = {k: media_dp(v) for k, v in acum.items()}

        def cel(k):
            m, dp = agg[k]
            return "-" if m is None else f"{n(m)} ± {n(dp)}"

        linhas.append([n(lim, 2), cel("TAR"), cel("FRR"), cel("ID_ERRADO"), cel("FAR"), cel("ACURACIA")])
        linha_csv = [n(lim, 2)]
        for k in ["TAR", "FRR", "ID_ERRADO", "FAR", "ACURACIA"]:
            linha_csv += [n_csv(agg[k][0]), n_csv(agg[k][1])]
        linhas_csv.append(linha_csv)

    p(f"\n=== Média ± desvio padrão entre as {len(rodadas)} rodadas (%) ===")
    imprimir_tabela(["Limiar", "TAR", "FRR", "ID errado", "FAR", "Acurácia"], linhas)
    cab_csv = ["limiar"]
    for k in ["TAR", "FRR", "ID_ERRADO", "FAR", "ACURACIA"]:
        cab_csv += [f"{k}_media", f"{k}_dp"]
    return cab_csv, linhas_csv


def secao_agregado(registros, limiares, excluir):
    linhas, linhas_csv = [], []
    for lim in limiares:
        c = contar(registros, lim, excluir)
        tx = taxas(c)
        tar_i, tar_s = wilson(c["acertos"], c["n_cad"])
        far_i, far_s = wilson(c["fa"], c["n_nao"])
        linhas.append([
            n(lim, 2),
            f"{n(tx['TAR'])} ({c['acertos']}/{c['n_cad']}) [{n(tar_i)}-{n(tar_s)}]",
            f"{c['fr']}",
            f"{c['id_errado']}",
            f"{n(tx['FAR'])} ({c['fa']}/{c['n_nao']}) [{n(far_i)}-{n(far_s)}]",
        ])
        linhas_csv.append([
            n(lim, 2), c["acertos"], c["n_cad"], n_csv(tx["TAR"]), n_csv(tar_i), n_csv(tar_s),
            c["fr"], c["id_errado"], c["fa"], c["n_nao"], n_csv(tx["FAR"]), n_csv(far_i),
            n_csv(far_s), n_csv(tx["ACURACIA"]),
        ])
    p("\n=== Agregado de todas as consultas (TAR e FAR com IC 95% de Wilson) ===")
    imprimir_tabela(["Limiar", "TAR (acertos/cadastradas) [IC95%]", "Falsas rej.", "ID errado",
                     "FAR (aceitas/não cad.) [IC95%]"], linhas)
    cab_csv = ["limiar", "acertos", "n_cad", "TAR", "TAR_ic_inf", "TAR_ic_sup", "falsas_rejeicoes",
               "id_errado", "falsas_aceitacoes", "n_nao_cad", "FAR", "FAR_ic_inf", "FAR_ic_sup",
               "acuracia"]
    return cab_csv, linhas_csv


def secao_pontos_decisao(registros, excluir, limiar_ref):
    p("\n=== Pontos de decisão ===")
    pontos = curva(registros, excluir)
    eer = calcular_eer(pontos)
    if eer:
        p(f"EER aproximado: {n(eer['eer'])}% no limiar {n(eer['limiar'], 3)} "
          f"(FAR {n(eer['far'])}% / 100-TAR {n(eer['frr'])}%)")

    imp = [r["dist"] for r in registros if r["tipo"] == "nao_cadastrada" and r["dist"] is not None]
    if imp:
        menor = min(imp)
        c = contar(registros, menor - 1e-9, excluir)
        p(f"FAR = 0% para limiares abaixo de {n(menor, 4)} (menor distância de uma não cadastrada); "
          f"TAR nesse ponto: {n(taxas(c)['TAR'])}%")
    c = contar(registros, limiar_ref, excluir)
    tx = taxas(c)
    p(f"No limiar de referência {n(limiar_ref, 2)}: TAR {n(tx['TAR'])}%, FAR {n(tx['FAR'])}%")
    return pontos, eer


def secao_erros(registros, limiar_ref):
    p(f"\n=== 10 quase-erros: não cadastradas mais próximas da base ===")
    imp = sorted((r for r in registros if r["tipo"] == "nao_cadastrada" and r["dist"] is not None),
                 key=lambda r: r["dist"])[:10]
    imprimir_tabela(["Arquivo", "Parecida com", "Distância", f"Aceita @{n(limiar_ref, 2)}"],
                    [[r["arquivo"], r["achado"], n(r["dist"], 4),
                      "SIM" if r["dist"] <= limiar_ref else "não"] for r in imp])

    p(f"\n=== 10 piores consultas de cadastradas (ID errado primeiro, depois maior distância) ===")
    gen = sorted((r for r in registros if r["tipo"] == "cadastrada" and r["dist"] is not None),
                 key=lambda r: (r["achado"] == r["pessoa"], -r["dist"]))[:10]
    imprimir_tabela(["Arquivo", "Real", "Achado", "Distância"],
                    [[r["arquivo"], r["pessoa"], r["achado"], n(r["dist"], 4)] for r in gen])


def secao_por_pessoa(registros, limiar_ref):
    p(f"\n=== Por pessoa (limiar de referência {n(limiar_ref, 2)}) ===")
    p("Cadastradas: 'Aceitas' = acertos | Não cadastradas: 'Aceitas' = falsas aceitações")
    grupos = defaultdict(list)
    for r in registros:
        grupos[(r["tipo"], r["pessoa"])].append(r)

    linhas, linhas_csv = [], []
    for (tipo, pessoa), regs in sorted(grupos.items(), key=lambda kv: (kv[0][0], chave_natural(Path(kv[0][1])))):
        dists = [r["dist"] for r in regs if r["dist"] is not None]
        sem_rosto = len(regs) - len(dists)
        if tipo == "cadastrada":
            aceitas = sum(1 for r in regs if r["dist"] is not None and r["dist"] <= limiar_ref
                          and r["achado"] == pessoa)
            parecida = ""
        else:
            aceitas = sum(1 for r in regs if r["dist"] is not None and r["dist"] <= limiar_ref)
            achados = Counter(r["achado"] for r in regs if r["achado"])
            parecida = achados.most_common(1)[0][0] if achados else ""
        mediana = statistics.median(dists) if dists else None
        minimo = min(dists) if dists else None
        rotulo = "cad" if tipo == "cadastrada" else "não cad"
        linhas.append([pessoa, rotulo, len(regs), sem_rosto, n(mediana, 3), n(minimo, 3),
                       f"{aceitas}/{len(regs)}", parecida])
        linhas_csv.append([pessoa, tipo, len(regs), sem_rosto, n_csv(mediana, 4), n_csv(minimo, 4),
                           aceitas, parecida])
    imprimir_tabela(["Pessoa", "Tipo", "Fotos", "Sem rosto", "Dist. mediana", "Dist. mín.",
                     "Aceitas", "Mais próxima de"], linhas)
    cab_csv = ["pessoa", "tipo", "fotos", "sem_rosto", "dist_mediana", "dist_minima",
               "aceitas_no_limiar_ref", "mais_proxima_de"]
    return cab_csv, linhas_csv


def gerar_graficos(registros, pontos, eer, limiar_ref, saida: Path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        p("\n(matplotlib não instalado: gráficos não gerados. Use: pip install matplotlib)")
        return

    cad = [r["dist"] for r in registros if r["tipo"] == "cadastrada" and r["dist"] is not None]
    nao = [r["dist"] for r in registros if r["tipo"] == "nao_cadastrada" and r["dist"] is not None]
    bins = np.arange(0, 1.0001, 0.025)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(cad, bins=bins, alpha=0.65, label="Cadastradas (vizinho mais próximo)")
    ax.hist(nao, bins=bins, alpha=0.65, label="Não cadastradas (vizinho mais próximo)")
    ax.axvline(limiar_ref, linestyle="--", color="k", label=f"Limiar {n(limiar_ref, 2)}")
    ax.set_xlabel("Distância euclidiana")
    ax.set_ylabel("Número de consultas")
    ax.legend()
    fig.tight_layout()
    fig.savefig(saida / "distancias.png", dpi=200)
    plt.close(fig)

    if pontos:
        ts = [x[0] for x in pontos]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(ts, [x[1] for x in pontos], label="FAR (falsa aceitação)")
        ax.plot(ts, [x[2] for x in pontos], label="100 - TAR (não reconhecidas)")
        if eer:
            ax.plot(eer["limiar"], eer["eer"], "ko", label=f"EER ~ {n(eer['eer'])}%")
        ax.set_xlabel("Limiar de distância")
        ax.set_ylabel("Taxa (%)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(saida / "far_frr.png", dpi=200)
        plt.close(fig)
    p("\nGráficos salvos: distancias.png e far_frr.png")


# ------------------------------------------------------------------------- main

def main():
    global DEC
    ap = argparse.ArgumentParser(description="Experimento 1 - Face-Guest")
    ap.add_argument("--pasta", required=True, help="Pasta com cadastro/, teste_cad/ e teste_nao_cad/")
    ap.add_argument("--limiares", type=lambda s: float(s.replace(",", ".")), nargs="+",
                    default=LIMIARES_PADRAO, help="Limiares a avaliar (ex.: 0.4 0.45 0.5)")
    ap.add_argument("--limiar-ref", type=lambda s: float(s.replace(",", ".")), default=0.5,
                    help="Limiar usado nas tabelas por pessoa e na lista de quase-erros (padrão 0.5)")
    ap.add_argument("--excluir-sem-rosto", action="store_true",
                    help="Tira da conta as fotos sem rosto (por padrão contam como rejeição)")
    ap.add_argument("--upsample", type=int, default=1,
                    help="number_of_times_to_upsample do detector (padrão 1, igual ao sistema)")
    ap.add_argument("--max-lado", type=int, default=0,
                    help="Reduz imagens maiores que N pixels antes de processar (0 = não reduz)")
    ap.add_argument("--sem-cache", action="store_true", help="Recalcula todos os encodings")
    ap.add_argument("--decimal-ponto", action="store_true", help="Usa ponto em vez de vírgula nos números")
    args = ap.parse_args()

    DEC = "." if args.decimal_ponto else ","
    base = Path(args.pasta)
    saida = base / "resultados" / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    saida.mkdir(parents=True, exist_ok=True)
    cache = Cache(base / ".cache_encodings.json", ativo=not args.sem_cache)

    p("=== Experimento 1 - Face-Guest ===")
    p(f"Pasta: {base}")
    p(f"Limiares: {', '.join(n(x, 2) for x in args.limiares)} | referência: {n(args.limiar_ref, 2)} | "
      f"sem rosto: {'excluído' if args.excluir_sem_rosto else 'conta como rejeição'} | "
      f"upsample={args.upsample} | max-lado={args.max_lado or 'sem limite'}")

    p("\n=== Lendo as pastas ===")
    vistos = {}
    itens_cad = coletar(base / "cadastro", "cadastro", vistos)
    itens_teste_cad = coletar(base / "teste_cad", "teste_cad", vistos)
    itens_teste_nao = coletar(base / "teste_nao_cad", "teste_nao_cad", vistos)
    p(f"Cadastro: {len(itens_cad)} foto(s) | teste_cad: {len(itens_teste_cad)} | "
      f"teste_nao_cad: {len(itens_teste_nao)}")

    p("\n=== Montando a base (cadastro) ===")
    colecao, cadastradas = montar_base(itens_cad, cache, args.upsample, args.max_lado)
    cache.salvar()

    p("\n=== Consultando fotos de teste ===")
    registros = []
    registros += consultar(colecao, itens_teste_cad, "cadastrada", cadastradas,
                           cache, args.upsample, args.max_lado)
    registros += consultar(colecao, itens_teste_nao, "nao_cadastrada", cadastradas,
                           cache, args.upsample, args.max_lado)
    cache.salvar()
    if not registros:
        raise SystemExit("ERRO: nenhuma consulta realizada.")

    secao_resumo(registros, cadastradas)
    cab_r, lin_r = secao_rodadas(registros, args.limiares, args.excluir_sem_rosto)
    cab_a, lin_a = secao_agregado(registros, args.limiares, args.excluir_sem_rosto)
    pontos, eer = secao_pontos_decisao(registros, args.excluir_sem_rosto, args.limiar_ref)
    secao_erros(registros, args.limiar_ref)
    cab_p, lin_p = secao_por_pessoa(registros, args.limiar_ref)
    gerar_graficos(registros, pontos, eer, args.limiar_ref, saida)

    cab_c = ["arquivo", "tipo", "pessoa", "rodada", "achado", "dist", "n_rostos", "tempo_enc_s", "tempo_busca_s"]
    lin_c = [[r["arquivo"], r["tipo"], r["pessoa"], r["rodada"], r["achado"] or "",
              n_csv(r["dist"], 4), r["n_rostos"], n_csv(r["tempo_enc"], 3), n_csv(r["tempo_busca"], 4)]
             for r in registros]
    salvar_csv(saida / "consultas.csv", cab_c, lin_c)
    salvar_csv(saida / "limiares_rodadas.csv", cab_r, lin_r)
    salvar_csv(saida / "limiares_agregado.csv", cab_a, lin_a)
    salvar_csv(saida / "por_pessoa.csv", cab_p, lin_p)

    p(f"\nArquivos salvos em: {saida}")
    (saida / "relatorio.txt").write_text("\n".join(LINHAS), encoding="utf-8")


if __name__ == "__main__":
    main()