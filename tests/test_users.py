from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


USER_DATA = {
    "email": "user@gmail.com",
    "password": "test1234",
    "full_name": "Test User"
}


async def _register_and_login(client: AsyncClient) -> str:
    with patch("app.tasks.tasks.send_registration_email.delay"), \
         patch("app.services.user_service.redis_client.set", new_callable=AsyncMock):
        await client.post("/auth/register", json=USER_DATA)

    with patch("app.services.auth_service.redis_client.set", new_callable=AsyncMock):
        response = await client.post("/auth/login", json={
            "email": USER_DATA["email"],
            "password": USER_DATA["password"]
        })

    return response.json()["access_token"]


async def test_update_user(client: AsyncClient):
    token = await _register_and_login(client)

    response = await client.patch(
        "/users/me",
        json={"full_name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


async def test_deactivate_user(client: AsyncClient):
    token = await _register_and_login(client)

    response = await client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204


async def test_add_payment_method(client: AsyncClient):
    token = await _register_and_login(client)

    response = await client.post(
        "/payment/method",
        json={"payment_id": "pm_test_123"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
