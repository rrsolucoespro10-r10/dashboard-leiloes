# ===============================================================
# DASHBOARD - Leilões de Imóveis (DADOS REAIS DA CAIXA)
# Feito em Python (Dash + Plotly) - RR Soluções
# Rodar:  python dashboard_leiloes.py   ->  abre em localhost:8050
# Base:   imoveis_caixa.csv.gz  (gere com _construir_base.py)
# ===============================================================

import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table

# ===============================================================
# >>> MARCA (troque aqui pra personalizar pra cada cliente) <<<
# ===============================================================
MARCA_NOME   = "RR Soluções"
MARCA_TITULO = "🏛️  Painel de Leilões de Imóveis"
MARCA_SUB    = "Imóveis da Caixa abaixo do valor de avaliação — dados reais"
COR_DESTAQUE = "#00E676"   # cor principal. Ex cliente azul: "#1E88E5"
COR_FUNDO    = "#0d1117"
COR_CARD     = "#161b22"
COR_TEXTO    = "#e6edf3"
# ===============================================================

# ---------------------------------------------------------------
# 1) CARREGA OS DADOS REAIS
# ---------------------------------------------------------------
BASE = os.path.join(os.path.dirname(__file__), "imoveis_caixa.csv.gz")
df = pd.read_csv(BASE)
df["Desconto"] = pd.to_numeric(df["Desconto"], errors="coerce").fillna(0)
df["Lance"] = pd.to_numeric(df["Lance"], errors="coerce")
df["Avaliacao"] = pd.to_numeric(df["Avaliacao"], errors="coerce")

# centro geográfico de cada estado (pro mapa)
UF_COORD = {
    "AC": (-8.77, -70.55), "AL": (-9.62, -36.82), "AP": (1.41, -51.77),
    "AM": (-3.47, -65.10), "BA": (-12.96, -41.70), "CE": (-5.20, -39.53),
    "DF": (-15.83, -47.86), "ES": (-19.19, -40.34), "GO": (-15.98, -49.86),
    "MA": (-5.42, -45.44), "MT": (-12.64, -55.42), "MS": (-20.51, -54.54),
    "MG": (-18.10, -44.38), "PA": (-3.79, -52.48), "PB": (-7.28, -36.72),
    "PR": (-24.89, -51.55), "PE": (-8.38, -37.86), "PI": (-6.60, -42.28),
    "RJ": (-22.25, -42.66), "RN": (-5.81, -36.59), "RS": (-30.17, -53.50),
    "RO": (-10.83, -63.34), "RR": (1.99, -61.33), "SC": (-27.45, -50.95),
    "SP": (-22.19, -48.79), "SE": (-10.57, -37.45), "TO": (-9.46, -48.26),
}

# ---------------------------------------------------------------
# 2) APP
# ---------------------------------------------------------------
app = Dash(__name__)
app.title = "Leilões de Imóveis | Caixa"
server = app.server  # necessário pro deploy (gunicorn/Render)

VERDE, FUNDO, CARD, TXT = COR_DESTAQUE, COR_FUNDO, COR_CARD, COR_TEXTO

def card_kpi(titulo, id_valor, cor=VERDE):
    return html.Div(style={
        "backgroundColor": CARD, "borderRadius": "14px", "padding": "20px",
        "flex": "1", "border": "1px solid #21262d",
        "boxShadow": "0 4px 14px rgba(0,0,0,0.4)"}, children=[
        html.Div(titulo, style={"color": "#8b949e", "fontSize": "13px",
                                "textTransform": "uppercase", "letterSpacing": "1px"}),
        html.Div(id=id_valor, className="kpi-valor",
                 style={"color": cor, "fontSize": "28px",
                        "fontWeight": "800", "marginTop": "6px"}),
    ])

dd_style = {"color": "#000"}

# CSS responsivo (mobile) — injetado no HTML da página
app.index_string = """<!DOCTYPE html>
<html>
<head>
  {%metas%}<title>{%title%}</title>{%favicon%}{%css%}
  <style>
    @media (max-width: 600px) {
      .approot { padding: 16px 14px !important; }
      .approot h1 { font-size: 21px !important; }
      .approot h3 { font-size: 16px !important; }
      .kpi-valor { font-size: 22px !important; }
    }
    .tabela-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  </style>
</head>
<body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body>
</html>"""

