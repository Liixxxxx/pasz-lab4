import { Navigate, NavLink, Route, Routes } from 'react-router'
import Login from './pages/Login'
import Register from './pages/Register'
import Resources from './pages/Resources'

export default function App() {
  return (
    <div className="page">
      <nav>
        <NavLink to="/register">Регистрация</NavLink>
        <NavLink to="/login">Вход</NavLink>
        <NavLink to="/resources">Ресурсы</NavLink>
      </nav>
      <Routes>
        <Route path="/" element={<Navigate to="/register" replace />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/resources" element={<Resources />} />
      </Routes>
    </div>
  )
}
