/**
 * O bairro OU a localidade de um endereco viajam num seletor so, como uma chave
 * "b:<id>" (bairro) ou "l:<id>" (localidade); a API recebe os dois campos separados.
 */
export function chaveLocal(bairroId, localidadeId) {
  if (bairroId) return `b:${bairroId}`;
  if (localidadeId) return `l:${localidadeId}`;
  return "";
}

/** "b:3" -> { bairro_id: 3, localidade_id: null }; vazio -> os dois nulos. */
export function separarLocal(chave) {
  const [tipo, id] = String(chave ?? "").split(":");
  return {
    bairro_id: tipo === "b" ? Number(id) : null,
    localidade_id: tipo === "l" ? Number(id) : null,
  };
}
