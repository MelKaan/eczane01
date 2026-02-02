import argparse
import pygame
import sys
import datetime

from settings import (
    PHARMACIES_PER_PAGE,
    PAGE_SCROLL_SECONDS,
    TITLE_TEXT,
)
from fetcher import fetch_today_pharmacies, should_fetch, next_scheduled_datetime, scheduled_datetime_for
from display import get_font, calculate_optimal_sizes, draw_pharmacies
from qr_utils import generate_qr_surface

last_fetch_date = None
last_fetch_attempt = None
FETCH_RETRY_SECONDS = 600  # retry every 10 minutes


def main():
    parser = argparse.ArgumentParser(description="Nöbetçi Eczaneler display")
    parser.add_argument("--fetch-now", action="store_true", help="Run a one-off fetch and print results then exit")
    parser.add_argument("--test-schedule", action="store_true", help="Print next scheduled fetch datetime and schedule checks")
    parser.add_argument("--windowed", action="store_true", help="Run in a window (800x600) instead of fullscreen — helpful for testing")
    args = parser.parse_args()

    # One-off fetch mode for testing or external scheduler
    if args.fetch_now:
        ph = fetch_today_pharmacies()
        if not ph:
            print("No pharmacies returned")
            return
        for p in ph:
            print(f"{p['name']} — {p['address']} — {p['phone']}")
        return

    # Schedule inspection helper
    if args.test_schedule:
        now = datetime.datetime.now()
        print("Now:", now)
        print("Next scheduled:", next_scheduled_datetime(now))
        print("Scheduled for today:", scheduled_datetime_for(now.date()))
        print("should_fetch(None):", should_fetch(None))
        # simulate already fetched today
        print("should_fetch(today):", should_fetch(now.date()))
        return

    pygame.init()
    if args.windowed:
        screen = pygame.display.set_mode((800, 600))
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption(TITLE_TEXT)
    clock = pygame.time.Clock()
    last_fetch_date = None
    last_fetch_attempt = None


    pharmacies = [{
        "name": "Veri alınamadı",
        "address": "08:00'den sonra otomatik güncellenecek.",
        "phone": ""
    }]

    # Dynamic sizing for initial/default content
    font_size, title_font_size, qr_box_size = calculate_optimal_sizes(screen, pharmacies, PHARMACIES_PER_PAGE)
    font = get_font(font_size)
    title_font = get_font(title_font_size)
    qr_surfaces = [generate_qr_surface(p["address"], box_size=qr_box_size) for p in pharmacies]

    page = 0
    last_scroll = pygame.time.get_ticks()

    while True:
        if should_fetch(last_fetch_date, last_fetch_attempt):
            last_fetch_attempt = datetime.datetime.now()
            new_pharmacies = fetch_today_pharmacies()

            if new_pharmacies:
                pharmacies = new_pharmacies
                last_fetch_date = last_fetch_attempt.date()

                font_size, title_font_size, qr_box_size = calculate_optimal_sizes(
                    screen, pharmacies, PHARMACIES_PER_PAGE
                )
                font = get_font(font_size)
                title_font = get_font(title_font_size)
                qr_surfaces = [
                    generate_qr_surface(p["address"], box_size=qr_box_size)
                    for p in pharmacies
                ]
                page = 0


        draw_pharmacies(screen, title_font, font, pharmacies, qr_surfaces, page, PHARMACIES_PER_PAGE)

        page_count = (len(pharmacies) + PHARMACIES_PER_PAGE - 1) // PHARMACIES_PER_PAGE
        now = pygame.time.get_ticks()
        if page_count > 1 and now - last_scroll > PAGE_SCROLL_SECONDS * 1000:
            page = (page + 1) % page_count
            last_scroll = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
        clock.tick(30)


if __name__ == "__main__":
    main()