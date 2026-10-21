import asyncio

import pytest

import main

from conftest import on_click_of, response

BLOCKS_UNITS = {
    "A": {"101": "1101", "102": None},
    "B": {"201": "1201"},
}


@pytest.fixture
def backend(monkeypatch):
    calls = []
    state = {"response": response(200, BLOCKS_UNITS)}

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return state["response"]

    monkeypatch.setattr(main.requests, "get", fake_get)
    state["calls"] = calls
    return state


def button_labels(ui_mock):
    return [c.args[0] for c in ui_mock.button.call_args_list]


def label_texts(ui_mock):
    return [c.args[0] for c in ui_mock.label.call_args_list]


def test_call_page_fetches_blocks_units_of_condo(fake_ui, settings, backend):
    asyncio.run(main.call("123456"))

    url, kwargs = backend["calls"][0]
    assert url == "https://backend.test/v1/condo/123456/blocks_units"
    assert kwargs == {"auth": ("api-user", "api-secret")}


def test_call_page_can_skip_ssl_verification(fake_ui, settings, backend):
    settings.backend_api["ignore-ssl-certificate-check"] = True

    asyncio.run(main.call("123456"))

    _, kwargs = backend["calls"][0]
    assert kwargs["verify"] is False


def test_call_page_lists_units_with_extension(fake_ui, settings, backend):
    asyncio.run(main.call("123456"))

    assert button_labels(fake_ui) == ["101", "201"]
    assert "Bloco: A" in label_texts(fake_ui)
    assert "Bloco: B" in label_texts(fake_ui)


def test_call_page_shows_error_when_backend_fails(fake_ui, settings, backend):
    backend["response"] = response(500)

    asyncio.run(main.call("123456"))

    assert "Erro ao buscar unidades do condomínio." in label_texts(fake_ui)
    fake_ui.button.assert_not_called()


def test_call_page_unit_buttons_open_dialpad_for_their_own_unit(fake_ui, settings, backend, monkeypatch):
    opened = []
    monkeypatch.setattr(
        main.Dialpad,
        "setup_dialpad_card",
        lambda self, card, origin: opened.append((self.condo, origin)),
    )
    asyncio.run(main.call("123456"))

    on_click_of(fake_ui, "101")()
    on_click_of(fake_ui, "201")()

    condo = settings.condos["gnovit"]
    assert opened == [(condo, "1101"), (condo, "1201")]


def test_call_page_unknown_condo_id(fake_ui, settings, backend):
    asyncio.run(main.call("999999"))

    fake_ui.label.assert_called_once_with("Condomínio não encontrado")
    assert backend["calls"] == []


def test_call_page_fetches_off_the_event_loop(fake_ui, settings, backend, monkeypatch):
    offloaded = []

    async def fake_io_bound(func, *args, **kwargs):
        offloaded.append(func)
        return func(*args, **kwargs)

    monkeypatch.setattr(main.run, "io_bound", fake_io_bound)

    asyncio.run(main.call("123456"))

    assert offloaded == [main.requests.get]


def test_root_items_navigate_to_their_own_condo(fake_ui, monkeypatch):
    monkeypatch.setattr(main, "condos", {"alpha": {}, "beta": {}})

    main.root()
    for call in fake_ui.item.call_args_list:
        call.kwargs["on_click"]()

    targets = [c.args[0] for c in fake_ui.navigate.to.call_args_list]
    assert targets == ["/qrcode/alpha", "/qrcode/beta"]


def test_dest_page_buttons_open_dialpad_prefilled_for_their_unit(fake_ui, settings, monkeypatch):
    opened = []
    monkeypatch.setattr(
        main.Dialpad,
        "setup_dialpad_card",
        lambda self, card, origin: opened.append((origin, self.destination)),
    )
    asyncio.run(main.dialpad())

    on_click_of(fake_ui, "101")()
    on_click_of(fake_ui, "102")()

    assert opened == [("1000", "5548999990101"), ("1000", "5548999990102")]


def test_qrcode_page_shows_condo_image(fake_ui, settings):
    main.show_qrcode("gnovit")

    fake_ui.image.assert_called_once_with("/static/123456.png")


def test_qrcode_page_unknown_condo(fake_ui, settings):
    main.show_qrcode("nope")

    fake_ui.image.assert_not_called()
    fake_ui.label.assert_called_once_with("Condomínio não encontrado")
