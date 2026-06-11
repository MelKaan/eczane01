import pygame
import math
import random

from settings import (
    TITLE_TEXT,
    WHITE, BLACK, RED, DARK_RED, CARD_BG,
    PHARMACIES_PER_PAGE,
    MIN_FONT_SIZE, MAX_FONT_SIZE,
    MIN_QR_BOX_SIZE, MAX_QR_BOX_SIZE,
    TITLE_FONT_RATIO,
    FONT_PATH,
    BLOCK_GAP, HORIZONTAL_GAP, PADDING, PADDING_X, PADDING_Y,
    CARD_RADIUS, BORDER_WIDTH,
    DRIFT_INTERVAL_SECONDS, DRIFT_MAX_PIXELS,
    DIM_AFTER_SECONDS, DIM_ALPHA, DIM_DURATION_SECONDS,
    PULSE_PERIOD_MS,
)
from qr_utils import generate_qr_surface


# ─────────────────────────────────────────────
#  Font helper
# ─────────────────────────────────────────────

def get_font(size, fallback="Arial", bold=True):
    try:
        return pygame.font.Font(FONT_PATH, size)
    except Exception:
        return pygame.font.SysFont(fallback, size, bold=bold)


# ─────────────────────────────────────────────
#  Rounded rectangle helper
#  pygame < 2.0 doesn't have draw.rect with border_radius,
#  so we provide a safe wrapper.
# ─────────────────────────────────────────────

def draw_rounded_rect(surface, color, rect, radius, width=0):
    """Draw a filled or outlined rounded rectangle safely."""
    try:
        pygame.draw.rect(surface, color, rect, width, border_radius=radius)
    except TypeError:
        # Fallback for older pygame without border_radius support
        pygame.draw.rect(surface, color, rect, width)


# ─────────────────────────────────────────────
#  Text surface cache
# ─────────────────────────────────────────────

_text_surface_cache: dict = {}


def get_text_surfaces(font, pharmacies):
    """Return pre-rendered (name, address, phone) surfaces, cached by content."""
    cache_key = id(font)
    result = []
    for p in pharmacies:
        key = (cache_key, p["name"], p["address"], p["phone"])
        if key not in _text_surface_cache:
            _text_surface_cache[key] = (
                font.render(p["name"],    True, WHITE),
                font.render(p["address"], True, WHITE),
                font.render(p["phone"],   True, WHITE),
            )
        result.append(_text_surface_cache[key])
    return result


# ─────────────────────────────────────────────
#  Optimal size calculation
# ─────────────────────────────────────────────

