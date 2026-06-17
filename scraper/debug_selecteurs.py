from bs4 import BeautifulSoup

with open('debug_robot-cuisine.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'lxml')

tests = [
    'div.p13n-sc-uncoverable-faceout',
    'div[id^=p13n-asin]',
    'li.zg-item-immersion',
    'div.zg-item',
    'div[class*=zg]',
    'div[data-asin]',
    'div[class*=p13n]',
    'span[class*=p13n]',
]

print("=== RÉSULTATS SÉLECTEURS ===")
for sel in tests:
    found = soup.select(sel)
    print(f'{len(found):4d} résultats  →  {sel}')

# Cherche aussi les data-asin directement
asins = soup.find_all(attrs={"data-asin": True})
print(f'\n{len(asins):4d} éléments avec attribut data-asin')
if asins:
    print("  Exemple premier élément :", asins[0].name, list(asins[0].attrs.keys()))
