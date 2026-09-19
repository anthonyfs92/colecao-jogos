import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import requests
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(page_title="Catálogo Bruna BoardGames", page_icon="🌰", layout="wide")

N8N_BASE_URL = st.secrets.get("N8N_BASE_URL", "https://136-114-39-177.sslip.io")
LISTAR_URL = f"{N8N_BASE_URL}/webhook/jogos-listar"
ADICIONAR_URL = f"{N8N_BASE_URL}/webhook/jogos-adicionar"
EXCLUIR_URL = f"{N8N_BASE_URL}/webhook/jogos-excluir"

ASSETS_DIR = Path(__file__).parent / "assets"
HEADER_IMG = ASSETS_DIR / "header.png"
BACKGROUND_IMG = ASSETS_DIR / "background.jpg"


@st.cache_data(show_spinner=False)
def imagem_para_base64(caminho):
    return base64.b64encode(Path(caminho).read_bytes()).decode("utf-8")


BACKGROUND_B64 = imagem_para_base64(BACKGROUND_IMG)

PAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Alegreya:wght@500;700&display=swap');

:root {
    --panel-bg: #232b27;
    --panel-bg-2: #2a332e;
    --wood-shadow:
        0 0 0 2px #3a2513,
        0 0 0 4px #a9773e,
        0 0 0 5px #3a2513,
        inset 0 1.5px 2px rgba(255,214,150,0.25),
        inset 0 -2px 4px rgba(0,0,0,0.5),
        0 6px 14px rgba(0,0,0,0.5);
}

