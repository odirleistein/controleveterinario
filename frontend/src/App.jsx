import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import RequerPropriedade from "./components/RequerPropriedade";
import { AuthProvider } from "./context/AuthContext";
import AnimaisPage from "./pages/AnimaisPage";
import ComparativoPage from "./pages/ComparativoPage";
import DashboardPage from "./pages/DashboardPage";
import EscolherPropriedadePage from "./pages/EscolherPropriedadePage";
import Login from "./pages/Login";
import MinhaContaPage from "./pages/MinhaContaPage";
import PropriedadesPage from "./pages/PropriedadesPage";
import Registrar from "./pages/Registrar";
import VeterinariosCadastroPage from "./pages/VeterinariosCadastroPage";
import VeterinariosPage from "./pages/VeterinariosPage";
import BairrosPage from "./pages/cadastros/BairrosPage";
import CepsPage from "./pages/cadastros/CepsPage";
import CidadesPage from "./pages/cadastros/CidadesPage";
import EstadosPage from "./pages/cadastros/EstadosPage";
import LocalidadesPage from "./pages/cadastros/LocalidadesPage";
import PessoasPage from "./pages/cadastros/PessoasPage";
import TiposAnimalPage from "./pages/cadastros/TiposAnimalPage";
import UsuariosPage from "./pages/cadastros/UsuariosPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/registrar" element={<Registrar />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="/escolher-propriedade" element={<EscolherPropriedadePage />} />
              {/* Telas de UMA propriedade: sem ela aberta, voltam para a escolha. */}
              <Route element={<RequerPropriedade />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/animais" element={<AnimaisPage />} />
                <Route path="/veterinarios" element={<VeterinariosPage />} />
              </Route>
              <Route path="/comparativo" element={<ComparativoPage />} />
              <Route path="/propriedades" element={<PropriedadesPage />} />
              <Route path="/cadastro-veterinarios" element={<VeterinariosCadastroPage />} />
              <Route path="/pessoas" element={<PessoasPage />} />
              <Route path="/tipos-animal" element={<TiposAnimalPage />} />
              <Route path="/estados" element={<EstadosPage />} />
              <Route path="/cidades" element={<CidadesPage />} />
              <Route path="/bairros" element={<BairrosPage />} />
              <Route path="/localidades" element={<LocalidadesPage />} />
              <Route path="/ceps" element={<CepsPage />} />
              <Route path="/usuarios" element={<UsuariosPage />} />
              <Route path="/minha-conta" element={<MinhaContaPage />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
