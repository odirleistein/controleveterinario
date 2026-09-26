# Controle Veterinário

Sistema de controle veterinário com foco em produção leiteira: propriedades
rurais, os animais de cada uma, os veterinários que as atendem e as pessoas
(donos, profissionais, usuários).

**A propriedade é o centro de tudo.** O acesso começa pela escolha da propriedade e,
dentro dela, só aparecem os dados dela — para o dono e para o veterinário. Só o
Comparativo olha várias propriedades ao mesmo tempo, e apenas as que o usuário
tem acesso.

Derivado do projeto `sociedadeesportiva` — mesma stack, mesmo `CrudPage`, mesmo
visual — recortado para este domínio: saíram multi-clube e financeiro; entraram
endereços (estado → cidade, com bairros, localidades e CEPs), pessoa física/jurídica
com telefones, propriedades, animais e controle de acesso por papel; e, do manejo
leiteiro, raças, peso, genealogia, reprodução, produção de leite, ficha da vaca e
indicadores zootécnicos (veja [docs/manejo-e-indicadores.md](docs/manejo-e-indicadores.md)).

## Stack

- **Backend:** FastAPI + SQLAlchemy 2 + PostgreSQL, migrations com Alembic
- **Frontend:** React 19 + Vite + React Router, requisições com axios
- **Autenticação:** JWT (todas as rotas, exceto login e primeiro acesso, exigem login)

## Como rodar

O banco `controleveterinario` já tem o schema aplicado. Para subir:

```powershell
# Backend (porta 8082)
scripts\start_backend.bat

# Frontend em modo desenvolvimento (porta 5175)
cd frontend
npm run dev
```

As portas são 8082 e 5175 de propósito: finanças pessoais usa 8080/5173 e a
sociedade esportiva 8081/5174, então os três podem ficar no ar juntos.

Em produção local, `npm run build` gera `frontend/dist` e o próprio backend passa
a servir o frontend no mesmo host e porta — basta acessar http://localhost:8082.

## Instalação do zero

```powershell
createdb -U postgres controleveterinario
psql -U postgres -d controleveterinario -f schema_bd\modelo_ajustado.sql
copy .env.example .env            # ajuste a senha do banco e gere a SECRET_KEY
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe -m alembic stamp 0001_baseline
venv\Scripts\python.exe -m alembic upgrade head    # semeia os 27 estados
cd frontend; npm install
```

Ao rodar `psql` nesta máquina, exporte `PGCLIENTENCODING=UTF8` antes: sem isso ele
lê o UTF-8 do arquivo como WIN1252 e grava "Cléber" como "ClÃ©ber".

Daí em diante, toda mudança de estrutura passa por migration do Alembic
(`alembic revision -m "..."` e `alembic upgrade head`).

Backups: `scripts\backup-schema.ps1` (só estrutura) e `scripts\backup-dados.ps1`
(estrutura + dados). Rode o de dados antes de qualquer carga em lote.

## Primeiros passos no sistema

1. Abra o sistema e use **Primeiro acesso** na tela de login: cria o usuário
   `MASTER`. Depois disso o cadastro aberto se fecha — novos usuários são criados
   por um MASTER em **Usuários**, escolhendo o papel.
2. **Endereços**: *Cidades* (os estados já vêm), depois os *Bairros* e as
   *Localidades* de cada cidade e, por fim, os *CEPs*, escolhendo a cidade e
   quais bairros e localidades usam cada CEP.
3. **Pessoas** — donos, veterinários e qualquer pessoa que vá ter login. Física
   (CPF, nascimento) ou jurídica (CNPJ, razão social), com vários telefones e um
   principal. O endereço é CEP + **um** bairro ou localidade (escolhido entre os
   que o CEP cobre) + número e complemento.
4. **Usuários** (MASTER) — o login. Pode ser ligado a uma pessoa.
5. **Cadastro de Veterinários** (MASTER) — a pessoa (física) + o usuário dela.
6. **Tipos de Animal** e **Propriedades**. Na linha de cada propriedade há dois
   botões: os veterinários que a atendem e os usuários com acesso a ela.
