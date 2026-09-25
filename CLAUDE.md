# Controle Veterinário

Cadastro de propriedades rurais, animais e veterinários. FastAPI + SQLAlchemy +
PostgreSQL no backend, React 19 + Vite no frontend. Veja o README.md para a visão
geral e as decisões de modelagem.

Derivado do projeto `sociedadeesportiva` (mesma stack, mesmos componentes e o
mesmo `CrudPage`), sem o multi-clube e sem a parte financeira.

## Ambiente

- Banco: `controleveterinario` no Postgres local (`.env` tem a `DATABASE_URL`).
- Backend na porta **8082**, Vite na **5175** — 8080/5173 são do projeto de
  finanças pessoais e 8081/5174 do de sociedade esportiva, que rodam em paralelo.
  Não troque para as portas deles.
- Ambiente virtual próprio em `venv/`.

## Acesso (o mais importante deste projeto)

**A propriedade é o centro de tudo.** O acesso começa pela escolha da propriedade e,
nesse contexto, só aparecem dados dela — para o dono e para o veterinário. Só o
comparativo (`/dashboard/comparativo`) olha várias, e apenas as que o usuário vê.
Toda tela e toda rota nova precisa considerar as regras de acesso e mostrar só o
que o usuário pode ver. Não há multi-tenant: nada é filtrado automaticamente, cada
rota chama as funções de `app/acesso.py`. **Esquecer isso vaza dados de outra propriedade.**

- Papéis (tabela `papeis`): `MASTER` (tudo, inclusive usuários e cadastro de
  veterinários), `ADMIN` (grava cadastros), `VISUALIZADOR` (só lê). Rota que grava
  depende de `exigir_escrita`; usuários e veterinários (escrita) de `exigir_master`
  (`app/security.py`).
- Quem não é MASTER só enxerga as propriedades ligadas a ele: pelo login
  (`propriedades_usuarios`) ou, se for veterinário ativo, pelas que atende
  (`veterinarios_propriedades`) — `ids_propriedades_visiveis`.
- **Dado de propriedade (animais e o que vier: produção, sanidade...)**: a rota
  depende de `propriedade_atual` (cabeçalho `X-Propriedade-Id`; 400 sem ele, 403 sem
  acesso ou propriedade inativa) e toda consulta passa pelo vínculo com ela. O dado
  novo nasce vinculado à propriedade do contexto. Não crie listagem "de todas as
  propriedades" fora do comparativo.
- **Dado de pessoa (pessoas, usuários, veterinários)**: use `condicao_pessoa_visivel`
  / `condicao_usuario_visivel`; `buscar_propriedade_visivel` para propriedades. Quem
  cadastrou uma pessoa a vê (`pessoas.usuario_inclusao_id`) até ela ser ligada a algo.
- **Referência comum** (estados, cidades, bairros, localidades, CEPs, tipos de animal):
  visível a todos.
- Comparativo: aceita ids de propriedade, mas **ignora** os que o usuário não vê.
- Sincronização de vínculos (`app/vinculos.py`) recebe `permitidos`: quem não vê
  todas as propriedades não pode apagar vínculos das que não vê.
- Frontend: `RequerPropriedade` protege as telas de uma propriedade; o axios manda o
  cabeçalho. Trocar de propriedade recarrega a página (as telas guardam listas em memória).
- Modelo novo: a chave no banco é `<tabela_singular>_id`, mas o atributo Python
  é sempre `id` (`mapped_column("pessoa_id", ...)`), para o `CrudPage` e a API
  seguirem o padrão `item.id`.

## Regras de trabalho

- O banco `controleveterinario` é do usuário. Para validar uma mudança, use
  consulta de leitura; cenários com escrita rodam no banco descartável
  `controleveterinario_teste` (crie, aplique o .sql e as migrations, apague no
  fim). Se um teste exigir escrever no banco real, pergunte antes.
- `schema_bd/modelo_ajustado.sql` é o script de modelagem inicial, aplicado uma
  vez num banco vazio. Toda alteração de estrutura depois disso é migration do
  Alembic (`0001_baseline` só marca o ponto de partida; `0002` semeia as UFs, `0003` guarda o criador do animal, `0004` refaz endereço: CEP N:N com bairros/localidades, `0005` bairro/localidade na pessoa, `0006` criador da pessoa, `0007` cadastro de raças e `raca_id` opcional no animal, `0008` pesagens, peso ideal por raça/idade e `data_nascimento` do animal).
- Antes de rodar `psql`, exporte `PGCLIENTENCODING=UTF8` — sem isso os acentos
  são gravados em dobro ("Cléber" vira "ClÃ©ber").
- Telas de lista usam a prop `larga` do `CrudPage` (sem teto de 1280px); formulário
  longo usa `largo` (modal em duas colunas).
- CPF, CNPJ, CEP e telefone são gravados **só com dígitos**; a máscara é do
  frontend (`utils/format.js`). O schema Pydantic já normaliza na entrada.
- Comentários no código em português sem acentos, explicando o *porquê* — siga o
  padrão dos arquivos existentes.
- `schema_bd/controleveterinario.sql` é o retrato atual do banco (`pg_dump -s`, via
  `scripts/backup-schema.ps1`); regere-o depois de cada migration.
- Endereço: bairro e localidade pertencem à **cidade**; o CEP pertence à cidade e
  liga a N bairros e N localidades. Não reintroduza a cadeia bairro → localidade → CEP.
- Vocabulário do domínio: "propriedade", "proprietário", "animal", "veterinário",
  "vínculo", "localidade" (sub-área da cidade, na zona rural: linha/comunidade).