html, body, [class*="css"] {
    font-family: 'Alegreya', serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(rgba(8,13,11,0.55), rgba(8,13,11,0.78)),
        url('data:image/jpeg;base64,__BACKGROUND_B64__');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
div[data-testid="stImage"] { margin-bottom: -18px; }
h1, h2, h3 {
    font-family: 'Berkshire Swash', cursive !important;
    font-weight: 400;
    letter-spacing: 0.5px;
    background: linear-gradient(90deg, #f2c14e, #4fd1a5 65%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
[data-testid="stCaptionContainer"] { color: #b9c9c0 !important; }
div[data-testid="stMetric"] {
    background: var(--panel-bg);
    border: none;
    border-radius: 14px;
    padding: 14px 16px;
    position: relative;
    box-shadow: var(--wood-shadow);
}
div[data-testid="stMetric"]::before, div[data-testid="stMetric"]::after {
    content: '🌿';
    position: absolute;
    font-size: 1.1rem;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.6));
    pointer-events: none;
    z-index: 2;
}
div[data-testid="stMetric"]::before { top: -11px; left: -9px; transform: rotate(-30deg); }
div[data-testid="stMetric"]::after { content: '🍂'; bottom: -11px; right: -9px; transform: rotate(150deg); }
div[data-testid="stMetricLabel"] { color: #dce8e1 !important; }
div[data-testid="stMetricValue"] { font-family: 'Berkshire Swash', cursive !important; }
h3 {
    border-bottom: 1px solid rgba(242,193,78,0.25);
    padding-bottom: 6px;
}
.tile-card {
    position: relative;
    padding: 9px;
    border-radius: 16px;
    background: var(--panel-bg);
    border: none;
    box-shadow: var(--wood-shadow);
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
    margin-bottom: 4px;
    isolation: isolate;
}
.tile-card:hover {
    transform: translateY(-3px) scale(1.015);
    box-shadow: var(--wood-shadow), 0 10px 24px rgba(0,0,0,0.55);
    filter: brightness(1.12);
}
.tile-card::before, .tile-card::after {
    content: '🌿';
    position: absolute;
    font-size: 1.15rem;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.6));
    pointer-events: none;
    z-index: 2;
}
.tile-card::before { top: -9px; left: -7px; transform: rotate(-25deg); }
.tile-card::after { content: '🍃'; bottom: -8px; right: -7px; transform: rotate(155deg); }
.tile-img img, .tile-img-placeholder {
    border-radius: 10px;
    width: 100%;
    object-fit: cover;
    aspect-ratio: 1 / 1;
    display: block;
}
.tile-img img {
    background: var(--panel-bg);
}
.tile-img-placeholder {
    background: var(--panel-bg-2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: #cfe0d9;
}
div[data-testid="column"] div[data-testid="stButton"] button {
    margin-top: -6px;
}
.detail-meta { color: #cfe0d9; font-size: 0.95rem; margin-top: 2px; }
.detail-desc { color: #cfe0d9; margin-top: 14px; line-height: 1.5; }
button, input, textarea, select, .stTextInput, .stButton, .stRadio label, .stCheckbox label {
    font-family: 'Alegreya', serif !important;
}
button {
    border-radius: 10px !important;
    background: var(--panel-bg) !important;
    border: none !important;
    box-shadow: var(--wood-shadow) !important;
}
div[data-testid="stTextInput"] div[data-baseweb="input"],
div[data-testid="stTextInputRootElement"],
.stTextInput > div > div,
div[data-testid="stTextInput"] > div {
    background: var(--panel-bg) !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: var(--wood-shadow) !important;
}
div[data-testid="stTextInput"] input {
    background: transparent !important;
    color: #eef5f1 !important;
}
div[data-testid="stForm"] {
    background: var(--panel-bg) !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 16px;
    box-shadow: var(--wood-shadow) !important;
}
div[data-testid="stExpander"],
div[data-testid="stExpander"] details,
div[data-testid="stExpander"] > div {
    background: var(--panel-bg) !important;
    border: none !important;
    border-radius: 14px !important;
    box-shadow: var(--wood-shadow) !important;
}
div[data-testid="stExpander"] summary {
    background: transparent !important;
}
</style>
"""
st.markdown(PAGE_CSS.replace("__BACKGROUND_B64__", BACKGROUND_B64), unsafe_allow_html=True)


def parse_valor(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


PARTY_KEYWORDS = [
    "festa", "party", "musical", "imaginação", "imaginacao", "destreza",
    "agilidade", "trivia", "perguntas", "conhecimentos gerais", "adivinh",
]
COLABORATIVO_KEYWORDS = ["cooperativ", "colaborat"]
CARTAS_KEYWORDS = ["carta", "card"]


def classificar_tipo(categoria):
    c = (categoria or "").lower()
    if any(k in c for k in COLABORATIVO_KEYWORDS):
        return "Colaborativo"
    if any(k in c for k in PARTY_KEYWORDS):
        return "Party Game"
    return "Estratégia"


def eh_jogo_de_cartas(categoria):
    c = (categoria or "").lower()
    return any(k in c for k in CARTAS_KEYWORDS)


def eh_expansao(jogo):
    blob = f"{jogo.get('categoria', '')} {jogo.get('descricao', '')}".lower()
    return "expans" in blob


def carregar_jogos():
    resp = requests.get(LISTAR_URL, timeout=15)
    resp.raise_for_status()
    texto = resp.text.strip()
    return resp.json() if texto else []


def adicionar_jogo(nome):
    resp = requests.post(
        ADICIONAR_URL,
        json={"nome": nome},
        timeout=90,
    )
    resp.raise_for_status()


@st.cache_data(show_spinner=False, ttl=3600)
def buscar_pdf_bytes(url):
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return resp.content


def excluir_jogo(jogo_id):
    resp = requests.post(
        EXCLUIR_URL,
        json={"id": jogo_id},
        timeout=30,
    )
    resp.raise_for_status()


if "jogos" not in st.session_state:
    try:
        st.session_state.jogos = carregar_jogos()
    except Exception as e:
        st.error(f"Não consegui carregar a coleção: {e}")
        st.session_state.jogos = []

if "jogo_selecionado" not in st.session_state:
    st.session_state.jogo_selecionado = None

jogos = st.session_state.jogos


def encontrar_jogo(jogo_id):
    for j in jogos:
        if j.get("id") == jogo_id:
            return j
    return None


def renderizar_detalhe(jogo):
    if st.button("← Voltar para a coleção"):
        st.session_state.jogo_selecionado = None
        st.rerun()

    col_img, col_info = st.columns([1, 2])
    with col_img:
        imagem = jogo.get("imagem_url") or ""
        if imagem:
            st.image(imagem, use_container_width=True)
        else:
            st.markdown('<div class="tile-img-placeholder">🌰</div>', unsafe_allow_html=True)

    with col_info:
        st.title(jogo.get("nome", ""))
        categoria = jogo.get("categoria") or "Sem categoria"
        ano = jogo.get("ano_publicacao") or "?"
        editora = jogo.get("editora") or "?"
        st.markdown(f'<div class="detail-meta">📂 {categoria}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-meta">📅 Ano: {ano}  ·  🏭 Editora: {editora}</div>', unsafe_allow_html=True)

        mercado = parse_valor(jogo.get("valor_mercado_estimado"))
        st.markdown(
            f'<div class="detail-meta">📈 Valor de mercado estimado: R$ {mercado:,.2f}</div>',
            unsafe_allow_html=True,
        )

        nota = jogo.get("bgg_nota") or ""
        if nota:
            st.markdown(f'<div class="detail-meta">⭐ Nota BGG: {nota}</div>', unsafe_allow_html=True)

        descricao = jogo.get("descricao") or ""
        if descricao:
            st.markdown(f'<div class="detail-desc">{descricao}</div>', unsafe_allow_html=True)

    manual = jogo.get("manual_url") or ""
    imagem_manual = jogo.get("imagem_manual_url") or ""
    if manual or imagem_manual:
        st.divider()
        st.subheader("📖 Manual / regras")

        if imagem_manual:
            st.image(imagem_manual, use_container_width=True, caption="Foto do manual/regras original")

        if manual:
            if "boardgamegeek.com" in manual:
                st.caption("Esse link está hospedado no BoardGameGeek, que não permite ser exibido incorporado nesta página.")
                st.link_button("Abrir manual no BoardGameGeek", manual)
            elif "/webhook/jogos-manual-pdf" in manual:
                try:
                    with st.spinner("Carregando manual..."):
                        pdf_bytes = buscar_pdf_bytes(manual)
                    pdf_viewer(pdf_bytes, height=700)
                except Exception as e:
                    st.error(f"Não consegui carregar o manual: {e}")
                    st.link_button("Abrir manual em uma nova aba", manual)
            else:
                components.iframe(manual, height=700, scrolling=True)
                st.caption(f"Se o manual não aparecer acima (alguns sites bloqueiam a exibição incorporada), [abra em uma nova aba]({manual}).")

    st.divider()
    if not st.session_state.get("confirmar_exclusao", False):
        if st.button("🗑️ Excluir jogo da coleção"):
            st.session_state.confirmar_exclusao = True
            st.rerun()
    else:
        st.warning(f"Tem certeza que deseja excluir **{jogo.get('nome', '')}**? Essa ação não pode ser desfeita.")
        col_sim, col_nao = st.columns(2)
        if col_sim.button("Sim, excluir", type="primary", use_container_width=True):
            try:
                excluir_jogo(jogo.get("id"))
                st.session_state.pop("jogos", None)
                st.session_state.jogo_selecionado = None
                st.session_state.confirmar_exclusao = False
                st.success("Jogo excluído da coleção.")
                st.rerun()
            except Exception as e:
                st.error(f"Não consegui excluir: {e}")
        if col_nao.button("Cancelar", use_container_width=True):
            st.session_state.confirmar_exclusao = False
            st.rerun()


def renderizar_lista():
    col_h1, col_h2, col_h3 = st.columns([1, 5, 1])
    with col_h2:
        st.image(str(HEADER_IMG), use_container_width=True)
    st.caption("Cadastre pelo nome — categoria, ano e valor de mercado são buscados automaticamente.")

    col_busca, col_add = st.columns([4, 1])
    busca = col_busca.text_input(
        "Buscar na coleção",
        placeholder="🌿 Buscar pelo nome de um jogo já cadastrado...",
        label_visibility="collapsed",
    )
    if col_add.button("🌱 Adicionar", use_container_width=True):
        st.session_state.mostrar_form_adicionar = not st.session_state.get("mostrar_form_adicionar", False)

    if st.session_state.get("mostrar_form_adicionar", False):
        with st.form("form_adicionar", clear_on_submit=True):
            col_nome, col_botao = st.columns([4, 1])
            nome_novo = col_nome.text_input("Nome do novo jogo", placeholder="Ex: Catan")
            col_botao.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
            enviar = col_botao.form_submit_button("Buscar e adicionar")

        if enviar:
            if not nome_novo.strip():
                st.warning("Digite o nome do jogo.")
            else:
                with st.spinner(f"Buscando informações de '{nome_novo}'..."):
                    try:
                        adicionar_jogo(nome_novo.strip())
                        st.session_state.pop("jogos", None)
                        st.session_state.mostrar_form_adicionar = False
                        st.success(f"'{nome_novo}' adicionado à coleção!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Não consegui adicionar: {e}")

    if st.button("🍃 Atualizar lista"):
        st.session_state.pop("jogos", None)
        st.rerun()

    total_jogos = len(jogos)
    total_mercado = sum(parse_valor(j.get("valor_mercado_estimado")) for j in jogos)
    valor_medio = total_mercado / total_jogos if total_jogos else 0.0
    total_expansoes = sum(1 for j in jogos if eh_expansao(j))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌰 Jogos na coleção", total_jogos)
    c2.metric("📈 Valor de mercado estimado", f"R$ {total_mercado:,.2f}")
    c3.metric("🌳 Valor médio de mercado por jogo", f"R$ {valor_medio:,.2f}")
    c4.metric("🍄 Expansões", total_expansoes)

    st.divider()

    if not jogos:
        st.info("Nenhum jogo cadastrado ainda. Adicione o primeiro usando o formulário acima.")
        return

    with st.expander("🌳 Destaques do catálogo"):
        d1, d2, d3 = st.columns(3)

        com_valor = [j for j in jogos if parse_valor(j.get("valor_mercado_estimado")) > 0]
        mais_caros = sorted(com_valor, key=lambda j: parse_valor(j.get("valor_mercado_estimado")), reverse=True)[:5]
        mais_baratos = sorted(com_valor, key=lambda j: parse_valor(j.get("valor_mercado_estimado")))[:5]
        com_nota = [j for j in jogos if parse_valor(j.get("bgg_nota")) > 0]
        melhor_avaliados = sorted(com_nota, key=lambda j: parse_valor(j.get("bgg_nota")), reverse=True)[:5]

        with d1:
            st.markdown("**💰 Top 5 valor mais alto**")
            for j in mais_caros:
                st.markdown(f"- {j.get('nome')} — R$ {parse_valor(j.get('valor_mercado_estimado')):,.2f}")
        with d2:
            st.markdown("**💸 Top 5 valor mais baixo**")
            for j in mais_baratos:
                st.markdown(f"- {j.get('nome')} — R$ {parse_valor(j.get('valor_mercado_estimado')):,.2f}")
        with d3:
            st.markdown("**⭐ Top 5 mais bem avaliados (BGG)**")
            if melhor_avaliados:
                for j in melhor_avaliados:
                    st.markdown(f"- {j.get('nome')} — nota {j.get('bgg_nota')}")
            else:
                st.caption("Ainda sem notas do BGG cadastradas para nenhum jogo da coleção.")

    st.divider()

    filtro = st.radio(
        "Filtrar por tipo",
        ["Todos", "Estratégia", "Party Game", "Colaborativo", "🃏 Jogos de Cartas"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if filtro == "Todos":
        lista = jogos
    elif filtro == "🃏 Jogos de Cartas":
        lista = [j for j in jogos if eh_jogo_de_cartas(j.get("categoria"))]
    else:
        lista = [j for j in jogos if classificar_tipo(j.get("categoria")) == filtro]

    if busca.strip():
        termo = busca.strip().lower()
        lista = [j for j in lista if termo in (j.get("nome") or "").lower()]

    lista = sorted(lista, key=lambda j: parse_valor(j.get("valor_mercado_estimado")), reverse=True)

    if not lista:
        st.info("Nenhum jogo encontrado.")
        return

    cols = st.columns(5)
    for i, jogo in enumerate(lista):
        with cols[i % 5]:
            imagem = jogo.get("imagem_url") or ""
            if imagem:
                st.markdown(f'<div class="tile-card"><div class="tile-img"><img src="{imagem}"></div></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="tile-card"><div class="tile-img-placeholder">🌰</div></div>', unsafe_allow_html=True)
            if st.button(jogo.get("nome", ""), key=f"tile_{jogo.get('id')}", use_container_width=True):
                st.session_state.jogo_selecionado = jogo.get("id")
                st.rerun()


if st.session_state.jogo_selecionado is not None:
    jogo_atual = encontrar_jogo(st.session_state.jogo_selecionado)
    if jogo_atual is None:
        st.session_state.jogo_selecionado = None
        st.rerun()
    else:
        renderizar_detalhe(jogo_atual)
else:
    renderizar_lista()
