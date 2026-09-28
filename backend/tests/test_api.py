import pytest

from app.db.models.complaint import ComplaintStatus


def payload() -> dict[str, str]:
    return {"text": "Burst water main flooding Street 12", "location": "Street 12"}


@pytest.mark.asyncio
async def test_health_does_not_require_database(client) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["x-request-id"]


@pytest.mark.asyncio
async def test_ready_checks_database(client) -> None:
    response = await client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.asyncio
async def test_provider_meta_exposes_active_provider_and_recent_outcomes(client) -> None:
    await client.post("/api/complaints", json=payload())
    response = await client.get("/api/meta/providers")
    assert response.status_code == 200
    assert response.json()["active_provider"] == "rules"
    assert response.json()["recent_outcomes"][0]["provider"] == "rules"
    assert response.json()["recent_outcomes"][0]["fallback"] is False


@pytest.mark.asyncio
async def test_create_complaint(client) -> None:
    response = await client.post("/api/complaints", json=payload())
    assert response.status_code == 201
    assert response.json()["status"] == ComplaintStatus.OPEN.value


@pytest.mark.asyncio
async def test_create_validation_error_is_field_level(client) -> None:
    response = await client.post("/api/complaints", json={"text": "short", "location": "x"})
    assert response.status_code == 400
    assert "detail" in response.json()
    assert isinstance(response.json()["detail"], list)


@pytest.mark.asyncio
async def test_get_existing_complaint(client) -> None:
    created = await client.post("/api/complaints", json=payload())
    response = await client.get(f"/api/complaints/{created.json()['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created.json()["id"]


@pytest.mark.asyncio
async def test_get_missing_complaint(client) -> None:
    response = await client.get("/api/complaints/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_complaints_with_pagination(client) -> None:
    await client.post("/api/complaints", json=payload())
    response = await client.get("/api/complaints?page=1&page_size=1")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert len(response.json()["items"]) == 1


@pytest.mark.asyncio
async def test_status_update_and_invalid_transition(client) -> None:
    created = await client.post("/api/complaints", json=payload())
    complaint_id = created.json()["id"]
    response = await client.patch(
        f"/api/complaints/{complaint_id}/status", json={"status": "in_progress"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    await client.patch(f"/api/complaints/{complaint_id}/status", json={"status": "resolved"})
    invalid = await client.patch(f"/api/complaints/{complaint_id}/status", json={"status": "open"})
    assert invalid.status_code == 409
    assert "resolved -> open" in invalid.json()["detail"]
