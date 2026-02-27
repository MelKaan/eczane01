## Automated Pharmacy Monitoring System
This project is a dedicated software solution that displays on-duty pharmacy information in real time for Marmaris, Turkey. It is designed to run on Raspberry Pi devices connected to monitors in fullscreen mode.

## Tech Stack
- Language: Python
- UI/Display: Pygame
- Data Fetching: Requests, BeautifulSoup
- QR Generation: qrcode, Pillow
- Data Source: Muğla Eczacı Odası (local pharmacy listings)

## Why I Built This
This project was built step-by-step to solve a real operational need: showing accurate, readable, and continuously updated on-duty pharmacy information on public screens.

The goal is to provide a reliable bridge between live pharmacy data and a simple display experience for end users.

## Challenges I Overcame
- Data Parsing Reliability:
I handled inconsistent HTML structures and text formatting from source pages by improving parsing logic and cleanup rules.

- Scheduling and Update Timing:
I implemented controlled fetch scheduling and retry behavior to avoid missing daily updates while preventing unnecessary request loops.

- Display Readability:
I optimized dynamic font sizing, pagination, and layout so the screen remains readable across different monitor resolutions.

## Deployment
- Target: Raspberry Pi + monitor
- Startup: manual run with Bash script (`start_pharmacy.sh`)
- Runtime: fullscreen pharmacy board
- Scope: Marmaris only (`MARMARİS (1)` and `MARMARİS (2)`)

## Run
```bash
pip install -r requirements.txt
python3 main.py
```

## Utility Commands
- `python3 main.py --windowed`
- `python3 main.py --fetch-now`
- `python3 main.py --test-schedule`

## How It Works (Short)

```python
if should_fetch(last_fetch_date, last_fetch_attempt):
    new_pharmacies = fetch_today_pharmacies()
```
Fetch runs only when needed (scheduled time + retry control), then refreshes the screen data.

```python
TARGET_ORDER = ["MARMARİS (1", "MARMARİS (2"]
```
Only Marmaris regions are accepted, so the display always stays in project scope.

```python
font_size, title_font_size, qr_box_size = calculate_optimal_sizes(screen, pharmacies)
```
Layout sizes are calculated dynamically to fit different monitor resolutions.

```python
if lat and lng:
    maps_url = f"https://www.google.com/maps?q={lat},{lng}"
```
QR codes use coordinates when available; otherwise they fall back to normalized address search.
