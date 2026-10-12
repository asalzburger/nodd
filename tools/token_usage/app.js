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
    tooltip.style.left = Math.max(8, Math.min(x + 12, shell.clientWidth - tooltip.offsetWidth - 8)) + "px";
    tooltip.style.top = Math.max(8, y - 65) + "px";
  };
  shell.addEventListener("pointermove", show);
  shell.addEventListener("focusin", show);
  shell.addEventListener("pointerleave", () => { tooltip.hidden = true; });
  shell.addEventListener("focusout", () => { tooltip.hidden = true; });
}
