# ===============================================================
# DASHBOARD DEMO - Leilões de Imóveis
# Feito em Python (Dash + Plotly) - RR Soluções
# Rodar:  python dashboard_leiloes.py   ->  abre em localhost:8050
# ===============================================================

import random
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table

# ---------------------------------------------------------------
# 1) GERA DADOS FICTÍCIOS DE LEILÕES
# ---------------------------------------------------------------
random.seed(42)

cidades = ["Caruaru", "Recife", "Garanhuns", "Petrolina", "Bezerros", "Gravatá"]
tipos = ["Apartamento", "Casa", "Terreno", "Galpão", "Loja", "Sítio"]
status_opcoes = ["Aberto", "1ª Praça", "2ª Praça", "Encerrado"]
bancos = ["Caixa", "Banco do Brasil", "Santander", "Itaú", "Bradesco"]

dados = []
for i in range(120):
    avaliacao = random.randint(80_000, 900_000)
    desconto = random.randint(20, 65)               # % de desconto
    lance_min = round(avaliacao * (1 - desconto / 100), -2)
    dados.append({
        "ID": f"LT-{1000 + i}",
        "Tipo": random.choice(tipos),
        "Cidade": random.choice(cidades),
        "Banco": random.choice(bancos),
        "Status": random.choice(status_opcoes),
        "Avaliação": avaliacao,
        "Lance Mínimo": lance_min,
        "Desconto %": desconto,
        "Área (m²)": random.randint(40, 600),
    })

df = pd.DataFrame(dados)

# ---------------------------------------------------------------
# 2) APP
# ---------------------------------------------------------------
app = Dash(__name__)
app.title = "Leilões de Imóveis | Demo"
server = app.server  # <-- necessário pro deploy (gunicorn/Render)

VERDE = "#00E676"
FUNDO = "#0d1117"
CARD = "#161b22"
TXT = "#e6edf3"

def card_kpi(titulo, id_valor, cor=VERDE):
    return html.Div(style={
        "backgroundColor": CARD, "borderRadius": "14px", "padding": "20px",
        "flex": "1", "border": f"1px solid #21262d",
        "boxShadow": "0 4px 14px rgba(0,0,0,0.4)"
    }, children=[
        html.Div(titulo, style={"color": "#8b949e", "fontSize": "13px",
                                "textTransform": "uppercase", "letterSpacing": "1px"}),
        html.Div(id=id_valor, style={"color": cor, "fontSize": "30px",
                                     "fontWeight": "800", "marginTop": "6px"}),
    ])

