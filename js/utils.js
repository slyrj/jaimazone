/* utils.js — Fonctions utilitaires JaiMaZone */

function formatPrix(prix) {
  return prix.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' });
}
function formatNombre(n) {
  return n.toLocaleString('fr-FR');
}
function renderEtoiles(note) {
  const full = Math.floor(note), half = note % 1 >= .5 ? 1 : 0, empty = 5 - full - half;
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty);
}
function animerCompteur(el, target, duree = 1200) {
  let start = null;
  const step = ts => {
    if (!start) start = ts;
    const p = Math.min((ts - start) / duree, 1);
    el.textContent = Math.round((1 - Math.pow(1 - p, 3)) * target);
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
function debounce(fn, delai = 200) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delai); };
}
async function chargerProduits(url = './data/produits.json') {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  } catch (err) {
    console.error('Erreur chargement produits:', err);
    return null;
  }
}
