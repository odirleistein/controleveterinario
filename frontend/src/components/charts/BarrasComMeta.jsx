import { Link } from "react-router-dom";

const num = (v, casas) =>
  v === null || v === undefined
    ? "-"
    : Number(v).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

/**
 * Uma barra por animal, com duas linhas verticais: a meta e a media. A barra fica
 * vermelha quando passa da meta (nos indicadores daqui, menos e melhor). O nome leva
 * a ficha do animal.
 *
 * linhas: [{ id, nome, valor }]. "casas" e o numero de decimais do valor.
 */
export default function BarrasComMeta({ linhas, meta, media, casas = 0, unidade = "" }) {
  const maior = Math.max(...linhas.map((l) => l.valor), meta, media ?? 0, 1) * 1.05;
  const pct = (v) => `${(v / maior) * 100}%`;

  return (
    <>
      <div className="del-legenda">
        <span><i className="del-marca meta" /> Meta ({num(meta, casas)}{unidade})</span>
        <span><i className="del-marca media" /> Média ({num(media, 1)}{unidade})</span>
      </div>
      <div className="del-linhas">
        {linhas.map((l) => (
          <div className="del-linha" key={l.id}>
            <Link to={`/animais/${l.id}/ficha`} className="del-nome">
              {l.nome}
            </Link>
            <span className="del-trilha">
              <span className={l.valor > meta ? "del-barra acima" : "del-barra"} style={{ width: pct(l.valor) }} />
              <span className="del-marcador meta" style={{ left: pct(meta) }} />
              {media != null && <span className="del-marcador media" style={{ left: pct(media) }} />}
            </span>
            <span className="del-valor">{num(l.valor, casas)}</span>
          </div>
        ))}
      </div>
    </>
  );
}
