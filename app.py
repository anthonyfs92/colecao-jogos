import streamlit as st
import streamlit.components.v1 as components
import requests

st.set_page_config(page_title="Coleção de Jogos", page_icon="🎲", layout="wide")

N8N_BASE_URL = st.secrets.get("N8N_BASE_URL", "https://34-30-243-201.sslip.io")
LISTAR_URL = f"{N8N_BASE_URL}/webhook/jogos-listar"
ADICIONAR_URL = f"{N8N_BASE_URL}/webhook/jogos-adicionar"
EXCLUIR_URL = f"{N8N_BASE_URL}/webhook/jogos-excluir"

PAGE_CSS = """
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 15% 0%, #16221f 0%, #0e1412 60%);
}
[data-testid="stHeader"] { background: transparent; }
h1 {
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #f2c14e, #4fd1a5 65%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
[data-testid="stCaptionContainer"] { color: #8b9c96 !important; }
div[data-testid="stMetric"] {
    background: #142019;
    border: 1px solid rgba(79,209,165,0.18);
    border-radius: 14px;
    padding: 14px 16px;
}
div[data-testid="stMetricLabel"] { color: #9fb8ae !important; }
h3 {
    border-bottom: 1px solid rgba(242,193,78,0.25);
    padding-bottom: 6px;
    color: #f2c14e;
}
.tile-img img {
    border-radius: 10px;
    width: 100%;
    object-fit: cover;
    aspect-ratio: 1 / 1;
}
.tile-img-placeholder {
    border-radius: 10px;
    width: 100%;
    aspect-ratio: 1 / 1;
    background: #1a2721;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: #3f544c;
}
div[data-testid="column"] div[data-testid="stButton"] button {
    margin-top: -6px;
}
.detail-meta { color: #8b9c96; font-size: 0.95rem; margin-top: 2px; }
.detail-desc { color: #cfe0d9; margin-top: 14px; line-height: 1.5; }
button { border-radius: 10px !important; }
</style>
"""
st.markdown(PAGE_CSS, unsafe_allow_html=True)


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


def classificar_tipo(categoria):
    c = (categoria or "").lower()
    if any(k in c for k in COLABORATIVO_KEYWORDS):
        return "Colaborativo"
    if any(k in c for k in PARTY_KEYWORDS):
        return "Party Game"
    return "Estratégia"


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
            st.markdown('<div class="tile-img-placeholder">🎲</div>', unsafe_allow_html=True)

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
    st.title("🎲 Coleção de Jogos de Tabuleiro")
    st.caption("Cadastre pelo nome — categoria, ano e valor de mercado são buscados automaticamente.")

    col_busca, col_add = st.columns([4, 1])
    busca = col_busca.text_input(
        "Buscar na coleção",
        placeholder="🔍 Buscar pelo nome de um jogo já cadastrado...",
        label_visibility="collapsed",
    )
    if col_add.button("➕ Adicionar", use_container_width=True):
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

    if st.button("🔄 Atualizar lista"):
        st.session_state.pop("jogos", None)
        st.rerun()

    total_jogos = len(jogos)
    total_mercado = sum(parse_valor(j.get("valor_mercado_estimado")) for j in jogos)
    valor_medio = total_mercado / total_jogos if total_jogos else 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("🎲 Jogos na coleção", total_jogos)
    c2.metric("📈 Valor de mercado estimado", f"R$ {total_mercado:,.2f}")
    c3.metric("📊 Valor médio de mercado por jogo", f"R$ {valor_medio:,.2f}")

    st.divider()

    if not jogos:
        st.info("Nenhum jogo cadastrado ainda. Adicione o primeiro usando o formulário acima.")
        return

    filtro = st.radio(
        "Filtrar por tipo",
        ["Todos", "Estratégia", "Party Game", "Colaborativo"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if filtro == "Todos":
        lista = jogos
    else:
        lista = [j for j in jogos if classificar_tipo(j.get("categoria")) == filtro]

    if busca.strip():
        termo = busca.strip().lower()
        lista = [j for j in lista if termo in (j.get("nome") or "").lower()]

    if not lista:
        st.info("Nenhum jogo encontrado.")
        return

    cols = st.columns(5)
    for i, jogo in enumerate(lista):
        with cols[i % 5]:
            imagem = jogo.get("imagem_url") or ""
            if imagem:
                st.markdown(f'<div class="tile-img"><img src="{imagem}"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="tile-img-placeholder">🎲</div>', unsafe_allow_html=True)
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
