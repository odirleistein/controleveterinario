/**
 * Extrai a mensagem de erro de uma resposta da API.
 *
 * O FastAPI devolve "detail" como string nos erros que a gente levanta a mao
 * (400/404/409) e como lista de objetos nos erros de validacao do Pydantic (422),
 * entao imprimir o detail direto na tela gera "[object Object]".
 */
export function mensagemErro(err, padrao = "Erro inesperado.") {
  const detail = err?.response?.data?.detail;
  if (!detail) return padrao;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const msgs = detail.map((d) => d?.msg).filter(Boolean);
    if (msgs.length > 0) return msgs.join(" ");
  }
  return padrao;
}
