/* Public evidence is rendered as plain text, never as HTML or Markdown. */
"use strict";
(function (root) {
  const LONG_MESSAGE = 1100;
  const PREVIEW_LENGTH = 360;
  const TOOL_GROUPS = [
    ["native_codex", "Native Codex tools"],
    ["codex_installed", "Tools installed by Codex"],
    ["instructed_software", "Software used by instruction"],
    ["unresolved", "Unresolved tool provenance"]
  ];
  const asArray = value => Array.isArray(value) ? value : [];
  const asText = value => typeof value === "string" ? value : "";
  const countText = (count, singular, plural = singular + "s") => `${count} ${count === 1 ? singular : plural}`;

  function safeURL(value) {
    if (typeof value !== "string") return null;
    try {
      const url = new URL(value);
      return ["https:", "http:"].includes(url.protocol) && !url.username && !url.password ? url.href : null;
    } catch (_) { return null; }
  }

  function dataPath(value) {
    return typeof value === "string" && /^interactions\/pr-[0-9]+\.json$/.test(value) ? value : null;
  }

  function readLocation(href) {
    const params = new URL(href, "https://example.invalid/").searchParams;
    const raw = params.get("pr");
    const number = raw && /^[1-9][0-9]*$/.test(raw) && Number.isSafeInteger(Number(raw)) ? Number(raw) : null;
    return {number, source: params.get("source") || null, invalid: raw !== null && number === null};
  }

  function locationFor(href, number, source) {
    const url = new URL(href, "https://example.invalid/");
    url.searchParams.set("pr", String(number));
    if (source) url.searchParams.set("source", source);
    else url.searchParams.delete("source");
    url.hash = "";
    return url.pathname + url.search;
  }

  function searchPRs(records, query) {
    const words = asText(query).trim().toLocaleLowerCase().replace(/^#(?=\d)/, "").split(/\s+/).filter(Boolean);
    return asArray(records).filter(pr => {
      const haystack = [String(pr.number), pr.title, ...asArray(pr.parties)].join(" ").toLocaleLowerCase();
      return words.every(word => haystack.includes(word));
    });
  }

  function senderFor(parties, actor) {
    const party = asArray(parties).find(item => item.id === actor);
    const kind = party && ["human", "agent", "account"].includes(party.kind) ? party.kind : "unknown";
    return {
      id: actor,
      name: party && asText(party.name) || "Unrecorded party",
      kind,
      label: {human: "Human", agent: "Agent", account: "Publishing account", unknown: "Identity unrecorded"}[kind]
    };
  }

  function initials(name) {
    return asText(name).split(/\s+/).filter(Boolean).slice(0, 2).map(word => Array.from(word)[0]).join("").toLocaleUpperCase() || "?";
  }

  function chooseSource(groups, requested, parties) {
    const available = asArray(groups).filter(group => asArray(group.threads).some(thread => asArray(thread.messages).length));
    const requestedGroup = available.find(group => group.id === requested);
    if (requestedGroup) return requestedGroup;
    const recorded = available.find(group => group.id === "recorded");
    if (recorded) return recorded;
    const github = available.find(group => group.id === "github");
    if (github && asArray(github.threads).some(thread => asArray(thread.messages).some(message =>
      message.direction === "action" && senderFor(parties, message.actor).kind === "human"))) return github;
    return available.find(group => group.id === "notes") || github || available[0] || null;
  }

  function messagePreview(text) {
    const source = asText(text);
    if (source.length <= LONG_MESSAGE) return {long: false, preview: source};
    return {long: true, preview: source.slice(0, PREVIEW_LENGTH).trimEnd() + "…"};
  }

  function dateLabel(value) {
    if (!value) return null;
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return null;
    return date.toISOString().replace("T", " · ").replace(/:\d\d(?:\.\d+)?Z$/, " UTC");
  }

  function element(doc, tag, className, text) {
    const node = doc.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text);
    return node;
  }

  function sourceLink(doc, url, label = "View source") {
    const safe = safeURL(url);
    if (!safe) return element(doc, "span", "source-unavailable", "Source link unavailable");
    const link = element(doc, "a", "source-link", label);
    link.href = safe;
    link.rel = "noopener noreferrer";
    return link;
  }

  function renderMessage(doc, message, parties, messageIds, index) {
    const sender = senderFor(parties, message.actor);
    const article = element(doc, "article", `message message--${sender.kind}`);
    article.id = messageIds.get(message.id) || `interaction-message-${index}`;
    article.setAttribute("aria-labelledby", article.id + "-sender");
    const avatar = element(doc, "span", "message-avatar", initials(sender.name));
    avatar.setAttribute("aria-hidden", "true");
    const bubble = element(doc, "div", "message-bubble");
    const header = element(doc, "div", "message-heading");
    const name = element(doc, "strong", "message-sender", sender.name);
    name.id = article.id + "-sender";
    header.append(name, element(doc, "span", "party-kind", sender.label));
    const meta = element(doc, "div", "message-meta");
    meta.append(element(doc, "span", "interaction-type", asText(message.type) || "Interaction"));
    if (["action", "reaction"].includes(message.direction)) meta.append(element(doc, "span", "interaction-direction", message.direction));
    asArray(message.roles).forEach(role => meta.append(element(doc, "span", "role-tag", role)));
    if (message.model) meta.append(element(doc, "span", "model-tag", "Model: " + message.model));
    const text = asText(message.text) || "No message text was retained.";
    const preview = messagePreview(text);
    let body;
    if (preview.long) {
      body = element(doc, "details", "message-expand");
      const summary = element(doc, "summary");
      summary.append(element(doc, "span", "message-preview", preview.preview),
        element(doc, "span", "expand-label expand-label--closed", "Read full message"),
        element(doc, "span", "expand-label expand-label--open", "Collapse message"));
      body.append(summary, element(doc, "div", "message-text", text));
    } else body = element(doc, "div", "message-text", text);
    const footer = element(doc, "div", "message-footer");
    footer.append(sourceLink(doc, message.source_url, asText(message.source_label) || "View source"));
    const timestamp = dateLabel(message.timestamp);
    if (timestamp) {
      const time = element(doc, "time", "message-time", timestamp);
      time.dateTime = message.timestamp;
      footer.append(time);
    }
    if (message.reply_to && messageIds.has(message.reply_to)) {
      const reply = element(doc, "a", "reply-link", "Linked interaction");
      reply.href = "#" + messageIds.get(message.reply_to);
      footer.append(reply);
    }
    bubble.append(header, meta, body, footer);
    article.append(avatar, bubble);
    return article;
  }

  function evidenceGroup(doc, title, items, renderItem) {
    const section = element(doc, "details", "evidence-group");
    const summary = element(doc, "summary");
    summary.append(element(doc, "span", "", title), element(doc, "span", "evidence-count", items.length));
    section.append(summary);
    if (!items.length) section.append(element(doc, "p", "evidence-empty", "No evidence retained in this category."));
    else {
      const list = element(doc, "ul", "evidence-list");
      items.forEach(item => list.append(renderItem(item)));
      section.append(list);
    }
    return section;
  }

  function renderEvidence(doc, record) {
    const container = element(doc, "div", "evidence-content");
    container.append(element(doc, "p", "evidence-note", "Execution models and agent roles appear only when recorded. Missing values remain unknown; role names do not prove native profile loading."));
    container.append(evidenceGroup(doc, "Agents & roles", asArray(record.agents), agent => {
      const item = element(doc, "li");
      item.append(element(doc, "strong", "", asText(agent.name) || "Unnamed agent"));
      item.append(element(doc, "p", "evidence-meta", asText(agent.role) || "Role unrecorded"));
      item.append(element(doc, "p", "evidence-meta", "Recorded models: " + (asArray(agent.models).join(", ") || "unknown")));
      if (agent.limitation) item.append(element(doc, "p", "evidence-meta", agent.limitation));
      if (agent.source) item.append(sourceLink(doc, agent.source));
      return item;
    }));
    TOOL_GROUPS.forEach(([key, title]) => container.append(evidenceGroup(doc, title, asArray((record.tools || {})[key]), tool => {
      const item = element(doc, "li");
      item.append(element(doc, "strong", "tool-name", asText(tool.name) || "Unnamed tool"));
      if (tool.version) item.append(element(doc, "span", "tool-version", " · " + tool.version));
      if (tool.evidence) item.append(element(doc, "p", "evidence-meta", tool.evidence));
      if (tool.provenance) item.append(element(doc, "p", "evidence-meta", tool.provenance));
      if (tool.token_account) item.append(element(doc, "p", "evidence-meta", "Account: " + tool.token_account));
      item.append(sourceLink(doc, tool.source));
      return item;
    })));
    container.append(element(doc, "p", "evidence-note", "Token accounts are source references, shared where recorded. Their turn counts are not per-message allocations or additive PR token totals."));
    container.append(evidenceGroup(doc, "Token account references", asArray(record.accounts), account => {
      const item = element(doc, "li");
      item.append(element(doc, "strong", "account-id", asText(account.id) || "Account unrecorded"));
      const turns = Number.isSafeInteger(account.turn_count) && account.turn_count >= 0 ? ` · ${countText(account.turn_count, "referenced turn")}` : "";
      item.append(element(doc, "p", "evidence-meta", (asText(account.status) || "Status unknown") + turns));
      item.append(sourceLink(doc, account.source));
      return item;
    }));
    return container;
  }

  function createController(doc, win, fetcher) {
    const byId = id => doc.getElementById(id);
    const ui = {};
    ["pr-search", "pr-results", "pr-list", "interaction-status", "pr-detail", "pr-number", "pr-title", "pr-coverage", "pr-github", "participants", "source-select", "conversation", "pr-evidence"].forEach(id => { ui[id] = byId(id); });
    if (Object.values(ui).some(node => !node)) throw new Error("The interaction page is missing required elements.");
    let records = [];
    let current = null;
    let selected = null;
    let request = 0;
    const cache = new Map();
    const sourceDescription = element(doc, "p", "source-description");
    sourceDescription.id = "source-description";
    ui["source-select"].setAttribute("aria-describedby", "source-description");
    ui["source-select"].parentNode.append(sourceDescription);

    function status(message, busy = false) {
      ui["interaction-status"].textContent = message;
      ui["interaction-status"].hidden = !message;
      ui.conversation.setAttribute("aria-busy", String(busy));
    }

    function writeLocation(number, source, mode) {
      const next = locationFor(win.location.href, number, source);
      const previous = win.location.pathname + win.location.search + (win.location.hash || "");
      if (next !== previous) win.history[mode === "push" ? "pushState" : "replaceState"]({}, "", next);
    }

    function renderList() {
      const matches = searchPRs(records, ui["pr-search"].value);
      const focusedLink = Array.from(ui["pr-list"].children).find(link => link === doc.activeElement);
      const focusedHref = focusedLink && focusedLink.href;
      ui["pr-list"].replaceChildren();
      ui["pr-results"].textContent = matches.length === records.length ? countText(records.length, "pull request") : `${matches.length} of ${countText(records.length, "pull request")}`;
      matches.forEach(pr => {
        const link = element(doc, "a", "pr-option");
        link.href = locationFor(win.location.href, pr.number, null);
        if (pr.number === selected) link.setAttribute("aria-current", "true");
        const top = element(doc, "span", "pr-option-top");
        top.append(element(doc, "span", "pr-option-number", "#" + pr.number), element(doc, "span", "pr-state", asText(pr.state) || "State unrecorded"));
        link.append(top, element(doc, "span", "pr-option-title", asText(pr.title) || "Untitled pull request"));
        const sources = asArray(pr.sources).map(source => asText(source.label)).filter(Boolean);
        link.append(element(doc, "span", "pr-option-meta", sources.join(" · ") || "No retained messages"));
        link.addEventListener("click", event => {
          if (event.button > 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
          event.preventDefault();
          selectPR(pr.number, null, "push");
        });
        ui["pr-list"].append(link);
        if (link.href === focusedHref) link.focus();
      });
      if (!matches.length) ui["pr-list"].append(element(doc, "p", "no-matches", "No pull requests match. Try a PR number, title or participant."));
    }

    function renderSource(requested, mode) {
      if (!current) return;
      const group = chooseSource(current.groups, requested, current.parties);
      ui["source-select"].replaceChildren();
      asArray(current.groups).filter(item => asArray(item.threads).some(thread => asArray(thread.messages).length)).forEach(item => {
        const option = element(doc, "option", "", item.label || item.id);
        option.value = item.id;
        ui["source-select"].append(option);
      });
      ui["source-select"].disabled = !group;
      ui["source-select"].value = group ? group.id : "";
      ui.conversation.replaceChildren();
      sourceDescription.textContent = group ? asText(group.description) : "No message evidence has been retained for this PR.";
      if (group) {
        const note = element(doc, "p", "conversation-order", "Showing one evidence source in its recorded order. Sources are kept separate; this is selected history.");
        ui.conversation.append(note);
        const ids = new Map();
        let index = 0;
        asArray(group.threads).forEach(thread => asArray(thread.messages).forEach(message => { ids.set(message.id, `interaction-message-${++index}`); }));
        index = 0;
        asArray(group.threads).forEach((thread, threadIndex) => {
          if (!asArray(thread.messages).length) return;
          const section = element(doc, "section", "conversation-thread");
          const heading = element(doc, "h3", "thread-heading", asText(thread.label) || "Recorded evidence");
          heading.id = "interaction-thread-" + threadIndex;
          section.setAttribute("aria-labelledby", heading.id);
          section.append(heading);
          const timestamp = dateLabel(thread.timestamp);
          if (timestamp) section.append(element(doc, "p", "thread-time", `${group.id === "recorded" ? "Turn started" : "Source time"}: ${timestamp}`));
          asArray(thread.messages).forEach(message => section.append(renderMessage(doc, message, current.parties, ids, ++index)));
          ui.conversation.append(section);
        });
      } else ui.conversation.append(element(doc, "p", "conversation-empty", "No messages to display. Source and token references may still be available below."));
      writeLocation(current.number, group && group.id, mode);
    }

    function renderRecord(record, source, mode) {
      current = record;
      ui["pr-number"].textContent = `PULL REQUEST #${record.number} · ${asText(record.state) || "state unrecorded"}`;
      ui["pr-title"].textContent = asText(record.title) || "Untitled pull request";
      const coverage = record.coverage || {};
      ui["pr-coverage"].replaceChildren();
      ui["pr-coverage"].append(element(doc, "p", "coverage-note", asText(coverage.note) || "Selected historical evidence; complete conversation coverage is unknown."));
      const coverageStats = element(doc, "div", "coverage-stats");
      if (Number.isSafeInteger(coverage.recovered_turns)) coverageStats.append(element(doc, "span", "coverage-chip", countText(coverage.recovered_turns, "recovered turn")));
      if (Number.isSafeInteger(coverage.missing_turns) && coverage.missing_turns > 0) coverageStats.append(element(doc, "span", "coverage-chip coverage-chip--missing", countText(coverage.missing_turns, "account turn without message history", "account turns without message history")));
      const capture = dateLabel(record.captured_at);
      if (capture) coverageStats.append(element(doc, "span", "coverage-capture", "GitHub snapshot: " + capture));
      ui["pr-coverage"].append(coverageStats);
      const github = safeURL(record.url);
      ui["pr-github"].hidden = !github;
      if (github) { ui["pr-github"].href = github; ui["pr-github"].rel = "noopener noreferrer"; }
      else ui["pr-github"].removeAttribute("href");
      ui.participants.replaceChildren();
      asArray(record.parties).forEach(party => {
        const sender = senderFor(record.parties, party.id);
        const chip = element(doc, "div", `participant participant--${sender.kind}`);
        const avatar = element(doc, "span", "participant-avatar", initials(sender.name));
        avatar.setAttribute("aria-hidden", "true");
        const name = element(doc, "span", "participant-name", sender.name);
        name.append(element(doc, "small", "", sender.label));
        chip.append(avatar, name);
        ui.participants.append(chip);
      });
      ui["pr-evidence"].replaceChildren(renderEvidence(doc, record));
      renderSource(source, mode);
      ui["pr-detail"].hidden = false;
      status("");
    }

    async function selectPR(number, source, mode = "replace") {
      const ticket = ++request;
      const pr = records.find(item => item.number === number);
      selected = number;
      current = null;
      ui["pr-detail"].hidden = true;
      renderList();
      if (!pr) {
        status(`PR #${number} is not in this published snapshot. Choose another pull request.`);
        return;
      }
      writeLocation(number, source, mode);
      status(`Loading conversation evidence for PR #${number}…`, true);
      try {
        let record = cache.get(number);
        if (!record) {
          const path = dataPath(pr.data);
          if (!path) throw new Error("Invalid PR evidence path");
          const response = await fetcher(path);
          if (!response.ok) throw new Error("PR request failed");
          record = await response.json();
          if (!record || record.number !== number || !Array.isArray(record.groups)) throw new Error("Invalid PR evidence");
          cache.set(number, record);
        }
        if (ticket !== request) return;
        renderRecord(record, source, "replace");
      } catch (_) {
        if (ticket !== request) return;
        status(`Could not load the evidence for PR #${number}. Select it again to retry.`);
      }
    }

    async function restoreLocation() {
      const state = readLocation(win.location.href);
      if (state.invalid) {
        ++request;
        selected = null;
        current = null;
        ui["pr-detail"].hidden = true;
        renderList();
        status("This PR link has an invalid number. Choose a pull request from the list.");
        return;
      }
      if (state.number !== null) return selectPR(state.number, state.source);
      if (records.length) return selectPR(records[0].number, state.source);
      status("No PR interaction records have been published yet.");
    }

    ui["pr-search"].addEventListener("input", renderList);
    ui["source-select"].addEventListener("change", () => renderSource(ui["source-select"].value, "push"));
    win.addEventListener("popstate", restoreLocation);
    return {
      selectPR, restoreLocation,
      async start() {
        status("Loading pull requests…", true);
        try {
          const response = await fetcher("interactions.json");
          if (!response.ok) throw new Error("Index request failed");
          const index = await response.json();
          if (!index || index.schema_version !== 1 || !Array.isArray(index.pull_requests)) throw new Error("Invalid interaction index");
          records = index.pull_requests.filter(pr => Number.isSafeInteger(pr.number) && pr.number > 0).sort((a, b) => b.number - a.number);
          renderList();
          await restoreLocation();
        } catch (_) {
          status("Could not load the PR index. Reload this page to try again.");
        }
      }
    };
  }

  const api = {safeURL, dataPath, readLocation, locationFor, searchPRs, senderFor, chooseSource, messagePreview, renderMessage, renderEvidence, createController};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else {
    const start = () => {
      if (root.document.querySelector(".interaction-page")) createController(root.document, root, root.fetch.bind(root)).start();
    };
    if (root.document.readyState === "loading") root.document.addEventListener("DOMContentLoaded", start, {once: true});
    else start();
  }
})(typeof window !== "undefined" ? window : globalThis);
