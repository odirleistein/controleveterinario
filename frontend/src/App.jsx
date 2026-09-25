import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import AnimaisPage from "./pages/AnimaisPage";
import DashboardPage from "./pages/DashboardPage";
import Login from "./pages/Login";
import MinhaContaPage from "./pages/MinhaContaPage";
import PropriedadesPage from "./pages/PropriedadesPage";
import Registrar from "./pages/Registrar";
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
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/propriedades" element={<PropriedadesPage />} />
              <Route path="/animais" element={<AnimaisPage />} />
              <Route path="/veterinarios" element={<VeterinariosPage />} />
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
