from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock


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


async def _empty_scan(*args, **kwargs):
    return
    yield


async def _create_completed_trip(client: AsyncClient, passenger_token: str, driver_token: str, driver_id: int) -> int:
    with patch("app.services.trip_service.redis_client.georadius", new_callable=AsyncMock, return_value=[f"driver:{driver_id}".encode()]):
        trip = await client.post("/trips/", json=TRIP_DATA, headers={"Authorization": f"Bearer {passenger_token}"})

    await client.post("/payment/method", json={"payment_id": "pm_test_123"}, headers={"Authorization": f"Bearer {passenger_token}"})

    trip_id = trip.json()["id"]

    with patch("app.services.trip_service.redis_client.scan_iter", new=_empty_scan), \
         patch("app.services.trip_service.redis_client.unlink", new_callable=AsyncMock), \
         patch("app.services.stripe_service.stripe.PaymentIntent.create", return_value=MagicMock(id="pi_test", status="succeeded")):
        await client.post(f"/trips/{trip_id}/complete", headers={"Authorization": f"Bearer {driver_token}"})

    return trip_id


async def test_create_rating(client: AsyncClient):
    passenger_token = await _register_and_login(client, PASSENGER_DATA)
    driver_token = await _register_and_login(client, DRIVER_DATA)

    trip_id = await _create_completed_trip(client, passenger_token, driver_token, driver_id=2)

    with patch("app.services.rating_service.redis_client.delete", new_callable=AsyncMock):
        response = await client.post(
            f"/ratings/?trip_id={trip_id}",
            json={"driver_id": 2, "score": 5},
            headers={"Authorization": f"Bearer {passenger_token}"}
        )

    assert response.status_code == 200
    assert response.json()["score"] == 5


async def test_create_rating_trip_not_completed(client: AsyncClient):
    passenger_token = await _register_and_login(client, PASSENGER_DATA)
    await _register_and_login(client, DRIVER_DATA)

    with patch("app.services.trip_service.redis_client.georadius", new_callable=AsyncMock, return_value=[b"driver:2"]):
        trip = await client.post("/trips/", json=TRIP_DATA, headers={"Authorization": f"Bearer {passenger_token}"})

    trip_id = trip.json()["id"]

    response = await client.post(
        f"/ratings/?trip_id={trip_id}",
        json={"driver_id": 2, "score": 5},
        headers={"Authorization": f"Bearer {passenger_token}"}
    )

    assert response.status_code == 400


async def test_create_rating_duplicate(client: AsyncClient):
    passenger_token = await _register_and_login(client, PASSENGER_DATA)
    driver_token = await _register_and_login(client, DRIVER_DATA)

    trip_id = await _create_completed_trip(client, passenger_token, driver_token, driver_id=2)

    with patch("app.services.rating_service.redis_client.delete", new_callable=AsyncMock):
        await client.post(
            f"/ratings/?trip_id={trip_id}",
            json={"driver_id": 2, "score": 5},
            headers={"Authorization": f"Bearer {passenger_token}"}
        )
        response = await client.post(
            f"/ratings/?trip_id={trip_id}",
            json={"driver_id": 2, "score": 4},
            headers={"Authorization": f"Bearer {passenger_token}"}
        )

    assert response.status_code == 409


async def test_get_avg_rating(client: AsyncClient):
    passenger_token = await _register_and_login(client, PASSENGER_DATA)
    driver_token = await _register_and_login(client, DRIVER_DATA)

    trip_id = await _create_completed_trip(client, passenger_token, driver_token, driver_id=2)

    with patch("app.services.rating_service.redis_client.delete", new_callable=AsyncMock):
        await client.post(
            f"/ratings/?trip_id={trip_id}",
            json={"driver_id": 2, "score": 5},
            headers={"Authorization": f"Bearer {passenger_token}"}
        )

    with patch("app.services.rating_service.redis_client.get", new_callable=AsyncMock, return_value=None), \
         patch("app.services.rating_service.redis_client.set", new_callable=AsyncMock):
        response = await client.get(
            "/ratings/driver/2/avg",
            headers={"Authorization": f"Bearer {driver_token}"}
        )

    assert response.status_code == 200
    assert float(response.json()) == 5.0
