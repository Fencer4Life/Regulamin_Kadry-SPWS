(() => {
  const dayMs = 24 * 60 * 60 * 1000;

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
})();
