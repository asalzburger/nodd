"use strict";
const buttons = Array.from(document.querySelectorAll("[data-mode]"));
const charts = Array.from(document.querySelectorAll("[data-chart]"));
buttons.forEach(button => button.addEventListener("click", () => {
  buttons.forEach(item => item.setAttribute("aria-pressed", String(item === button)));
  charts.forEach(chart => { chart.hidden = chart.dataset.chart !== button.dataset.mode; });
  if (tooltip) tooltip.hidden = true;
}));
const shell = document.querySelector(".chart-shell");
const tooltip = document.querySelector(".tooltip");
if (shell && tooltip) {
  const show = event => {
    const point = event.target.closest("[data-tip]");
    if (!point) { tooltip.hidden = true; return; }
    tooltip.textContent = point.dataset.tip;
    tooltip.hidden = false;
    const rect = shell.getBoundingClientRect();
    const target = point.getBoundingClientRect();
    const x = (event.clientX ?? target.left) - rect.left;
    const y = (event.clientY ?? target.top) - rect.top;
    tooltip.style.left = (shell.scrollLeft || 0) + Math.max(8, Math.min(x + 12, shell.clientWidth - tooltip.offsetWidth - 8)) + "px";
    const above = y - tooltip.offsetHeight - 12;
    tooltip.style.top = Math.max(8, above >= 8 ? above : y + 20) + "px";
  };
  shell.addEventListener("pointermove", show);
  shell.addEventListener("focusin", show);
  shell.addEventListener("pointerleave", () => { tooltip.hidden = true; });
  shell.addEventListener("focusout", () => { tooltip.hidden = true; });
  shell.addEventListener("click", event => {
    const point = event.target.closest("[data-step]");
    if (point) revealStep(point.dataset.step);
  });
}
function revealStep(id) {
  if (!/^usage-step-\d{4}-\d{2}-\d{2}$/.test(id)) return;
  const detail = document.getElementById(id);
  if (detail && detail.tagName === "DETAILS") detail.open = true;
}
if (typeof window !== "undefined") {
  const revealHash = () => revealStep(window.location.hash.slice(1));
  revealHash();
  window.addEventListener("hashchange", revealHash);
}