7. Escolha a propriedade (ela vira o contexto) e cadastre os **Animais** dentro
   dela.
8. Manejo: cadastre **Raças**, **Reprodutores** (touros e ascendentes) e o **Peso
   ideal por raça**; marque em **Tipos de Animal** quais produzem leite. Depois, na
   propriedade, lance **Reprodução**, **Produção de leite** e **Pesagens** — a ficha
   da vaca e os **Indicadores** saem desses lançamentos. As regras de cálculo e as
   premissas a validar estão em [docs/manejo-e-indicadores.md](docs/manejo-e-indicadores.md).

## Como o sistema se organiza

Depois do login vem a **escolha da propriedade** (quem tem uma só entra direto nela).
O menu tem três blocos:

- **Nesta propriedade** — Visão Geral, Animais (com a ficha de cada vaca), Reprodução,
  Produção de leite, Indicadores, Pesagens, Peso x ideal e Veterinários, sempre da
  propriedade aberta. Dá para trocar de propriedade no seletor do topo do menu.
- **Comparar** — o Comparativo: propriedades lado a lado (animais total e por tipo,
  veterinários, usuários). Filtra por quais propriedades comparar; sem escolher, compara
  todas as suas. Serve ao veterinário que atende várias e ao produtor com mais de uma.
- **Cadastros** — administração que não depende do contexto: propriedades, pessoas,
  tipos de animal, raças, reprodutores, peso ideal por raça, endereços e, só para o MASTER, usuários e cadastro de veterinários.

## Controle de acesso

| Papel | Lê | Grava | Gerencia usuários e veterinários |
|---|---|---|---|
| `MASTER` | tudo | sim | sim |
| `ADMIN` | só o que é das suas propriedades | sim | não |
| `VISUALIZADOR` | só o que é das suas propriedades | não | não |

"As suas propriedades" são as ligadas ao login (`propriedades_usuarios`) mais, para
quem é veterinário, as que atende (`veterinarios_propriedades`). Três níveis de dado:

1. **Da propriedade — animais.** Só existem dentro do contexto de UMA propriedade
   (cabeçalho `X-Propriedade-Id`). Sem o cabeçalho a API responde 400; com uma
   propriedade a que o usuário não tem acesso, 403. O MASTER também escolhe uma.
   O animal criado já nasce vinculado à propriedade aberta.
2. **Das pessoas ligadas às propriedades — pessoas, usuários, veterinários.** Quem
   não é MASTER vê só os donos das suas propriedades, os veterinários e os usuários
   ligados a elas, a si mesmo e o que ele próprio cadastrou (uma pessoa recém-criada
   ainda não está ligada a nada — sem isso quem a cadastrou não a acharia para
   escolher como proprietária).
3. **Referência comum — estados, cidades, bairros, localidades, CEPs, tipos de
   animal, raças, reprodutores, tipos de evento, peso ideal por raça.** Visível a todos; gravar exige MASTER ou ADMIN.

Outras regras:

- Quem não é MASTER e cria uma propriedade fica automaticamente vinculado a ela.
- Quem administra uma propriedade vincula a ela veterinários já cadastrados
  (`/veterinarios/candidatos` devolve só id e nome) e os usuários que já enxerga.
- O comparativo ignora ids de propriedades que o usuário não pode ver.
- Propriedade inativa não vira contexto.
- Ao editar vínculos pelo lado do veterinário, quem não é MASTER só mexe nos das
  propriedades que enxerga; os demais ficam como estão.
- Não dá para desativar a si mesmo, nem o último usuário ativo, nem o último MASTER.

## Estrutura

