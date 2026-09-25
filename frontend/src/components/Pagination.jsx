import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react";

const OPCOES_PADRAO = [10, 20, 50, 100];

/**
 * Paginacao client-side generica: recebe o total de itens (ja filtrados) e a
 * pagina/tamanho atuais e emite onMudarPagina/onMudarItensPorPagina. Nao
 * renderiza nada quando nao ha itens.
 */
export default function Pagination({
  pagina,
  totalItens,
  itensPorPagina,
  onMudarPagina,
  onMudarItensPorPagina,
  opcoesPorPagina = OPCOES_PADRAO,
}) {
  if (totalItens === 0) return null;

  const totalPaginas = Math.max(1, Math.ceil(totalItens / itensPorPagina));
  const paginaAtual = Math.min(Math.max(pagina, 1), totalPaginas);
  const inicio = (paginaAtual - 1) * itensPorPagina + 1;
  const fim = Math.min(paginaAtual * itensPorPagina, totalItens);

  return (
    <div className="pagination">
      <span className="pagination-info">
        Mostrando {inicio}–{fim} de {totalItens}
      </span>
      <div className="pagination-controls">
        {onMudarItensPorPagina && (
          <select value={itensPorPagina} onChange={(e) => onMudarItensPorPagina(Number(e.target.value))}>
            {opcoesPorPagina.map((n) => (
              <option key={n} value={n}>
                {n} por página
              </option>
            ))}
          </select>
        )}
        <button
          type="button"
          className="btn-secondary pagination-btn"
          onClick={() => onMudarPagina(1)}
          disabled={paginaAtual === 1}
          title="Primeira página"
        >
          <ChevronsLeft size={15} />
        </button>
        <button
          type="button"
          className="btn-secondary pagination-btn"
          onClick={() => onMudarPagina(paginaAtual - 1)}
          disabled={paginaAtual === 1}
          title="Página anterior"
        >
          <ChevronLeft size={15} />
        </button>
        <span className="pagination-pagina">
          Página {paginaAtual} de {totalPaginas}
        </span>
        <button
          type="button"
          className="btn-secondary pagination-btn"
          onClick={() => onMudarPagina(paginaAtual + 1)}
          disabled={paginaAtual === totalPaginas}
          title="Próxima página"
        >
          <ChevronRight size={15} />
        </button>
        <button
          type="button"
          className="btn-secondary pagination-btn"
          onClick={() => onMudarPagina(totalPaginas)}
          disabled={paginaAtual === totalPaginas}
          title="Última página"
        >
          <ChevronsRight size={15} />
        </button>
      </div>
    </div>
  );
}
