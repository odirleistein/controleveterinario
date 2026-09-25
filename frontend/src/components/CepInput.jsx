import { useEffect, useState } from "react";
import api from "../api/client";
import { formatarCep } from "../utils/format";

/**
 * Campo de CEP: aceita digitando com ou sem hifen e, ao completar os 8 digitos,
 * consulta o cadastro de CEPs e mostra abaixo a cidade/bairro/localidade. CEP nao
 * cadastrado nao bloqueia a digitacao, mas o banco vai recusar ao salvar - por
 * isso o aviso aparece antes, em vez de so depois do erro.
 */
export default function CepInput({ value, onChange, required = false }) {
  const [situacao, setSituacao] = useState(null);
  const digitos = String(value ?? "").replace(/\D/g, "");

  useEffect(() => {
    if (digitos.length !== 8) return;
    let cancelado = false;
    api
      .get(`/ceps/${digitos}`)
      .then((res) => !cancelado && setSituacao({ cep: digitos, ok: true, texto: [res.data.cidade_uf, res.data.bairros_nomes, res.data.localidades_nomes].filter(Boolean).join(" — ") }))
      .catch(() => !cancelado && setSituacao({ cep: digitos, ok: false, texto: "CEP não cadastrado (cadastre em CEPs)" }));
    return () => {
      cancelado = true;
    };
  }, [digitos]);

  return (
    <>
      <input
        type="text"
        inputMode="numeric"
        placeholder="00000-000"
        maxLength={9}
        value={digitos.length === 8 ? formatarCep(digitos) : value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
      />
      {/* O resultado guarda de qual CEP veio: se o campo mudou depois, some sozinho. */}
      {situacao?.cep === digitos && (
        <span className={situacao.ok ? "cep-situacao" : "cep-situacao cep-situacao-erro"}>{situacao.texto}</span>
      )}
    </>
  );
}
