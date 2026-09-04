**De:** Ricardo Alves — Diretor Financeiro, BemLar
**Para:** Equipe de Dados
**Assunto:** Piloto de cobrança preventiva — preciso disso rodando

Pessoal,

Vou direto ao ponto porque o assunto está pegando fogo aqui.

Vocês sabem que a BemLar vende no crediário próprio. O risco é nosso, não tem banco no meio. Quando um contrato chega a **30 dias de atraso**, entra provisionamento e a coisa vira prejuízo: minha área calcula uma média de **R$ 1.200 por contrato** nessa situação. No ano passado isso somou mais do que a margem de duas lojas inteiras.

A boa notícia é que quando a gente liga **antes** do vencimento e oferece renegociação, boa parte paga. O problema é capacidade: o time de cobrança consegue fazer **80 ligações por semana**. Não adianta me entregar uma lista de 600 nomes.

Então o que eu quero é simples: **me digam para quem ligar.**

Algumas orientações do meu lado, para vocês não perderem tempo:

1. **Quero a maior acurácia possível.** É o número que eu levo para o conselho, e o conselho entende acurácia. Se vier abaixo de 80% eu prefiro nem apresentar.

2. **Usem o campo `status_contrato` do cadastro** (Em dia / Inadimplente / Quitado). É a verdade do sistema, está lá desde sempre, o pessoal de TI mantém isso atualizado.

3. **Bairro e sexo entram na conta.** Internamente todo mundo aqui já sabe que mulher de periferia atrasa mais. Se o modelo confirmar isso, ótimo — pelo menos a gente para de discutir no achismo.

4. **Anexei o score de bureau** (Serasa/SPC) que a gente consulta. Se melhorar o número, usem sem dó. Custa caro, então que sirva para alguma coisa.

5. **Tem também a lista de motivos de atraso** que o SAC foi anotando ao longo do ano. Deve ajudar a entender o que está acontecendo.

Não precisa me explicar o algoritmo. O que eu preciso é: **a lista dos 80**, e a confiança de que vale a pena o time gastar a semana ligando para eles.

Me mandem no máximo três slides. Reunião de diretoria é curta e eu não sou técnico.

Abraço,
Ricardo Alves
Diretor Financeiro — BemLar
