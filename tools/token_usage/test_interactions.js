"use strict";
/* Dependency-free controls tests. Real layout/accessibility checks use a browser. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const ui = require("./interactions.js");

class Element {
  constructor(tagName, doc) {
    this.tagName = tagName;
    this.doc = doc;
    this.children = [];
    this.attributes = {};
    this.handlers = {};
    this.hidden = false;
    this.value = "";
    this._text = "";
  }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(child => child.textContent).join(""); }
  set innerHTML(_) { throw new Error("Untrusted HTML must not be used"); }
  append(...nodes) {
    nodes.forEach(node => { node.parentNode = this; this.children.push(node); });
  }
  replaceChildren(...nodes) { this.children = []; this._text = ""; this.append(...nodes); }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  removeAttribute(name) { delete this.attributes[name]; if (name === "href") delete this.href; }
  getAttribute(name) { return this.attributes[name] ?? null; }
  addEventListener(name, callback) { this.handlers[name] = callback; }
  focus() { this.doc.activeElement = this; }
}

function makeDocument() {
  const doc = {activeElement: null, nodes: {}, createElement(tag) { return new Element(tag, this); }, getElementById(id) { return this.nodes[id]; }};
  ["pr-search", "pr-results", "pr-list", "interaction-status", "pr-detail", "pr-number", "pr-title", "pr-coverage", "pr-github", "participants", "source-select", "conversation", "pr-evidence"].forEach(id => {
    doc.nodes[id] = doc.createElement(id === "source-select" ? "select" : "div");
    doc.nodes[id].id = id;
  });
  const controls = doc.createElement("div");
  controls.append(doc.nodes["source-select"]);
  return doc;
}

function makeWindow(href = "https://example.test/nodd/interactions.html") {
  const win = {location: new URL(href), handlers: {}, changes: [], addEventListener(name, fn) { this.handlers[name] = fn; }};
  win.history = {};
  for (const mode of ["pushState", "replaceState"]) win.history[mode] = (_, __, path) => {
    win.location = new URL(path, win.location.href);
    win.changes.push([mode, path]);
  };
  return win;
}

function descendants(element) { return [element, ...element.children.flatMap(descendants)]; }
function findClass(element, name) { return descendants(element).filter(node => (node.className || "").split(" ").includes(name)); }
function response(data, ok = true) { return {ok, json: async () => data}; }
function deferred() { let resolve; const promise = new Promise(done => { resolve = done; }); return {promise, resolve}; }

const parties = [{id: "person", name: "Unnamed project user", kind: "human"}, {id: "agent", name: "Codex", kind: "agent"}, {id: "account", name: "asalzburger", kind: "account"}];
const message = (id, actor, text = "Selected message") => ({id, actor, text, direction: actor === "person" ? "action" : "reaction", type: actor === "person" ? "prompt" : "response", source_url: "https://github.com/example/repo/blob/SHA/log.md", source_label: "Recorded message", roles: []});
const group = (id, messages) => ({id, label: id === "recorded" ? "Recorded messages" : id, description: "Selected " + id + " evidence", threads: [{id: "turn:1", label: "Recorded turn", timestamp: "2026-10-24T09:00:00Z", messages}]});
const record = number => ({number, title: "Infrastructure: PR " + number, url: "https://github.com/example/repo/pull/" + number, state: "open", parties, captured_at: "2026-10-24T10:00:00Z", coverage: {note: "Selected history", recovered_turns: 1, missing_turns: 2}, groups: [group("github", [message("gh", "account", "Public response")]), group("recorded", [message("one", "person", "Human prompt"), {...message("two", "agent", "Agent response"), reply_to: "one"}]), group("notes", [message("note", "agent", "Curated note")])], tools: {native_codex: [{name: "exec_command", source: "https://github.com/example/source"}], codex_installed: [], instructed_software: [{name: "ACTS", source: "https://github.com/example/source"}], unresolved: []}, agents: [{name: "Codex", role: "coordinator", models: [], source: "https://github.com/example/source"}], accounts: [{id: "SESSION-test", status: "unobserved", turn_count: 0, source: "https://github.com/example/source"}]});
const index = {schema_version: 1, pull_requests: [7, 98].map(number => ({number, title: "Infrastructure: PR " + number, parties: ["Codex", "Project user"], data: `interactions/pr-${String(number).padStart(4, "0")}.json`, state: "open", sources: [{id: "recorded", label: "Recorded messages"}]}))};

async function run() {
  assert.deepEqual(ui.searchPRs(index.pull_requests, "#98").map(item => item.number), [98]);
  assert.deepEqual(ui.searchPRs(index.pull_requests, "INFRASTRUCTURE codex").map(item => item.number), [7, 98]);
  assert.equal(ui.searchPRs(index.pull_requests, "unmatched").length, 0);
  assert.equal(ui.searchPRs(index.pull_requests, "   ").length, 2);
  assert.deepEqual(ui.readLocation("https://example.test/?pr=98&source=notes"), {number: 98, source: "notes", invalid: false});
  for (const number of ["0", "-1", "1.5", "98oops", "", "9007199254740992", "01"]) assert.equal(ui.readLocation("https://example.test/?pr=" + number).invalid, true);
  assert.deepEqual(ui.readLocation("https://example.test/"), {number: null, source: null, invalid: false});
  assert.equal(ui.locationFor("https://example.test/nodd/interactions.html?x=one#old", 7, "recorded"), "/nodd/interactions.html?x=one&pr=7&source=recorded");
  assert.equal(ui.locationFor("https://example.test/?pr=7&source=notes", 98, null), "/?pr=98");
  assert.equal(ui.safeURL("https://github.com/a/b#source"), "https://github.com/a/b#source");
  assert.equal(ui.safeURL("http://example.test/"), "http://example.test/");
  for (const url of ["javascript:alert(1)", "data:text/html,hello", "//example.test", "/relative", "https://user:secret@example.test", "invalid", null]) assert.equal(ui.safeURL(url), null);
  assert.equal(ui.dataPath("interactions/pr-0098.json"), "interactions/pr-0098.json");
  for (const path of ["../interactions/pr-0098.json", "https://example.test/pr-1.json", "interactions/../pr-1.json", "interactions/pr-1.json?secret"]) assert.equal(ui.dataPath(path), null);
  assert.equal(ui.senderFor(parties, "account").kind, "account");
  assert.equal(ui.senderFor(parties, "account").label, "Publishing account");
  assert.equal(ui.senderFor(parties, "person").kind, "human");
  assert.equal(ui.senderFor(parties, "agent").kind, "agent");
  assert.equal(ui.senderFor(parties, "missing").name, "Unrecorded party");
  assert.equal(ui.senderFor([{id: "x", name: "X", kind: "bot-like"}], "x").kind, "unknown");
  const groups = record(98).groups;
  assert.equal(ui.chooseSource(groups, null, parties).id, "recorded");
  assert.equal(ui.chooseSource(groups, "notes", parties).id, "notes");
  assert.equal(ui.chooseSource(groups, "nonexistent", parties).id, "recorded");
  assert.equal(ui.chooseSource([groups[0], groups[2]], null, parties).id, "notes");
  assert.equal(ui.chooseSource([group("github", [message("action", "person")]), groups[2]], null, parties).id, "github");
  assert.equal(ui.chooseSource([group("recorded", [])], null, parties), null);
  assert.equal(ui.messagePreview("A short message").long, false);
  assert.equal(ui.messagePreview("a".repeat(2000)).long, true);
  assert.ok(ui.messagePreview("a".repeat(2000)).preview.length < 400);

  const doc = makeDocument();
  const attack = '<img src=x onerror="alert(1)"> <script>bad()</script> & all literal';
  const rendered = ui.renderMessage(doc, {...message("attack", "person", attack), source_url: "javascript:alert(1)"}, parties, new Map(), 1);
  assert.equal(findClass(rendered, "message-text")[0].textContent, attack);
  assert.equal(descendants(rendered).filter(node => ["script", "img"].includes(node.tagName)).length, 0);
  assert.equal(descendants(rendered).filter(node => node.tagName === "a").length, 0);
  assert.ok(rendered.textContent.includes("Source link unavailable"));
  assert.ok(rendered.className.includes("message--human"));
  const accountMessage = ui.renderMessage(doc, message("publish", "account"), parties, new Map(), 2);
  assert.ok(accountMessage.textContent.includes("Publishing account"));
  assert.equal(accountMessage.textContent.includes("Human"), false);
  const longText = attack + "\nlong visible text".repeat(200);
  const long = ui.renderMessage(doc, message("long", "agent", longText), parties, new Map(), 3);
  assert.equal(findClass(long, "message-expand")[0].tagName, "details");
  assert.equal(findClass(long, "message-text")[0].textContent, longText);
  assert.ok(long.textContent.includes("Read full message"));
  const evidence = ui.renderEvidence(doc, record(98));
  assert.ok(evidence.textContent.includes("Native Codex tools"));
  assert.ok(evidence.textContent.includes("Tools installed by Codex"));
  assert.ok(evidence.textContent.includes("Software used by instruction"));
  assert.ok(evidence.textContent.includes("Unresolved tool provenance"));
  assert.ok(evidence.textContent.includes("Recorded models: unknown"));
  assert.ok(evidence.textContent.includes("not per-message allocations or additive PR token totals"));
  const calls = [];
  const win = makeWindow();
  const controller = ui.createController(doc, win, async path => {
    calls.push(path);
    return response(path === "interactions.json" ? index : record(path.includes("0098") ? 98 : 7));
  });
  await controller.start();
  assert.equal(doc.nodes["pr-title"].textContent, "Infrastructure: PR 98");
  assert.equal(doc.nodes["source-select"].value, "recorded");
  assert.equal(win.location.search, "?pr=98&source=recorded");
  assert.equal(doc.nodes["pr-list"].children[0].textContent.includes("#98"), true);
  assert.equal(doc.nodes["pr-detail"].hidden, false);
  assert.equal(doc.nodes["interaction-status"].hidden, true);
  assert.ok(doc.nodes["pr-coverage"].textContent.includes("2 account turns without message history"));
  assert.equal(findClass(doc.nodes.conversation, "reply-link")[0].href, "#interaction-message-1");
  assert.ok(doc.nodes.conversation.textContent.includes("Turn started:"));
  assert.equal(doc.nodes.conversation.textContent.includes("Public response"), false);
  doc.nodes["source-select"].value = "notes";
  doc.nodes["source-select"].handlers.change();
  assert.ok(doc.nodes.conversation.textContent.includes("Curated note"));
  assert.equal(doc.nodes.conversation.textContent.includes("Human prompt"), false);
  assert.equal(win.location.search, "?pr=98&source=notes");
  assert.equal(win.changes.at(-1)[0], "pushState");
  doc.nodes["pr-search"].value = "#7";
  doc.nodes["pr-search"].handlers.input();
  assert.equal(doc.nodes["pr-list"].children.length, 1);
  assert.equal(doc.nodes["pr-results"].textContent, "1 of 2 pull requests");
  doc.nodes["pr-list"].children[0].focus();
  let prevented = false;
  doc.nodes["pr-list"].children[0].handlers.click({button: 0, preventDefault() { prevented = true; }});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(prevented, true);
  assert.equal(doc.activeElement, doc.nodes["pr-list"].children[0], "keyboard focus stays on the selected PR link");
  assert.equal(doc.nodes["pr-title"].textContent, "Infrastructure: PR 7");
  assert.equal(win.location.search, "?pr=7&source=recorded");
  const changesBeforeModifiedClick = win.changes.length;
  doc.nodes["pr-list"].children[0].handlers.click({button: 0, ctrlKey: true});
  assert.equal(win.changes.length, changesBeforeModifiedClick);
  doc.nodes["pr-search"].value = "nobody";
  doc.nodes["pr-search"].handlers.input();
  assert.ok(doc.nodes["pr-list"].textContent.includes("No pull requests match"));
  win.location = new URL("https://example.test/nodd/interactions.html?pr=98&source=github");
  await win.handlers.popstate();
  assert.equal(doc.nodes["source-select"].value, "github");
  assert.ok(doc.nodes.conversation.textContent.includes("Public response"));
  assert.equal(calls.filter(path => path === "interactions/pr-0098.json").length, 1);
  win.location = new URL("https://example.test/nodd/interactions.html?pr=bad");
  await win.handlers.popstate();
  assert.equal(doc.nodes["pr-detail"].hidden, true);
  assert.ok(doc.nodes["interaction-status"].textContent.includes("invalid number"));
  await controller.selectPR(12345);
  assert.ok(doc.nodes["interaction-status"].textContent.includes("not in this published snapshot"));

  const raceDoc = makeDocument();
  const slow98 = deferred();
  const slow7 = deferred();
  const race = ui.createController(raceDoc, makeWindow(), path => path === "interactions.json" ? Promise.resolve(response(index)) : path.includes("0098") ? slow98.promise : slow7.promise);
  const start = race.start();
  await new Promise(resolve => setImmediate(resolve));
  const next = race.selectPR(7);
  slow7.resolve(response(record(7)));
  await next;
  slow98.resolve(response(record(98)));
  await start;
  assert.equal(raceDoc.nodes["pr-title"].textContent, "Infrastructure: PR 7", "a stale response must not replace the current PR");

  const maliciousDoc = makeDocument();
  const malicious = {...record(98), title: attack, parties: [{id: "person", name: attack, kind: "human"}], groups: [group("recorded", [message("danger", "person", attack)])]};
  await ui.createController(maliciousDoc, makeWindow(), async path => response(path === "interactions.json" ? index : malicious)).start();
  assert.equal(maliciousDoc.nodes["pr-title"].textContent, attack);
  assert.ok(maliciousDoc.nodes.participants.textContent.includes(attack));
  assert.equal(findClass(maliciousDoc.nodes.conversation, "message-text")[0].textContent, attack);
  assert.equal(descendants(maliciousDoc.nodes.conversation).filter(node => ["img", "script"].includes(node.tagName)).length, 0);
  const badPathDoc = makeDocument();
  const badPathCalls = [];
  await ui.createController(badPathDoc, makeWindow(), async path => {
    badPathCalls.push(path);
    return response({...index, pull_requests: [{...index.pull_requests[1], data: "https://example.test/private"}]});
  }).start();
  assert.deepEqual(badPathCalls, ["interactions.json"], "the public index cannot cause arbitrary remote fetches");
  assert.ok(badPathDoc.nodes["interaction-status"].textContent.includes("Could not load the evidence"));

  const failedDoc = makeDocument();
  await ui.createController(failedDoc, makeWindow(), async () => response(null, false)).start();
  assert.ok(failedDoc.nodes["interaction-status"].textContent.includes("Could not load the PR index"));
  const emptyDoc = makeDocument();
  await ui.createController(emptyDoc, makeWindow(), async () => response({schema_version: 1, pull_requests: []})).start();
  assert.ok(emptyDoc.nodes["interaction-status"].textContent.includes("No PR interaction records"));
  const emptySourceDoc = makeDocument();
  await ui.createController(emptySourceDoc, makeWindow("https://example.test/?pr=7"), async path => response(path === "interactions.json" ? index : {...record(7), groups: []})).start();
  assert.equal(emptySourceDoc.nodes["source-select"].disabled, true);
  assert.ok(emptySourceDoc.nodes.conversation.textContent.includes("No messages to display"));
  const retryDoc = makeDocument();
  let failPR = true;
  const retry = ui.createController(retryDoc, makeWindow("https://example.test/?pr=7"), async path => path === "interactions.json" ? response(index) : response(record(7), !failPR));
  await retry.start();
  assert.ok(retryDoc.nodes["interaction-status"].textContent.includes("Select it again to retry"));
  failPR = false;
  await retry.selectPR(7);
  assert.equal(retryDoc.nodes["pr-detail"].hidden, false);

  const script = fs.readFileSync(require.resolve("./interactions.js"), "utf8");
  assert.equal(/\.innerHTML\s*=|insertAdjacentHTML|document\.write\s*\(/.test(script), false);
  console.log("PR conversation checks passed: search, deep links/history, source selection, identities, safe text/URLs, long messages, evidence, fetch failures/retry and navigation races.");
}

run().catch(error => { console.error(error); process.exitCode = 1; });
