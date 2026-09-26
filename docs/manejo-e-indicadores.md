# Manejo, produção e indicadores — regras de negócio

Este documento registra **o que o sistema faz e por quê** nas áreas que vieram da
planilha da granja: raças, peso, genealogia, reprodução, produção de leite, ficha da
vaca e indicadores zootécnicos. Serve para o entendimento de quem chega e, sobretudo,
para a **validação com o usuário final**: cada regra abaixo é uma decisão que pode ser
trocada. A seção [Premissas a validar](#premissas-a-validar-com-o-usuário-final) lista
o que mais vale confirmar; a coluna "Onde mudar" diz em que arquivo cada regra vive.

Convenções gerais (acesso por propriedade, papéis, chaves `<tabela>_id`) estão no
[README](../README.md) e no [CLAUDE.md](../CLAUDE.md).

## Visão geral

| Área | O que guarda | Escopo | Menu |
|---|---|---|---|
| Raças | Cadastro de raças; o animal pode ou não ter uma | Referência comum | Cadastros → Raças |
| Peso ideal por raça | Peso ideal por raça e idade (meses), com observações | Referência comum | Cadastros → Peso ideal por raça |
| Pesagens | Peso real de um animal numa data | Propriedade | Nesta propriedade → Pesagens |
| Peso x ideal | Comparativo entre o peso real e o ideal | Propriedade | Nesta propriedade → Peso x ideal |
| Reprodutores | Touros e vacas da genealogia (pais, avós…) | Referência comum | Cadastros → Reprodutores |
| Reprodução | Histórico reprodutivo da vaca (eventos) | Propriedade | Nesta propriedade → Reprodução |
| Produção de leite | Litros por animal e data | Propriedade | Nesta propriedade → Produção de leite |
| Ficha da vaca | Tudo da vaca numa tela, com situação e prazos calculados | Propriedade | Animais → ícone da ficha |
| Indicadores | DEL, fertilidade, intervalo entre partos, idades, roda | Propriedade | Nesta propriedade → Indicadores |

**Referência comum** é visível a todos e quem tem perfil de escrita altera para todas as
propriedades. **Propriedade** só aparece dentro da propriedade aberta: cada lançamento
guarda o `propriedade_id` e a API confere que o animal pertence a ela
(`conferir_animal_da_propriedade` em `app/acesso.py`).

Migrations desta parte: `0007` raças · `0008` pesagens e peso ideal · `0009` reprodução e
produção · `0010` `produz_leite` no tipo de animal · `0011` metas dos indicadores.

## Animal

Campos acrescentados ao animal: `raca_id` (opcional), `data_nascimento`,
`peso_nascimento_kg`, `pai_id` e `mae_id` (apontam para **reprodutores**, não para outro
animal) e `observacao`.

- **Por que pai e mãe são "reprodutores" e não animais:** touros de central e ascendentes
  quase nunca existiram na propriedade. Um cadastro geral evita criar "animais fantasmas"
  que apareceriam nas listas e nos indicadores.
- O pai tem de ser reprodutor **macho** e a mãe **fêmea** (a API confere).
- A data de nascimento é necessária para a idade em meses (peso ideal, idade ao 1º parto,
  idade de cobertura).

## Reprodutores e genealogia

`reprodutores`: nome, registro/código da central, sexo (M/F), raça, empresa (central de
sêmen), `pai_id` e `mae_id` (para a própria tabela).

Avós e bisavós **não têm coluna**: saem da cadeia. Na ficha:

| Campo da ficha | De onde vem |
|---|---|
| Mãe / Pai | `animal.mae` / `animal.pai` |
| Avô materno | pai da mãe |
| Bisavô materno | pai do avô materno |
| Avô paterno | pai do pai |
| Bisavô paterno | pai do avô paterno |

Só aparece até onde a cadeia foi preenchida. Um reprodutor não pode ser pai/mãe de si
mesmo. Limitação conhecida: uma vaca da propriedade que é mãe de outra precisa ter um
registro também em Reprodutores (fica duplicada).

## Peso: pesagens e peso ideal

- **Peso ideal por raça** (`padroes_peso`): uma linha por raça e idade em meses, com peso em
  kg e observações. Não aceita duas linhas para a mesma raça e idade.
- **Pesagem** (`pesagens`): animal, data, peso real (kg), observações. Um animal só tem uma
  pesagem por data.
- **Idade na pesagem** = meses **completos** entre o nascimento e a data (se o dia do mês da
  pesagem é menor que o do nascimento, ainda não completou o mês).
- **Comparativo (Peso x ideal):** para cada pesagem, busca o peso ideal da raça do animal na
  idade em meses **exata** daquele dia.
  - Diferença = peso real − peso ideal.
  - **GMD real** = (peso − peso da pesagem anterior) ÷ dias entre elas.
  - **GMD ideal** = (ideal de agora − ideal da pesagem anterior) ÷ dias, quando os dois
    existem.
  - Sem raça, sem data de nascimento ou sem padrão para aquele mês, os campos ficam vazios.
- Onde mudar: `app/routers/pesagens.py`.

## Reprodução: eventos

`eventos_reprodutivos` é uma lista única por vaca (como o "HISTÓRICO" da planilha):
animal, data, tipo do evento, e campos opcionais conforme o tipo.

| Tipo (código) | Uso | Campos extras |
|---|---|---|
| Inseminação (`INSEMINACAO`) | cobertura por inseminação | touro, valor do sêmen |
| IATF (`IATF`) | inseminação em tempo fixo | touro, valor do sêmen |
| Retorno de cio (`RETORNO_CIO`) | a vaca voltou ao cio: não pegou | — |
| Prenhez confirmada (`PRENHEZ`) | diagnóstico positivo | — |
| Secagem (`SECAGEM`) | fim da lactação | — |
| Parto (`PARTO`) | nascimento da cria | sexo da cria, cria (se cadastrada) |
| Aborto (`ABORTO`) | perda da gestação | — |
| Descarte (`DESCARTE`) | a vaca saiu do rebanho | — |

O **código** é o que o sistema usa nos cálculos; a descrição é só o texto da tela. Por isso
os tipos vêm da migration e não têm cadastro livre. O touro de uma inseminação tem de ser
um reprodutor macho.

## Produção de leite

- Só é lançada para animais de um **tipo que produz leite** (`tipos_animal.produz_leite`).
  Hoje só "Vacas"; um tipo novo produtor (ex.: cabras) só precisa da caixa marcada. A tela
  só oferece esses tipos e a API recusa os demais. Se só um tipo produz, o formulário já
  abre com ele escolhido.
- **Um lançamento por animal e data.** Pode ser diário, ou o **total do mês** lançado na
  data do fechamento, com `dias_referentes` = quantidade de dias que o lançamento cobre
  (1 = diário; 30 = mês). Litros por dia = litros ÷ dias.
- **Acumulado da lactação** (na ficha): soma dos litros desde o último parto, e **zera a
  cada parto**.
- Onde mudar: `app/routers/producao.py`.

## Ficha da vaca

Tela só de leitura (`/animais/:id/ficha`). Só entram eventos, produção e pesagens lançados
na propriedade aberta. Nada abaixo é gravado: tudo é calculado (`app/ficha.py`).

**Situação** — pelo **último** evento (desempate por ordem de lançamento):

| Último evento | Situação |
|---|---|
| nenhum, parto, aborto ou retorno de cio | Vazia |
| inseminação ou IATF | Inseminada |
| prenhez confirmada | Prenhe |
| secagem | Seca |
| descarte | Descartada |

**DEL (dias em lactação)** = hoje − data do último parto, **enquanto a vaca lacta**: some se
houve secagem ou descarte depois desse parto.

**Prazos** — a partir da **última inseminação/IATF**:

| Prazo | Regra | Aparece quando |
|---|---|---|
| Retorno de cio | inseminação + **21** dias | situação Inseminada |
| Provável parto | inseminação + **282** dias | Inseminada, Prenhe ou Seca |
| Secagem | provável parto − **60** dias | Inseminada ou Prenhe |

O 282 foi tirado do exemplo da planilha (inseminação em 22/05/2020 → parto em 28/02/2021);
o valor mais comum na literatura para Jersey é 279.

**Doses até a confirmação** = inseminações desde o último parto ou aborto, até a prenhez
confirmada (ou todas, se ainda não confirmou). **Partos** são numerados por ordem de data.
**Média da lactação atual** = litros ÷ dias cobertos desde o último parto.

Onde mudar: prazos em `app/ficha.py` (`DIAS_RETORNO_CIO`, `DIAS_GESTACAO`,
`DIAS_SECA_ANTES_DO_PARTO`).

## Indicadores zootécnicos

Quem entra nas contas é a **"vaca"**: animal **ativo** da propriedade cujo tipo **produz leite**
(exceto a idade de cobertura, que olha todos os animais). Os eventos são os lançados na
propriedade aberta. As datas de período aplicam-se ao **evento medido** (a inseminação, o
parto…). Padrão de período: últimos 12 meses; atalhos: 90 dias, 6 meses, 12 meses, este ano,
ano passado ou datas livres. Onde mudar: `app/calculo_indicadores.py` e
`app/routers/indicadores.py`.

### Resultado de uma inseminação

Olha o que veio **depois** dela, na ordem:

| O que veio depois | Resultado |
|---|---|
| prenhez confirmada, parto ou secagem | Concebeu |
| retorno de cio, nova inseminação/IATF ou aborto | Não concebeu |
| descarte, ou nada | Sem resultado (fora das taxas) |

### Fertilidade

| Indicador | Fórmula | Meta padrão |
|---|---|---|
| Taxa de concepção | prenhezes ÷ inseminações **com resultado**, das feitas no período | 40 % |
| Serviço de concepção | inseminações com resultado ÷ prenhezes (doses por prenhez) | 2,5 |
| Taxa de serviço | por ciclo de 21 dias: vacas aptas inseminadas ÷ vacas aptas; soma dos ciclos do período | 60 % |
| Taxa de prenhez | taxa de serviço × taxa de concepção | 20 % |
| IATF | quantas inseminações foram IATF, e a taxa de concepção da IATF × convencional | — |

- **Vaca apta** num ciclo: já tem algum evento lançado antes do ciclo, está **Vazia** no início
  dele (não inseminada, prenhe, seca nem descartada) e passou o **período voluntário de espera**
  (padrão **50 dias**) desde o último parto.
- Só ciclos de 21 dias **inteiros** dentro do período entram; o último, incompleto, fica de fora.
  Período menor que 21 dias não tem taxa de serviço.

### Por vaca

| Indicador | Fórmula | Meta padrão |
|---|---|---|
| DEL | dias em lactação de cada vaca em lactação; média do rebanho | 160 dias |
| Intervalo entre partos | dias entre partos seguidos, dos partos do período; cada barra é a média da vaca, a média geral considera todos os intervalos | 395 dias (≈ 13 meses) |
| Idade ao 1º parto | do nascimento ao primeiro parto lançado, se ele cai no período | 24 meses |
| Idade de cobertura | do nascimento à primeira inseminação lançada (novilhas e vacas), se cai no período | 15 meses |

Nas idades, 1 mês = 30,4375 dias. As barras ficam vermelhas acima da meta (menos é melhor).
DEL não tem período: é a situação de hoje.

### Roda da reprodução

Quantas vacas estão hoje em cada situação (Vazia, Inseminada, Prenhe, Seca, Descartada), pela
mesma regra da ficha, e quantas estão em lactação.

### Metas

Cada propriedade pode ajustar as suas na própria tela do painel (quem tem perfil de escrita).
Ficam em `metas_indicadores` (propriedade + indicador → valor); sem linha vale o padrão do
sistema, em `METAS_PADRAO` (`app/routers/indicadores.py`). O período voluntário de espera
(`PERIODO_ESPERA`) é guardado do mesmo jeito.

## Premissas a validar com o usuário final

Decisões tomadas sem confirmação, em ordem de impacto nos números:

- [ ] **Gestação de 282 dias** (prazo do provável parto e da secagem). Jersey costuma ser 279.
      Deveria variar por raça?
- [ ] **Período voluntário de espera de 50 dias** para a vaca ser considerada apta.
- [ ] **Ciclo de 21 dias** na taxa de serviço e **retorno de cio em 21 dias**.
- [ ] **Metas padrão** (tabela acima): as usadas são valores típicos, não da granja.
- [ ] **Diagnóstico negativo:** hoje não existe evento "prenhez negativa"; a falha é deduzida do
      retorno de cio, de nova inseminação ou de aborto. Vale criar um evento próprio?
- [ ] **Situação "Vazia" após o parto:** a vaca recém-parida aparece como Vazia (a planilha usa
      o mesmo rótulo). Ela deveria aparecer como "Lactação" ou "Pós-parto" até o fim do período de
      espera?
- [ ] **Secagem calculada 60 dias antes do parto**, e só sugerida: não há alerta de prazo vencido.
- [ ] **DEL só das vacas em lactação:** vacas secas ou sem parto lançado ficam de fora da média
      (na planilha entravam como 0 e puxavam a média para baixo).
- [ ] **Idade ao 1º parto e de cobertura** usam o primeiro parto/inseminação **lançados**; se o
      histórico começou depois, o "primeiro" pode não ser o verdadeiro.
- [ ] **Só entram vacas com algum evento lançado** na taxa de serviço. Vaca sem histórico não é
      apta, para não inflar o denominador.
- [ ] **Um período de taxas único** para todos os painéis (12 meses por padrão). Os manejos
      costumam olhar ciclos ou meses; o seletor cobre ambos, mas o padrão é discutível.
- [ ] **Peso ideal só na idade exata em meses:** não interpola entre meses nem usa o mês mais
      próximo.
- [ ] **Cria do parto:** o sexo é opcional e a cria só é ligada se já estiver cadastrada
      como animal. Ao registrar um parto, o sistema não cria o animal da cria.
- [ ] **Taxa de concepção por cobertura, não por vaca:** uma vaca inseminada três vezes conta
      três inseminações.
- [ ] **Produção:** sem turnos de ordenha; sem separação de leite descartado (tratamento).

## Ainda não implementado (ideias da planilha)

- Sanidade: vacinas e vermífugos (aparecem na ficha das terneiras).
- Alertas de prazo (retorno de cio, secagem, parto) e lista de "vacas a inseminar".
- Gráficos de evolução no tempo (os painéis mostram o período escolhido, não a série).
- Registro automático do animal da cria ao lançar o parto.