```
app/
  main.py          ponto de entrada da API e montagem dos routers
  models.py        modelos SQLAlchemy (espelham o schema do banco)
  schemas.py       schemas Pydantic de entrada e saída
  security.py      hash de senha, JWT e papéis (exigir_escrita / exigir_master)
  acesso.py        propriedade do contexto (X-Propriedade-Id) e o que cada usuário enxerga
  vinculos.py      sincronização das tabelas associativas
  ficha.py         regras da ficha da vaca (situação, DEL, prazos) — funções puras
  calculo_indicadores.py   regras das taxas reprodutivas — funções puras
  erros_db.py      IntegrityError do Postgres -> 409/400 com mensagem clara
  routers/         um arquivo por área da API (geografia.py agrupa os 5 cadastros de endereço)
docs/              regras de negócio do manejo e dos indicadores (para validar com o usuário)
alembic/           migrations (o schema inicial vem do .sql, não daqui)
schema_bd/
  modelo_ajustado.sql   modelagem inicial (aplicada uma vez, antes das migrations)
  controleveterinario.sql   retrato atual do schema (pg_dump -s), com as migrations aplicadas
frontend/src/
  pages/           telas (Escolher propriedade, Visão Geral, Animais, Comparativo, cadastros/...)
  components/      CrudPage genérico, CepInput, TelefonesField, VinculosModal, RequerPropriedade
scripts/           subir backend, parar backend, backups
```

## Decisões de modelagem que valem conhecer

**Chave `<tabela>_id` no banco, `id` no código.** O schema nomeia cada chave pela
tabela (`pessoa_id`, `animal_id`). Nos modelos o atributo é sempre `id`
(`mapped_column("pessoa_id", ...)`), então a API e o `CrudPage` seguem o padrão
`item.id` do resto da família de projetos. A exceção é o CEP, cuja chave natural é
o próprio código: o modelo expõe `id` = `cep`.

**Pessoa é supertipo; física e jurídica são subtipos.** `pessoas` guarda o que é
comum (nome, e-mail, endereço); `pessoas_fisicas` e `pessoas_juridicas` têm PK igual
à FK. Na API a pessoa é **um formulário só**: os campos do subtipo vêm achatados e
os telefones vão junto, como lista. Trocar de física para jurídica (ou o inverso)
apaga o subtipo antigo. CPF/CNPJ são únicos mas opcionais, e string vazia vira
`NULL` — o índice único ignora NULL, não ignora "".

**Telefone principal é garantido pelo banco.** O índice único parcial permite um
único `principal = true` por pessoa. Ao salvar, os telefones antigos saem *antes*
dos novos entrarem, senão o novo principal colidiria com o antigo.

**Veterinário é um papel, não uma pessoa.** Nome, endereço e telefone vêm de
`pessoas`; o login, de `usuarios`. Precisa ser pessoa física, e os dois vínculos
(pessoa e usuário) são únicos.

**Endereço: bairros e localidades são da cidade; o CEP é da cidade e cobre vários
deles.** Uma cidade tem vários bairros e várias localidades (na zona rural: linha,
distrito, comunidade), cadastros paralelos — nenhum fica dentro do outro. O mesmo
CEP pode valer para vários bairros e várias localidades (`ceps_bairros` e
`ceps_localidades`), porque em cidade pequena todos os endereços dividem um CEP; e o
mesmo bairro pode aparecer em mais de um CEP. O CEP guarda a `cidade_id`, então ele
identifica a cidade mesmo sem nenhum bairro ou localidade ligado. A API exige que
os bairros e localidades de um CEP sejam da mesma cidade dele. Cidade, bairro e
localidade são desativados em vez de apagados, para não esconder o endereço de
cadastros existentes.

**A pessoa guarda o CEP e qual bairro *ou* qual localidade dele é o seu.** Como
um CEP pode cobrir vários, `pessoas` tem `bairro_id` e `localidade_id` (no máximo um
dos dois, garantido por `ck_pessoas_bairro_localidade`). A API confere que o escolhido
pertence ao CEP da pessoa, e não deixa tirar de um CEP um bairro/localidade que uma
pessoa ainda usa. No formulário o seletor só aparece com o CEP completo e, se o CEP
cobre um único local, ele já vem escolhido.

**Vínculos são sempre o conjunto completo.** `PUT /propriedades/{id}/animais`
(e `/veterinarios`, `/usuarios`, e `/veterinarios/{id}/propriedades`) recebe a
lista final de ids; a API calcula o que entra e o que sai, preservando os vínculos
que não mudaram.
