import { useEffect, useMemo, useState } from 'react'

import { apiClient } from '../api/client'

function formatDateTime(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('ru-RU')
}

function parseSummary(summary) {
  if (!summary) return null
  try {
    return JSON.parse(summary)
  } catch {
    return null
  }
}

export default function SyncPage() {
  const [config, setConfig] = useState(null)
  const [latest, setLatest] = useState(null)
  const [runs, setRuns] = useState([])
  const [selectedRun, setSelectedRun] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const loadSyncData = async () => {
    setLoading(true)
    setError('')
    try {
      const [configResp, latestResp, runsResp] = await Promise.all([
        apiClient.get('/moodle-sync/config'),
        apiClient.get('/moodle-sync/runs/latest'),
        apiClient.get('/moodle-sync/runs', { params: { limit: 10 } }),
      ])

      setConfig(configResp.data)
      setLatest(latestResp.data)
      setRuns(runsResp.data)

      if (runsResp.data.length > 0) {
        const detail = await apiClient.get(`/moodle-sync/runs/${runsResp.data[0].run_id}`)
        setSelectedRun(detail.data)
      } else {
        setSelectedRun(null)
      }
    } catch (apiError) {
      console.error(apiError)
      setError('Не удалось загрузить данные синхронизации Moodle.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSyncData()
  }, [])

  const runSync = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await apiClient.post('/moodle-sync/run')
      await loadSyncData()
      setSelectedRun(response.data)
    } catch (apiError) {
      console.error(apiError)
      setError('Не удалось выполнить синхронизацию Moodle.')
    } finally {
      setLoading(false)
    }
  }

  const openRunDetails = async (runId) => {
    setLoading(true)
    try {
      const detail = await apiClient.get(`/moodle-sync/runs/${runId}`)
      setSelectedRun(detail.data)
    } catch (apiError) {
      console.error(apiError)
      setError('Не удалось загрузить детали запуска синхронизации.')
    } finally {
      setLoading(false)
    }
  }

  const summary = useMemo(() => parseSummary(selectedRun?.summary), [selectedRun])

  return (
    <section>
      <h1>Синхронизация Moodle</h1>
      {error && <p className="error-text">{error}</p>}

      <div className="sync-card-grid">
        <article className="sync-card">
          <h3>Текущая конфигурация</h3>
          <p><b>Режим:</b> {config?.mode || '—'}</p>
          <p><b>Moodle URL:</b> {config?.base_url || '—'}</p>
          <button onClick={runSync} disabled={loading}>{loading ? 'Выполнение...' : 'Запустить синхронизацию'}</button>
        </article>

        <article className="sync-card">
          <h3>Последняя синхронизация</h3>
          <p><b>Дата и время:</b> {formatDateTime(latest?.last_sync_at)}</p>
          <p><b>Статус:</b> {latest?.last_status || '—'}</p>
          <p><b>Run ID:</b> {latest?.last_run_id ?? '—'}</p>
        </article>

        <article className="sync-card">
          <h3>Краткая статистика последнего запуска</h3>
          {!summary && <p>Нет данных.</p>}
          {summary && (
            <ul>
              {Object.entries(summary).map(([entity, stat]) => (
                <li key={entity}>
                  <b>{entity}</b>: обработано {stat.processed}, создано {stat.created}, обновлено {stat.updated}, ошибок {stat.errors}
                </li>
              ))}
            </ul>
          )}
        </article>
      </div>

      <div className="sync-layout">
        <article className="sync-card">
          <h3>Последние запуски</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Режим</th>
                  <th>Статус</th>
                  <th>Старт</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr key={run.run_id}>
                    <td>{run.run_id}</td>
                    <td>{run.mode}</td>
                    <td>{run.status}</td>
                    <td>{formatDateTime(run.started_at)}</td>
                    <td>
                      <button onClick={() => openRunDetails(run.run_id)} disabled={loading}>Детали</button>
                    </td>
                  </tr>
                ))}
                {runs.length === 0 && (
                  <tr><td colSpan={5}>Запусков пока нет.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </article>

        <article className="sync-card">
          <h3>Детали запуска</h3>
          {!selectedRun && <p>Выберите запуск.</p>}
          {selectedRun && (
            <>
              <p><b>Run ID:</b> {selectedRun.run_id}</p>
              <p><b>Статус:</b> {selectedRun.status}</p>
              <p><b>Старт:</b> {formatDateTime(selectedRun.started_at)}</p>
              <p><b>Завершение:</b> {formatDateTime(selectedRun.finished_at)}</p>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Сущность</th>
                      <th>Обработано</th>
                      <th>Создано</th>
                      <th>Обновлено</th>
                      <th>Ошибки</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedRun.entities.map((entity) => (
                      <tr key={entity.entity_name}>
                        <td>{entity.entity_name}</td>
                        <td>{entity.processed_count}</td>
                        <td>{entity.created_count}</td>
                        <td>{entity.updated_count}</td>
                        <td>{entity.error_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {selectedRun.entities.some((e) => e.errors) && (
                <details>
                  <summary>Ошибки</summary>
                  {selectedRun.entities.filter((e) => e.errors).map((e) => (
                    <pre key={e.entity_name}>{e.entity_name}: {e.errors}</pre>
                  ))}
                </details>
              )}
            </>
          )}
        </article>
      </div>
    </section>
  )
}
