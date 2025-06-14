from types import SimpleNamespace, ModuleType
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

if "requests" not in sys.modules:
    requests_stub = ModuleType("requests")
    requests_stub.get = lambda *a, **k: None
    sys.modules["requests"] = requests_stub

if "dotenv" not in sys.modules:
    dotenv_stub = ModuleType("dotenv")
    dotenv_stub.load_dotenv = lambda: None
    sys.modules["dotenv"] = dotenv_stub


import src.fetcher as fetcher


def test_fetch_json(monkeypatch, tmp_path):
    path = tmp_path / "cache"
    path.mkdir()
    fetcher.CACHE_DIR = path

    def fake_get(url, headers=None):
        resp = SimpleNamespace()
        resp.status_code = 200
        resp.json = lambda: {"url": url}
        resp.raise_for_status = lambda: None
        return resp

    monkeypatch.setattr(fetcher.requests, "get", fake_get)
    data = fetcher.fetch_json("https://example.com", "test", use_cache=False)
    assert data["url"] == "https://example.com"
