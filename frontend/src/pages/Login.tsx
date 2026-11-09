import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router'
import { api, setToken } from '../api'

export default function Login() {
  const navigate = useNavigate()
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const data = await api<{ access_token: string }>('/login', {
        method: 'POST',
        body: JSON.stringify({ login, password }),
      })
      setToken(data.access_token)
      navigate('/resources')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'неизвестная ошибка')
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Вход</h1>
      <label>
        Логин
        <input value={login} onChange={(e) => setLogin(e.target.value)} autoComplete="username" required />
      </label>
      <label>
        Пароль
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
      </label>
      <button disabled={busy}>Войти</button>
      {error && <p className="error">{error}</p>}
    </form>
  )
}