def calculate_optimal_sizes(screen, pharmacies, per_page=PHARMACIES_PER_PAGE):
    """
    Binary-searches for the largest font + QR box size where everything fits.
    Returns: (font_size, title_font_size, qr_box_size)
    """
    width, height = screen.get_width(), screen.get_height()

    font_size    = MAX_FONT_SIZE
    qr_box_size  = MAX_QR_BOX_SIZE
    pharmacies_on_page = pharmacies[:per_page]

    while font_size >= MIN_FONT_SIZE and qr_box_size >= MIN_QR_BOX_SIZE:
        font       = get_font(font_size)
        title_font = get_font(int(font_size * TITLE_FONT_RATIO))

        title_surf = title_font.render(TITLE_TEXT, True, WHITE)
        title_rect = title_surf.get_rect(center=(width // 2, 60))
        title_rect.inflate_ip(PADDING_X * 2, PADDING_Y * 2)
        vertical_margin_top = title_rect.bottom + 20

        qr_surfaces = [
            generate_qr_surface(p["address"], lat=p.get("lat"), lng=p.get("lng"), box_size=qr_box_size)
            for p in pharmacies_on_page
        ]

        block_heights = []
        block_widths  = []
        for i, eczane in enumerate(pharmacies_on_page):
            name_surf  = font.render(eczane["name"],    True, WHITE)
            addr_surf  = font.render(eczane["address"], True, WHITE)
            phone_surf = font.render(eczane["phone"],   True, WHITE)

            max_w       = max(name_surf.get_width(), addr_surf.get_width(), phone_surf.get_width())
            text_height = name_surf.get_height() + addr_surf.get_height() + phone_surf.get_height() + 20
            qr_h        = qr_surfaces[i].get_height()

            # Card inner content height = tallest of text column vs QR
            content_h  = max(text_height, qr_h)
            card_h     = content_h + PADDING * 2
            card_w     = max_w + HORIZONTAL_GAP + qr_surfaces[i].get_width() + PADDING * 2

            block_heights.append(card_h)
            block_widths.append(card_w)

        total_h = sum(block_heights) + (len(block_heights) - 1) * BLOCK_GAP
        max_w   = max(block_widths) if block_widths else 0

        if total_h + vertical_margin_top < height - 20 and max_w < width - 40:
            return font_size, int(font_size * TITLE_FONT_RATIO), qr_box_size

        font_size -= 2
        if font_size % 4 == 0 and qr_box_size > MIN_QR_BOX_SIZE:
            qr_box_size -= 1

    return MIN_FONT_SIZE, int(MIN_FONT_SIZE * TITLE_FONT_RATIO), MIN_QR_BOX_SIZE


# ─────────────────────────────────────────────
#  Drift state  (tiny layout shift for burn-in)
# ─────────────────────────────────────────────

class DriftState:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.last_drift_ms = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_drift_ms > DRIFT_INTERVAL_SECONDS * 1000:
            self.dx = random.randint(-DRIFT_MAX_PIXELS, DRIFT_MAX_PIXELS)
            self.dy = random.randint(-DRIFT_MAX_PIXELS, DRIFT_MAX_PIXELS)
            self.last_drift_ms = now


# ─────────────────────────────────────────────
#  Dim state  (periodic screen dimming)
# ─────────────────────────────────────────────

class DimState:
    def __init__(self):
        self.start_ms   = pygame.time.get_ticks()
        self.is_dimmed  = False
        self.dim_surface = None  # created lazily at draw time

    def update(self):
        elapsed = (pygame.time.get_ticks() - self.start_ms) / 1000
        cycle   = DIM_AFTER_SECONDS + DIM_DURATION_SECONDS
        pos_in_cycle = elapsed % cycle
        self.is_dimmed = pos_in_cycle >= DIM_AFTER_SECONDS

    def apply(self, screen):
        """Overlay a semi-transparent black surface when dimmed."""
        if not self.is_dimmed:
            return
        if self.dim_surface is None or self.dim_surface.get_size() != screen.get_size():
            self.dim_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        alpha = 255 - DIM_ALPHA   # how much to darken (higher = darker)
        self.dim_surface.fill((0, 0, 0, alpha))
        screen.blit(self.dim_surface, (0, 0))


# ─────────────────────────────────────────────
#  Border pulse colour
# ─────────────────────────────────────────────

def get_pulse_color():
    """
    Returns a red colour that pulses smoothly between DARK_RED and RED
    using a sine wave, so the border gently breathes.
    """
    t      = pygame.time.get_ticks() % PULSE_PERIOD_MS
    factor = (math.sin(2 * math.pi * t / PULSE_PERIOD_MS) + 1) / 2  # 0.0 → 1.0
    r = int(DARK_RED[0] + (RED[0] - DARK_RED[0]) * factor)
    g = int(DARK_RED[1] + (RED[1] - DARK_RED[1]) * factor)
    b = int(DARK_RED[2] + (RED[2] - DARK_RED[2]) * factor)
    return (r, g, b)


# ─────────────────────────────────────────────
#  Main draw function
# ─────────────────────────────────────────────

def draw_pharmacies(screen, title_font, font, pharmacies, qr_surfaces,
                    page, pharmacies_per_page, drift: DriftState, dim: DimState):

    screen.fill(BLACK)

    dx, dy = drift.dx, drift.dy
    pulse_color = get_pulse_color()

    # ── Title ──────────────────────────────────────────────────────
    title_surf = title_font.render(TITLE_TEXT, True, WHITE)
    title_cx   = screen.get_width() // 2 + dx
    title_cy   = 60 + dy
    title_rect = title_surf.get_rect(center=(title_cx, title_cy))
    title_rect.inflate_ip(PADDING_X * 2, PADDING_Y * 2)
    draw_rounded_rect(screen, CARD_BG,      title_rect, CARD_RADIUS)
    draw_rounded_rect(screen, pulse_color,  title_rect, CARD_RADIUS, width=BORDER_WIDTH)
    screen.blit(title_surf, title_surf.get_rect(center=title_rect.center))

    vertical_margin_top = title_rect.bottom + 20

    # ── Pharmacy cards ─────────────────────────────────────────────
    total            = len(pharmacies)
    pages            = (total + pharmacies_per_page - 1) // pharmacies_per_page
    start            = page * pharmacies_per_page
    end              = min(start + pharmacies_per_page, total)
    all_text_surfs   = get_text_surfaces(font, pharmacies)

    # Build card metrics
    cards = []
    for i in range(start, end):
        name_surf, addr_surf, phone_surf = all_text_surfs[i]
        qr_surf   = qr_surfaces[i]
        max_w     = max(name_surf.get_width(), addr_surf.get_width(), phone_surf.get_width())
        text_h    = name_surf.get_height() + addr_surf.get_height() + phone_surf.get_height() + 20
        content_h = max(text_h, qr_surf.get_height())
        card_h    = content_h + PADDING * 2
        card_w    = max_w + HORIZONTAL_GAP + qr_surf.get_width() + PADDING * 2
        cards.append({
            "i":          i,
            "name_surf":  name_surf,
            "addr_surf":  addr_surf,
            "phone_surf": phone_surf,
            "qr_surf":    qr_surf,
            "max_w":      max_w,
            "text_h":     text_h,
            "content_h":  content_h,
            "card_h":     card_h,
            "card_w":     card_w,
        })

    # ── Enforce uniform card size across all cards on this page ───
    unified_card_w = max(c["card_w"] for c in cards)
    unified_card_h = max(c["card_h"] for c in cards)
    for c in cards:
        c["card_w"] = unified_card_w
        c["card_h"] = unified_card_h
    # Unify text column width too, so QR lands at the same x on every card
    unified_max_w = max(c["max_w"] for c in cards)
    for c in cards:
        c["card_w"] = unified_card_w
        c["card_h"] = unified_card_h
        c["max_w"]  = unified_max_w

    # ── Draw cards ─────────────────────────────────────────────────
    total_cards_h = sum(c["card_h"] for c in cards) + (len(cards) - 1) * BLOCK_GAP
    y = vertical_margin_top + dy + max(0, (screen.get_height() - vertical_margin_top - total_cards_h) // 2)

    for card in cards:
        card_w = card["card_w"]
        card_h = card["card_h"]
        x      = (screen.get_width() - card_w) // 2 + dx

        card_rect = pygame.Rect(x, y, card_w, card_h)

        # Card background
        draw_rounded_rect(screen, CARD_BG, card_rect, CARD_RADIUS)

        # Pulsing red border
        draw_rounded_rect(screen, pulse_color, card_rect, CARD_RADIUS, width=BORDER_WIDTH)

        # Text — vertically centred inside the card
        text_x = x + PADDING
        text_y = y + (card_h - card["text_h"]) // 2

        screen.blit(card["name_surf"],  (text_x, text_y))
        screen.blit(card["addr_surf"],  (text_x, text_y + card["name_surf"].get_height() + 8))
        screen.blit(card["phone_surf"], (text_x, text_y + card["name_surf"].get_height()
                                                         + card["addr_surf"].get_height() + 16))

        # QR code — vertically centred inside the card
        qr_surf = card["qr_surf"]
        qr_x = x + PADDING + card["max_w"] + HORIZONTAL_GAP
        qr_y = y + (card_h - qr_surf.get_height()) // 2
        screen.blit(qr_surf, (qr_x, qr_y))

        y += card_h + BLOCK_GAP

    # ── Page indicator ─────────────────────────────────────────────
    if pages > 1:
        page_text = f"Sayfa {page + 1}/{pages}"
        page_surf = font.render(page_text, True, WHITE)
        screen.blit(page_surf, (
            screen.get_width()  - page_surf.get_width()  - 30 + dx,
            screen.get_height() - page_surf.get_height() - 20 + dy,
        ))

    # ── Dim overlay (applied last, on top of everything) ───────────
    dim.apply(screen)

    pygame.display.flip()