import { useEffect, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";

/**
 * Seletor de varias opcoes (checkboxes num dropdown). "value" e a lista de
 * valores marcados; lista vazia significa "todas" - e o que o filtro de
 * contas quer: sem marcar nada, olha o clube inteiro.
 */
export default function MultiSelect({ value, onChange, options, todasLabel, nomeMultiplo = "selecionadas" }) {
  const [aberto, setAberto] = useState(false);
  const ref = useRef(null);
  const marcados = value.map(String);

  useEffect(() => {
    function aoClicarFora(e) {
      if (ref.current && !ref.current.contains(e.target)) setAberto(false);
    }
    document.addEventListener("mousedown", aoClicarFora);
    return () => document.removeEventListener("mousedown", aoClicarFora);
  }, []);

  function alternar(opcao) {
    const id = String(opcao.value);
    onChange(
      marcados.includes(id) ? marcados.filter((v) => v !== id) : [...marcados, id],
    );
  }

  const escolhidas = options.filter((o) => marcados.includes(String(o.value)));
  const resumo =
    escolhidas.length === 0
      ? todasLabel
      : escolhidas.length === 1
        ? escolhidas[0].label
        : `${escolhidas.length} ${nomeMultiplo}`;

  return (
    <div className="searchable-select multi-select" ref={ref}>
      <button
        type="button"
        className="searchable-select-input multi-select-botao"
        onClick={() => setAberto((a) => !a)}
        aria-expanded={aberto}
      >
        {resumo}
      </button>
      <ChevronDown size={14} className="searchable-select-caret" />
      {aberto && (
        <div className="searchable-select-list">
          <label className="multi-select-opcao">
            <input type="checkbox" checked={marcados.length === 0} onChange={() => onChange([])} />
            {todasLabel}
          </label>
          {options.map((o) => (
            <label key={o.value} className="multi-select-opcao">
              <input
                type="checkbox"
                checked={marcados.includes(String(o.value))}
                onChange={() => alternar(o)}
              />
              {o.label}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
