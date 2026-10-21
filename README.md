# QRCode2Call

Web app that lets a visitor call a condominium unit by scanning a QR code at the entrance. The visitor picks the unit, types their own phone number, and the PBX (FreeSWITCH) calls them back and connects them to the unit's extension, so no app or intercom hardware is needed.

Built with [NiceGUI](https://nicegui.io). The UI is in Portuguese (pt-BR).

## How it works

1. `create-qrcodes.py` generates one QR code per condominium pointing to `https://<your-host>/call/<condo_id>`.
2. The visitor scans it and opens `/call/<condo_id>`. The app asks the backend API for the condominium's blocks and units (`GET v1/condo/{condo_id}/blocks_units`).
3. The visitor selects a unit and enters their phone number on a dialpad.
4. The app calls the backend's `GET v1/originate?origin=<unit extension>&destination=<visitor phone>`, and the PBX bridges the call.

The backend API (FreeSWITCH connector) is a separate service and is not part of this repository.

### Pages

| Path | Description |
|---|---|
| `/` | Condominium selector |
| `/qrcode/{condo}` | Shows the QR code for a condominium |
| `/call/{condo_id}` | Unit selection + dialpad (QR code target) |
| `/dest` | Static destination list from `config/settings.py` (testing). Calls from the condo's `origin` to the selected number |

## Configuration

Everything lives in `config/settings.py`:

```python
backend_api = {
    "base_url": "https://pbx-api.example.com:8099/",
    "username": "api-user",
    "password": "CHANGE_ME",
    "ignore-ssl-certificate-check": False,
    "endpoints": {
        "originate": "v1/originate",
        "blocks_units_by_condo": "v1/condo/{condo_id}/blocks_units",
    },
}

qrcode2call_url = "https://qrcode2call.example.com/call"

condos = {
    "my_condo": {
        "url": "https://pbx-api.example.com:8099",
        "origin": "1000",
        "destination": {"101": "5548999999999"},
        "username": "api-user",
        "password": "CHANGE_ME",
        "condo_id": "123456",
    },
}
```

In production the compose file mounts `/etc/qrcode2call/` over `config/`, so the real `settings.py`, with credentials, stays outside the repository. Don't commit real credentials.

## Running

### Docker Compose (with Caddy for TLS)

```bash
git clone https://github.com/marujofln/qrcode2call.git
cd qrcode2call
sudo mkdir -p /etc/qrcode2call
sudo cp config/settings.py /etc/qrcode2call/settings.py      # then edit it
sudo cp config/Caddyfile.sample /etc/qrcode2call/Caddyfile   # set your hostname
docker compose up -d --build
```

For development, `docker-compose-dev.yml` mounts `./.etc` instead of `/etc/qrcode2call`.

### Local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python create-qrcodes.py   # writes static/<condo_id>.png
python main.py             # http://localhost:8080
```

## Notes

- Generated QR codes (`static/*.png`) are git-ignored. Run `create-qrcodes.py` after changing `condos` or `qrcode2call_url`.
- `/call/<condo_id>` uses the `condos` entry with that `condo_id` for the originate URL and credentials, so every condominium served needs an entry in `condos`.
- Anyone with the QR code can trigger calls to the units. Consider rate limiting at the reverse proxy.
