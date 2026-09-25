import CrudPage from "../components/CrudPage";
import { useAuth } from "../context/AuthContext";
import { formatarTelefone } from "../utils/format";

// Veterinarios que atendem a propriedade aberta. Tela so de consulta: quem os
// cadastra e o MASTER (Cadastro de Veterinarios) e quem administra a propriedade
// os vincula em Propriedades.
const columns = [
  { key: "nome", label: "Veterinário" },
  { key: "usuario_email", label: "Login", opcional: true },
  { key: "telefone_principal", label: "Telefone", render: (v) => (v ? formatarTelefone(v) : "-") },
  { key: "ativo", label: "Situação", render: (v) => (v ? "Ativo" : "Inativo") },
];

export default function VeterinariosPage() {
  const { propriedade } = useAuth();
  return (
    <CrudPage
      larga
      somenteLeitura
      resource="veterinarios"
      params={{ propriedade_id: propriedade.id }}
      title={`Veterinários — ${propriedade.nome}`}
      fields={[]}
      columns={columns}
      campoBusca="nome"
    />
  );
}
