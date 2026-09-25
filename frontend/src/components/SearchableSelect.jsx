import { useEffect, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";
import { semAcento } from "../utils/format";

export default function SearchableSelect({
  value,
  onChange,
  options,
  placeholder = "Selecione",
  allowEmpty = true,
  emptyLabel = "Nenhuma",
  required = false,
}) {
  const [aberto, setAberto] = useState(false);
  const [busca, setBusca] = useState("");
  const [destaque, setDestaque] = useState(0);
  const ref = useRef(null);

  const listaCompleta = allowEmpty ? [{ value: "", label: emptyLabel }, ...options] : options;
  const selecionado = listaCompleta.find((o) => String(o.value) === String(value ?? ""));
  const filtradas = busca.trim()
    ? listaCompleta.filter((o) => semAcento(o.label).includes(semAcento(busca.trim())))
    : listaCompleta;

  useEffect(() => {
    function aoClicarFora(e) {
      if (ref.current && !ref.current.contains(e.target)) {
        setAberto(false);
        setBusca("");
      }
    }
    document.addEventListener("mousedown", aoClicarFora);
    return () => document.removeEventListener("mousedown", aoClicarFora);
  }, []);

  function selecionar(opt) {
    onChange(String(opt.value));
    setAberto(false);
    setBusca("");
  }

  function aoTeclar(e) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setAberto(true);
      setDestaque((d) => Math.min(d + 1, filtradas.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setDestaque((d) => Math.max(d - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (aberto && filtradas[destaque]) selecionar(filtradas[destaque]);
    } else if (e.key === "Escape") {
      setAberto(false);
      setBusca("");
    }
  }

  return (
    <div className="searchable-select" ref={ref}>
      <input
        type="text"
        className="searchable-select-input"
        value={aberto ? busca : (selecionado?.label ?? "")}
        placeholder={placeholder}
        onFocus={() => {
          setAberto(true);
          setBusca("");
          setDestaque(0);
        }}
        onChange={(e) => {
          setBusca(e.target.value);
          setAberto(true);
          setDestaque(0);
        }}
        onKeyDown={aoTeclar}
        autoComplete="off"
      />
      <ChevronDown size={14} className="searchable-select-caret" />
      {required && (
        <select
          tabIndex={-1}
          aria-hidden="true"
          className="searchable-select-native-required"
          value={value ?? ""}
          required
          onChange={() => {}}
        >
          <option value="" />
          {options.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      )}
      {aberto && (
        <div className="searchable-select-list">
          {filtradas.length === 0 && <div className="searchable-select-empty">Nada encontrado</div>}
          {filtradas.map((o, i) => (
            <div
              key={o.value === "" ? "__vazio" : o.value}
              className={i === destaque ? "searchable-select-option active" : "searchable-select-option"}
              onMouseDown={(e) => {
                e.preventDefault();
                selecionar(o);
              }}
              onMouseEnter={() => setDestaque(i)}
            >
              {o.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
