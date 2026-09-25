export function formatarMoeda(valor) {
  const numero = Number(valor);
  if (Number.isNaN(numero)) return valor;
  return numero.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export function formatarData(data) {
  if (!data) return "";
  const [ano, mes, dia] = data.split("-");
  return `${dia}/${mes}/${ano}`;
}

export function hoje() {
  return new Date().toISOString().slice(0, 10);
}

export function diaAnterior(data) {
  const dia = new Date(`${data}T00:00:00`);
  dia.setDate(dia.getDate() - 1);
  return dia.toISOString().slice(0, 10);
}

const MESES_ABREV = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

export function formatarMesAbrev(data) {
  const [ano, mes] = data.split("-");
  return `${MESES_ABREV[Number(mes) - 1]}/${ano.slice(2)}`;
}

const MESES_EXTENSO = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

/** 1 -> "Janeiro", 12 -> "Dezembro". Para widgets que navegam por mês (1-12), sem ano. */
export function nomeDoMes(mes) {
  return MESES_EXTENSO[Number(mes) - 1];
}

/** "2026-09" -> "Setembro/2026". Usado em cabeçalhos de widgets navegáveis por mês+ano. */
export function formatarMesExtenso(mesAno) {
  const [ano, mes] = mesAno.split("-");
  return `${nomeDoMes(mes)}/${ano}`;
}

/** Desloca "2026-09" em N meses (N negativo anda para trás). */
export function deslocarMes(mesAno, delta) {
  const [ano, mes] = mesAno.split("-").map(Number);
  const data = new Date(Date.UTC(ano, mes - 1 + delta, 1));
  return `${data.getUTCFullYear()}-${String(data.getUTCMonth() + 1).padStart(2, "0")}`;
}

export function formatarMoedaCompacta(valor) {
  const numero = Number(valor);
  if (Number.isNaN(numero)) return valor;
  const abs = Math.abs(numero);
  const sinal = numero < 0 ? "-" : "";
  if (abs >= 1_000_000) {
    const milhoes = (abs / 1_000_000).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    return `${sinal}R$ ${milhoes}mi`;
  }
  return formatarMoeda(numero);
}

/** Minusculo e sem acento/cedilha: "Cléber" e "cleber" viram a mesma coisa nas buscas. */
export function semAcento(texto) {
  return String(texto ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

/** "99700000" -> "99700-000". Devolve o original se nao tiver 8 digitos. */
export function formatarCep(cep) {
  const d = String(cep ?? "").replace(/\D/g, "");
  return d.length === 8 ? `${d.slice(0, 5)}-${d.slice(5)}` : (cep ?? "");
}

/** CPF (11 digitos) ou CNPJ (14) com pontuacao; outro tamanho volta como veio. */
export function formatarDocumento(doc) {
  const d = String(doc ?? "").replace(/\D/g, "");
  if (d.length === 11) return d.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
  if (d.length === 14) return d.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
  return doc ?? "";
}

/** "54999998888" -> "(54) 99999-8888"; fixo de 10 digitos -> "(54) 3333-4444". */
export function formatarTelefone(tel) {
  const d = String(tel ?? "").replace(/\D/g, "");
  if (d.length === 11) return d.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
  if (d.length === 10) return d.replace(/(\d{2})(\d{4})(\d{4})/, "($1) $2-$3");
  return tel ?? "";
}
