# Controle Veterinário

Sistema de controle veterinário: propriedades rurais, os animais de cada uma, os
veterinários que as atendem e as pessoas (donos, profissionais, usuários). Cada
usuário enxerga só as propriedades a que está vinculado.

Derivado do projeto `sociedadeesportiva` — mesma stack, mesmo `CrudPage`, mesmo
visual — recortado para este domínio: saíram multi-clube e financeiro; entraram
endereços (estado → cidade, com bairros, localidades e CEPs), pessoa física/jurídica
com telefones, propriedades, animais e controle de acesso por papel.

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
   quais bairros e localidades usam cada CEP. Todo endereço de pessoa e
   propriedade precisa de um CEP cadastrado; o formulário mostra a cidade assim
   que o CEP é digitado e avisa se ele ainda não existe.
3. **Pessoas** — donos, veterinários e qualquer pessoa que vá ter login. Física
   (CPF, nascimento) ou jurídica (CNPJ, razão social), com vários telefones e um
   principal.
4. **Usuários** — o login. Pode ser ligado a uma pessoa.
5. **Veterinários** — a pessoa (física) + o usuário dela. Todo veterinário precisa
   de login.
6. **Tipos de Animal** → **Animais** → **Propriedades**. Na linha de cada
   propriedade há três botões: animais, veterinários e usuários com acesso.

## Controle de acesso

| Papel | Lê | Grava cadastros | Gerencia usuários |
|---|---|---|---|
| `MASTER` | tudo | sim | sim |
| `ADMIN` | só as suas propriedades | sim | não (só lista) |
| `VISUALIZADOR` | só as suas propriedades | não | não |

"As suas propriedades" são as ligadas ao login (`propriedades_usuarios`) mais, para
quem é veterinário, as que atende (`veterinarios_propriedades`). Pessoas,
geografia, tipos de animal e veterinários são cadastros comuns e visíveis a todos.

Regras que valem conhecer:

- Quem não é MASTER e cria uma propriedade fica automaticamente vinculado a ela —
  senão ela sumiria da própria tela.
- Um **animal** só aparece para quem vê alguma propriedade em que ele esteja, ou,
  enquanto ele não estiver em propriedade nenhuma, para quem o cadastrou
  (`animais.usuario_inclusao_id`, migration `0003`). O MASTER vê todos.
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
  acesso.py        recorte de propriedades por usuário
  vinculos.py      sincronização das tabelas associativas
  erros_db.py      IntegrityError do Postgres -> 409/400 com mensagem clara
  routers/         um arquivo por área da API (geografia.py agrupa os 5 cadastros de endereço)
alembic/           migrations (o schema inicial vem do .sql, não daqui)
schema_bd/
  modelo_ajustado.sql   modelagem inicial (aplicada uma vez, antes das migrations)
  controleveterinario.sql   retrato atual do schema (pg_dump -s), com as migrations aplicadas
frontend/src/
  pages/           telas (Propriedades, Animais, Veterinários, cadastros/...)
  components/      CrudPage genérico, CepInput, TelefonesField, VinculosModal
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

**Vínculos são sempre o conjunto completo.** `PUT /propriedades/{id}/animais`
(e `/veterinarios`, `/usuarios`, e `/veterinarios/{id}/propriedades`) recebe a
lista final de ids; a API calcula o que entra e o que sai, preservando os vínculos
que não mudaram.
