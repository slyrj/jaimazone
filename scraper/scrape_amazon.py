#!/usr/bin/env python3
"""
JaiMaZone — Amazon.fr Bestsellers Scraper
Scrape → Mistral → produits.json

Usage:
  python scrape_amazon.py                     # toutes catégories, 10 produits chacune
  python scrape_amazon.py --cat cafe          # une seule catégorie
  python scrape_amazon.py --max 20            # plus de produits
  python scrape_amazon.py --no-mistral        # sans réécriture IA
"""

import requests
from bs4 import BeautifulSoup
import json, time, random, re, os, argparse
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
AFFILIATE_TAG   = "slyrj2409-21"
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "wALNkwnXoXJXPRIdBRYRPgcai7wtlBfc")
OUTPUT_FILE     = "../data/produits.json"

# Catégories JaiMaZone → URLs Amazon (toutes testées et fonctionnelles)
CATEGORIES = {
    "robot-cuisine": ("Robots Cuisine", "🤖", "https://www.amazon.fr/gp/bestsellers/kitchen/57696031"),
    "cafe":          ("Café & Boissons", "☕", "https://www.amazon.fr/gp/bestsellers/kitchen/57692031"),
    "entretien":     ("Entretien",       "🧹", "https://www.amazon.fr/gp/bestsellers/kitchen/3575195031"),
    "cuisson":       ("Cuisson",         "🍳", "https://www.amazon.fr/gp/bestsellers/kitchen/32039698031"),
    "rangement":     ("Rangement",       "📦", "https://www.amazon.fr/gp/bestsellers/kitchen/2916060031"),
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

def add_tag(url):
    if not url: return ""
    url = re.sub(r'\?.*', '', url.strip())
    m = re.search(r'/dp/([A-Z0-9]{10})', url)
    if m:
        return f"https://www.amazon.fr/dp/{m.group(1)}?tag={AFFILIATE_TAG}"
    return f"{url}?tag={AFFILIATE_TAG}"

def prix_float(texte):
    if not texte: return None
    m = re.search(r'(\d[\d\s]*[,.]?\d*)', texte.replace("\xa0","").replace(" ",""))
    if m:
        try: return float(m.group(1).replace(",","."))
        except: return None
    return None

def badge_auto(rang, note, avis, prix_val, prix_barre):
    if rang == 1: return "N°1 Ventes", "gold"
    if prix_barre and prix_val and prix_barre > prix_val:
        pct = round((1 - prix_val / prix_barre) * 100)
        if pct >= 10: return f"-{pct}%", "red"
    if note >= 4.8: return "Top qualité", "gold"
    if avis >= 10000: return "Choix populaire", "green"
    if rang <= 3: return "Bestseller", "gold"
    if rang <= 5: return "Coup de ♥", "pink"
    return "", ""

# ─────────────────────────────────────────────────────────────
# SCRAPING
# ─────────────────────────────────────────────────────────────
def scrape_categorie(cat_id, max_produits=10):
    label, icone, url = CATEGORIES[cat_id]
    print(f"\n  📦 [{cat_id}] {url}")

    try:
        resp = requests.get(url, headers=get_headers(), timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ❌ Erreur : {e}")
        return []

    soup = BeautifulSoup(resp.text, 'lxml')
    items = soup.select('div.p13n-sc-uncoverable-faceout')

    if not items:
        # fallback si Amazon change encore
        items = soup.select('div[data-asin]')

    if not items:
        debug = f"debug_{cat_id}.html"
        open(debug, "w", encoding="utf-8").write(resp.text)
        print(f"  ⚠️  0 produit — HTML sauvegardé dans {debug}")
        return []

    print(f"  ✅ {min(len(items), max_produits)} produits trouvés")
    produits = []

    for rang, item in enumerate(items[:max_produits], 1):
        try:
            # Titre (depuis l'alt de l'image — le plus fiable)
            img = item.select_one("img")
            titre = img.get("alt", "").strip() if img else ""
            if not titre:
                span = item.select_one("span.p13n-sc-line-clamp-2, div[class*=line-clamp]")
                titre = span.get_text(strip=True) if span else ""
            if not titre:
                continue

            # Lien + ASIN
            lien_el = item.select_one("a[href*='/dp/']")
            lien_brut = lien_el["href"] if lien_el else ""
            if lien_brut and not lien_brut.startswith("http"):
                lien_brut = "https://www.amazon.fr" + lien_brut
            lien = add_tag(lien_brut)
            asin_m = re.search(r'/dp/([A-Z0-9]{10})', lien)
            asin = asin_m.group(1) if asin_m else f"{cat_id}_{rang}"

            # Image
            image = ""
            if img:
                image = img.get("src") or img.get("data-src") or ""

            # Prix
            prix_el = (
                item.select_one("span._cDEzb_p13n-sc-price_3mJ9Z") or
                item.select_one("span.p13n-sc-price") or
                item.select_one("span.a-color-price")
            )
            prix_texte = prix_el.get_text(strip=True) if prix_el else ""
            prix_val = prix_float(prix_texte) or 0.0

            # Note
            note_el = item.select_one("span.a-icon-alt")
            note_texte = note_el.get_text(strip=True) if note_el else ""
            note_m = re.search(r'(\d[.,]\d)', note_texte)
            note_val = float(note_m.group(1).replace(",",".")) if note_m else 0.0

            # Avis
            avis_el = item.select_one("span.a-size-small") or item.select_one("a[href*='reviews'] span")
            avis_texte = avis_el.get_text(strip=True).replace("\xa0","").replace(" ","") if avis_el else ""
            avis_m = re.search(r'(\d+)', avis_texte)
            avis_val = int(avis_m.group(1)) if avis_m else 0

            produits.append({
                "_asin": asin, "_cat_id": cat_id, "_rang": rang,
                "titre": titre, "prix_val": prix_val, "prix_texte": prix_texte,
                "note_val": note_val, "avis_val": avis_val,
                "image": image, "lien": lien,
            })

        except Exception as e:
            print(f"  ⚠️  Item #{rang} erreur : {e}")
            continue

    return produits

# ─────────────────────────────────────────────────────────────
# MISTRAL — génère desc + points en JSON
# ─────────────────────────────────────────────────────────────
def enrichir_mistral(brut):
    cat_label = CATEGORIES[brut["_cat_id"]][0]
    prompt = f"""Tu es rédacteur e-commerce pour un site d'affiliation Amazon français, niche Maison & Cuisine.
Génère du contenu pour ce produit bestseller Amazon.

Produit : {brut['titre']}
Catégorie : {cat_label}
Prix : {brut['prix_texte']}
Note : {brut['note_val']}/5 ({brut['avis_val']} avis)

Réponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans backticks, avec exactement ces champs :
{{
  "desc": "2-3 phrases, 60-80 mots. Bénéfices concrets, style direct.",
  "points": ["Caractéristique 1", "Caractéristique 2", "Caractéristique 3", "Caractéristique 4"],
  "prix_barre": null
}}

points = 3-4 specs courtes (ex: "Capacité 4,5L", "12 programmes", "Garantie 2 ans")
prix_barre = prix conseillé en float si souvent en promo, sinon null"""

    try:
        resp = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
            json={"model": "mistral-small-latest", "messages": [{"role":"user","content":prompt}],
                  "max_tokens": 300, "temperature": 0.6},
            timeout=25,
        )
        resp.raise_for_status()
        texte = resp.json()["choices"][0]["message"]["content"].strip()
        texte = re.sub(r"```(?:json)?", "", texte).strip().rstrip("`").strip()
        return json.loads(texte)
    except json.JSONDecodeError:
        return {"desc": "", "points": [], "prix_barre": None}
    except Exception as e:
        print(f"  ⚠️  Mistral erreur : {e}")
        return {"desc": "", "points": [], "prix_barre": None}

# ─────────────────────────────────────────────────────────────
# ASSEMBLAGE final au format JaiMaZone exact
# ─────────────────────────────────────────────────────────────
def assembler(brut, enrichi, id_global, rang_global):
    prix_val   = brut["prix_val"]
    prix_barre = enrichi.get("prix_barre")
    note_val   = brut["note_val"]
    avis_val   = brut["avis_val"]
    badge_txt, badge_c = badge_auto(rang_global, note_val, avis_val, prix_val, prix_barre)
    return {
        "id":        id_global,
        "rang":      rang_global,
        "categorie": brut["_cat_id"],
        "titre":     brut["titre"],
        "desc":      enrichi.get("desc", ""),
        "points":    enrichi.get("points", [])[:4],
        "prix":      prix_val,
        "prix_barre": prix_barre,
        "note":      note_val,
        "avis":      avis_val,
        "badge":     badge_txt,
        "badge_c":   badge_c,
        "lien":      brut["lien"],
        "icone":     CATEGORIES[brut["_cat_id"]][1],
        "image":     brut["image"],
        "asin":      brut["_asin"],
        "date_maj":  datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }

def load_existing(filepath):
    if not os.path.exists(filepath): return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {p["asin"]: p for p in data.get("produits", []) if p.get("asin")}
    except: return {}

def build_json(produits):
    return {
        "meta": {
            "site": "jaimazone.fr", "niche": "Maison & Cuisine",
            "tag_affiliation": AFFILIATE_TAG,
            "derniere_maj": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "total_produits": len(produits),
        },
        "categories": [
            {"id":"tout",          "label":"Tout voir",       "icon":"⭐"},
            {"id":"robot-cuisine", "label":"Robots Cuisine",  "icon":"🤖"},
            {"id":"cafe",          "label":"Café & Boissons", "icon":"☕"},
            {"id":"entretien",     "label":"Entretien",       "icon":"🧹"},
            {"id":"cuisson",       "label":"Cuisson",         "icon":"🍳"},
            {"id":"rangement",     "label":"Rangement",       "icon":"📦"},
        ],
        "produits": produits,
    }

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cat", choices=list(CATEGORIES.keys()) + ["toutes"], default="toutes")
    parser.add_argument("--max", type=int, default=10)
    parser.add_argument("--no-mistral", action="store_true")
    parser.add_argument("--output", default=OUTPUT_FILE)
    args = parser.parse_args()

    cats = list(CATEGORIES.keys()) if args.cat == "toutes" else [args.cat]
    use_mistral = not args.no_mistral and MISTRAL_API_KEY != "COLLE_TA_CLE_ICI"

    print(f"""
╔══════════════════════════════════════════════════════╗
║   JaiMaZone Scraper — Amazon → produits.json         ║
║   Catégories : {str(cats):<38}║
║   Max/cat    : {args.max:<38}║
║   Tag        : {AFFILIATE_TAG:<38}║
║   Mistral    : {'✅ activé' if use_mistral else '⛔ désactivé':<38}║
╚══════════════════════════════════════════════════════╝""")

    existants = load_existing(args.output)
    print(f"\n📂 {len(existants)} produits existants (réutilisation descriptions)")

    tous_bruts = []
    for i, cat_id in enumerate(cats):
        bruts = scrape_categorie(cat_id, args.max)
        tous_bruts.extend(bruts)
        if i < len(cats) - 1:
            delai = random.uniform(3, 6)
            print(f"  ⏳ Pause {delai:.1f}s...")
            time.sleep(delai)

    if not tous_bruts:
        print("\n❌ Aucun produit. Vérifie les fichiers debug_*.html")
        return

    print(f"\n📊 {len(tous_bruts)} produits — enrichissement Mistral...")
    produits_finaux = []

    for i, brut in enumerate(tous_bruts, 1):
        asin = brut["_asin"]
        print(f"  [{i}/{len(tous_bruts)}] {brut['titre'][:55]}")

        if asin in existants and existants[asin].get("desc"):
            ex = existants[asin]
            enrichi = {"desc": ex.get("desc",""), "points": ex.get("points",[]), "prix_barre": ex.get("prix_barre")}
            print(f"          ♻️  desc réutilisée")
        elif use_mistral:
            print(f"          ✍️  Mistral...")
            enrichi = enrichir_mistral(brut)
            time.sleep(random.uniform(0.6, 1.2))
        else:
            enrichi = {"desc": "", "points": [], "prix_barre": None}

        produits_finaux.append(assembler(brut, enrichi, i, i))

    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(build_json(produits_finaux), f, ensure_ascii=False, indent=2)

    print(f"""
✅ Terminé !
   • Produits : {len(produits_finaux)}
   • Fichier  : {args.output}
   • Avec desc: {sum(1 for p in produits_finaux if p.get('desc'))}
""")

if __name__ == "__main__":
    main()