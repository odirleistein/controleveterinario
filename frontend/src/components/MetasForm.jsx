import { useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

/**
 * Metas (e parametros) de um indicador, por propriedade. So quem grava as ve: para os
 * demais, a meta aparece nos cartoes do proprio painel.
 *
 * campos: [{ chave, rotulo, passo }]; valores: { CHAVE: numero }; onSalvo() recarrega o painel.
 */
export default function MetasForm({ campos, valores, onSalvo }) {
  const { podeEscrever } = useAuth();
  const [edicao, setEdicao] = useState({});
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");

  if (!podeEscrever) return null;

  async function salvar(e) {
    e.preventDefault();
    setSalvando(true);
    setErro("");
    try {
      // So o que foi mexido: o resto continua com o valor (ou o padrao) de antes.
      await Promise.all(
        Object.entries(edicao).map(([chave, valor]) => api.put(`/indicadores/metas/${chave}`, { valor: Number(valor) })),
      );
      setEdicao({});
      onSalvo();
    } catch (err) {
      setErro(String(err.response?.data?.detail ?? "Erro ao salvar."));
    } finally {
      setSalvando(false);
    }
  }

  return (
    <>
      {erro && <div className="alert-error">{erro}</div>}
      <form className="filtros" onSubmit={salvar}>
        {campos.map((c) => (
          <label className="meta-form" key={c.chave}>
            {c.rotulo}
            <input
              type="number"
              min="0.1"
              step={c.passo ?? "1"}
              value={edicao[c.chave] ?? valores[c.chave] ?? ""}
              onChange={(e) => setEdicao({ ...edicao, [c.chave]: e.target.value })}
              required
            />
          </label>
        ))}
        <button type="submit" disabled={salvando || Object.keys(edicao).length === 0}>
          {salvando ? "Salvando..." : "Salvar metas"}
        </button>
      </form>
    </>
  );
}
