import pygame
import sys
from settings import PHARMACIES_PER_PAGE, TITLE_TEXT, TARGET_FPS
from display import get_font, calculate_optimal_sizes, draw_pharmacies, DriftState, DimState
from qr_utils import generate_qr_surface

# ── Fake pharmacy data ─────────────────────────────────────────────────────────
MOCK_PHARMACIES = [
    {
        "name":    "MERKEZ ECZANESİ",
        "address": "ATATÜRK CADDESİ NO:12 MARMARİS",
        "phone":   "02522123456",
        "lat":     36.8553,
        "lng":     28.2753,
    },
    {
        "name":    "GÜVEN ECZANESİ",
        "address": "ULUSAL EGEMENLİK CADDESİ NO:45 MARMARİS",
        "phone":   "02522134567",
        "lat":     36.8561,
        "lng":     28.2761,
    },
]

# ── Speeded-up timings for testing (in seconds / ms) ──────────────────────────
TEST_PAGE_SCROLL_SECONDS  = 5      # flip page every 5 seconds
TEST_DRIFT_INTERVAL_MS    = 5000   # drift every 5 seconds   (real: 120s)
TEST_DIM_AFTER_MS         = 8000   # dim after 8 seconds     (real: 600s)
TEST_DIM_DURATION_MS      = 6000   # stay dimmed for 6 secs  (real: 300s)
TEST_PULSE_PERIOD_MS      = 2000   # pulse every 2 seconds   (real: 4000ms)


class TestDriftState:
    """DriftState with accelerated interval for testing."""
    import random as _random

    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.last_drift_ms = pygame.time.get_ticks()

    def update(self):
        import random
        now = pygame.time.get_ticks()
        if now - self.last_drift_ms > TEST_DRIFT_INTERVAL_MS:
            self.dx = random.randint(-6, 6)
            self.dy = random.randint(-6, 6)
            self.last_drift_ms = now
            print(f"[DRIFT] shifted to dx={self.dx}, dy={self.dy}")


class TestDimState:
    """DimState with accelerated timings for testing."""
    from settings import DIM_ALPHA

    def __init__(self):
        self.start_ms    = pygame.time.get_ticks()
        self.is_dimmed   = False
        self.dim_surface = None
        self._was_dimmed = False

    def update(self):
        elapsed      = pygame.time.get_ticks() - self.start_ms
        cycle_ms     = TEST_DIM_AFTER_MS + TEST_DIM_DURATION_MS
        pos_in_cycle = elapsed % cycle_ms
        self.is_dimmed = pos_in_cycle >= TEST_DIM_AFTER_MS

        if self.is_dimmed and not self._was_dimmed:
            print("[DIM] Screen dimmed")
        elif not self.is_dimmed and self._was_dimmed:
            print("[DIM] Screen brightened")
        self._was_dimmed = self.is_dimmed

    def apply(self, screen):
        if not self.is_dimmed:
            return
        if self.dim_surface is None or self.dim_surface.get_size() != screen.get_size():
            self.dim_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        from settings import DIM_ALPHA
        alpha = 255 - DIM_ALPHA
        self.dim_surface.fill((0, 0, 0, alpha))
        screen.blit(self.dim_surface, (0, 0))


def draw_pharmacies_test(screen, title_font, font, pharmacies, qr_surfaces,
                         page, pharmacies_per_page, drift, dim):
    """
    Wrapper around draw_pharmacies that temporarily overrides PULSE_PERIOD_MS
    so the pulse is fast during testing.
    """
    import display as _display
    original_pulse = _display.PULSE_PERIOD_MS if hasattr(_display, 'PULSE_PERIOD_MS') else None

    # Monkey-patch the pulse period in the display module for this frame
    import settings as _settings
    _orig_setting = _settings.PULSE_PERIOD_MS
    _settings.PULSE_PERIOD_MS = TEST_PULSE_PERIOD_MS

    draw_pharmacies(screen, title_font, font, pharmacies, qr_surfaces,
                    page, pharmacies_per_page, drift, dim)

    _settings.PULSE_PERIOD_MS = _orig_setting


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption(f"{TITLE_TEXT} — TEST MODE")
    clock = pygame.time.Clock()

    font_size, title_font_size, qr_box_size = calculate_optimal_sizes(
        screen, MOCK_PHARMACIES, PHARMACIES_PER_PAGE
    )
    font        = get_font(font_size)
    title_font  = get_font(title_font_size)
    qr_surfaces = [
        generate_qr_surface(p["address"], lat=p.get("lat"), lng=p.get("lng"), box_size=qr_box_size)
        for p in MOCK_PHARMACIES
    ]

    page        = 0
    last_scroll = pygame.time.get_ticks()
    drift       = TestDriftState()
    dim         = TestDimState()

    print("── Test mode running ──────────────────────────────────────────")
    print(f"  Pharmacies      : {len(MOCK_PHARMACIES)}")
    print(f"  Font size       : {font_size}  |  Title: {title_font_size}  |  QR box: {qr_box_size}")
    print(f"  Border pulse    : every {TEST_PULSE_PERIOD_MS/1000:.1f}s  (real: 4s)")
    print(f"  Drift           : every {TEST_DRIFT_INTERVAL_MS/1000:.0f}s   (real: 120s)")
    print(f"  Dim after       : {TEST_DIM_AFTER_MS/1000:.0f}s       (real: 600s)")
    print(f"  Dim duration    : {TEST_DIM_DURATION_MS/1000:.0f}s       (real: 300s)")
    print(f"  Page scroll     : every {TEST_PAGE_SCROLL_SECONDS}s  (real: 8s)")
    print(f"  Press ESC to quit")
    print("───────────────────────────────────────────────────────────────")

    while True:
        drift.update()
        dim.update()

        draw_pharmacies_test(
            screen, title_font, font,
            MOCK_PHARMACIES, qr_surfaces,
            page, PHARMACIES_PER_PAGE,
            drift, dim,
        )

        # Page scroll
        page_count = (len(MOCK_PHARMACIES) + PHARMACIES_PER_PAGE - 1) // PHARMACIES_PER_PAGE
        now_ms = pygame.time.get_ticks()
        if page_count > 1 and now_ms - last_scroll > TEST_PAGE_SCROLL_SECONDS * 1000:
            page        = (page + 1) % page_count
            last_scroll = now_ms
            print(f"[PAGE] flipped to page {page + 1}/{page_count}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

        clock.tick(TARGET_FPS)


if __name__ == "__main__":
    main()