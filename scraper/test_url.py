import requests
import random
import re
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

# URLs candidates à tester
URLS = [
    "https://www.amazon.fr/gp/bestsellers/kitchen",
    "https://www.amazon.fr/bestsellers/kitchen",
    "https://www.amazon.fr/gp/bestsellers/kitchen/?ref=zg_bs_nav_kitchen_0",
]

headers = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

for url in URLS:
    print(f"\n🔍 Test : {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')
        titre = soup.find('title')
        liens_dp = soup.find_all('a', href=lambda h: h and '/dp/' in h)
        print(f"   Status  : {resp.status_code}")
        print(f"   Titre   : {titre.get_text()[:80] if titre else 'N/A'}")
        print(f"   Liens /dp/ : {len(liens_dp)}")
        if liens_dp:
            print(f"   Exemple : {liens_dp[0].get('href','')[:60]}")
    except Exception as e:
        print(f"   ❌ Erreur : {e}")