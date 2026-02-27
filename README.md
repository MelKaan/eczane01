# Marmaris On-Duty Pharmacy Display

Fullscreen pharmacy board app for Raspberry Pi devices connected to a monitor. It fetches and displays only Marmaris (Turkey) on-duty pharmacy data.

## Target Setup
- Raspberry Pi + monitor
- Manual start on each device via Bash script
- Fullscreen display mode for public viewing

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
python3 main.py
```

Or use the included startup script:
```bash
bash start_pharmacy.sh
```

## Test / Utility Modes
- `python3 main.py --windowed` : test in 800x600 window
- `python3 main.py --fetch-now` : fetch once, print results, exit
- `python3 main.py --test-schedule` : show fetch scheduling info

## Scope
- Data source: Muğla Eczacı Odası
- Region filter: Marmaris only (`MARMARİS (1)` and `MARMARİS (2)`)
