from httpx import AsyncClient

TICKET_PAYLOAD = {
    "title": "Не работает вход",
    "description": "После смены пароля пользователь не может войти в систему",
    "source": "email",
}


async def test_create_ticket(client: AsyncClient) -> None:
    response = await client.post("/tickets", json=TICKET_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["title"] == TICKET_PAYLOAD["title"]
    assert body["description"] == TICKET_PAYLOAD["description"]
    assert body["source"] == TICKET_PAYLOAD["source"]
    assert body["status"] == "new"
    assert body["created_at"]


async def test_get_ticket(client: AsyncClient) -> None:
    created = (await client.post("/tickets", json=TICKET_PAYLOAD)).json()

    response = await client.get(f"/tickets/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


async def test_get_ticket_not_found(client: AsyncClient) -> None:
    response = await client.get("/tickets/999999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found"}


async def test_create_ticket_empty_title(client: AsyncClient) -> None:
    response = await client.post("/tickets", json={**TICKET_PAYLOAD, "title": ""})

    assert response.status_code == 422
