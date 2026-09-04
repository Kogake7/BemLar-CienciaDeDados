"""Gera um dashboard 16:9 a partir dos resultados salvos no notebook e dos CSVs.

Executar: python dashboard_bemlar.py
Saidas: dashboard_bemlar.png e dashboard_bemlar.svg (mesma pagina, tres graficos).
Nao treina modelos nem modifica o notebook.
"""
import json
from html.parser import HTMLParser
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = []
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = []
        elif tag in ('th', 'td'):
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('th', 'td') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        elif tag == 'tr' and self.row:
            self.rows.append(self.row)


nb = json.loads((ROOT / 'enunciado.ipynb').read_text(encoding='utf-8'))
tables = []
selected = None
for cell in nb['cells']:
    for output in cell.get('outputs', []):
        stream = ''.join(output.get('text', ''))
        for line in stream.splitlines():
            prefix = 'Modelo escolhido somente na validação temporal:'
            if line.startswith(prefix):
                selected = line.split(prefix, 1)[1].strip()
        html = ''.join(output.get('data', {}).get('text/html', ''))
        if '<table' in html:
            parser = TableParser()
            parser.feed(html)
            if parser.rows:
                tables.append(pd.DataFrame(parser.rows[1:], columns=parser.rows[0]))

assert selected is not None, 'Execute o notebook completo antes de gerar o dashboard.'
results = next(t for t in tables if {'candidato', 'n_teste', 'TP_80', 'FP_80', 'FN_80', 'acuracia_05'}.issubset(t.columns))
results = results.set_index('candidato')
for column in ['n_teste', 'positivos', 'TP_80', 'FP_80', 'FN_80', 'acuracia_05']:
    results[column] = pd.to_numeric(results[column], errors='coerce')

features = pd.read_csv(ROOT / 'features.csv', sep=';', decimal=',')
queue = pd.read_csv(ROOT / 'fila_80.csv', sep=';', decimal=',')
assert len(queue) == 80 and queue['id_contrato'].is_unique
assert queue['probabilidade'].is_monotonic_decreasing
row = results.loc[selected]
tp = int(queue.merge(features[['id_contrato', 'inadimplente_30d']], validate='one_to_one')['inadimplente_30d'].sum())
assert tp == int(row['TP_80'])
fp, fn = int(row['FP_80']), int(row['FN_80'])
positives, n_test = int(row['positivos']), int(row['n_teste'])
assert tp + fn == positives and tp + fp == 80
precision, recall = tp / 80, tp / positives
accuracy = float(row['acuracia_05'])
baseline_value = int(results.loc['Maior valor de parcela', 'TP_80'])
baseline_random = int(results.loc['Fila aleatória', 'TP_80'])
gain = tp - baseline_value
assert gain > 0 and tp > baseline_random

features['data_referencia'] = pd.to_datetime(features['data_referencia'], format='%d/%m/%Y')
daily = features.groupby('data_referencia').size().sort_index()
before_day = daily.cumsum().shift(fill_value=0)
valid = before_day[(before_day > 0) & (before_day < len(features))]
cut = (valid - 0.75 * len(features)).abs().idxmin()
test = features.loc[features['data_referencia'].ge(cut)]
assert len(test) == n_test and test['inadimplente_30d'].sum() == positives
assert set(queue['id_contrato']).issubset(test['id_contrato'])


def pct(value):
    return f'{value * 100:.1f}%'.replace('.', ',')


BG = '#F3F3ED'
PAPER = '#FFFFFF'
INK = '#17373B'
MUTED = '#52696C'
TEAL = '#147C72'
PALE = '#DDE8E3'
GRAY = '#8FABA9'
LINE = '#D2DDDA'
AMBER = '#9D501F'

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'text.color': INK, 'axes.labelcolor': MUTED,
                     'xtick.color': MUTED, 'ytick.color': INK,
                     'svg.fonttype': 'none'})
fig = plt.figure(figsize=(16, 9), facecolor=BG)


def text(x, y, value, size=11, weight='normal', color=INK, **kwargs):
    return fig.text(x, y, value, fontsize=size, fontweight=weight, color=color, **kwargs)


