import pygame

# ------------------- SETTINGS and CONSTANTS -------------------

WEBSITE_URL = "https://www.muglaeczaciodasi.org.tr/nobetci-eczaneler"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

FONT_PATH = "assets/FreeSansBold.ttf"
TITLE_TEXT = "Nöbetçi Eczaneler"

FETCH_HOUR =0
FETCH_MINUTE = 5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)

# --- Dynamic Display Settings ---

PHARMACIES_PER_PAGE = 4
PAGE_SCROLL_SECONDS = 8

MIN_FONT_SIZE = 20
MAX_FONT_SIZE = 60

MIN_QR_BOX_SIZE = 2
MAX_QR_BOX_SIZE = 7

TITLE_FONT_RATIO = 1.2