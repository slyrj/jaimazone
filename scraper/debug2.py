from bs4 import BeautifulSoup

with open('debug_robot-cuisine.html', encoding='utf-8') as f:
    contenu = f.read()

soup = BeautifulSoup(contenu, 'lxml')

# Le titre de la page
titre = soup.find('title')
print("TITRE PAGE :", titre.get_text() if titre else "Pas de titre")

# Cherche un captcha
if 'captcha' in contenu.lower() or 'robot' in contenu.lower()[:5000]:
    print("⚠️  CAPTCHA détecté !")
else:
    print("✅ Pas de captcha visible")

# Cherche si c'est une page de connexion
if 'ap_signin' in contenu or 'sign-in' in contenu.lower()[:5000]:
    print("⚠️  Page de CONNEXION détectée !")

# Affiche les 5 premiers divs avec leurs classes
print("\n--- 10 premiers DIVs avec classes ---")
divs = soup.find_all('div', class_=True)[:10]
for d in divs:
    classes = ' '.join(d.get('class', []))
    print(f"  <div class='{classes[:80]}'>")

# Cherche des liens /dp/ (liens produits Amazon)
liens_dp = soup.find_all('a', href=lambda h: h and '/dp/' in h)
print(f"\n🔗 Liens produits /dp/ trouvés : {len(liens_dp)}")
if liens_dp:
    for lien in liens_dp[:5]:
        print(f"  {lien.get('href', '')[:80]}")
