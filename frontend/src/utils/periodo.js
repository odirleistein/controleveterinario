// Periodos pre-definidos dos indicadores (ver components/SeletorPeriodo.jsx).

// Data local em AAAA-MM-DD. toISOString() usaria UTC e, a noite, cairia no dia seguinte.
function iso(data) {
  const p = (n) => String(n).padStart(2, "0");
  return `${data.getFullYear()}-${p(data.getMonth() + 1)}-${p(data.getDate())}`;
}

/** Inicio e fim de um periodo pre-definido, contados a partir de hoje. */
export function calcularPeriodo(chave) {
  const hoje = new Date();
  const fim = new Date(hoje);
  const inicio = new Date(hoje);
  if (chave === "90d") inicio.setDate(inicio.getDate() - 90);
  else if (chave === "6m") inicio.setMonth(inicio.getMonth() - 6);
  else if (chave === "ano") inicio.setMonth(0, 1);
  else if (chave === "ano-passado") {
    inicio.setFullYear(hoje.getFullYear() - 1, 0, 1);
    fim.setFullYear(hoje.getFullYear() - 1, 11, 31);
  } else inicio.setFullYear(inicio.getFullYear() - 1); // 12m (e ponto de partida do personalizado)
  return { inicio: iso(inicio), fim: iso(fim) };
}

/** Estado inicial de uma tela com periodo: os ultimos 12 meses. */
export function periodoInicial() {
  return { chave: "12m", ...calcularPeriodo("12m") };
}
