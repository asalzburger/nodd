/* Synthetic DOM fixtures for filter/deep-link logic; not browser layout tests.
   Run with Node, or macOS JavaScriptCore (whose URL test shim is below). */
const source = typeof require === 'function'
  ? require('fs').readFileSync('dashboard/app.js', 'utf8') : readFile('dashboard/app.js');
const report = typeof print === 'function' ? print : console.log;
if (typeof URLSearchParams === 'undefined') {
  // JavaScriptCore's shell lacks browser URL APIs. Node uses its native APIs.
  globalThis.URLSearchParams = class {
    constructor(query = '') {
      this.values = new Map(query.replace(/^\?/, '').split('&').filter(Boolean).map(pair => {
        const [key, value = ''] = pair.split('=');
        return [decodeURIComponent(key), decodeURIComponent(value.replace(/\+/g, ' '))];
      }));
    }
    get(key) { return this.values.get(key) || null; }
    set(key, value) { this.values.set(key, value); }
    delete(key) { this.values.delete(key); }
    toString() { return [...this.values].map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(v)).join('&'); }
  };
  globalThis.URL = class {
    constructor(href) {
      this.base = href.split(/[?#]/)[0];
      this.hash = href.includes('#') ? '#' + href.split('#')[1] : '';
      this.searchParams = new URLSearchParams(href.includes('?') ? href.split('?')[1].split('#')[0] : '');
    }
    toString() { const q = this.searchParams.toString(); return this.base + (q ? '?' + q : '') + this.hash; }
  };
}
let checks = 0;
function assert(value, message) { if (!value) throw Error(message); checks++; }
const pending = [];
globalThis.setTimeout = callback => pending.push(callback);
class Form {
  constructor(names) { this.elements = names.map(name => ({ name, value: '' })); this.events = {}; }
  addEventListener(name, callback) { this.events[name] = callback; }
  reset() { if (this.events.reset) this.events.reset(); this.elements.forEach(el => { el.value = ''; }); }
  set(name, value) { this.elements.find(el => el.name === name).value = value; this.events.input(); }
}
function row(id, kind, attrs, content) {
  return { id, kind, attrs, textContent: content, hidden: false, detail: { open: false },
    getAttribute(name) { return this.attrs[name]; },
    matches(selector) { return selector.split(',').includes(this.kind); },
    querySelector() { return this.kind === '.task' ? this.detail : null; },
    scrollIntoView() { this.scrolled = true; } };
}
const tasks = [
  row('TEST-TASK-A', '.task', { 'data-stage': 'B', 'data-milestone': 'M0 M1', 'data-role': 'Software', 'data-state': 'active' }, 'Synthetic dashboard task'),
  row('TEST-TASK-B', '.task', { 'data-stage': 'C', 'data-milestone': 'M2', 'data-role': 'Tracker', 'data-state': 'planned' }, 'Synthetic tracking task')
];
const reviews = [
  row('TEST-ROUND-A', '.review', { 'data-review-type': 'technical', 'data-review-state': 'open' }, 'Synthetic open review'),
  row('TEST-ROUND-B', '.review', { 'data-review-type': 'expert', 'data-review-state': 'closed' }, 'Synthetic adverse closed review')
];
const work = new Form(['stage', 'milestone', 'role', 'subsystem', 'state', 'q']);
const reviewForm = new Form(['review-type', 'review-state']);
const nodes = { 'work-filters': work, 'review-filters': reviewForm };
['work-count', 'review-count', 'work-empty', 'review-empty'].forEach(id => { nodes[id] = {}; });
[...tasks, ...reviews].forEach(item => { nodes[item.id] = item; });
const lanes = tasks.map(task => ({ hidden: false, querySelectorAll() { return [task]; } }));
globalThis.document = {
  getElementById(id) { return nodes[id] || null; },
  querySelectorAll(selector) { return selector === '.task' ? tasks : selector === '.review' ? reviews : lanes; }
};
const windowEvents = {};
globalThis.window = { addEventListener(name, callback) { windowEvents[name] = callback; } };
globalThis.location = { href: 'https://example.invalid/nodd/?milestone=M1', search: '?milestone=M1', hash: '' };
globalThis.history = { replaceState(a, b, url) {
  location.href = String(url);
  location.search = location.href.includes('?') ? '?' + location.href.split('?')[1].split('#')[0] : '';
  location.hash = location.href.includes('#') ? '#' + location.href.split('#')[1] : '';
} };
eval(source);
assert(!tasks[0].hidden && tasks[1].hidden, 'Restore milestone filter and match multiple milestone IDs');
assert(nodes['work-count'].textContent === '1 of 2 tasks shown', 'Announce filtered count');
assert(lanes[1].hidden, 'Hide empty workstream');
work.reset(); pending.splice(0).forEach(fn => fn());
assert(tasks.every(t => !t.hidden), 'Reset restores tasks');
work.set('q', 'TRACKING');
assert(tasks[0].hidden && !tasks[1].hidden, 'Search ignores case');
assert(location.search.includes('q=TRACKING'), 'Filters persist in shareable URL');
reviewForm.set('review-state', 'closed');
assert(reviews[0].hidden && !reviews[1].hidden, 'Filter closed archive separately from open queue');
assert(tasks[0].hidden, 'Review filter preserves work filter');
work.set('q', 'NO SYNTHETIC MATCH');
assert(nodes['work-empty'].hidden === false, 'Explain zero matching tasks');
location.hash = '#TEST-TASK-A'; location.href = 'https://example.invalid/nodd/' + location.search + location.hash;
windowEvents.hashchange();
assert(!tasks[0].hidden && tasks[0].detail.open, 'Deep link reveals task and opens details despite filters');
assert(tasks[0].scrolled, 'Deep link scrolls to task');
location.search = '?stage=C'; location.hash = ''; location.href = 'https://example.invalid/nodd/?stage=C';
windowEvents.popstate();
assert(tasks[0].hidden && !tasks[1].hidden, 'History navigation restores URL filter');
const original = work.events.submit;
let prevented = false; original({ preventDefault() { prevented = true; } });
assert(prevented, 'Submitting filters does not navigate away');
location.hash = '#%invalid'; windowEvents.hashchange();
assert(true, 'Malformed hash does not crash');
report(`Passed ${checks} JavaScript assertions (synthetic DOM; no layout verification).`);
