from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


USER_DATA = {
    "email": "user@gmail.com",
    "password": "test1234",
    "full_name": "Test User"
}

ADMIN_DATA = {
    "email": "admin@gmail.com",
    "password": "test1234",
    "full_name": "Admin User",
    "role": "admin"
}


async def _register_and_login(client: AsyncClient, data: dict) -> str:
    with patch("app.tasks.tasks.send_registration_email.delay"), \
         patch("app.services.user_service.redis_client.set", new_callable=AsyncMock):
        await client.post("/auth/register", json=data)

    with patch("app.services.auth_service.redis_client.set", new_callable=AsyncMock):
        response = await client.post("/auth/login", json={
            "email": data["email"],
            "password": data["password"]
        })

    return response.json()["access_token"]


async def test_admin_get_users(client: AsyncClient, session):
    await _register_and_login(client, USER_DATA)
    admin_token = await _register_and_login(client, ADMIN_DATA)

    with patch("app.services.user_service.redis_client.get", new_callable=AsyncMock, return_value=None), \
         patch("app.services.user_service.redis_client.set", new_callable=AsyncMock):
        response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_admin_get_users_forbidden(client: AsyncClient):
    token = await _register_and_login(client, USER_DATA)

    response = await client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


async def test_admin_get_trips(client: AsyncClient):
    admin_token = await _register_and_login(client, ADMIN_DATA)

    with patch("app.services.trip_service.redis_client.get", new_callable=AsyncMock, return_value=None):
        response = await client.get(
            "/admin/trips",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

    assert response.status_code == 404


async def test_admin_get_active_verified(client: AsyncClient):
    admin_token = await _register_and_login(client, ADMIN_DATA)

    response = await client.get(
        "/admin/active/verified",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404
