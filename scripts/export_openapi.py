import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import Settings
from app.main import create_app


def main() -> None:
    app = create_app(
        Settings(
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/15",
            triage_provider="simulated",
        )
    )
    destination = ROOT / "backend" / "openapi.json"
    destination.write_text(
        json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
