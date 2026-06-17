import requests
import random
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

headers = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

url = "https://www.amazon.fr/gp/bestsellers/kitchen"
resp = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'lxml')

print("=== SÉLECTEURS PRODUITS ===")
tests = [
    'div.p13n-sc-uncoverable-faceout',
    'div[id^=p13n-asin]',
    'li.zg-item-immersion',
    'div.zg-item',
    'div[class*=zg-grid-general]',
    'div[class*=zg_itemImmersion]',
    'div[data-asin]',
    'div[class*=s-result-item]',
]
for sel in tests:
    found = soup.select(sel)
    print(f"  {len(found):3d}  →  {sel}")

# Cherche tous les éléments avec data-asin
asins = soup.find_all(attrs={"data-asin": True})
print(f"\n  {len(asins)}  →  [data-asin] (tous éléments)")

# Affiche le premier produit trouvé
liens = soup.find_all('a', href=lambda h: h and '/dp/' in h)
print(f"\n=== PREMIER LIEN PRODUIT ===")
if liens:
    parent = liens[0].find_parent('div')
    if parent:
        print("Parent div classes:", parent.get('class'))
        pp = parent.find_parent('div')
        if pp:
            print("Grand-parent div classes:", pp.get('class'))
        print("Contenu parent (100 chars):", parent.get_text()[:100].strip())
