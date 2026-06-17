/* app.js — Logique principale JaiMaZone
   Dépend de utils.js (chargé avant dans index.html) */

let DATA = null;
let filter = 'tout';
let sort = 'rang';
let query = '';

/* ── Rendu d'une carte produit ── */
function renderCard(p, i) {
  const cat =
    DATA.categories.find((c) => c.id === p.categorie)?.label || p.categorie;
  const promo = p.prix_barre
    ? `<div class="price-old">${formatPrix(p.prix_barre)}</div>`
    : '';
  const pts = (p.points || [])
    .slice(0, 3)
    .map((t) => `<span class="card-point">${t}</span>`)
    .join('');

  // Image : photo Amazon si dispo, sinon emoji fallback
  const imageHTML = p.image
    ? `<img src="${p.image}" alt="${p.titre}" loading="lazy"
            style="width:100%;height:100%;object-fit:contain;padding:12px;"
            onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
       <span style="display:none;font-size:72px;width:100%;height:100%;align-items:center;justify-content:center;">${p.icone}</span>`
    : `<span style="font-size:72px;">${p.icone}</span>`;

  // Prix : peut être un nombre ou une chaîne selon la source
  const prixFormate =
    typeof p.prix === 'number' && p.prix > 0
      ? formatPrix(p.prix)
      : p.prix || '—';

  // Description : champ "desc" (scraper) ou "description" (ancienne version)
  const desc = p.desc || p.description || '';

  return `
  <article class="product-card" style="animation-delay:${Math.min(i * 0.06, 0.6)}s">
    <div class="card-rank ${p.rang <= 3 ? 'top3' : ''}">${p.rang}</div>
    ${p.badge ? `<div class="card-badge badge-${p.badge_c}">${p.badge}</div>` : ''}
    <div class="card-image">${imageHTML}</div>
    <div class="card-body">
      <div class="card-category">${cat}</div>
      <h2 class="card-title">${p.titre}</h2>
      <p class="card-desc">${desc}</p>
      <div class="card-points">${pts}</div>
      <div class="card-rating">
        <span class="stars">${renderEtoiles(p.note || 0)}</span>
        <span class="rating-num">${p.note || '—'}</span>
        <span class="rating-count">(${formatNombre(p.avis || 0)} avis)</span>
      </div>
    </div>
    <div class="card-footer">
      <div class="card-price">
        <div class="price-current">${prixFormate}</div>
        ${promo}
      </div>
      <a href="${p.lien}" target="_blank" rel="noopener sponsored" class="btn-amazon">
        Voir sur Amazon
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
          <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
      </a>
    </div>
  </article>`;
}

/* ── Filtrage + tri ── */
function getList() {
  let l = [...DATA.produits];
  if (filter !== 'tout') l = l.filter((p) => p.categorie === filter);
  if (query) {
    const q = query.toLowerCase();
    l = l.filter(
      (p) =>
        p.titre.toLowerCase().includes(q) ||
        (p.desc || p.description || '').toLowerCase().includes(q) ||
        (p.points || []).some((t) => t.toLowerCase().includes(q)),
    );
  }
  if (sort === 'prix-asc') l.sort((a, b) => a.prix - b.prix);
  else if (sort === 'prix-desc') l.sort((a, b) => b.prix - a.prix);
  else if (sort === 'note') l.sort((a, b) => b.note - a.note);
  else if (sort === 'avis') l.sort((a, b) => b.avis - a.avis);
  else l.sort((a, b) => a.rang - b.rang);
  return l;
}

/* ── Rendu complet ── */
function render() {
  const l = getList();
  const grid = document.getElementById('productsGrid');
  document.getElementById('countAffiche').textContent = l.length;
  grid.innerHTML = l.length
    ? l.map((p, i) => renderCard(p, i)).join('')
    : `<div class="empty-state"><div class="icon">🔍</div><h3>Aucun produit trouvé</h3><p>Essayez un autre terme ou une autre catégorie.</p></div>`;
}

/* ── Filtres ── */
function buildFilters() {
  document.getElementById('filtersContainer').innerHTML = DATA.categories
    .map(
      (c) =>
        `<button class="filter-btn ${c.id === 'tout' ? 'active' : ''}" data-cat="${c.id}">${c.icon} ${c.label}</button>`,
    )
    .join('');
  document.getElementById('filtersContainer').addEventListener('click', (e) => {
    const btn = e.target.closest('.filter-btn');
    if (!btn) return;
    filter = btn.dataset.cat;
    document
      .querySelectorAll('.filter-btn')
      .forEach((b) => b.classList.toggle('active', b === btn));
    render();
  });
}

/* ── Liens footer catégories ── */
function buildFooterCats() {
  const ul = document.getElementById('footerCats');
  if (!ul) return;
  ul.innerHTML = DATA.categories
    .filter((c) => c.id !== 'tout')
    .map((c) => `<li><a href="#" data-cat="${c.id}">${c.label}</a></li>`)
    .join('');
  ul.addEventListener('click', (e) => {
    const a = e.target.closest('a[data-cat]');
    if (!a) return;
    e.preventDefault();
    filter = a.dataset.cat;
    document
      .querySelectorAll('.filter-btn')
      .forEach((b) => b.classList.toggle('active', b.dataset.cat === filter));
    window.scrollTo({ top: 0, behavior: 'smooth' });
    render();
  });
}

/* ── Scroll to top ── */
function initScrollTop() {
  const btn = document.getElementById('scrollTop');
  window.addEventListener(
    'scroll',
    () => btn.classList.toggle('visible', scrollY > 400),
    { passive: true },
  );
}

/* ── Init ── */
document.addEventListener('DOMContentLoaded', async () => {
  const raw = await chargerProduits('./data/produits.json');
  if (!raw) {
    document.getElementById('productsGrid').innerHTML =
      `<div class="empty-state"><div class="icon">⚠️</div><h3>Erreur de chargement</h3><p>Impossible de charger les produits. Vérifiez que produits.json existe.</p></div>`;
    return;
  }
  DATA = raw;
  buildFilters();
  buildFooterCats();
  render();
  animerCompteur(
    document.getElementById('counterProduits'),
    DATA.produits.length,
  );
  document.getElementById('searchInput').addEventListener(
    'input',
    debounce((e) => {
      query = e.target.value.trim();
      render();
    }),
  );
  document.getElementById('sortSelect').addEventListener('change', (e) => {
    sort = e.target.value;
    render();
  });
  initScrollTop();
});