app.layout = html.Div(className="approot", style={
    "backgroundColor": FUNDO, "minHeight": "100vh", "fontFamily": "Segoe UI, sans-serif",
    "padding": "30px 40px", "color": TXT}, children=[

    # Cabeçalho
    html.Div(style={"display": "flex", "justifyContent": "space-between",
                    "alignItems": "center", "marginBottom": "10px"}, children=[
        html.Div([
            html.H1(MARCA_TITULO, style={"margin": "0", "fontSize": "30px"}),
            html.P(MARCA_SUB, style={"color": "#8b949e", "margin": "4px 0 0 0"}),
        ]),
        html.Div(f"{MARCA_NOME}", style={"backgroundColor": VERDE, "color": "#000",
                 "padding": "8px 16px", "borderRadius": "20px",
                 "fontWeight": "700", "fontSize": "13px"}),
    ]),

    html.Hr(style={"borderColor": "#21262d", "margin": "20px 0"}),

    # Filtros
    html.Div(style={"display": "flex", "gap": "16px", "marginBottom": "24px",
                    "flexWrap": "wrap"}, children=[
        html.Div([html.Label("Estado", style={"color": "#8b949e", "fontSize": "13px"}),
            dcc.Dropdown(id="f-uf", value="Todos", clearable=False, style=dd_style,
                options=[{"label": "Todos", "value": "Todos"}] +
                        [{"label": u, "value": u} for u in sorted(df["UF"].unique())])],
            style={"flex": "1", "minWidth": "150px"}),
        html.Div([html.Label("Cidade", style={"color": "#8b949e", "fontSize": "13px"}),
            dcc.Dropdown(id="f-cidade", value="Todas", clearable=False, style=dd_style)],
            style={"flex": "2", "minWidth": "200px"}),
        html.Div([html.Label("Tipo", style={"color": "#8b949e", "fontSize": "13px"}),
            dcc.Dropdown(id="f-tipo", value="Todos", clearable=False, style=dd_style,
                options=[{"label": "Todos", "value": "Todos"}] +
                        [{"label": t, "value": t} for t in sorted(df["Tipo"].unique())])],
            style={"flex": "1", "minWidth": "150px"}),
        html.Div([html.Label("Buscar (bairro / endereço)",
                             style={"color": "#8b949e", "fontSize": "13px"}),
            dcc.Input(id="f-busca", type="text", placeholder="ex: boa viagem",
                debounce=True, style={"width": "100%", "padding": "7px",
                "borderRadius": "6px", "border": "1px solid #30363d"})],
            style={"flex": "2", "minWidth": "200px"}),
    ]),

    # KPIs
    html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "26px",
                    "flexWrap": "wrap"}, children=[
        card_kpi("Imóveis encontrados", "kpi-qtd"),
        card_kpi("Valor total (lance mín.)", "kpi-valor"),
        card_kpi("Desconto médio", "kpi-desc", cor="#FFD600"),
        card_kpi("Maior oportunidade", "kpi-top", cor="#FF5252"),
    ]),

    # Gráficos
    html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "26px",
                    "flexWrap": "wrap"}, children=[
        html.Div(dcc.Graph(id="g-cidade"), style={"flex": "1", "minWidth": "320px",
                 "backgroundColor": CARD, "borderRadius": "14px", "padding": "10px"}),
        html.Div(dcc.Graph(id="g-tipo"), style={"flex": "1", "minWidth": "320px",
                 "backgroundColor": CARD, "borderRadius": "14px", "padding": "10px"}),
    ]),

    html.Div(dcc.Graph(id="g-desconto"), style={"backgroundColor": CARD,
             "borderRadius": "14px", "padding": "10px", "marginBottom": "26px"}),

    # Mapa
    html.H3("🗺️ Distribuição por estado", style={"marginBottom": "12px"}),
    html.Div(dcc.Graph(id="g-mapa"), style={"backgroundColor": CARD,
             "borderRadius": "14px", "padding": "10px", "marginBottom": "26px"}),

    # Tabela
    html.H3("📋 Lista de imóveis", style={"marginBottom": "12px"}),
    html.Div(className="tabela-wrap", children=[
    dash_table.DataTable(
        id="tabela", page_size=10, sort_action="native",
        columns=[
            {"name": "Tipo", "id": "Tipo"}, {"name": "Cidade", "id": "Cidade"},
            {"name": "Bairro", "id": "Bairro"},
            {"name": "Avaliação", "id": "Avaliacao"}, {"name": "Lance", "id": "Lance"},
            {"name": "Desc.%", "id": "Desconto"},
            {"name": "Link", "id": "Link", "presentation": "markdown"},
        ],
        style_header={"backgroundColor": "#21262d", "color": VERDE,
                      "fontWeight": "bold", "border": "none"},
        style_cell={"backgroundColor": CARD, "color": TXT, "border": "1px solid #21262d",
                    "padding": "10px", "fontSize": "13px", "textAlign": "left",
                    "maxWidth": "220px", "overflow": "hidden",
                    "textOverflow": "ellipsis"},
        style_data_conditional=[{"if": {"row_index": "odd"},
                                 "backgroundColor": "#1b2129"}],
    ),
    ]),

    html.P(f"Fonte: Caixa Econômica Federal • {len(df):,} imóveis • Gerado em Python"
           .replace(",", "."),
           style={"color": "#586069", "textAlign": "center",
                  "marginTop": "30px", "fontSize": "12px"}),
])

