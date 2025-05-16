import requests, os, re
from bs4 import BeautifulSoup

base = "https://blog.piprime.fr/asymptote/"
os.makedirs("asyncrawl", exist_ok=True)

def crawl(url):
    r = requests.get(url)
    fn = url.replace(base, "").rstrip("/")
    fn = fn if fn else "index.html"
    path = os.path.join("asyncrawl", fn)

    # ← add this to make sure ‘asyncrawl/...’ exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(r.content)

    for link in BeautifulSoup(r.text, "html.parser").select("a[href]"):
        href = link["href"]
        if href.startswith(base) or href.startswith("/asymptote"):
            nxt = href if href.startswith("http") else base + href.lstrip("/")
            if "asyncrawl/" not in nxt:
                crawl(nxt)

crawl(base)
# afterwards you can still do your grep

# then grep in asyncrawl/
matches = []
for root,_,files in os.walk("asyncrawl"):
    for f in files:
        with open(os.path.join(root,f), errors="ignore") as ff:
            if "import tube;" in ff.read():
                matches.append(os.path.join(root,f))
print("\n".join(matches))
