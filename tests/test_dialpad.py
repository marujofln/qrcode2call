from main import Dialpad

from conftest import on_click_of


def test_insert_number_appends_digits():
    d = Dialpad({})
    d.insert_number("4")
    d.insert_number(8)

    assert d.destination == "48"


def test_remove_number_drops_last_digit():
    d = Dialpad({})
    d.destination = "489"
    d.remove_number()

    assert d.destination == "48"


def test_remove_number_on_empty_destination():
    d = Dialpad({})
    d.remove_number()

    assert d.destination == ""


def test_dialpad_buttons_edit_destination(fake_ui):
    d = Dialpad({})
    d.setup_dialpad_card(fake_ui.card(), origin="1101")

    on_click_of(fake_ui, "5")()
    on_click_of(fake_ui, "0")()
    on_click_of(fake_ui, "7")()
    on_click_of(fake_ui, "<-")()

    assert d.destination == "50"
    assert d.origin == "1101"


def test_dialpad_call_button_originates_from_unit_to_typed_number(fake_ui, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "main.handle_originate", lambda condo, o, dest: calls.append((condo, o, dest))
    )
    condo = {"condo_id": "123456"}
    d = Dialpad(condo)
    d.setup_dialpad_card(fake_ui.card(), origin="1101")
    d.destination = "5548999999999"

    on_click_of(fake_ui, "->")()

    assert calls == [(condo, "1101", "5548999999999")]
