"""Gera relatorio_dynamic_programming.pdf (4 páginas).

Antes de entregar: preencha EQUIPE e LINK_REPO e rode
    pip install reportlab
    python gerar_relatorio.py
As figuras vêm do notebook já executado em ../dynamic-programming/.
"""
import base64
from xml.sax.saxutils import escape
import io
import json
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

# ----------------------------------------------------------------------------
# PREENCHER ANTES DE ENTREGAR (ordem alfabética)
EQUIPE = [
    ("Carlos Santiago Clementino", "RM575749"),
    ("Eduarda da Silva Brito", "RM567347"),
    ("Gustavo Castilho Gonçalves", "RM566970"),
    ("Gustavo Moretim Canzi", "RM567683"),
    ("Lucca Ghiraldi Urso", "RM566739"),
]
NOME_EQUIPE = "Vagalume"
LINK_REPO = "https://github.com/Gucastilho/Dynamic-programming-GS/tree/main/dynamic-programming"
# ----------------------------------------------------------------------------

AQUI = Path(__file__).resolve().parent
PASTA_DP = AQUI.parent / "dynamic-programming"
SAIDA = AQUI / "relatorio_dynamic_programming.pdf"

AMARELO, AMARELO_CLARO, ESCURO, CINZA = (colors.HexColor(c) for c in
                                         ("#F9D657", "#FDEEB9", "#323232", "#4B4B4B"))

FONTES = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FONTES / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONTES / "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Italic", str(FONTES / "ariali.ttf")))
pdfmetrics.registerFont(TTFont("Consolas", str(FONTES / "consola.ttf")))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

corpo = ParagraphStyle("corpo", fontName="Arial", fontSize=9.6, leading=13.2, textColor=ESCURO,
                       spaceAfter=5)
titulo = ParagraphStyle("titulo", parent=corpo, fontName="Arial-Bold", fontSize=17, leading=21,
                        spaceAfter=8)
sub = ParagraphStyle("sub", parent=corpo, fontName="Arial-Bold", fontSize=11, leading=14,
                     spaceBefore=6, spaceAfter=4)
lista = ParagraphStyle("lista", parent=corpo, leftIndent=12, bulletIndent=2, spaceAfter=2.5)
legenda = ParagraphStyle("legenda", parent=corpo, fontSize=8, leading=10, textColor=CINZA,
                         alignment=TA_CENTER)
celula = ParagraphStyle("celula", parent=corpo, fontSize=8.4, leading=10.6, spaceAfter=0)
celula_b = ParagraphStyle("celula_b", parent=celula, fontName="Arial-Bold")
formula = ParagraphStyle("formula", parent=corpo, fontName="Consolas", fontSize=9, leading=12.5,
                         backColor=AMARELO_CLARO, borderPadding=(5, 7, 5, 7), leftIndent=7,
                         rightIndent=7, spaceBefore=4, spaceAfter=9)
codigo = ParagraphStyle("codigo", fontName="Consolas", fontSize=7.6, leading=9.4, textColor=ESCURO)

P = lambda t, s=corpo: Paragraph(t, s)
B = lambda t: Paragraph(t, lista, bulletText="•")


def tabela(linhas, larguras, cabecalho=True):
    dados = [[P(str(c), celula_b if (cabecalho and i == 0) else celula) for c in l]
             for i, l in enumerate(linhas)]
    t = Table(dados, colWidths=larguras, hAlign="LEFT")
    estilo = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
              ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if cabecalho:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), AMARELO))
    t.setStyle(TableStyle(estilo))
    return t


def figuras_do_notebook():
    nb = json.loads((PASTA_DP / "vagalume_rota_segura.ipynb").read_text(encoding="utf-8"))
    return [base64.b64decode(o["data"]["image/png"]) for c in nb["cells"] if c["cell_type"] == "code"
            for o in c.get("outputs", []) if "image/png" in o.get("data", {})]


def imagem(png, largura):
    img = Image(io.BytesIO(png))
    img.drawHeight = largura * img.imageHeight / img.imageWidth
    img.drawWidth = largura
    return img


