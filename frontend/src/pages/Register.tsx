import { useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api'

type Status = { ok: boolean; text: string }

export default function Register() {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus] = useState<Status | null>(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setStatus(null)
    try {
      const data = await api<{ message: string }>('/register', {
        method: 'POST',
        body: JSON.stringify({ login, password }),
      })
      setStatus({ ok: true, text: data.message })
      setPassword('')
    } catch (err) {
      setStatus({ ok: false, text: err instanceof Error ? err.message : 'неизвестная ошибка' })
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Регистрация</h1>
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
          autoComplete="new-password"
          required
        />
      </label>
      <p className="hint">
        Пароль: от 8 символов, заглавная и строчная латинские буквы, цифра и спецсимвол.
      </p>
      <button disabled={busy}>Зарегистрироваться</button>
      {status && <p className={status.ok ? 'ok' : 'error'}>{status.text}</p>}
    </form>
  )
}
