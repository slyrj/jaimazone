#!/usr/bin/env python3
"""
Génère une page guide d'achat HTML pour une catégorie,
basée sur les produits réels de produits.json + Mistral.

Usage:
  python generate_guide.py --cat robot-cuisine
"""

import json
import requests
import re
import os
import argparse

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "wALNkwnXoXJXPRIdBRYRPgcai7wtlBfc")
PRODUITS_FILE = "../data/produits.json"
OUTPUT_DIR = ".."  # racine du site

CAT_LABELS = {
    "robot-cuisine": "Robot Cuisine",
    "cafe": "Machine à Café",
    "entretien": "Aspirateur & Entretien",
    "cuisson": "Friteuse & Cuisson",
    "rangement": "Rangement & Organisation",
}


def charger_produits(cat_id):
    with open(PRODUITS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    produits = [p for p in data["produits"] if p["categorie"] == cat_id]
    produits.sort(key=lambda p: p["rang"])
    return produits[:5]  # top 5 pour le guide


def generer_intro_mistral(cat_id, produits):
    cat_label = CAT_LABELS.get(cat_id, cat_id)
    liste_produits = "\n".join(
        f"- {p['titre'][:80]} ({p['prix']}€, note {p['note']}/5)"
        for p in produits
    )
    prompt = f"""Tu es rédacteur expert pour un site comparatif Amazon français.
Rédige un guide d'achat pour la catégorie "{cat_label}".

Top 5 produits actuels :
{liste_produits}

Réponds UNIQUEMENT avec un JSON valide, sans markdown, avec ces champs exacts :
{{
  "titre_guide": "Titre accrocheur du guide (ex: Comment bien choisir son robot de cuisine en 2026)",
  "intro": "Introduction de 80-100 mots expliquant les critères de choix pour cette catégorie",
  "criteres": ["Critère 1 à vérifier", "Critère 2", "Critère 3", "Critère 4"],
  "conclusion": "Phrase de conclusion de 30-40 mots qui invite à consulter le classement ci-dessous"
}}"""

    try:
        resp = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
            json={"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 500, "temperature": 0.6},
            timeout=25,
        )
        resp.raise_for_status()
        texte = resp.json()["choices"][0]["message"]["content"].strip()
        texte = re.sub(r"```(?:json)?", "", texte).strip().rstrip("`").strip()
        return json.loads(texte)
    except Exception as e:
        print(f"⚠️ Erreur Mistral : {e}")
        return {
            "titre_guide": f"Guide d'achat : {cat_label}",
            "intro": "Découvrez notre sélection des meilleurs produits.",
            "criteres": ["Qualité", "Prix", "Avis clients", "Garantie"],
            "conclusion": "Consultez notre classement ci-dessous."
        }


def generer_avis_produit_mistral(produit):
    """Génère un petit avis 'pourquoi ce choix' pour un produit du top 3."""
    prompt = f"""Produit : {produit['titre'][:100]}
Prix : {produit['prix']}€, Note : {produit['note']}/5 ({produit['avis']} avis)
Description : {produit.get('desc', '')}

Rédige UNE phrase (25-35 mots) expliquant pourquoi ce produit mérite sa place dans le classement.
Style direct, factuel. Réponds uniquement avec la phrase, sans guillemets."""

    try:
        resp = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
            json={"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 100, "temperature": 0.6},
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip().strip('"')
    except Exception:
        return ""


def build_html(cat_id, guide_data, produits, avis_top3):
    cat_label = CAT_LABELS.get(cat_id, cat_id)
    criteres_html = "\n".join(f"<li>{c}</li>" for c in guide_data["criteres"])

    produits_html = ""
    for i, p in enumerate(produits):
        avis = avis_top3.get(p["asin"], "")
        avis_block = f'<p style="font-size:13px;color:var(--orange-lt);margin-top:6px;font-style:italic;">{avis}</p>' if avis else ""
        produits_html += f"""
    <div style="display:flex;gap:16px;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:var(--r-lg);margin-bottom:12px;">
      <img src="{p['image']}" alt="{p['titre']}" style="width:80px;height:80px;object-fit:contain;flex-shrink:0;">
      <div style="flex:1;">
        <div style="font-size:11px;color:var(--orange);font-weight:600;">#{p['rang']} — {cat_label}</div>
        <h3 style="font-family:var(--font-display);font-size:15px;font-weight:700;margin:4px 0;color:var(--cream);">{p['titre'][:80]}</h3>
        <div style="display:flex;gap:12px;align-items:center;font-size:13px;color:var(--grey-lt);">
          <span style="color:var(--orange);font-weight:700;font-family:var(--font-display);">{p['prix']}€</span>
          <span>★ {p['note']}/5 ({p['avis']} avis)</span>
        </div>
        {avis_block}
        <a href="{p['lien']}" target="_blank" rel="noopener sponsored" class="btn-amazon" style="margin-top:10px;display:inline-flex;">Voir sur Amazon</a>
      </div>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{guide_data['titre_guide']} | JaiMaZone</title>
<meta name="description" content="{guide_data['intro'][:155]}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://jaimazone.fr/guide-{cat_id}.html">
<link rel="icon" type="image/svg+xml" href="./assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="./css/variables.css">
<link rel="stylesheet" href="./css/utils.css">
<link rel="stylesheet" href="./css/styles.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{guide_data['titre_guide']}",
  "description": "{guide_data['intro'][:155]}",
  "author": {{"@type": "Organization", "name": "JaiMaZone"}},
  "publisher": {{"@type": "Organization", "name": "JaiMaZone"}}
}}
</script>
</head>
<body>

<nav class="nav">
  <a href="/" style="text-decoration:none;"><div class="nav-logo">Jai<span>Ma</span>Zone</div></a>
</nav>

<div style="max-width:760px;margin:0 auto;padding:48px var(--padding-x) 80px;">
  <a href="/" style="font-size:13px;color:var(--orange);">&larr; Retour au classement complet</a>

  <h1 style="font-family:var(--font-display);font-size:clamp(26px,4vw,38px);font-weight:800;margin:16px 0 20px;color:var(--cream);line-height:1.2;">{guide_data['titre_guide']}</h1>

  <p style="font-size:15px;color:var(--grey-lt);line-height:1.8;margin-bottom:28px;">{guide_data['intro']}</p>

  <h2 style="font-family:var(--font-display);font-size:18px;font-weight:700;margin-bottom:14px;color:var(--orange);">Critères essentiels à vérifier</h2>
  <ul style="padding-left:20px;margin-bottom:32px;">
    {criteres_html}
  </ul>

  <h2 style="font-family:var(--font-display);font-size:18px;font-weight:700;margin-bottom:16px;color:var(--orange);">Notre Top 5 du moment</h2>
  {produits_html}

  <p style="font-size:14px;color:var(--grey-lt);line-height:1.8;margin-top:24px;">{guide_data['conclusion']}</p>

  <a href="/" class="btn-amazon" style="display:inline-flex;margin-top:16px;">Voir le classement complet &rarr;</a>
</div>

<div class="footer-bottom">
  <span>© 2026 JaiMaZone.fr — Tous droits réservés</span>
  <span><a href="./mentions-legales.html">Mentions légales</a> · <a href="./confidentialite.html">Confidentialité</a></span>
</div>

</body>
</html>"""

    output_path = os.path.join(OUTPUT_DIR, f"guide-{cat_id}.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cat", required=True, choices=list(CAT_LABELS.keys()))
    args = parser.parse_args()

    print(f"📖 Génération guide pour : {args.cat}")
    produits = charger_produits(args.cat)
    if not produits:
        print("❌ Aucun produit trouvé pour cette catégorie.")
        return

    print("✍️  Génération intro Mistral...")
    guide_data = generer_intro_mistral(args.cat, produits)

    print("✍️  Génération avis top 3...")
    avis_top3 = {}
    for p in produits[:3]:
        avis_top3[p["asin"]] = generer_avis_produit_mistral(p)

    output_path = build_html(args.cat, guide_data, produits, avis_top3)
    print(f"✅ Guide généré : {output_path}")


if __name__ == "__main__":
    main()
