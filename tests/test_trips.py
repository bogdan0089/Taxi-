from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


PASSENGER_DATA = {
    "email": "passenger@gmail.com",
    "password": "test1234",
    "full_name": "Passenger Test"
}

DRIVER_DATA = {
    "email": "driver@gmail.com",
    "password": "test1234",
    "full_name": "Driver Test",
    "role": "driver"
}

TRIP_DATA = {
    "pickup_address": "Khreshchatyk 1",
    "dropoff_address": "Boryspil Airport",
    "pickup_lat": 50.4501,
    "pickup_lon": 30.5234,
    "dropoff_lat": 50.3450,
    "dropoff_lon": 30.8947
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


async def test_create_trip(client: AsyncClient):
    token = await _register_and_login(client, PASSENGER_DATA)

    with patch("app.services.trip_service.redis_client.georadius", new_callable=AsyncMock, return_value=[b"driver:1"]), \
         patch("app.services.trip_service.redis_client.scan_iter") as mock_scan, \
         patch("app.services.trip_service.redis_client.unlink", new_callable=AsyncMock):
        mock_scan.return_value.__aiter__ = lambda s: iter([])
        response = await client.post("/trips/", json=TRIP_DATA, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200


async def test_create_trip_no_drivers(client: AsyncClient):
    token = await _register_and_login(client, PASSENGER_DATA)

    with patch("app.services.trip_service.redis_client.georadius", new_callable=AsyncMock, return_value=[]):
        response = await client.post("/trips/", json=TRIP_DATA, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404


async def test_get_my_trips(client: AsyncClient):
    token = await _register_and_login(client, PASSENGER_DATA)

    with patch("app.services.trip_service.redis_client.get", new_callable=AsyncMock, return_value=None), \
         patch("app.services.trip_service.redis_client.set", new_callable=AsyncMock):
        response = await client.get("/trips/my", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code in [200, 404]
