import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import {
  Building2,
  LayoutDashboard,
  LogOut,
  MapPin,
  MapPinned,
  Menu,
  Milestone,
  Stethoscope,
  Tags,
  UserCog,
  Users,
  Map as MapaIcon,
  X,
  Wheat,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import ErroNaTela from "./ErroNaTela";
import VacaIcon from "./VacaIcon";

const LINKS = [
  { to: "/dashboard", label: "Visão Geral", icon: LayoutDashboard },
  { to: "/propriedades", label: "Propriedades", icon: Wheat },
  { to: "/animais", label: "Animais", icon: VacaIcon },
  { to: "/veterinarios", label: "Veterinários", icon: Stethoscope },
  { to: "/pessoas", label: "Pessoas", icon: Users },
  { to: "/tipos-animal", label: "Tipos de Animal", icon: Tags },
  { to: "/estados", label: "Estados", icon: MapaIcon },
  { to: "/cidades", label: "Cidades", icon: Building2 },
  { to: "/bairros", label: "Bairros", icon: Milestone },
  { to: "/localidades", label: "Localidades", icon: MapPinned },
  { to: "/ceps", label: "CEPs", icon: MapPin },
  // So o MASTER gerencia usuarios (ver "exigir_master" no backend).
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
  const { usuario, logout, ehMaster } = useAuth();
  const [menuAberto, setMenuAberto] = useState(false);
  const links = LINKS.filter((l) => !l.soMaster || ehMaster);

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
          Controle Veterinário
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

        <nav>
          {links.map((link) => {
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
