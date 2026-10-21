from unittest.mock import MagicMock

import pytest

import main

CONDOS = {
    "gnovit": {
        "url": "https://pbx.test:8099",
        "origin": "1000",
        "destination": {"101": "5548999990101", "102": "5548999990102"},
        "username": "user",
        "password": "secret",
        "condo_id": "123456",
    },
}

BACKEND_API = {
    "base_url": "https://backend.test/",
    "username": "api-user",
    "password": "api-secret",
    "ignore-ssl-certificate-check": False,
    "endpoints": {
        "originate": "v1/originate",
        "blocks_units_by_condo": "v1/condo/{condo_id}/blocks_units",
    },
}


@pytest.fixture
def fake_ui(monkeypatch):
    """Replaces nicegui's `ui` in main with a mock, so pages run without a client."""
    ui = MagicMock()
    monkeypatch.setattr(main, "ui", ui)
    return ui


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setattr(main, "condos", CONDOS)
    monkeypatch.setattr(main, "backend_api", dict(BACKEND_API))
    return main


def response(status_code=200, json_data=None):
    r = MagicMock(status_code=status_code)
    r.json.return_value = json_data
    return r


def on_click_of(ui_mock, label):
    """Returns the on_click callback of the ui.button created with `label`."""
    for call in ui_mock.button.call_args_list:
        if call.args and call.args[0] == label:
            return call.kwargs["on_click"]
    raise AssertionError(f"no button labeled {label!r}")
