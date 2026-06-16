/* =============================================
   utils.js — Fonctions utilitaires JaiMaZone
   ============================================= */

/**
 * Formate un prix en euros français
 * ex: 149.9 → "149,90 €"
 */
function formatPrix(prix) {
  return prix.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' });
}

/**
 * Formate un nombre avec séparateur de milliers
 * ex: 12043 → "12 043"
 */
function formatNombre(n) {
  return n.toLocaleString('fr-FR');
}

/**
 * Génère le HTML des étoiles à partir d'une note
 * ex: 4.5 → "★★★★½"
 */
function renderEtoiles(note) {
  const full  = Math.floor(note);
  const half  = note % 1 >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty);
}

/**
 * Anime un compteur de 0 à target
 */
function animerCompteur(el, target, duree = 1200) {
  let start = null;
  const step = (ts) => {
    if (!start) start = ts;
    const progress = Math.min((ts - start) / duree, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(ease * target);
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/**
 * Affiche un toast de notification temporaire
 */
function afficherToast(message, duree = 3000) {
  let toast = document.querySelector('.toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duree);
}

/**
 * Debounce — évite les appels trop fréquents
 */
function debounce(fn, delai = 200) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delai);
  };
}

/**
 * Charge un JSON externe (pour produits.json en prod)
 */
async function chargerProduits(url = './data/produits.json') {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Erreur chargement produits:', err);
    return null;
  }
}

/**
 * Sauvegarde un état dans sessionStorage
 */
function sauvegarderEtat(cle, valeur) {
  try { sessionStorage.setItem(`jaimazone_${cle}`, JSON.stringify(valeur)); }
  catch(e) {}
}

/**
 * Récupère un état depuis sessionStorage
 */
function lireEtat(cle, defaut = null) {
  try {
    const val = sessionStorage.getItem(`jaimazone_${cle}`);
    return val ? JSON.parse(val) : defaut;
  } catch(e) { return defaut; }
}