app.layout = html.Div(style={
    "backgroundColor": FUNDO, "minHeight": "100vh", "fontFamily": "Segoe UI, sans-serif",
    "padding": "30px 40px", "color": TXT
}, children=[

    # Cabeçalho
    html.Div(style={"display": "flex", "justifyContent": "space-between",
                    "alignItems": "center", "marginBottom": "10px"}, children=[
        html.Div([
            html.H1("🏛️  Painel de Leilões de Imóveis",
                    style={"margin": "0", "fontSize": "30px"}),
            html.P("Oportunidades abaixo do valor de mercado — atualizado em tempo real",
                   style={"color": "#8b949e", "margin": "4px 0 0 0"}),
        ]),
        html.Div("DEMO • RR Soluções",
                 style={"backgroundColor": VERDE, "color": "#000", "padding": "8px 16px",
                        "borderRadius": "20px", "fontWeight": "700", "fontSize": "13px"}),
    ]),

    html.Hr(style={"borderColor": "#21262d", "margin": "20px 0"}),

    # Filtros
    html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "24px"}, children=[
        html.Div([
            html.Label("Cidade", style={"color": "#8b949e", "fontSize": "13px"}),
            dcc.Dropdown(id="f-cidade",
                         options=[{"label": "Todas", "value": "Todas"}] +
                                 [{"label": c, "value": c} for c in sorted(cidades)],
                         value="Todas", clearable=False,
                         style={"color": "#000"}),
        ], style={"flex": "1"}),
        html.Div([
            html.Label("Tipo de Imóvel", style={"color": "#8b949e", "fontSize": "13px"}),
            dcc.Dropdown(id="f-tipo",
                         options=[{"label": "Todos", "value": "Todos"}] +
                                 [{"label": t, "value": t} for t in sorted(tipos)],
                         value="Todos", clearable=False,
                         style={"color": "#000"}),
        ], style={"flex": "1"}),
    ]),

    # KPIs
    html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "26px"}, children=[
        card_kpi("Imóveis disponíveis", "kpi-qtd"),
        card_kpi("Valor total (lance mín.)", "kpi-valor"),
        card_kpi("Desconto médio", "kpi-desc", cor="#FFD600"),
        card_kpi("Maior oportunidade", "kpi-top", cor="#FF5252"),
    ]),

    # Gráficos
    html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "26px"}, children=[
        html.Div(dcc.Graph(id="g-cidade"), style={"flex": "1", "backgroundColor": CARD,
                 "borderRadius": "14px", "padding": "10px"}),
        html.Div(dcc.Graph(id="g-tipo"), style={"flex": "1", "backgroundColor": CARD,
                 "borderRadius": "14px", "padding": "10px"}),
    ]),

    html.Div(dcc.Graph(id="g-desconto"), style={"backgroundColor": CARD,
             "borderRadius": "14px", "padding": "10px", "marginBottom": "26px"}),

    # Tabela
    html.H3("📋 Lista de imóveis", style={"marginBottom": "12px"}),
    dash_table.DataTable(
        id="tabela",
        columns=[{"name": c, "id": c} for c in
                 ["ID", "Tipo", "Cidade", "Banco", "Status", "Avaliação", "Lance Mínimo", "Desconto %"]],
        page_size=8,
        style_header={"backgroundColor": "#21262d", "color": VERDE, "fontWeight": "bold",
                      "border": "none"},
        style_cell={"backgroundColor": CARD, "color": TXT, "border": "1px solid #21262d",
                    "padding": "10px", "fontSize": "13px", "textAlign": "left"},
        style_data_conditional=[{"if": {"row_index": "odd"},
                                 "backgroundColor": "#1b2129"}],
    ),

    html.P("Dashboard gerado em Python • Dados fictícios para demonstração",
           style={"color": "#586069", "textAlign": "center", "marginTop": "30px", "fontSize": "12px"}),
])

# ---------------------------------------------------------------
# 3) INTERATIVIDADE (callbacks) - é o que faz reagir aos filtros
# ---------------------------------------------------------------
@app.callback(
    [Output("kpi-qtd", "children"), Output("kpi-valor", "children"),
     Output("kpi-desc", "children"), Output("kpi-top", "children"),
     Output("g-cidade", "figure"), Output("g-tipo", "figure"),
     Output("g-desconto", "figure"), Output("tabela", "data")],
    [Input("f-cidade", "value"), Input("f-tipo", "value")],
)
def atualizar(cidade, tipo):
    d = df.copy()
    if cidade != "Todas":
        d = d[d["Cidade"] == cidade]
    if tipo != "Todos":
        d = d[d["Tipo"] == tipo]

    # KPIs
    qtd = len(d)
    valor = f"R$ {d['Lance Mínimo'].sum():,.0f}".replace(",", ".")
    desc = f"{d['Desconto %'].mean():.0f}%" if qtd else "—"
    top = f"{d['Desconto %'].max():.0f}% OFF" if qtd else "—"

    tema = dict(paper_bgcolor=CARD, plot_bgcolor=CARD, font_color=TXT,
                margin=dict(l=20, r=20, t=50, b=20))

    # Gráfico por cidade
    g1 = px.bar(d.groupby("Cidade")["ID"].count().reset_index(),
                x="Cidade", y="ID", title="Imóveis por cidade",
                color="ID", color_continuous_scale="Greens", text_auto=True)
    g1.update_layout(**tema, coloraxis_showscale=False)

    # Gráfico por tipo (pizza)
    g2 = px.pie(d, names="Tipo", title="Distribuição por tipo de imóvel", hole=0.5)
    g2.update_layout(**tema)

    # Desconto vs valor
    g3 = px.scatter(d, x="Avaliação", y="Desconto %", size="Área (m²)",
                    color="Tipo", title="Desconto x Valor de avaliação (bolha = área)",
                    hover_data=["ID", "Cidade"])
    g3.update_layout(**tema)

    return qtd, valor, desc, top, g1, g2, g3, d.to_dict("records")


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  DASHBOARD RODANDO!  Abra no navegador:")
    print("  >>>  http://localhost:8050  <<<")
    print("=" * 55 + "\n")
    app.run(debug=False, port=8050)
