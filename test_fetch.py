from fetcher import fetch_today_pharmacies

data = fetch_today_pharmacies()

print("COUNT:", len(data))

for p in data:
    print(p)
