import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { apiClient } from '../api/client'

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const onSubmit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      const response = await apiClient.post('/auth/login', { email, password })
      window.localStorage.setItem('access_token', response.data.access_token)
      navigate('/attendance')
    } catch (_apiError) {
      setError('Ошибка входа. Проверьте логин и пароль.')
    }
  }

  return (
    <form className="centered-card" onSubmit={onSubmit}>
      <h1>Вход в систему</h1>
      <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input placeholder="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      {error && <p className="error-text">{error}</p>}
      <button type="submit">Войти</button>
    </form>
  )
}