def box(x, y, width, height, fill=PAPER, radius=0.012):
    patch = FancyBboxPatch((x, y), width, height, boxstyle=f'round,pad=0,rounding_size={radius}',
                          transform=fig.transFigure, facecolor=fill, edgecolor='none', zorder=-1)
    fig.add_artist(patch)


text(.04, .948, 'BEMLAR  /  COBRANÇA PREVENTIVA', 11, 'bold', TEAL)
text(.04, .888, 'Uma fila melhor para 80 ligações', 29, 'bold')
model_name = {'Arvore': 'Árvore de decisão', 'Logistica': 'Regressão logística', 'Floresta': 'Floresta aleatória'}[selected.split(' | ')[0]]
variant_name = 'com bureau' if selected.endswith('com_bureau') else 'sem bureau'
period = f'{cut:%d/%m} a {test.data_referencia.max():%d/%m/%Y}'
text(.04, .85, f'{model_name} {variant_name}  •  Teste temporal: {n_test} contratos  •  {period}', 11, color=MUTED)

stats = [
    ('ACERTOS NA FILA', pct(precision), f'{tp} inadimplentes entre 80 selecionados', TEAL),
    ('GANHO SOBRE A MAIOR PARCELA', f'+{gain} contratos', 'Na mesma capacidade de 80 ligações', TEAL),
    ('ACURÁCIA GLOBAL', pct(accuracy), 'Meta >80% não atingida · limiar 0,50', AMBER),
    ('EXPOSIÇÃO ADICIONAL IDENTIFICADA', f'R$ {gain * 1200 / 1000:.1f} mil'.replace('.', ','), 'Comparação com a fila por maior parcela', TEAL),
]
for index, (label, value, detail, color) in enumerate(stats):
    x = .04 + index * .233
    box(x, .695, .221, .125)
    text(x + .014, .788, label, 8.5, 'bold', MUTED)
    text(x + .014, .738, value, 25, 'bold', color)
    text(x + .014, .715, detail, 8.6, color=MUTED)

# Grafico 1: acertos entre os mesmos 80 selecionados.
box(.04, .215, .32, .455)
text(.055, .637, '01  /  QUALIDADE DA FILA', 10, 'bold', TEAL)
text(.055, .603, 'Mais acertos com a mesma capacidade', 12, 'bold')
ax1 = fig.add_axes([.062, .35, .27, .225], facecolor=PAPER)
counts = [tp, baseline_value, baseline_random]
names = ['Modelo escolhido', 'Maior parcela', 'Aleatória · semente 42']
for index, (name, count) in enumerate(zip(names, counts)):
    y = 2 - index
    ax1.text(0, y + .30, name, fontsize=10, color=INK)
    ax1.text(80, y + .30, f'{count}/80 · {pct(count / 80)}', ha='right', fontsize=10,
             color=INK, fontweight='bold')
    ax1.barh(y, 80, height=.23, color=PALE)
    ax1.barh(y, count, height=.23, color=TEAL if index == 0 else GRAY)
ax1.set(xlim=(0, 80), ylim=(-.4, 2.6), xticks=[0, 20, 40, 60, 80], yticks=[])
ax1.set_xlabel('Inadimplentes entre os 80 selecionados', fontsize=9, labelpad=9)
ax1.tick_params(axis='x', labelsize=9, length=0)
for spine in ax1.spines.values():
    spine.set_visible(False)
text(.055, .269, f'{fp} contatos da fila pagaram até D+30.', 10, 'bold')
text(.055, .242, 'Cada contato consome capacidade da equipe.', 9, color=MUTED)

# Grafico 2: parte do total de inadimplentes coberta pela fila.
box(.375, .215, .245, .455)
text(.39, .637, '02  /  ALCANCE DO RISCO', 10, 'bold', TEAL)
text(.39, .603, 'A fila alcança uma parte do risco', 12, 'bold')
ax2 = fig.add_axes([.401, .347, .19, .235], facecolor=PAPER)
ax2.pie([tp, fn], colors=[TEAL, PALE], startangle=90, counterclock=False,
        wedgeprops={'width': .24, 'edgecolor': PAPER, 'linewidth': 2})
