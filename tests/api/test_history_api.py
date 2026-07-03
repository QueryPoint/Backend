
"""История поиска в текущей реализации доступна только на очистку.
Этот тест документирует фактический контракт и защищает от незаметной регрессии."""
from pathlib import Path

def test_history_read_endpoint_is_not_implemented_yet():
    source=(Path(__file__).resolve().parents[2]/'src/api/search/router.py').read_text(encoding='utf-8')
    assert '@router.delete("/history"' in source
    assert '@router.get("/history"' not in source
