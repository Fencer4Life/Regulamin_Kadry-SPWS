(() => {
  const dayMs = 24 * 60 * 60 * 1000;
  const archivePageSize = 20;

  function calendarDayAge(value, now = new Date()) {
    const created = new Date(value);
    const today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
    const createdDay = Date.UTC(created.getFullYear(), created.getMonth(), created.getDate());
    return Math.max(0, Math.round((today - createdDay) / dayMs));
  }

  function ageClass(age) {
    if (age >= 14) return "discussion-age-long";
    if (age >= 4) return "discussion-age-medium";
    return "discussion-age-fresh";
  }

  document.querySelectorAll("[data-created-at]").forEach((rail) => {
    const age = calendarDayAge(rail.dataset.createdAt);
    rail.classList.remove("discussion-age-fresh", "discussion-age-medium", "discussion-age-long");
    rail.classList.add(ageClass(age));
    rail.querySelector("[data-discussion-age]").textContent = String(age);
    rail.querySelector("[data-discussion-age-unit]").textContent = age === 1 ? "dzień" : "dni";
  });

  document.querySelector("[data-discussion-refresh]")?.addEventListener("click", () => {
    const url = new URL(window.location.href);
    url.searchParams.set("odswiez", String(Date.now()));
    window.location.assign(url);
  });

  const archivePanel = document.querySelector(".discussion-archive-panel");
  const archiveToggle = document.querySelector("[data-discussion-archive-toggle]");
  archiveToggle?.addEventListener("click", () => {
    const isOpen = archivePanel.classList.toggle("is-open");
    archiveToggle.setAttribute("aria-expanded", String(isOpen));
  });

  const archiveItems = Array.from(document.querySelectorAll("[data-discussion-archive-item]"));
  const archivePrevious = document.querySelector("[data-discussion-archive-previous]");
  const archiveNext = document.querySelector("[data-discussion-archive-next]");
  const archivePage = document.querySelector("[data-discussion-archive-page]");
  const archivePagination = document.querySelector(".discussion-archive-pagination");
  const archivePageCount = Math.max(1, Math.ceil(archiveItems.length / archivePageSize));
  let currentArchivePage = 0;

  function renderArchivePage() {
    const first = currentArchivePage * archivePageSize;
    archiveItems.forEach((item, index) => {
      item.hidden = index < first || index >= first + archivePageSize;
    });
    if (archivePage) archivePage.textContent = `${currentArchivePage + 1} / ${archivePageCount}`;
    if (archivePrevious) archivePrevious.disabled = currentArchivePage === 0;
    if (archiveNext) archiveNext.disabled = currentArchivePage >= archivePageCount - 1;
    if (archivePagination) archivePagination.hidden = archiveItems.length <= archivePageSize;
  }

  archivePrevious?.addEventListener("click", () => {
    currentArchivePage = Math.max(0, currentArchivePage - 1);
    renderArchivePage();
  });
  archiveNext?.addEventListener("click", () => {
    currentArchivePage = Math.min(archivePageCount - 1, currentArchivePage + 1);
    renderArchivePage();
  });
  renderArchivePage();
})();
