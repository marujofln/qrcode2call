import asyncio

import pytest

import main

from conftest import CONDOS, response

CONDO = CONDOS["gnovit"]


@pytest.fixture
def io_bound(monkeypatch):
    """Captures the blocking call handed to run.io_bound and returns a canned response."""
    captured = {"response": response(200)}

    async def fake_io_bound(func, *args, **kwargs):
        captured.update(func=func, args=args, kwargs=kwargs)
        return captured["response"]

    monkeypatch.setattr(main.run, "io_bound", fake_io_bound)
    return captured


def test_requests_originate_with_condo_credentials(fake_ui, io_bound):
    asyncio.run(main.handle_originate(CONDO, "1101", "5548999999999"))

    assert io_bound["func"] is main.requests.get
    assert io_bound["args"] == (
        "https://pbx.test:8099/v1/originate?origin=1101&destination=5548999999999",
    )
    assert io_bound["kwargs"] == {
        "timeout": 20,
        "auth": ("user", "secret"),
        "verify": False,
    }


def test_success_notifies_info(fake_ui, io_bound):
    asyncio.run(main.handle_originate(CONDO, "1101", "5548999999999"))

    fake_ui.notification.return_value.dismiss.assert_called_once()
    fake_ui.notify.assert_called_once()
    assert fake_ui.notify.call_args.kwargs["type"] == "info"


def test_failure_notifies_status_code(fake_ui, io_bound):
    io_bound["response"] = response(503)

    asyncio.run(main.handle_originate(CONDO, "1101", "5548999999999"))

    fake_ui.notification.return_value.dismiss.assert_called_once()
    message = fake_ui.notify.call_args.args[0]
    assert "503" in message
    assert fake_ui.notify.call_args.kwargs["type"] == "negative"


def test_uses_credentials_of_the_given_condo(fake_ui, io_bound):
    other = {"url": "https://other.test", "username": "u2", "password": "p2"}

    asyncio.run(main.handle_originate(other, "2201", "5548888888888"))

    assert io_bound["args"][0].startswith("https://other.test/v1/originate?")
    assert io_bound["kwargs"]["auth"] == ("u2", "p2")
