"use strict";
const fs = require("fs");
const vm = require("vm");
const assert = require("assert");
function element(dataset) {
  return {dataset, hidden: false, attributes: {}, handlers: {},
    addEventListener(name, fn) {this.handlers[name] = fn;},
    setAttribute(name, value) {this.attributes[name] = value;}};
}
const buttons = [element({mode: "total_tokens"}), element({mode: "output_tokens"})];
const charts = [element({chart: "total_tokens"}), element({chart: "output_tokens"})];
const shell = element({}); shell.getBoundingClientRect = () => ({left: 0, top: 0}); shell.clientWidth = 700;
const tooltip = {style: {}, hidden: true, offsetWidth: 200, offsetHeight: 120};
const step = {tagName: "DETAILS", open: false};
const document = {querySelectorAll: query => query === "[data-mode]" ? buttons : charts,
  querySelector: query => query === ".chart-shell" ? shell : tooltip,
  getElementById: id => id === "usage-step-2026-10-30" ? step : null};
vm.runInNewContext(fs.readFileSync("tools/token_usage/app.js", "utf8"), {document});
buttons[1].handlers.click();
assert.equal(charts[0].hidden, true); assert.equal(charts[1].hidden, false);
assert.equal(buttons[1].attributes["aria-pressed"], "true");
const point = {dataset: {tip: "<b>literal counter text</b>"}, getBoundingClientRect: () => ({left: 50, top: 90})};
shell.handlers.focusin({target: {closest: () => point}});
assert.equal(tooltip.textContent, "<b>literal counter text</b>"); assert.equal(tooltip.hidden, false);
assert.equal(tooltip.style.left, "62px");
shell.scrollLeft = 400;
shell.handlers.focusin({target: {closest: () => point}});
assert.equal(tooltip.style.left, "462px");
assert.equal(tooltip.style.top, "110px");
shell.handlers.pointerleave(); assert.equal(tooltip.hidden, true);
shell.handlers.click({target: {closest: () => ({dataset:{step:"usage-step-2026-10-30"}})}});
assert.equal(step.open, true);
step.open = false;
shell.handlers.click({target: {closest: () => ({dataset:{step:"unrelated-id"}})}});
assert.equal(step.open, false);
const window = {location:{hash:"#usage-step-2026-10-30"},handlers:{},
  addEventListener(name,fn){this.handlers[name]=fn;}};
vm.runInNewContext(fs.readFileSync("tools/token_usage/app.js", "utf8"), {document,window});
assert.equal(step.open, true);
step.open = false;
window.handlers.hashchange();
assert.equal(step.open, true);
console.log("Token chart mode, keyboard labels, step selection and deep-link checks passed");
