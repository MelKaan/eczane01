import pygame
from settings import (
    TITLE_TEXT,
    WHITE,
    BLACK,
    RED,
    PHARMACIES_PER_PAGE,
    PAGE_SCROLL_SECONDS,
    MIN_FONT_SIZE,
    MAX_FONT_SIZE,
    MIN_QR_BOX_SIZE,
    MAX_QR_BOX_SIZE,
    TITLE_FONT_RATIO,
    FONT_PATH,
)
from qr_utils import generate_qr_surface


def get_font(size, fallback="Arial", bold=True):
    try:
        return pygame.font.Font(FONT_PATH, size)
    except:
        return pygame.font.SysFont(fallback, size, bold=bold)


def calculate_optimal_sizes(screen, pharmacies, per_page=PHARMACIES_PER_PAGE):
    """
    Dynamically finds the best font size and QR code size so that all blocks fit on the screen.
    Returns: (font_size, title_font_size, qr_box_size)
    """
    width, height = screen.get_width(), screen.get_height()
    block_gap = 40
    horizontal_gap = 80
    padding = 16
    padding_x, padding_y = 30, 15

    font_size = MAX_FONT_SIZE
    qr_box_size = MAX_QR_BOX_SIZE

    # Only consider the pharmacies to be shown on a single page
    pharmacies_on_page = pharmacies[:per_page]
    while font_size >= MIN_FONT_SIZE and qr_box_size >= MIN_QR_BOX_SIZE:
        font = get_font(font_size)
        title_font = get_font(int(font_size * TITLE_FONT_RATIO))
        title_surf = title_font.render(TITLE_TEXT, True, WHITE)
        title_rect = title_surf.get_rect(center=(width // 2, 110))
        title_rect.inflate_ip(padding_x * 2, padding_y * 2)
        vertical_margin_top = title_rect.bottom + 10

        qr_surfaces = [generate_qr_surface(p["address"], box_size=qr_box_size) for p in pharmacies_on_page]
        block_heights = []
        block_widths = []
        for i, eczane in enumerate(pharmacies_on_page):
            name_surf = font.render(eczane["name"], True, WHITE)
            addr_surf = font.render(eczane["address"], True, WHITE)
            phone_surf = font.render(eczane["phone"], True, WHITE)
            max_w = max(name_surf.get_width(), addr_surf.get_width(), phone_surf.get_width())
            text_height = name_surf.get_height() + addr_surf.get_height() + phone_surf.get_height() + 20
            qr_height = qr_surfaces[i].get_height()
            block_height = max(text_height, qr_height) + 25
            block_width = max_w + horizontal_gap + qr_surfaces[i].get_width() + padding*2
            block_heights.append(block_height)
            block_widths.append(block_width)
        total_height = sum(block_heights) + (len(block_heights) - 1) * block_gap
        max_width = max(block_widths) if block_widths else 0
        if total_height + vertical_margin_top < height and max_width < width:
            return font_size, int(font_size * TITLE_FONT_RATIO), qr_box_size
        font_size -= 2
        if font_size % 4 == 0 and qr_box_size > MIN_QR_BOX_SIZE:
            qr_box_size -= 1
    return MIN_FONT_SIZE, int(MIN_FONT_SIZE * TITLE_FONT_RATIO), MIN_QR_BOX_SIZE


def draw_pharmacies(screen, title_font, font, pharmacies, qr_surfaces, page, pharmacies_per_page):
    screen.fill(BLACK)
    padding_x, padding_y = 30, 15
    title_surf = title_font.render(TITLE_TEXT, True, WHITE)
    title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 110))
    title_rect.inflate_ip(padding_x * 2, padding_y * 2)
    pygame.draw.rect(screen, RED, title_rect)
    title_pos = (title_rect.centerx - title_surf.get_width() // 2, title_rect.centery - title_surf.get_height() // 2)
    screen.blit(title_surf, title_pos)

    total = len(pharmacies)
    pages = (total + pharmacies_per_page - 1) // pharmacies_per_page
    start = page * pharmacies_per_page
    end = min(start + pharmacies_per_page, total)
    vertical_margin_top = title_rect.bottom + 10

    block_gap = 40
    horizontal_gap = 80
    padding = 16
    rendered_blocks = []
    for i in range(start, end):
        eczane = pharmacies[i]
        name_surf = font.render(eczane["name"], True, WHITE)
        addr_surf = font.render(eczane["address"], True, WHITE)
        phone_surf = font.render(eczane["phone"], True, WHITE)
        max_w = max(name_surf.get_width(), addr_surf.get_width(), phone_surf.get_width())
        text_height = name_surf.get_height() + addr_surf.get_height() + phone_surf.get_height() + 20
        qr_height = qr_surfaces[i].get_height()
        block_height = max(text_height, qr_height) + 25
        rendered_blocks.append({
            "name_surf": name_surf,
            "addr_surf": addr_surf,
            "phone_surf": phone_surf,
            "max_text_width": max_w,
            "text_height": text_height,
            "block_height": block_height
        })
    total_height = sum(b["block_height"] for b in rendered_blocks) + (len(rendered_blocks) - 1) * block_gap
    y = vertical_margin_top + max(0, (screen.get_height() - vertical_margin_top - total_height) // 2)
    for idx, block in enumerate(rendered_blocks):
        i = start + idx
        qr_surf = qr_surfaces[i]
        total_width = block["max_text_width"] + horizontal_gap + qr_surf.get_width()
        x_start = (screen.get_width() - total_width) // 2
        box_rect = pygame.Rect(
            x_start - padding,
            y + (block["block_height"] - block["text_height"]) // 2 - padding,
            block["max_text_width"] + padding * 2,
            block["text_height"] + padding * 2
        )
        pygame.draw.rect(screen, RED, box_rect)
        text_x = x_start
        text_y = y + (block["block_height"] - block["text_height"]) // 2
        screen.blit(block["name_surf"], (text_x, text_y))
        screen.blit(block["addr_surf"], (text_x, text_y + block["name_surf"].get_height() + 8))
        screen.blit(block["phone_surf"], (text_x, text_y + block["name_surf"].get_height() + block["addr_surf"].get_height() + 16))
        qr_x = x_start + block["max_text_width"] + horizontal_gap
        qr_y = y + (block["block_height"] - qr_surf.get_height()) // 2
        screen.blit(qr_surf, (qr_x, qr_y))
        y += block["block_height"] + block_gap
    if pages > 1:
        page_text = f"Sayfa {page+1}/{pages}"
        page_surf = font.render(page_text, True, WHITE)
        screen.blit(page_surf, (screen.get_width() - page_surf.get_width() - 30, screen.get_height() - page_surf.get_height() - 20))
    pygame.display.flip()
