/**
 * Par de campos para lancamentos de um animal (pesagem, evento, producao): o tipo de
 * animal e so um filtro do formulario (nao vai no payload) que recorta a lista de
 * animais logo abaixo. Na edicao o tipo ja vem preenchido, pelo tipo do animal.
 *
 * "soProdutoresDeLeite" limita tipos e animais aos tipos marcados como produtores de
 * leite (producao de leite nao existe para terneiras e novilhas).
 */
export function camposAnimalComTipo({ soProdutoresDeLeite = false } = {}) {
  return [
    {
      name: "tipo_animal_id", label: "Tipo de animal", type: "select", optionsResource: "tipos-animal",
      labelKey: "descricao", soFiltro: true, vazioLabel: "Todos os tipos", limpaAoMudar: ["animal_id"],
      optionsFilter: (t) => t.ativo && (!soProdutoresDeLeite || t.produz_leite),
      carregar: (lancamento) => lancamento.tipo_animal_id,
    },
    {
      name: "animal_id", label: "Animal", type: "select", optionsResource: "animais",
      labelKey: "nome", isId: true, required: true,
      optionsFilter: (a, dados) =>
        a.ativo &&
        (!soProdutoresDeLeite || a.tipo_produz_leite) &&
        (!dados?.tipo_animal_id || String(a.tipo_animal_id) === String(dados.tipo_animal_id)),
    },
  ];
}