ax2.text(0, .04, pct(recall), ha='center', va='center', fontsize=26, fontweight='bold', color=INK)
ax2.text(0, -.24, 'recall@80', ha='center', va='center', fontsize=10, color=MUTED)
ax2.set_aspect('equal')
text(.393, .33, f'{tp}', 18, 'bold', TEAL)
text(.428, .333, 'alcançados', 10)
text(.393, .295, f'{fn}', 18, 'bold', MUTED)
text(.428, .298, 'fora da fila', 10)
text(.39, .247, f'{positives} inadimplentes no teste temporal.', 9, color=MUTED)

# Grafico 3: mesmo corte para cada par com/sem bureau.
box(.635, .215, .325, .455)
text(.65, .637, '03  /  CONTRIBUIÇÃO DO BUREAU', 10, 'bold', TEAL)
text(.65, .603, 'O score traz ganho pequeno neste teste', 12, 'bold')
ax3 = fig.add_axes([.661, .35, .272, .223], facecolor=PAPER)
family_labels = [('Arvore', 'Árvore*'), ('Logistica', 'Reg. logística'), ('Floresta', 'Floresta')]
for index, (family, label) in enumerate(family_labels):
    y = 2 - index
    with_score = int(results.loc[f'{family} | com_bureau', 'TP_80'])
    without_score = int(results.loc[f'{family} | sem_bureau', 'TP_80'])
    ax3.text(0, y + .43, label, fontsize=10, color=INK)
    ax3.barh(y + .13, without_score, height=.18, color=GRAY)
    ax3.barh(y - .10, with_score, height=.18, color=TEAL)
    ax3.text(without_score + 1, y + .13, str(without_score), va='center', fontsize=10, color=INK)
    ax3.text(with_score + 1, y - .10, str(with_score), va='center', fontsize=10, color=INK, fontweight='bold')
ax3.set(xlim=(0, 80), ylim=(-.4, 2.6), xticks=[0, 20, 40, 60, 80], yticks=[])
ax3.set_xlabel('Inadimplentes entre os 80 selecionados', fontsize=9, labelpad=9)
ax3.tick_params(axis='x', labelsize=9, length=0)
for spine in ax3.spines.values():
    spine.set_visible(False)
fig.add_artist(plt.Line2D([.65, .663], [.287, .287], color=GRAY, linewidth=5, transform=fig.transFigure))
text(.669, .282, 'Sem bureau', 9)
fig.add_artist(plt.Line2D([.774, .787], [.287, .287], color=TEAL, linewidth=5, transform=fig.transFigure))
text(.793, .282, 'Com bureau', 9)
text(.65, .249, '*Árvore escolhida na validação, antes do teste.', 9, color=MUTED)

box(.04, .096, .92, .096, fill=INK)
text(.057, .155, 'RECOMENDAÇÃO', 9, 'bold', '#BAD9D1')
text(.057, .12, 'Ligar com ressalva', 19, 'bold', PAPER)
text(.287, .151, 'Piloto prospectivo com grupo de controle e medição do efeito das ligações.', 11, color=PAPER)
text(.287, .122, f'Exposição identificada: R$ {tp * 1200:,.0f}'.replace(',', '.') + '  •  Não representa economia comprovada.',
     10, color='#D3E7E1')
text(.04, .06, 'Alvo: parcela não paga até D+30. Avaliação histórica; o lote de teste não equivale a uma semana de operação.',
     9, color=MUTED)
text(.04, .036, 'Fontes: enunciado.ipynb, features.csv e fila_80.csv. Exposição estimada a R$ 1.200 por contrato.',
     9, color=MUTED)

assert len(fig.axes) == 3, 'O dashboard deve conter no máximo três gráficos.'
fig.savefig(ROOT / 'dashboard_bemlar.png', dpi=200, facecolor=BG)
fig.savefig(ROOT / 'dashboard_bemlar.svg', facecolor=BG)
plt.close(fig)
print('Dashboard gerado: dashboard_bemlar.png e dashboard_bemlar.svg')
print(f'{n_test} contratos no teste; {tp}/80 acertos; recall {pct(recall)}; três gráficos.')
