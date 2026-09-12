(() => {
  const list = document.querySelector("#decision-list");
  if (!list) return;
  const cards = [...list.querySelectorAll(".decision-card")];
  const search = document.querySelector("#search");
  const filters = {
    type: document.querySelector("#filter-type"), status: document.querySelector("#filter-status"),
    season: document.querySelector("#filter-season"), subject: document.querySelector("#filter-subject"),
  };
  const count = document.querySelector("#result-count");
  const normalize = (value) => value.toLocaleLowerCase("pl-PL").trim();
  function applyFilters() {
    const query = normalize(search?.value || "");
    let visible = 0;
    for (const card of cards) {
      const matchesSearch = !query || normalize(card.dataset.search || "").includes(query);
      const matchesFilters = Object.entries(filters).every(([key, element]) => !element?.value || card.dataset[key] === element.value);
      const matches = matchesSearch && matchesFilters;
      card.classList.toggle("hidden", !matches);
      if (matches) visible += 1;
    }
    if (count) count.textContent = `Widoczne decyzje: ${visible} z ${cards.length}`;
  }
  search?.addEventListener("input", applyFilters);
  Object.values(filters).forEach((element) => element?.addEventListener("change", applyFilters));
  applyFilters();
})();
