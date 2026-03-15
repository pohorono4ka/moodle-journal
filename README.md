# Электронный журнал преподавателя (MVP)

## Архитектура
- Backend: **FastAPI**
- Frontend: **React + Vite**
- Database: **PostgreSQL**
- Deploy: **Docker Compose**

## Структура проекта
```text
moodle-journal/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   ├── models/
│   │   └── services/
│   ├── alembic/
│   ├── seed_demo.py
│   └── Dockerfile
├── frontend/
│   └── src/
├── docker-compose.yml
└── .env.example
```

## Настройка .env для Moodle
```env
MOODLE_BASE_URL=https://your-moodle.example.com
MOODLE_TOKEN=your-moodle-token
MOODLE_SYNC_MODE=demo
MOODLE_TIMEOUT_SECONDS=30
```

- `MOODLE_SYNC_MODE=demo` — встроенный demo-режим синхронизации для текущего MVP.
- `MOODLE_SYNC_MODE=live` — реальный вызов Moodle REST Web Services.

> В live-режиме используется вызов `local_journal_export_structure` через `webservice/rest/server.php`.
> Для продакшена подключите/реализуйте этот webservice в Moodle (или адаптируйте функции клиента под ваши доступные wsfunction).

## Demo seed-данные
При старте backend выполняет:
1. `alembic upgrade head`
2. `python seed_demo.py`

Создаётся demo-структура: преподаватель, студенты, курсы, группы, дисциплины, типы оценивания, статусы посещаемости.

Тестовый преподаватель:
- `teacher@example.com`
- `Teacher123!`

## Запуск
```bash
cp .env.example .env
docker compose up --build
```

Открыть:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Endpoints

### Attendance
- `GET /api/v1/attendance/journal`
- `POST /api/v1/attendance/journal/save`
- `POST /api/v1/attendance/bulk-all-present`
- `POST /api/v1/attendance/`

### Grades
- `GET /api/v1/grades/journal`
- `POST /api/v1/grades/journal/save`
- `GET /api/v1/grades?discipline_id=<id>`
- `POST /api/v1/grades/`

### Moodle Sync
- `POST /api/v1/moodle-sync/run` — ручной запуск синхронизации
- `GET /api/v1/moodle-sync/runs/latest` — время/статус последней синхронизации
- `GET /api/v1/moodle-sync/runs` — список запусков
- `GET /api/v1/moodle-sync/runs/{run_id}` — детали запуска и entity-логи

### Reference Data
- `GET /api/v1/reference-data/academic-years`
- `GET /api/v1/reference-data/semesters`
- `GET /api/v1/reference-data/courses`
- `GET /api/v1/reference-data/groups`
- `GET /api/v1/reference-data/disciplines`
- `GET /api/v1/reference-data/grade-types`
- `GET /api/v1/reference-data/students?group_id=<id>`

## Как работает синхронизация Moodle
Сервисный слой (`app/services/moodle_sync.py`) включает:
1. `MoodleApiClient` для HTTP-запросов к Moodle REST API.
2. Загрузку и трансформацию данных (`demo` или `live`).
3. Upsert сущностей в PostgreSQL:
   - преподаватели,
   - студенты,
   - группы,
   - дисциплины,
   - курсы,
   - связки преподаватель–дисциплина–группа.
4. Логирование запусков в таблицы:
   - `moodle_sync_runs` (статус, время старта/завершения, summary),
   - `moodle_sync_logs` (по сущностям: processed/created/updated/errors).

Attendance и grades **не пишутся в Moodle**, хранятся только локально.


## UI: страница «Синхронизация Moodle»
1. Войдите под `teacher@example.com / Teacher123!`.
2. В левом меню откройте раздел `Синхронизация` (маршрут `/sync`).
3. На странице доступны:
   - текущий режим синхронизации (`demo/live`),
   - дата/время и статус последней синхронизации,
   - краткая статистика последнего запуска,
   - таблица последних запусков,
   - просмотр деталей запуска (сущности, created/updated/errors),
   - кнопка ручного запуска `Запустить синхронизацию`.
4. Нажмите `Запустить синхронизацию`.
5. Проверьте, что в таблице появился новый run и в деталях видны обработанные сущности.

## Проверка синхронизации (MVP)
1. Войти под `teacher@example.com / Teacher123!`.
2. Вызвать `POST /api/v1/moodle-sync/run` через Swagger.
3. Проверить `GET /api/v1/moodle-sync/runs/latest`.
4. Получить детали `GET /api/v1/moodle-sync/runs/{run_id}`.
5. Проверить данные в БД:
```bash
docker compose exec db psql -U moodle -d moodle_journal -c "SELECT id, moodle_id, email, full_name FROM users ORDER BY id;"
docker compose exec db psql -U moodle -d moodle_journal -c "SELECT id, moodle_id, code, course_id FROM groups ORDER BY id;"
docker compose exec db psql -U moodle -d moodle_journal -c "SELECT run_id, entity_name, processed_count, created_count, updated_count, error_count FROM moodle_sync_logs ORDER BY id DESC;"
```

## Ручная проверка: attendance
1. Открыть `Журнал посещаемости`.
2. Выбрать параметры и дату.
3. Нажать `Открыть журнал`, изменить статусы, нажать `Сохранить`.

## Ручная проверка: grades
1. Открыть `Журнал оценок`.
2. Выбрать параметры и дату.
3. Нажать `Открыть журнал`, изменить значения, нажать `Сохранить оценки`.
4. Перезагрузить журнал и убедиться, что значения сохранены.

## Защита от дублей
- Attendance: `uq_attendance_row`.
- Grades: `uq_grade_row`.
- Teacher-discipline-group links: `uq_teacher_discipline_group`.
