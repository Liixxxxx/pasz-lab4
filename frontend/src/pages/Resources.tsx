import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { api, ApiError, clearToken, getToken } from '../api'

type Me = { id: number; login: string; clearance: string }
type Item = { id: number; title: string; classification: string; allowed: boolean }
type Resource = { id: number; title: string; classification: string; content: string }

export default function Resources() {
  const navigate = useNavigate()
  const [me, setMe] = useState<Me | null>(null)
  const [items, setItems] = useState<Item[]>([])
  const [opened, setOpened] = useState<Resource | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!getToken()) {
      navigate('/login')
      return
    }
    Promise.all([api<Me>('/me'), api<Item[]>('/resources')])
      .then(([meData, list]) => {
        setMe(meData)
        setItems(list)
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          clearToken()
          navigate('/login')
        } else {
          setError(err.message)
        }
      })
  }, [navigate])

  async function open(item: Item) {
    setError('')
    setOpened(null)
    try {
      setOpened(await api<Resource>(`/resources/${item.id}`))
    } catch (err) {
      const text = err instanceof Error ? err.message : 'ошибка'
      setError(`«${item.title}»: ${text}`)
    }
  }

  function logout() {
    clearToken()
    navigate('/login')
  }

  if (!me) {
    return <p>{error || 'Загрузка...'}</p>
  }

  return (
    <section>
      <h1>Ресурсы</h1>
      <p>
        Пользователь: <b>{me.login}</b>, уровень допуска: <b>{me.clearance}</b>{' '}
        <button type="button" onClick={logout}>
          Выйти
        </button>
      </p>
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>Гриф</th>
            <th>Доступ</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>{item.title}</td>
              <td>{item.classification}</td>
              <td className={item.allowed ? 'ok' : 'error'}>{item.allowed ? 'есть' : 'нет'}</td>
              <td>
                <button type="button" onClick={() => open(item)}>
                  Открыть
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {error && <p className="error">{error}</p>}
      {opened && (
        <div className="card">
          <h2>{opened.title}</h2>
          <p>Гриф: {opened.classification}</p>
          <p>{opened.content}</p>
        </div>
      )}
    </section>
  )
}
