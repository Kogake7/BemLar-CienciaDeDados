# Avaliação Final — Piloto de Cobrança Preventiva (BemLar)

**Entrega:** segunda-feira, 7h00
**Formato:** individual
**Peso:** avaliação final da disciplina

---

## 1. O contexto

A **BemLar** é uma rede de móveis e eletrodomésticos. Ela vende no **crediário próprio** — o cliente parcela direto na loja, sem banco no meio. Isso significa que o risco do parcelamento é da BemLar, não de terceiros.

O diretor financeiro, **Ricardo Alves**, procurou o time de dados com um pedido urgente. Leia o e-mail dele em `00_email_financeiro.md` antes de qualquer outra coisa — ele é a especificação do problema, com tudo que uma especificação real tem de bom e de ruim.

Os números que sustentam o caso:

- Um contrato que chega a **30 dias de atraso** custa, em média, **R$ 1.200** (provisionamento + perda).
- Ligar antes do vencimento e renegociar custa pouco.
- A equipe de cobrança consegue fazer **80 ligações por semana**. Não 81.

Ou seja: você não vai entregar uma classificação. Vai entregar **uma fila de 80 nomes**, e alguém vai ligar para eles na segunda-feira.

---

## 2. O que você recebe

| Arquivo | O que é |
|---|---|
| `00_email_financeiro.md` | O e-mail do Ricardo |
| `dicionario.md` | Dicionário das colunas |
| `contratos.csv` | Cadastro do contrato e do cliente |
| `pagamentos.csv` | Histórico de parcelas |
| `compras.csv` | Outras compras do cliente na rede |
| `ocorrencias_sac.csv` | Registros de atendimento (reclamações, 2ª via de boleto, etc.) |
| `score_bureau.csv` | Score de bureau de crédito, com a data em que foi consultado |
| `motivos_atraso.csv` | Anotações do SAC sobre motivos de atraso |
| `enunciado.ipynb` | Notebook de apoio, com a função `filtra_por_data` já pronta |

> **Sobre os dados:** são extrações de sistemas diferentes, feitas às pressas. Não foram preparadas para análise. Trate cada arquivo como algo que precisa ser verificado antes de ser usado — não como algo que já está certo.

---

## 3. A definição do alvo

Esta parte **não é para você descobrir**, é para você implementar corretamente:

```
inadimplente_30d = 1  se a parcela de referência não foi paga até D+30
inadimplente_30d = 0  caso contrário
```

Consequências que você precisa respeitar:

- Contrato **quitado** não é 1.
- Atraso de **2 dias** não é 1.
- A regra vale para **todo contrato**, não só para os que já quebraram.

### Data de referência

O modelo simula uma **ligação preventiva** — ele roda *antes* do problema acontecer. Portanto:

- Para contratos que vieram a atrasar: a data de referência é **o vencimento da parcela de referência menos 7 dias**.
- Para contratos em dia: a data do **snapshot** do arquivo.

**Nenhum evento posterior à data de referência pode entrar em nenhuma feature.** A função `filtra_por_data` no notebook faz esse recorte — é a mesma lógica que vocês usaram na Aula 3. Use-a em todas as bases de eventos.

---

## 4. A pergunta que você deve fazer a cada coluna

Antes de colocar qualquer variável no modelo, responda três perguntas — as mesmas da auditoria da Aula 4:

1. **Essa informação existiria no momento em que a previsão seria feita?** Se a resposta for não, ou "depende", investigue antes de usar.
2. **É uma variável protegida ou sensível?** Nesse caso a decisão é ética, não métrica.
3. **Ela descreve comportamento ou só descreve quem a pessoa é?**

O Ricardo faz pedidos específicos no e-mail dele. Alguns desses pedidos você vai atender. Outros, não. **Cada recusa precisa estar escrita, com o motivo e — sempre que possível — com uma alternativa.** "Não dá" não é resposta profissional. "Não dá desse jeito; me mande X e dá" é.

---

## 5. Como o piloto será avaliado

A equipe faz 80 ligações. Portanto, a pergunta de negócio não é "o modelo acerta muito?", e sim:

> **Dos 80 contratos que eu mandei a cobrança ligar, quantos de fato iam atrasar?**

Você deve reportar, no mínimo:

- **Precision no corte de 80** — quantos da fila eram realmente inadimplentes.
- **Recall no corte de 80** — quantos inadimplentes reais a fila deixou de fora.
- A comparação com pelo menos **uma fila-base burra** (aleatória, ou ordenada por valor da parcela). Sem essa comparação, o número da sua fila não significa nada.

