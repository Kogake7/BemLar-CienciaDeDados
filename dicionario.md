# Dicionário de Dados — BemLar

Extrações feitas pelo time de sistemas a partir de três origens diferentes: o sistema de crediário, o CRM da loja e o atendimento (SAC). Não foram preparadas para análise.

**Convenções:** separador `;`, decimal `,`, datas em `dd/mm/aaaa`, encoding UTF-8.
**Chaves:** `id_contrato` liga contrato, parcelas, SAC e consultas de crédito. `id_cliente` liga contratos e compras. Um cliente pode ter mais de um contrato.
**Snapshot:** todos os arquivos foram extraídos em **15/03/2026**. Nada acontece depois dessa data.

---

## contratos.csv
Uma linha por contrato de crediário.

| Coluna | Descrição |
|---|---|
| `id_contrato` | Identificador do contrato |
| `id_cliente` | Identificador do cliente |
| `data_venda` | Data em que a venda foi fechada |
| `loja` | Loja onde a venda ocorreu |
| `canal_venda` | Loja física, Televendas ou Site |
| `valor_total` | Valor total financiado (R$) |
| `n_parcelas` | Quantidade de parcelas contratadas |
| `valor_parcela` | Valor de cada parcela (R$) |
| `bairro` | Bairro do endereço do cliente, como digitado no cadastro |
| `sexo` | Sexo declarado no cadastro |
| `idade` | Idade do cliente, calculada a partir da data de nascimento do cadastro |
| `renda_declarada` | Renda mensal informada pelo cliente na aprovação (R$) |
| `status_contrato` | Situação do contrato no sistema no momento da extração: Em dia, Inadimplente ou Quitado |
| `data_snapshot` | Data da extração |

---

## pagamentos.csv
Uma linha por parcela **já vencida** até a data do snapshot. Parcelas com vencimento futuro não aparecem.

| Coluna | Descrição |
|---|---|
| `id_contrato` | Identificador do contrato |
| `n_parcela` | Número da parcela dentro do contrato (1, 2, 3…) |
| `data_vencimento` | Data de vencimento da parcela |
| `data_pagamento` | Data em que a parcela foi paga. **Vazia se ainda não foi paga** |
| `valor_parcela` | Valor da parcela (R$) |

---

## compras.csv
Outras compras do cliente na rede, à vista ou em outro contrato. Ligada por `id_cliente`, não por contrato.

| Coluna | Descrição |
|---|---|
| `id_cliente` | Identificador do cliente |
| `data_compra` | Data da compra |
| `valor` | Valor da compra (R$) |
| `categoria` | Categoria do produto |

---

## ocorrencias_sac.csv
Uma linha por atendimento registrado no SAC.

| Coluna | Descrição |
|---|---|
| `id_contrato` | Contrato ao qual o atendimento se refere |
| `data_ocorrencia` | Data do atendimento |
| `tipo_ocorrencia` | Motivo do contato (segunda via de boleto, reclamação de entrega, negociação de dívida, etc.) |
| `canal` | Canal do atendimento |

---

## score_bureau.csv
Consultas ao birô de crédito (Serasa/SPC) feitas pela BemLar sobre o cliente. Uma linha por consulta — **o mesmo contrato pode ter mais de uma**, feitas em momentos diferentes.

| Coluna | Descrição |
|---|---|
| `id_contrato` | Contrato ao qual a consulta se refere |
| `data_consulta` | Dia em que a consulta foi feita ao birô |
| `score` | Score retornado pelo birô, de 0 a 1000. Quanto maior, menor o risco segundo o birô |
| `motivo_consulta` | Por que a consulta foi feita (aprovação de crediário, revisão de carteira) |

---

## motivos_atraso.csv
Anotações em texto livre feitas pelos atendentes do SAC quando o cliente explica o motivo do atraso.

| Coluna | Descrição |
|---|---|
| `motivo_relatado` | Texto digitado pelo atendente |
| `data_registro` | Data da anotação |

---

## Como identificar a parcela de referência

O piloto simula uma ligação preventiva: o modelo roda **antes** de o atraso acontecer, e precisamos poder verificar depois se o atraso aconteceu de fato.

- A **parcela de referência** de um contrato é a **última parcela cujo vencimento é anterior ou igual a `data_snapshot` menos 30 dias** (ou seja, vencimento até **13/02/2026**). Só nessas parcelas é possível observar o desfecho de 30 dias — nas mais recentes, o prazo ainda não fechou.
- A **data de referência** é o **vencimento da parcela de referência menos 7 dias** — o momento em que a cobrança faria a ligação.

Todo contrato do arquivo tem pelo menos uma parcela elegível.
