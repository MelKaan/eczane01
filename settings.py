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

FETCH_HOUR = 8
FETCH_MINUTE = 5

WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0  )
RED        = (255, 0,   0  )
DARK_RED   = (180, 0,   0  )
CARD_BG    = (18,  18,  18 )  # very dark grey, slightly off-black for card background

# --- Dynamic Display Settings ---
PHARMACIES_PER_PAGE = 4
PAGE_SCROLL_SECONDS = 8

MIN_FONT_SIZE = 20
MAX_FONT_SIZE = 60

MIN_QR_BOX_SIZE = 2
MAX_QR_BOX_SIZE = 7

TITLE_FONT_RATIO = 1.2

# --- Layout Constants ---
BLOCK_GAP      = 30   # vertical gap between cards
HORIZONTAL_GAP = 40   # gap between text and QR inside a card
PADDING        = 20   # inner padding inside each card
PADDING_X      = 30   # title box horizontal padding
PADDING_Y      = 15   # title box vertical padding
CARD_RADIUS    = 12   # rounded corner radius for cards

# --- Burn-in Protection ---
# Pixel drift: every DRIFT_INTERVAL_SECONDS, the layout shifts by up to DRIFT_MAX_PIXELS
DRIFT_INTERVAL_SECONDS = 120       # shift position every 2 minutes
DRIFT_MAX_PIXELS       = 6         # max pixels to drift in any direction

# Dimming: after DIM_AFTER_SECONDS of running, dim to DIM_ALPHA (0=black, 255=full)
# then brighten back after DIM_DURATION_SECONDS
DIM_AFTER_SECONDS    = 600         # dim after 10 minutes
DIM_ALPHA            = 60          # dim to ~25% brightness (out of 255)
DIM_DURATION_SECONDS = 300         # stay dimmed for 5 minutes, then brighten

# Border pulse: full cycle duration in milliseconds
PULSE_PERIOD_MS = 4000             # one full fade in/out every 4 seconds
BORDER_WIDTH    = 3                # card border thickness in pixels

# --- FPS ---
TARGET_FPS = 10                    # low FPS to reduce Pi CPU load