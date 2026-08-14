import asyncio

from backend.app.main import health


def test_health_contract():
    assert asyncio.run(health()) == {"status": "ok"}