# ---------------------------------------------------------------
# 3) CALLBACK: opções de cidade dependem do estado
# ---------------------------------------------------------------
@app.callback(
    [Output("f-cidade", "options"), Output("f-cidade", "value")],
    Input("f-uf", "value"),
)
def cidades_do_estado(uf):
    d = df if uf == "Todos" else df[df["UF"] == uf]
    opts = [{"label": "Todas", "value": "Todas"}] + \
           [{"label": c, "value": c} for c in sorted(d["Cidade"].dropna().unique())]
    return opts, "Todas"

# ---------------------------------------------------------------
# 4) CALLBACK PRINCIPAL
# ---------------------------------------------------------------
def reais(v):
    return ("R$ " + f"{v:,.0f}").replace(",", ".")

@app.callback(
    [Output("kpi-qtd", "children"), Output("kpi-valor", "children"),
     Output("kpi-desc", "children"), Output("kpi-top", "children"),
     Output("g-cidade", "figure"), Output("g-tipo", "figure"),
     Output("g-desconto", "figure"), Output("g-mapa", "figure"),
     Output("tabela", "data")],
    [Input("f-uf", "value"), Input("f-cidade", "value"),
     Input("f-tipo", "value"), Input("f-busca", "value")],
)
def atualizar(uf, cidade, tipo, busca):
    d = df.copy()
    if uf != "Todos":
        d = d[d["UF"] == uf]
    if cidade and cidade != "Todas":
        d = d[d["Cidade"] == cidade]
    if tipo != "Todos":
        d = d[d["Tipo"] == tipo]
    if busca:
        b = busca.strip().lower()
        d = d[d["Bairro"].str.lower().str.contains(b, na=False) |
              d["Endereco"].str.lower().str.contains(b, na=False)]

    qtd = len(d)
    valor = reais(d["Lance"].sum()) if qtd else "—"
    desc = f"{d['Desconto'].mean():.0f}%" if qtd else "—"
    top = f"{d['Desconto'].max():.0f}% OFF" if qtd else "—"

    tema = dict(paper_bgcolor=CARD, plot_bgcolor=CARD, font_color=TXT,
                margin=dict(l=20, r=20, t=50, b=20))

    # Top 10 cidades
    topc = d.groupby("Cidade")["ID"].count().sort_values(ascending=False).head(10)
    g1 = px.bar(topc.reset_index(), x="ID", y="Cidade", orientation="h",
                title="Top 10 cidades (nº de imóveis)", text_auto=True,
                color="ID", color_continuous_scale="Greens")
    g1.update_layout(**tema, coloraxis_showscale=False,
                     yaxis={"categoryorder": "total ascending"})

    # Tipos
    g2 = px.pie(d, names="Tipo", title="Distribuição por tipo", hole=0.5)
    g2.update_layout(**tema)

    # Desconto x avaliação
    amostra = d.sample(min(len(d), 800)) if qtd else d
    g3 = px.scatter(amostra, x="Avaliacao", y="Desconto", color="Tipo",
                    title="Desconto x Valor de avaliação",
                    hover_data=["Cidade", "Bairro"])
    g3.update_layout(**tema)

    # Mapa por estado
    por_uf = d.groupby("UF").agg(qtd=("ID", "count"),
                                 desc=("Desconto", "mean")).reset_index()
    por_uf["lat"] = por_uf["UF"].map(lambda u: UF_COORD.get(u, (0, 0))[0])
    por_uf["lon"] = por_uf["UF"].map(lambda u: UF_COORD.get(u, (0, 0))[1])
    if len(por_uf):
        g4 = px.scatter_map(por_uf, lat="lat", lon="lon", size="qtd", color="desc",
                            color_continuous_scale="Greens", zoom=3.3, height=520,
                            hover_name="UF", size_max=55,
                            hover_data={"qtd": True, "desc": ":.0f", "lat": False, "lon": False},
                            map_style="carto-darkmatter")
    else:
        g4 = px.scatter_map(lat=[], lon=[], zoom=3.3, height=520,
                            map_style="carto-darkmatter")
    g4.update_layout(paper_bgcolor=CARD, font_color=TXT,
                     margin=dict(l=0, r=0, t=10, b=0))

    # Tabela (formatada)
    t = d.head(300).copy()
    t["Avaliacao"] = t["Avaliacao"].map(lambda v: reais(v) if pd.notna(v) else "—")
    t["Lance"] = t["Lance"].map(lambda v: reais(v) if pd.notna(v) else "—")
    t["Desconto"] = t["Desconto"].map(lambda v: f"{v:.0f}%")
    t["Link"] = t["Link"].map(lambda u: f"[ver imóvel]({u})" if isinstance(u, str) and u.startswith("http") else "")

    return qtd, valor, desc, top, g1, g2, g3, g4, t.to_dict("records")


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  DASHBOARD (DADOS REAIS DA CAIXA) RODANDO!")
    print("  >>>  http://localhost:8050  <<<")
    print("=" * 55 + "\n")
    app.run(debug=False, port=8050)
