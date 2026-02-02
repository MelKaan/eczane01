import requests
from bs4 import BeautifulSoup
import datetime
import re

from settings import WEBSITE_URL, USER_AGENT, FETCH_HOUR, FETCH_MINUTE


PHONE_REGEX = re.compile(r"0\d{10}")

# relaxed prefixes
TARGET_ORDER = [
    "MARMARİS (1",
    "MARMARİS (2"
]

# Google Maps coordinate patterns
COORD_REGEX = re.compile(r"@(-?\d+\.\d+),(-?\d+\.\d+)")
QUERY_COORD_REGEX = re.compile(r"query=(-?\d+\.\d+),(-?\d+\.\d+)")


def normalize_spaces(text):
    return " ".join(text.replace("\xa0", " ").split()).strip()


def clean_text(text):
    remove_phrases = [
        "Haritada görüntülemek için tıklayınız",
        "arasında nöbetçidir"
    ]

    for phrase in remove_phrases:
        text = text.replace(phrase, "")
        text = text.replace("...", "")
        text = text.replace(" ... ", " ")

    text = re.sub(
        r"\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}\s*-\s*\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}",
        "",
        text
    )

    text = normalize_spaces(text)

    while text.endswith("."):
        text = text[:-1]

    text = re.sub(r"NO:\s+", "NO:", text)

    return normalize_spaces(text)


def is_pharmacy_header(tag):
    if tag.name not in ["h1", "h2", "h3", "h4", "h5", "strong"]:
        return False

    text = tag.get_text(strip=True).upper()
    return ("ECZANE" in text or "ECZANESİ" in text) and "-" in text


def region_matches(region_text):
    region_clean = normalize_spaces(region_text.upper())

    for target in TARGET_ORDER:
        if region_clean.startswith(target):
            return True

    return False


def extract_coordinates(block):
    """
    Extract coordinates from map links if present
    """

    links = block.find_all("a", href=True)

    for a in links:
        href = a["href"]

        m1 = COORD_REGEX.search(href)
        if m1:
            return float(m1.group(1)), float(m1.group(2))

        m2 = QUERY_COORD_REGEX.search(href)
        if m2:
            return float(m2.group(1)), float(m2.group(2))

    return None, None


def fetch_today_pharmacies():
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(WEBSITE_URL, headers=headers, timeout=15)

        if resp.status_code != 200:
            print(f"Veri alınamadı: {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        possible_headers = soup.find_all(is_pharmacy_header)

        found = {}

        for header in possible_headers:

            raw_title = normalize_spaces(header.get_text(strip=True))

            try:
                name_part, region_part = raw_title.split("-", 1)
            except ValueError:
                continue

            name = normalize_spaces(name_part)
            region = normalize_spaces(region_part)

            if not region_matches(region):
                continue

            raw_block_text = ""
            raw_block_node = header.find_next_sibling()

            block_root = None

            while raw_block_node:

                if is_pharmacy_header(raw_block_node):
                    break

                if block_root is None:
                    block_root = raw_block_node

                raw_block_text += " " + raw_block_node.get_text(" ", strip=True)
                raw_block_node = raw_block_node.find_next_sibling()

            raw_block_text = clean_text(raw_block_text)

            phone_match = PHONE_REGEX.search(raw_block_text)
            phone = phone_match.group() if phone_match else ""

            address = raw_block_text.replace(phone, "")
            address = normalize_spaces(address)

            lat, lng = (None, None)

            if block_root:
                lat, lng = extract_coordinates(block_root)

            found[region] = {
                "name": name,
                "address": address,
                "phone": phone,
                "lat": lat,
                "lng": lng
            }

        pharmacies = []

        for prefix in TARGET_ORDER:
            for region in found:
                if region.startswith(prefix):
                    pharmacies.append(found[region])
                    break

        if not pharmacies:
            print("Marmaris nöbetçi eczane bulunamadı.")

        return pharmacies

    except Exception as e:
        print(f"Hata oluştu: {e}")
        return []


def should_fetch(last_fetch_date, last_attempt=None):
    now = datetime.datetime.now()

    scheduled_today = datetime.datetime(
        now.year,
        now.month,
        now.day,
        FETCH_HOUR,
        FETCH_MINUTE
    )

    if now < scheduled_today:
        return False

    if last_fetch_date == now.date():
        return False

    if last_attempt and (now - last_attempt).total_seconds() < 600:
        return False

    return True


def scheduled_datetime_for(date: datetime.date):
    return datetime.datetime(
        date.year,
        date.month,
        date.day,
        FETCH_HOUR,
        FETCH_MINUTE
    )


def next_scheduled_datetime(now: datetime.datetime = None):

    if now is None:
        now = datetime.datetime.now()

    today_sched = scheduled_datetime_for(now.date())

    if now < today_sched:
        return today_sched

    tomorrow = now.date() + datetime.timedelta(days=1)
    return scheduled_datetime_for(tomorrow)