**Dica de implementação:** ordene o conjunto de teste pela probabilidade prevista (`predict_proba`), corte nos 80 primeiros, e calcule as métricas nesse recorte — não no threshold padrão de 0,50.

Traduza tudo para a linguagem do Ricardo:

- **Falso positivo** é o que para o Ricardo?.
- **Falso negativo** é o que para o Ricardo?.

E escolha um lado: você prefere **precision** (não incomodar quem ia pagar) ou **recall** (não deixar prejuízo passar)? Não existe resposta certa aqui — existe resposta **justificada**.

---

## 6. Modelagem

- Treino e teste.
- Faça também um **split temporal** (mais antigos treinam, mais recentes testam) e compare com o aleatório. Comente a diferença.
- Pelo menos **dois modelos**, sendo um deles um baseline simples.
- Reporte **importância de variáveis** — e cuidado ao interpretá-la: importância não é causa.

Organize o notebook seguindo as fases do **CRISP-DM**, com as fases nomeadas. Se você voltou de Modelagem para Preparação dos Dados em algum momento — o que é normal e esperado — **registre isso**. Um projeto que segue em linha reta do começo ao fim geralmente está escondendo alguma coisa.

---

## 7. O que entregar

Cinco arquivos, em um arquivo .zip:

### 7.1 `features.csv`
Uma linha por contrato, com o alvo e as features. Respeitando o corte temporal.

### 7.2 `modelo.ipynb`
Precisa **rodar de ponta a ponta**, sem edição manual, a partir dos CSVs originais. Notebook que só funciona na sua máquina não é entregável.

A construção das features deve estar isolada em uma função:

```python
def construir_features(caminho_dados, datas_referencia):
    ...
    return df
```

### 7.3 `fila_80.csv`
Os 80 contratos que você recomenda para a cobrança ligar. Colunas: `id_contrato`, `probabilidade`, ordenados do maior risco para o menor.

### 7.4 `decisoes.md`
O documento mais importante da entrega depois do deck. Deve conter:

- **Definição do alvo** e por que ela é essa.
- **O que entrou** no modelo e por quê.
- **O que ficou de fora** e por quê — incluindo cada pedido do Ricardo que você recusou, com alternativa.
- **Model card**: qual dado gerou este modelo, quais features usa, para que serve, e quais são os limites conhecidos de uso.

### 7.5 `apresentacao.pptx` — exatamente 3 slides

A plateia é o **Ricardo**, não a banca. Sem jargão, sem "fizemos um `groupby`", sem tabela de 40 linhas. Um gráfico por slide.

**Slide 1 — O problema em R$ e o que estamos prevendo.**
Manchete em dinheiro. O que é inadimplência neste projeto e por que a definição é essa. Se algum pressuposto do Ricardo estiver errado, é aqui que você o corrige — com evidência e sem soberba.

**Slide 2 — O perfil do contrato de risco, e o que ficou de fora.**
Dois sinais que separam bem, ordenados por poder de separação. Pelo menos **um achado negativo** (algo que você testou e não explica nada — isso poupa a empresa de uma política inútil). E as recusas, uma linha cada, com alternativa.

**Slide 3 — O piloto funciona? E a recomendação.**
Precision e recall no corte de 80, contra a fila-base. FP e FN traduzidos em reais. E uma decisão explícita: **liga / liga com ressalva / não liga ainda** — mais o que faltaria para melhorar.

---


## 8. Checklist antes de enviar

- [ ] Meu alvo segue a regra dos 30 dias, e eu consigo explicá-la em uma frase.
- [ ] Nenhuma feature usa evento posterior à data de referência.
- [ ] Verifiquei os **valores** das colunas categóricas, não só os nomes das colunas.
- [ ] Toda base que agreguei virou uma linha por contrato, e ausência de evento virou o valor certo.
- [ ] Comparei minha fila com uma fila-base.
- [ ] Cada pedido do e-mail do Ricardo foi respondido: atendido ou recusado, com motivo.
- [ ] O notebook roda do zero, em outra máquina, a partir dos CSVs originais.
- [ ] O slide 3 não diz "acurácia de 81%, piloto aprovado".

---

## 9. Regras

- Trabalho individual. Discutir o problema com colegas é permitido; entregar o mesmo código, não.
- Uso de IA é permitido, desde que você consiga **explicar e defender cada decisão** da entrega. Haverá defesa oral, se necessário.
- Entrega até **segunda, 7h00**. Depois disso, não há entrega.
