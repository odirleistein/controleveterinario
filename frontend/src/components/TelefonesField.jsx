import { Plus, Trash2 } from "lucide-react";

const TIPOS = ["Celular", "Residencial", "Comercial", "WhatsApp"];

/**
 * Lista de telefones de uma pessoa, com exatamente um marcado como principal
 * (o banco so aceita um por pessoa). "value" e "onChange" trabalham com a lista
 * inteira, do jeito que a API espera receber.
 */
export default function TelefonesField({ value, onChange }) {
  function atualizar(indice, campos) {
    onChange(value.map((t, i) => (i === indice ? { ...t, ...campos } : t)));
  }

  function marcarPrincipal(indice) {
    onChange(value.map((t, i) => ({ ...t, principal: i === indice })));
  }

  function remover(indice) {
    const restante = value.filter((_, i) => i !== indice);
    // Removeu o principal: o primeiro que sobrou assume, para nunca ficar sem.
    if (restante.length > 0 && !restante.some((t) => t.principal)) restante[0] = { ...restante[0], principal: true };
    onChange(restante);
  }

  function adicionar() {
    onChange([...value, { numero: "", tipo_telefone: "Celular", principal: value.length === 0 }]);
  }

  return (
    <div className="telefones-field">
      {value.map((t, i) => (
        <div className="telefone-linha" key={i}>
          <input
            type="tel"
            placeholder="(54) 99999-8888"
            value={t.numero ?? ""}
            onChange={(e) => atualizar(i, { numero: e.target.value })}
          />
          <select value={t.tipo_telefone ?? ""} onChange={(e) => atualizar(i, { tipo_telefone: e.target.value })}>
            <option value="">Tipo</option>
            {TIPOS.map((tipo) => (
              <option key={tipo} value={tipo}>
                {tipo}
              </option>
            ))}
          </select>
          <label className="telefone-principal" title="Telefone principal">
            <input type="radio" checked={!!t.principal} onChange={() => marcarPrincipal(i)} />
            Principal
          </label>
          <button type="button" className="icon-btn danger" title="Remover telefone" onClick={() => remover(i)}>
            <Trash2 size={15} />
          </button>
        </div>
      ))}
      <button type="button" className="btn-secondary telefone-adicionar" onClick={adicionar}>
        <Plus size={14} />
        Adicionar telefone
      </button>
    </div>
  );
}
