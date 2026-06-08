from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server import LearnifyHandler, cleanup_sessions, init_db  # noqa: E402


init_db()
cleanup_sessions()


class handler(LearnifyHandler):
    def serve_static(self, request_path: str) -> None:
        self.send_error(404)
