import { useEffect, useState } from "react";
import api from "../api/client";
import SearchableSelect from "./SearchableSelect";

/**
 * Escolha do bairro OU da localidade do endereco, entre os que o CEP cobre.
 *
 * O valor e uma chave unica "b:<id>" (bairro) ou "l:<id>" (localidade), para o
 * mesmo seletor servir aos dois. Em cidade pequena o CEP cobre varios: o cadastro
 * guarda qual deles e o da pessoa, em vez de parecer que ela mora em todos.
 *
 * - CEP incompleto: o campo nao aparece (a tela usa "mostrarSe"); CEP sem
 *   bairros/localidades cadastrados: aparece so um aviso.
 * - So uma opcao possivel: ela ja vem escolhida.
 * - CEP trocado e a escolha anterior nao vale mais: limpa.
 */
export default function LocalEnderecoField({ cep, value, onChange }) {
  const digitos = String(cep ?? "").replace(/\D/g, "");
  // Guarda de qual CEP vieram as opcoes: se o CEP mudou, elas somem ate a nova consulta.
  const [consulta, setConsulta] = useState({ cep: null, opcoes: [] });

  useEffect(() => {
    if (digitos.length !== 8) return;
    let cancelado = false;
    api
      .get(`/ceps/${digitos}`)
      .then((res) => {
        if (cancelado) return;
        const opcoes = [
          ...res.data.bairros.map((b) => ({ value: `b:${b.id}`, label: `${b.nome} (bairro)` })),
          ...res.data.localidades.map((l) => ({ value: `l:${l.id}`, label: `${l.nome} (localidade)` })),
        ];
        setConsulta({ cep: digitos, opcoes });
        const valida = opcoes.some((o) => o.value === value);
        if (!valida) onChange(opcoes.length === 1 ? opcoes[0].value : "");
      })
      .catch(() => !cancelado && setConsulta({ cep: digitos, opcoes: [] }));
    return () => {
      cancelado = true;
    };
    // So a mudanca do CEP dispara a consulta; "value"/"onChange" mudam a cada tecla.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [digitos]);

  if (consulta.cep !== digitos) return null;
  if (consulta.opcoes.length === 0) {
    return <span className="cep-situacao">Este CEP não tem bairro nem localidade cadastrados.</span>;
  }

  return (
    <SearchableSelect
      value={value ?? ""}
      onChange={onChange}
      options={consulta.opcoes}
      allowEmpty
      emptyLabel="Não informar"
      placeholder="Selecione o bairro ou a localidade"
    />
  );
}
