import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import {
  Building2,
  Dna,
  LayoutDashboard,
  LineChart,
  LogOut,
  MapPin,
  MapPinned,
  Menu,
  Milestone,
  Ruler,
  Scale,
  Stethoscope,
  Tags,
  UserCog,
  Users,
  Weight,
  Map as MapaIcon,
  X,
  Wheat,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import ErroNaTela from "./ErroNaTela";
import VacaIcon from "./VacaIcon";

// O menu tem tres blocos. "Nesta propriedade" so existe com uma propriedade
// aberta e mostra apenas dados dela; "Comparar" olha varias propriedades ao mesmo
// tempo (so as do usuario); "Cadastros" e a administracao, que nao depende do
// contexto (e cujas listas a API recorta pelo acesso de cada um).
const NA_PROPRIEDADE = [
  { to: "/dashboard", label: "Visão Geral", icon: LayoutDashboard },
  { to: "/animais", label: "Animais", icon: VacaIcon },
  { to: "/pesagens", label: "Pesagens", icon: Weight },
  { to: "/peso-comparativo", label: "Peso x ideal", icon: LineChart },
  { to: "/veterinarios", label: "Veterinários", icon: Stethoscope },
];

const COMPARAR = [{ to: "/comparativo", label: "Comparativo", icon: Scale }];

const CADASTROS = [
  { to: "/propriedades", label: "Propriedades", icon: Wheat },
  { to: "/pessoas", label: "Pessoas", icon: Users },
  { to: "/tipos-animal", label: "Tipos de Animal", icon: Tags },
  { to: "/racas", label: "Raças", icon: Dna },
  { to: "/padroes-peso", label: "Peso ideal por raça", icon: Ruler },
  { to: "/estados", label: "Estados", icon: MapaIcon },
  { to: "/cidades", label: "Cidades", icon: Building2 },
  { to: "/bairros", label: "Bairros", icon: Milestone },
  { to: "/localidades", label: "Localidades", icon: MapPinned },
  { to: "/ceps", label: "CEPs", icon: MapPin },
  // So o MASTER cadastra veterinarios e usuarios (ver "exigir_master" no backend).
  { to: "/cadastro-veterinarios", label: "Cadastro de Veterinários", icon: Stethoscope, soMaster: true },
  { to: "/usuarios", label: "Usuários", icon: UserCog, soMaster: true },
];

function iniciaisDe(nome) {
  return (nome ?? "")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte[0]?.toUpperCase())
    .join("");
}

export default function Layout() {
  const { usuario, logout, ehMaster, propriedade, propriedades, escolherPropriedade } = useAuth();
  const [menuAberto, setMenuAberto] = useState(false);

  const grupos = [
    propriedade && { titulo: "Nesta propriedade", links: NA_PROPRIEDADE },
    propriedades.length > 1 && { titulo: "Comparar", links: COMPARAR },
    { titulo: "Cadastros", links: CADASTROS.filter((l) => !l.soMaster || ehMaster) },
  ].filter(Boolean);

  return (
    <div className="app-shell">
      <header className="topbar">
        <button type="button" className="icon-btn" onClick={() => setMenuAberto(true)} aria-label="Abrir menu">
          <Menu size={20} />
        </button>
        <span className="brand">
          <span className="brand-mark">
            <VacaIcon size={20} />
          </span>
          {propriedade?.nome ?? "Controle Veterinário"}
        </span>
      </header>

      {menuAberto && <div className="sidebar-overlay" onClick={() => setMenuAberto(false)} />}

      <aside className={menuAberto ? "sidebar sidebar-open" : "sidebar"}>
        <div className="sidebar-head">
          <span className="brand">
            <span className="brand-mark">
              <VacaIcon size={20} />
            </span>
            Controle Veterinário
          </span>
          <button
            type="button"
            className="icon-btn sidebar-close"
            onClick={() => setMenuAberto(false)}
            aria-label="Fechar menu"
          >
            <X size={18} />
          </button>
        </div>

        {/* Propriedade aberta: e o contexto de tudo o que aparece em "Nesta propriedade". */}
        <div className="entidade-atual">
          {propriedades.length > 1 ? (
            <select
              value={propriedade?.id ?? ""}
              onChange={(e) => escolherPropriedade(e.target.value)}
              aria-label="Trocar de propriedade"
            >
              {!propriedade && <option value="">Escolha a propriedade</option>}
              {propriedades.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nome}
                </option>
              ))}
            </select>
          ) : (
            <span title={propriedade?.nome}>{propriedade?.nome ?? "Nenhuma propriedade"}</span>
          )}
        </div>

        <nav>
          {grupos.map((grupo) => (
            <div key={grupo.titulo} className="nav-grupo">
              <span className="nav-grupo-titulo">{grupo.titulo}</span>
              {grupo.links.map((link) => {
                const Icon = link.icon;
                return (
                  <NavLink
                    key={link.to}
                    to={link.to}
                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                    onClick={() => setMenuAberto(false)}
                  >
                    <Icon size={17} className="nav-icon" />
                    {link.label}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <NavLink
            to="/minha-conta"
            className="user-info"
            title={`Minha conta (${usuario?.papel_nome ?? ""})`}
            onClick={() => setMenuAberto(false)}
          >
            <span className="user-avatar">{iniciaisDe(usuario?.nome) || "?"}</span>
            <span className="user-name">{usuario?.nome}</span>
          </NavLink>
          <button type="button" className="icon-btn" onClick={logout} aria-label="Sair" title="Sair">
            <LogOut size={17} />
          </button>
        </div>
      </aside>
      <main className="content">
        {/* A barreira fica aqui dentro: se uma tela quebrar, o menu continua
            funcionando e da para navegar para outra. */}
        <ErroNaTela>
          <Outlet />
        </ErroNaTela>
      </main>
    </div>
  );
}
