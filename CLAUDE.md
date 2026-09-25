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

Não há multi-tenant: os cadastros comuns (pessoas, geografia, tipos de animal,
veterinários) são globais. O que é restrito é **propriedade e o que pende dela**:

- Papéis (tabela `papeis`): `MASTER` (tudo, inclusive usuários), `ADMIN` (grava
  cadastros), `VISUALIZADOR` (só lê). Rota que grava depende de `exigir_escrita`;
  rota de usuários depende de `exigir_master` (`app/security.py`).
- Quem não é MASTER só enxerga as propriedades ligadas a ele: pelo login
  (`propriedades_usuarios`) ou, se for veterinário, pelas que atende
  (`veterinarios_propriedades`). O recorte é **chamado rota a rota**, não é
  automático: use `ids_propriedades_visiveis` / `buscar_propriedade_visivel`
  (`app/acesso.py`) em toda rota nova que devolva propriedade ou dado dela, e
  `condicao_visivel` (`routers/animais.py`) para animais (animal solto só é visto por quem o criou). Esquecer isso vaza
  dados de outra propriedade.
- Sincronização de vínculos (`app/vinculos.py`) recebe `permitidos`: quem não vê
  todas as propriedades não pode apagar vínculos das que não vê.
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
  Alembic (`0001_baseline` só marca o ponto de partida; `0002` semeia as UFs, `0003` guarda o criador do animal, `0004` refaz endereço: CEP N:N com bairros/localidades).
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
