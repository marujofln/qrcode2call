from condos import condos
import qrcode

QR2CALL_URL = "https://south-america.on-air.io/devices/DEVICE_ID/call"


def generate_qrcode(condo: str = None):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"{QR2CALL_URL}/{condo}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white")
    file_name = f"{condo}.png"
    qr_img.save(f"static/{file_name}")


if __name__ == '__main__':
    for condo in condos.keys():
        generate_qrcode(condo)
