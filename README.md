# 🛒 JaiMaZone.fr — Site d'affiliation Amazon Maison & Cuisine

Site vitrine d'affiliation Amazon automatisé, catégorie **Maison & Cuisine**.  
Les 50 meilleurs produits Amazon mis à jour quotidiennement via script Python + Mistral API.

## 📁 Structure du projet

```
jaimazone/
├── index.html          ← Page principale du site
├── data/
│   └── produits.json   ← Données produits (généré automatiquement)
├── assets/             ← Images, favicon
├── css/                ← Feuilles de style supplémentaires
├── js/                 ← Scripts supplémentaires
└── README.md
```

## 🚀 Déploiement sur le VPS OVH

```bash
# Cloner le repo sur le VPS
git clone https://github.com/TONUSER/jaimazone.git /var/www/jaimazone

# Pointer Nginx vers /var/www/jaimazone
# Puis pointer le domaine jaimazone.fr vers l'IP du VPS
```

## 🤖 Automatisation

Le fichier `data/produits.json` est régénéré toutes les 24h par le script Python
`../scripts/update_all.py` qui :
1. Appelle l'API Amazon PA v5 pour récupérer les best-sellers
2. Réécrit les descriptions via Mistral API (SEO unique)
3. Injecte les liens d'affiliation avec le tag `jaimazone-21`
4. Régénère `produits.json`

## 🔗 Tag affiliation

```
tag=jaimazone-21
```

## 📊 Catégories

| ID | Label |
|---|---|
| robot-cuisine | Robots de cuisine |
| cafe | Café & Boissons |
| entretien | Entretien maison |
| cuisson | Cuisson |
| rangement | Rangement |
