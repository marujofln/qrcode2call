import importlib.util
from pathlib import Path

import qrcode

ROOT = Path(__file__).resolve().parent.parent


def load_script():
    # create-qrcodes.py has a dash in its name, so it can't be imported normally
    spec = importlib.util.spec_from_file_location("create_qrcodes", ROOT / "create-qrcodes.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generate_qrcode_writes_png_pointing_to_call_url(tmp_path, monkeypatch):
    script = load_script()
    monkeypatch.setattr(script, "qrcode2call_url", "https://qr.test/call")
    data = []
    original_add_data = qrcode.QRCode.add_data
    monkeypatch.setattr(
        qrcode.QRCode,
        "add_data",
        lambda self, d, *a, **kw: (data.append(d), original_add_data(self, d, *a, **kw)),
    )
    (tmp_path / "static").mkdir()
    monkeypatch.chdir(tmp_path)

    script.generate_qrcode({"condo_id": "123456"})

    assert data == ["https://qr.test/call/123456"]
    png = tmp_path / "static" / "123456.png"
    assert png.read_bytes().startswith(b"\x89PNG")
