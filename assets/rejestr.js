(() => {
  const list = document.querySelector("#decision-list");
  if (!list) return;
  const cards = [...list.querySelectorAll(".decision-card")];
  const search = document.querySelector("#search");
  const pageSize = document.querySelector("#page-size");
  const filters = { type: document.querySelector("#filter-type"), status: document.querySelector("#filter-status"), effect: document.querySelector("#filter-effect"), season: document.querySelector("#filter-season"), subject: document.querySelector("#filter-subject") };
  const controls = [...document.querySelectorAll(".pagination")];
  const allowedSizes = [20, 50, 100];
  const params = new URLSearchParams(location.search);
  const savedSize = Number(localStorage.getItem("registryPageSize"));
  let size = Number(params.get("na_stronie")) || savedSize || 20;
  if (!allowedSizes.includes(size)) size = 20;
  let page = Math.max(1, Number(params.get("strona")) || 1);
  if (pageSize) pageSize.value = String(size);
  const normalize = (value) => value.toLocaleLowerCase("pl-PL").trim();
  function updateUrl() { const next = new URLSearchParams(location.search); next.set("strona", String(page)); next.set("na_stronie", String(size)); history.replaceState(null, "", `${location.pathname}?${next}`); }
  function applyFilters(resetPage = false) {
    if (resetPage) page = 1;
    const query = normalize(search?.value || "");
    const matching = cards.filter((card) => !query || normalize(card.dataset.search || "").includes(query)).filter((card) => Object.entries(filters).every(([key, element]) => !element?.value || card.dataset[key] === element.value));
    const pages = Math.max(1, Math.ceil(matching.length / size)); page = Math.min(page, pages);
    const start = (page - 1) * size, end = Math.min(start + size, matching.length);
    cards.forEach((card) => card.classList.add("hidden")); matching.slice(start, end).forEach((card) => card.classList.remove("hidden"));
    controls.forEach((control) => {
      const summary = control.querySelector("[data-page-summary]");
      if (summary) summary.textContent = matching.length ? `Decyzje ${start + 1}–${end} z ${matching.length} · Strona ${page} z ${pages}` : "Brak pasujących decyzji";
      const previous = control.querySelector('[data-page="previous"]'), next = control.querySelector('[data-page="next"]');
      if (previous) previous.disabled = page === 1; if (next) next.disabled = page === pages;
    }); updateUrl();
  }
  search?.addEventListener("input", () => applyFilters(true));
  Object.values(filters).forEach((element) => element?.addEventListener("change", () => applyFilters(true)));
  pageSize?.addEventListener("change", () => { size = Number(pageSize.value); localStorage.setItem("registryPageSize", String(size)); applyFilters(true); });
  controls.forEach((control) => control.addEventListener("click", (event) => { const direction = event.target.dataset?.page; if (direction === "previous") page -= 1; if (direction === "next") page += 1; if (direction) { applyFilters(); list.scrollIntoView({ behavior: "smooth", block: "start" }); } }));
  applyFilters();
})();
