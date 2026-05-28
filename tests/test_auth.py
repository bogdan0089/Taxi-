from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


REGISTER_DATA = {
    "email": "test@gmail.com",
    "password": "test1234",
    "full_name": "Bohdan Test"
}


async def test_register(client: AsyncClient):
    with patch("app.tasks.tasks.send_registration_email.delay"), \
         patch("app.services.user_service.redis_client.set", new_callable=AsyncMock):
        response = await client.post("/auth/register", json=REGISTER_DATA)

    assert response.status_code == 201


async def test_register_duplicate_email(client: AsyncClient):
    with patch("app.tasks.tasks.send_registration_email.delay"), \
         patch("app.services.user_service.redis_client.set", new_callable=AsyncMock):
        await client.post("/auth/register", json=REGISTER_DATA)
        response = await client.post("/auth/register", json=REGISTER_DATA)

    assert response.status_code == 409


async def test_login(client: AsyncClient):
    with patch("app.tasks.tasks.send_registration_email.delay"), \
         patch("app.services.user_service.redis_client.set", new_callable=AsyncMock):
        await client.post("/auth/register", json=REGISTER_DATA)

    with patch("app.services.auth_service.redis_client.set", new_callable=AsyncMock):
        response = await client.post("/auth/login", json={
            "email": REGISTER_DATA["email"],
            "password": REGISTER_DATA["password"]
        })

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


async def test_login_wrong_password(client: AsyncClient):
    with patch("app.tasks.tasks.send_registration_email.delay"), \
         patch("app.services.user_service.redis_client.set", new_callable=AsyncMock):
        await client.post("/auth/register", json=REGISTER_DATA)

    response = await client.post("/auth/login", json={
        "email": REGISTER_DATA["email"],
        "password": "wrongpassword"
    })

    assert response.status_code == 400


async def test_logout(client: AsyncClient):
    with patch("app.tasks.tasks.send_registration_email.delay"), \
         patch("app.services.user_service.redis_client.set", new_callable=AsyncMock):
        await client.post("/auth/register", json=REGISTER_DATA)

    with patch("app.services.auth_service.redis_client.set", new_callable=AsyncMock):
        login = await client.post("/auth/login", json={
            "email": REGISTER_DATA["email"],
            "password": REGISTER_DATA["password"]
        })

    token = login.json()["access_token"]

    with patch("app.services.auth_service.redis_client.delete", new_callable=AsyncMock):
        response = await client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
