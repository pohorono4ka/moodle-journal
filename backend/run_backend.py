"""Run backend in two modes:
1) Full mode (FastAPI + Uvicorn) when dependencies are installed.
2) Offline MVP fallback (stdlib HTTP server) for restricted environments.
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class OfflineHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health':
            self._send_json({
                'status': 'ok',
                'mode': 'offline-fallback',
                'message': 'Install backend/requirements.txt to run full FastAPI mode.'
            })
            return
        self._send_json({'detail': 'Not Found'}, status=404)


def run_offline_server(host: str = '0.0.0.0', port: int = 8000):
    server = ThreadingHTTPServer((host, port), OfflineHandler)
    print(f'Backend started in offline fallback mode at http://{host}:{port}')
    server.serve_forever()


def run():
    try:
        import uvicorn  # type: ignore
        from app.main import app

        uvicorn.run(app, host='0.0.0.0', port=8000, reload=False)
    except ModuleNotFoundError as exc:
        print(f'[WARN] Full backend dependencies are unavailable: {exc}')
        run_offline_server()


if __name__ == '__main__':
    run()
