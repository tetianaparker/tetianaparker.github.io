import json, os, re, html, urllib.request

SHOP = "68325894"
KEY = os.environ["ETSY_KEY"]
API = "https://openapi.etsy.com/v3/application"

def get(url):
    req = urllib.request.Request(url, headers={"x-api-key": KEY, "User-Agent": "linkpage"})
    return json.load(urllib.request.urlopen(req, timeout=30))

listings, off = [], 0
while True:
    r = get(f"{API}/shops/{SHOP}/listings/active?limit=100&offset={off}&sort_on=created&sort_order=desc")
    listings += r["results"]
    off += 100
    if off >= r["count"]:
        break

images = {}
for i in range(0, len(listings), 100):
    ids = ",".join(str(l["listing_id"]) for l in listings[i:i + 100])
    for l in get(f"{API}/listings/batch?listing_ids={ids}&includes=Images")["results"]:
        imgs = sorted(l.get("images") or [], key=lambda x: x.get("rank", 99))
        if imgs:
            images[l["listing_id"]] = imgs[0]["url_570xN"]

def card(l, cls):
    name = html.escape(l["title"].split(",")[0].replace(" Original Painting", ""))
    img = images[l["listing_id"]]
    big = img.replace("il_570xN", "il_1140xN")
    return f'<a class="card" href="{big}"><img src="{img}" alt="{name}" loading="lazy"><span>{name}</span></a>'

listings = [l for l in listings if l["listing_id"] in images]
library = [l for l in listings if "custom" not in l["title"].lower()]

page = open("index.html").read()
for tag, items in (("GALLERY", [card(l, "card") for l in library]),):
    if items:
        page = re.sub(rf"<!--{tag}-->.*?<!--/{tag}-->", f"<!--{tag}-->\n" + "\n".join(items) + f"\n<!--/{tag}-->", page, flags=re.S)
open("index.html", "w").write(page)
print(len(library), "paintings in library")
