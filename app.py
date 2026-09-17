import streamlit as st
import requests

st.set_page_config(page_title="Coleção de Jogos", page_icon="🎲", layout="wide")

N8N_BASE_URL = st.secrets.get("N8N_BASE_URL", "https://34-30-243-201.sslip.io")
LISTAR_URL = f"{N8N_BASE_URL}/webhook/jogos-listar"
ADICIONAR_URL = f"{N8N_BASE_URL}/webhook/jogos-adicionar"

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
.game-card {
    background: #142019;
    border: 1px solid rgba(79,209,165,0.15);
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 14px;
    height: 100%;
}
.game-card img {
    border-radius: 8px;
    width: 100%;
    object-fit: cover;
    aspect-ratio: 1 / 1;
}
.game-title { font-weight: 700; color: #eef5f1; margin-top: 8px; font-size: 0.95rem; }
.game-meta { color: #8b9c96; font-size: 0.8rem; margin-top: 2px; }
.game-link a { color: #4fd1a5; font-size: 0.8rem; text-decoration: none; }
button { border-radius: 10px !important; }
</style>
"""
st.markdown(PAGE_CSS, unsafe_allow_html=True)


def parse_valor(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def carregar_jogos():
    resp = requests.get(LISTAR_URL, timeout=15)
    resp.raise_for_status()
    texto = resp.text.strip()
    return resp.json() if texto else []


def adicionar_jogo(nome, valor_pago):
    resp = requests.post(
        ADICIONAR_URL,
        json={"nome": nome, "valor_pago": valor_pago},
        timeout=90,
    )
    resp.raise_for_status()


st.title("🎲 Coleção de Jogos de Tabuleiro")
st.caption("Cadastre pelo nome — categoria, ano e valor de mercado são buscados automaticamente.")

with st.form("form_adicionar", clear_on_submit=True):
    col_nome, col_valor, col_botao = st.columns([3, 1, 1])
    nome_novo = col_nome.text_input("Nome do jogo", placeholder="Ex: Catan")
    valor_novo = col_valor.number_input("Valor pago (R$)", min_value=0.0, step=10.0, format="%.2f")
    col_botao.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
    enviar = col_botao.form_submit_button("➕ Adicionar")

if enviar:
    if not nome_novo.strip():
        st.warning("Digite o nome do jogo.")
    else:
        with st.spinner(f"Buscando informações de '{nome_novo}'..."):
            try:
                adicionar_jogo(nome_novo.strip(), valor_novo)
                st.session_state.pop("jogos", None)
                st.success(f"'{nome_novo}' adicionado à coleção!")
            except Exception as e:
                st.error(f"Não consegui adicionar: {e}")

if st.button("🔄 Atualizar lista"):
    st.session_state.pop("jogos", None)

if "jogos" not in st.session_state:
    try:
        st.session_state.jogos = carregar_jogos()
    except Exception as e:
        st.error(f"Não consegui carregar a coleção: {e}")
        st.session_state.jogos = []

jogos = st.session_state.jogos

total_jogos = len(jogos)
total_investido = sum(parse_valor(j.get("valor_pago")) for j in jogos)
valor_medio = total_investido / total_jogos if total_jogos else 0.0
total_mercado = sum(parse_valor(j.get("valor_mercado_estimado")) for j in jogos)

c1, c2, c3, c4 = st.columns(4)
c1.metric("🎲 Jogos na coleção", total_jogos)
c2.metric("💰 Total investido", f"R$ {total_investido:,.2f}")
c3.metric("📊 Valor médio por jogo", f"R$ {valor_medio:,.2f}")
c4.metric("📈 Valor de mercado estimado", f"R$ {total_mercado:,.2f}")

st.divider()

if not jogos:
    st.info("Nenhum jogo cadastrado ainda. Adicione o primeiro usando o formulário acima.")
else:
    categorias = {}
    for j in jogos:
        cat = (j.get("categoria") or "").strip() or "Sem categoria"
        categorias.setdefault(cat, []).append(j)

    for categoria in sorted(categorias.keys()):
        lista = categorias[categoria]
        st.subheader(f"{categoria} · {len(lista)} jogo(s)")
        cols = st.columns(5)
        for i, jogo in enumerate(lista):
            with cols[i % 5]:
                imagem = jogo.get("imagem_url") or ""
                img_html = f'<img src="{imagem}">' if imagem else ""
                pago = parse_valor(jogo.get("valor_pago"))
                mercado = parse_valor(jogo.get("valor_mercado_estimado"))
                ano = jogo.get("ano_publicacao") or ""
                link = jogo.get("manual_url") or ""
                link_html = f'<div class="game-link"><a href="{link}" target="_blank">📖 Manual / BGG</a></div>' if link else ""
                card_html = (
                    '<div class="game-card">'
                    + img_html
                    + f'<div class="game-title">{jogo.get("nome", "")}</div>'
                    + f'<div class="game-meta">{ano}</div>'
                    + f'<div class="game-meta">Pago: R$ {pago:,.2f}</div>'
                    + f'<div class="game-meta">Mercado: R$ {mercado:,.2f}</div>'
                    + link_html
                    + "</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)

with st.expander("Detalhes técnicos"):
    for j in jogos:
        st.write(f"**{j.get('nome')}** — {j.get('descricao') or '_sem descrição (aguardando BGG)_'}")
