import qrcode
import pygame
from functools import lru_cache
from urllib.parse import quote
import re


def pil_image_to_surface(pil_image):
    pil_image = pil_image.convert("RGB")
    data = pil_image.tobytes()
    size = pil_image.size
    return pygame.image.fromstring(data, size, "RGB").convert()


def normalize_address(address: str) -> str:

    addr = address.upper()

    addr = re.sub(r"\bN\s*:\s*", "NO:", addr)
    addr = re.sub(r"NO\s*:\s*", "NO:", addr)

    replacements = {
        " MAH.": " MAHALLESİ",
        " CAD.": " CADDESİ",
        " SK.": " SOKAK",
        " BLV.": " BULVARI",
        " CD.": " CADDESİ",
        " MH.": " MAHALLESİ",
    }

    for k, v in replacements.items():
        addr = addr.replace(k, v)

    addr = " ".join(addr.replace("/", " ").split())

    if "MARMARİS" not in addr:
        addr += ", MARMARİS"

    if "MUĞLA" not in addr:
        addr += ", MUĞLA"

    if "TÜRKİYE" not in addr:
        addr += ", TÜRKİYE"

    return addr


@lru_cache(maxsize=256)
def _make_qr(lat, lng, address, box_size):

    # Prefer coordinates
    if lat and lng:
        maps_url = f"https://www.google.com/maps?q={lat},{lng}"
    else:
        fixed_address = normalize_address(address)
        maps_url = f"https://www.google.com/maps/search/?api=1&query={quote(fixed_address)}"

    qr = qrcode.QRCode(box_size=box_size, border=2)
    qr.add_data(maps_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img


def generate_qr_surface(address, lat=None, lng=None, box_size=5):

    img = _make_qr(lat, lng, address, box_size)
    return pil_image_to_surface(img)
