/* Optional progressive enhancement: all records are rendered in HTML. */
(() => {
  const groups = [
    { form: 'work-filters', selector: '.task', count: 'work-count', empty: 'work-empty', noun: 'tasks' },
    { form: 'review-filters', selector: '.review', count: 'review-count', empty: 'review-empty', noun: 'review rounds' }
  ];
  function apply(group) {
    const form = document.getElementById(group.form);
    const rows = [...document.querySelectorAll(group.selector)];
    const values = [...form.elements].filter(el => el.name).map(el => [el.name, el.value]);
    let shown = 0;
    rows.forEach(row => {
      const visible = values.every(([name, value]) => {
        if (!value) return true;
        if (name === 'q') return row.textContent.toLowerCase().includes(value.toLowerCase());
        const actual = row.getAttribute(`data-${name}`) || '';
        return name === 'milestone' ? actual.split(' ').includes(value) : actual === value;
      });
      row.hidden = !visible;
      if (visible) shown++;
    });
    if (group.noun === 'tasks') {
      document.querySelectorAll('.lane').forEach(lane => {
        lane.hidden = ![...lane.querySelectorAll('.task')].some(row => !row.hidden);
      });
    }
    document.getElementById(group.count).textContent = `${shown} of ${rows.length} ${group.noun} shown`;
    document.getElementById(group.empty).hidden = shown > 0 || rows.length === 0;
  }
  function syncFromUrl() {
    const params = new URLSearchParams(location.search);
    groups.forEach(group => {
      const form = document.getElementById(group.form);
      [...form.elements].filter(el => el.name).forEach(el => { el.value = params.get(el.name) || ''; });
      apply(group);
    });
    revealTarget();
  }
  function updateUrl() {
    const url = new URL(location.href);
    groups.forEach(group => {
      const form = document.getElementById(group.form);
      [...form.elements].filter(el => el.name).forEach(el => {
        if (el.value) url.searchParams.set(el.name, el.value);
        else url.searchParams.delete(el.name);
      });
    });
    history.replaceState(null, '', url);
    groups.forEach(apply);
  }
  function revealTarget() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target || !target.matches('.task,.review')) return;
    const group = groups.find(g => target.matches(g.selector));
    if (target.hidden) {
      document.getElementById(group.form).reset();
      updateUrl();
    }
    const details = target.querySelector('details');
    if (details) details.open = true;
    target.scrollIntoView({ block: 'start' });
  }
  groups.forEach(group => {
    const form = document.getElementById(group.form);
    form.addEventListener('submit', event => event.preventDefault());
    form.addEventListener('input', updateUrl);
    form.addEventListener('change', updateUrl);
    form.addEventListener('reset', () => setTimeout(updateUrl, 0));
  });
  window.addEventListener('popstate', syncFromUrl);
  window.addEventListener('hashchange', revealTarget);
  syncFromUrl();
})();
