# CLAUDE.md

QRCode2Call: a NiceGUI web app where a visitor scans a QR code at a condominium entrance, picks a unit, types their phone number, and the PBX (FreeSWITCH, via a separate backend API not in this repo) calls them back and bridges them to the unit's extension. See README.md for the user-facing overview.

## Commands

```bash
uv venv .venv && uv pip install --python .venv/bin/python -r requirements-dev.txt  # or python -m venv + pip
.venv/bin/pytest                    # run tests (config in pytest.ini)
.venv/bin/pytest tests/test_pages.py::test_qrcode_page_unknown_condo  # single test
.venv/bin/python create-qrcodes.py  # writes static/<condo_id>.png (git-ignored)
.venv/bin/python main.py            # http://localhost:8080
docker compose up -d --build        # prod: mounts /etc/qrcode2call over config/, plus Caddy for TLS
docker compose -f docker-compose-dev.yml up --build  # dev: mounts ./.etc instead
```

## Layout

- `main.py`: the whole app. `Dialpad` class, `handle_originate()`, and the `@ui.page` routes `/`, `/qrcode/{condo}`, `/call/{condo}` (QR code target), `/dest`.
- `config/settings.py`: `backend_api` (base URL, credentials, endpoint templates), `qrcode2call_url`, and `condos`. The repo copy holds placeholders only. In Docker the real file is mounted over `config/`, so never commit real credentials.
- `create-qrcodes.py`: generates one QR code per entry in `condos`, pointing at `{qrcode2call_url}/{condo_id}`.
- `tests/`: pytest suite. The UI is not rendered: the `fake_ui` fixture swaps `main.ui` for a `MagicMock`, and `settings` swaps `main.condos`/`main.backend_api` for test data. HTTP calls are mocked (`main.requests.get`, `main.run.io_bound`). Async pages and handlers run with `asyncio.run`, so there is no pytest-asyncio.

## Flow

1. `/call/{condo_id}` looks up the `condos` entry whose `condo_id` matches (and shows "Condomínio não encontrado" if there is none), then does a `GET {base_url}v1/condo/{condo_id}/blocks_units` with basic auth. The response is `{block: {unit: extension_or_null}}`. Units with a `null` extension are skipped.
2. Clicking a unit opens the dialpad (`Dialpad.setup_dialpad_card`) with that unit's extension as `origin`.
3. `->` calls `handle_originate(condo, origin, destination)`, which does a `GET {condo['url']}/v1/originate?origin=&destination=` through `run.io_bound` with a 20s timeout and `verify=False`, then shows a notification.

## Conventions and gotchas

- UI text is in Portuguese (pt-BR). Keep new strings in Portuguese.
- `ui.run()` sits under `if __name__ in {"__main__", "__mp_main__"}` so tests can import `main` without starting the server. Keep it that way.
- Pinned to NiceGUI 1.4.27. Its testing helpers (`User` fixture) only exist in 2.x, which is why the tests mock `ui`.
- Inside loops, `on_click` lambdas must bind the loop variable as a default argument (`lambda u=unit: ...`). Otherwise every button acts on the last item. Tests cover this for `/`, `/call` and `/dest`.
- Blocking HTTP calls inside pages and handlers go through `await run.io_bound(requests.get, ...)` so they don't block the event loop.
