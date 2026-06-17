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

# Page principale kitchen — on cherche les liens de sous-catégories
url = "https://www.amazon.fr/gp/bestsellers/kitchen"
resp = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'lxml')

print("=== SOUS-CATÉGORIES TROUVÉES ===\n")

# Cherche tous les liens qui ressemblent à des sous-catégories
liens = soup.find_all('a', href=True)
sous_cats = []
for lien in liens:
    href = lien['href']
    texte = lien.get_text(strip=True)
    if '/gp/bestsellers/kitchen/' in href and texte and len(texte) > 2:
        if href not in [s[1] for s in sous_cats]:
            sous_cats.append((texte, href))

for texte, href in sous_cats:
    url_complete = href if href.startswith('http') else 'https://www.amazon.fr' + href
    print(f"  {texte}")
    print(f"  → {url_complete}\n")
