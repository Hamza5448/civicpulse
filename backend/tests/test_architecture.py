from pathlib import Path


def test_routes_do_not_open_database_sessions_or_execute_sql() -> None:
    routes = Path(__file__).parents[1] / "app" / "routes"
    route_source = "\n".join(path.read_text(encoding="utf-8") for path in routes.glob("*.py"))
    assert "session_factory" not in route_source
    assert "sqlalchemy" not in route_source
    assert "SELECT " not in route_source