def trecho_do_codigo(inicio, fim):
    """Copia o trecho de rota_dp.py entre dois comentários, com número de linha."""
    linhas = (PASTA_DP / "rota_dp.py").read_text(encoding="utf-8").splitlines()
    a = next(i for i, l in enumerate(linhas) if inicio in l)
    b = next(i for i, l in enumerate(linhas) if fim in l and i > a)
    usadas = [i for i in range(a, b) if linhas[i].strip()]
    texto = "\n".join(f"{i + 1:3d}  {linhas[i][4:]}" for i in usadas)
    return texto, usadas[0] + 1, usadas[-1] + 1


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 7.5)
    canvas.setFillColor(CINZA)
    canvas.drawString(2 * cm, 1.1 * cm, "Vagalume · Global Solution FIAP 2026.2 · Dynamic Programming")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, str(doc.page))
    canvas.setFillColor(AMARELO)
    canvas.rect(0, A4[1] - 0.35 * cm, A4[0], 0.35 * cm, stroke=0, fill=1)
    canvas.restoreState()


def capa(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(AMARELO)
    canvas.rect(0, A4[1] - 9.5 * cm, A4[0], 9.5 * cm, stroke=0, fill=1)
    canvas.restoreState()


def montar():
    W = A4[0] - 4 * cm
    mapa, bench = figuras_do_notebook()
    story = []

    # ---------------- Página 1: capa ----------------
    story += [Spacer(1, 2.2 * cm),
              P("Vagalume", ParagraphStyle("capa1", parent=titulo, fontSize=40, leading=46)),
              P("Rota mais segura dentro de um orçamento de desvio, por programação dinâmica",
                ParagraphStyle("capa2", parent=corpo, fontSize=14, leading=18)),
              Spacer(1, 0.3 * cm),
              P("Global Solution FIAP 2026.2 · CitizenTech · Engenharia de Software, 2º ano · "
                "Disciplina: <b>Dynamic Programming</b>", corpo),
              Spacer(1, 2.6 * cm),
              P(f"Equipe: <b>{NOME_EQUIPE}</b>", sub)]
    story.append(tabela([("Integrante", "RM")] + EQUIPE, [11 * cm, 4 * cm]))
    story += [Spacer(1, 0.6 * cm),
              P("<b>Repositório</b> (pasta <font face='Consolas'>dynamic-programming/</font>):"),
              P(f"<link href='{escape(LINK_REPO)}' color='blue'>{escape(LINK_REPO)}</link>"),
              Spacer(1, 0.6 * cm),
              P("<b>Conteúdo da pasta:</b> <font face='Consolas'>vagalume_rota_segura.ipynb</font> "
                "(cenário, fonte dos dados, exemplos, testes e benchmark), "
                "<font face='Consolas'>rota_dp.py</font> (algoritmo), "
                "<font face='Consolas'>test_rota_dp.py</font> (13 testes), "
                "<font face='Consolas'>dados/</font> (CSVs) e "
                "<font face='Consolas'>README.md</font>."),
              Spacer(1, 1.2 * cm),
              P(f"São Paulo, {date(2026, 11, 19).strftime('%d/%m/%Y')}", corpo),
              PageBreak()]

    # ---------------- Página 2: problema ----------------
    story += [P("1. Problema", titulo),
              P("O Vagalume é a CitizenTech da equipe: um aplicativo que sugere a rota mais segura "
                "de A até B e, se a pessoa se sentir em risco no caminho, indica o Ponto Seguro aberto "
                "mais próximo. O piloto cobre a região da Av. Paulista e da Bela Vista, em São Paulo."),
              P("<b>Problema, em uma frase:</b> muitas pessoas, principalmente mulheres, não sabem quais "
                "trechos do caminho são mais seguros e acabam escolhendo a rota pelo tempo, e não pela "
                "segurança."),
              P("<b>Cidadão beneficiado:</b> quem se desloca a pé ou de transporte público, com foco em "
                "mulheres, e também pessoas LGBTQIA+, idosos e quem volta tarde do trabalho ou da "
                "faculdade. ODS conectados: 3 (metas 3.4, 3.5 e 3.6), 10 e 11 (metas 11.2 e 11.7)."),
              P("O problema computacional", sub),
              P("A rota mais segura quase nunca é a mais curta, e a pessoa não aceita andar qualquer "
                "distância a mais. Por isso, o app tem um controle simples: <i>\"aceito andar até "
                "B metros a mais\"</i>. O algoritmo precisa encontrar:"),
              P("a rota de <b>menor risco acumulado</b> da origem ao destino cuja distância seja, "
                "no máximo, a distância mínima + B.", formula),
              tabela([("", "Descrição"),
                      ("Entrada", "Grafo de ruas, origem, destino, orçamento de desvio B (metros) e "
                                  "horário da consulta"),
                      ("Saída", "Sequência de esquinas, distância, desvio usado, nota de segurança de "
                                "0 a 100 e os fatores que mais pesaram na nota"),
                      ("Restrição", "Distância ≤ distância mínima + B")],
                     [2.6 * cm, W - 2.6 * cm]),
              P("Por que programação dinâmica", sub),
              P("Há duas grandezas em jogo, a distância e o risco, e uma delas é restrição. O Dijkstra "
                "minimiza uma só e é um algoritmo guloso: ao fixar o caminho mais barato até uma esquina, "
                "ele descarta caminhos mais seguros que chegam ali um pouco mais longos e que poderiam "
                "caber no orçamento. Esse é o <b>caminho mínimo com restrição de recurso</b>, um problema "
                "clássico de DP: ele tem <b>subestrutura ótima</b> (a melhor rota até B com <i>d</i> "
                "metros termina na melhor rota até a esquina anterior com <i>d − w</i> metros) e "
                "<b>subproblemas sobrepostos</b> (a mesma esquina é alcançada por muitos caminhos com a "
                "mesma distância). Testar todos os caminhos é exponencial, como mostra a seção 3."),
              P("Integração com as outras disciplinas", sub),
              B("<b>Data Science:</b> as ocorrências por trecho e os pesos por horário vêm da análise "
                "descritiva da base da SSP-SP."),
              B("<b>Database Design:</b> os nós, trechos, reports, ocorrências e Pontos Seguros são as "
                "entidades <font face='Consolas'>TRECHO</font>, <font face='Consolas'>REPORT</font>, "
                "<font face='Consolas'>OCORRENCIA_OFICIAL</font> e "
                "<font face='Consolas'>PONTO_APOIO</font>, e a rota calculada é gravada em "
                "<font face='Consolas'>ROTA_CONSULTADA</font>."),
              B("<b>Java (DDD):</b> o mesmo algoritmo é o <font face='Consolas'>RoteirizadorService</font>, "
                "e o motor de risco é a <font face='Consolas'>CalculadoraRisco</font>."),
              B("<b>Network:</b> a API que executa o algoritmo roda no servidor do Ponto Seguro montado "
                "no Packet Tracer."),
              B("<b>Agile e pitch:</b> a demonstração da rota mudando com o orçamento é o momento central "
                "do pitch."),
              PageBreak()]

    # ---------------- Página 3: modelagem ----------------
    story += [P("2. Modelagem", titulo),
              P("<b>Estrutura escolhida: grafo em lista de adjacência.</b> As esquinas são nós e os "
                "trechos de rua são arestas nos dois sentidos (a pé não há contramão). A lista de adjacência "
                "(<font face='Consolas'>grafo.adj[u]</font> = trechos que saem de <i>u</i>) ocupa "
                "O(V + E) e percorre só os vizinhos reais. Uma matriz de adjacência gastaria O(V²) com uma "
                "malha viária esparsa, em que cada esquina tem 2 a 4 vizinhos. Cada aresta guarda dois pesos:"),
              B("<b>distância</b>, discretizada em passos de 10 m (arredondada para cima, mínimo 1 passo);"),
              B("<b>risco = comprimento × densidade de risco</b>, isto é, a exposição. Andar 300 m numa "
                "rua escura pesa mais que andar 30 m nela."),
              P("A densidade de risco (por metro) combina os fatores do motor de risco do Vagalume. "
                "Os pesos p, q e r valem 1 à noite e são menores de dia. Há um mínimo de 0,02, então "
                "todo trecho tem risco > 0:", corpo),
              P("dens = (0,05 + 0,40·ocorr/10·p + 0,30·(1−ilum)·q + 0,25·reports/8·r + 0,10·acid/5)<br/>"
                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;× (1 − 0,5·movimento)", formula),
              P("<b>Tabela da DP:</b> uma matriz <font face='Consolas'>dp[v][d]</font> de V × (D + 1), "
                "com D = passos mínimos + B/10. Ela guarda o menor risco para chegar à esquina <i>v</i> "
                "andando exatamente <i>d</i> passos. Uma segunda matriz, "
                "<font face='Consolas'>pai[v][d]</font>, guarda de onde veio cada valor, para "
                "reconstruir a rota."),
              P("Fonte dos dados", sub),
              tabela([("Dado", "Origem", "Situação"),
                      ("Ruas, esquinas e comprimentos", "OpenStreetMap (Paulista e Bela Vista)",
                       "Real, simplificado em grade 5 × 5"),
                      ("Ocorrências por trecho", "Formato SSP-SP; base de Data Science", "Simulado"),
                      ("Iluminação, movimento e acidentes", "Prefeitura de SP, OSM e CET", "Simulado"),
                      ("Reports da comunidade", "Usuários do app", "Simulado"),
                      ("10 Pontos Seguros e horários", "Rede de comércios parceiros", "Simulado")],
                     [5.2 * cm, 6.4 * cm, W - 11.6 * cm]),
              Spacer(1, 6),
              P("Nenhum dado pessoal real é usado, conforme os combinados da GS.", legenda),
              Spacer(1, 4),
              imagem(mapa, W * 0.86),
              P("Figura 1. Grafo do piloto: 25 esquinas e 40 trechos. Quanto mais vermelho, maior o risco "
                "às 23h. As linhas são as rotas calculadas para orçamentos de 0, 200 e 500 m.", legenda),
              PageBreak()]

    # ---------------- Página 4: algoritmo ----------------
    trecho, l_ini, l_fim = trecho_do_codigo("# 3) Tabela dp[v][d]", "# 6) Reconstrução")
    story += [P("3. Algoritmo", titulo),
              P("dp[origem][0] = 0  ;  dp[v][0] = ∞ para v ≠ origem<br/>"
                "dp[v][d] = min sobre trechos (u→v) de  dp[u][d − w(u,v)] + risco(u,v)<br/>"
                "resposta = min dp[destino][d]  para  d ≤ D", formula),
              P(f"<b>A ideia central no código</b> (<font face='Consolas'>rota_dp.py</font>, função "
                f"<font face='Consolas'>rota_mais_segura</font>, linhas {l_ini}–{l_fim}):"),
              KeepTogether([Preformatted(trecho, codigo)]),
              Spacer(1, 4),
              P("<b>Correção.</b> (1) Todo trecho tem pelo menos 1 passo, então "
                "<font face='Consolas'>dp[v][d]</font> só depende de valores com <i>d</i> menor. "
                "Preenchendo a tabela em ordem crescente de <i>d</i>, cada valor usado já está pronto. "
                "(2) Todo trecho tem risco > 0. Uma rota que repete uma esquina pode perder o ciclo e fica "
                "mais curta e menos arriscada, então a solução ótima é sempre um caminho simples. "
                "(3) Os testes confirmam o resultado contra a força bruta em 30 grafos aleatórios e cobrem "
                "orçamento zero, destino inalcançável e origem igual ao destino."),
              P("<b>Complexidade.</b> Tempo <b>O(E · D)</b> e memória <b>O(V · D)</b>, mais um Dijkstra "
                "O(E log V) só para medir a distância mínima e dimensionar a tabela. No piloto, com "
                "E = 80 trechos e D = 130 passos, são cerca de 10 mil operações."),
              P("Exemplos de entrada e saída (B1 → B5, às 23h)", sub),
              tabela([("Orçamento B", "Rota", "Distância", "Risco", "Nota", "Alto risco"),
                      ("0 m", "R. Cincinato Braga (reto)", "800 m", "484", "39", "800 m"),
                      ("200 m", "Augusta → São Carlos do Pinhal → J. E. de Lima", "1000 m", "303", "70", "0 m"),
                      ("500 m", "Augusta → Av. Paulista → J. E. de Lima", "1280 m", "270", "79", "0 m"),
                      ("500 m, às 15h", "Augusta → São Carlos do Pinhal → J. E. de Lima", "1000 m", "166",
                       "83", "0 m")],
                     [2.4 * cm, 7.3 * cm, 1.8 * cm, 1.4 * cm, 1.2 * cm, W - 14.1 * cm]),
              Spacer(1, 5),
              Table([[imagem(bench, 8.4 * cm),
                      P("<b>Eficiência na prática.</b> Em grades de ruas cada vez maiores, com orçamento de "
                        "1000 m, a força bruta testa 1,5 milhão de caminhos e leva cerca de 2,5 s na grade "
                        "7 × 7. A DP resolve a mesma grade em cerca de 4 ms e chega à grade 10 × 10 em "
                        "cerca de 10 ms. <b>Extensão:</b> o Ponto Seguro mais próximo usa Bellman-Ford, "
                        "também uma DP sobre o número de trechos, O(V&nbsp;·&nbsp;E), e nunca sugere um ponto fechado.",
                        ParagraphStyle("lado", parent=corpo, fontSize=8.8, leading=11.8))]],
                    colWidths=[8.7 * cm, W - 8.7 * cm],
                    style=[("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)])]

    doc = SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.6 * cm,
                            title="Vagalume — Dynamic Programming", author=NOME_EQUIPE)
    doc.build(story, onFirstPage=capa, onLaterPages=rodape)
    print(f"PDF gerado: {SAIDA}")


if __name__ == "__main__":
    montar()
