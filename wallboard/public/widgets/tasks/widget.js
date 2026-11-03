// Tasks with priority. Stored in the "tasks" collection: offline-first (localStorage)
// and synced to the server so every screen sees the same list.
const PRI = { 1: { name: 'High', short: '!!!' }, 2: { name: 'Normal', short: '!!' }, 3: { name: 'Low', short: '!' } };

export function mount(root, ctx) {
  const { el } = ctx.util;
  const s = ctx.settings;
  const listName = s.list || 'default';
  const col = ctx.collection('tasks');
  let newPri = Number(s.defaultPriority) || 2;

  const input = el('input.tk-input', { type: 'text', placeholder: 'Add a task…', enterkeyhint: 'done', maxlength: 300, 'aria-label': 'New task' });
  const priBtn = el('button.tk-pri-pick', { type: 'button', title: 'Priority for the new task', onclick: () => { newPri = (newPri % 3) + 1; paintPri(); } });
  const paintPri = () => { priBtn.textContent = PRI[newPri].short; priBtn.dataset.p = String(newPri); priBtn.setAttribute('aria-label', `Priority: ${PRI[newPri].name}. Tap to change.`); };
  paintPri();
  const add = () => {
    const text = input.value.trim();
    if (!text) return;
    col.add({ text, priority: newPri, done: false, list: listName });
    input.value = '';
  };
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); add(); } });

  const meta = el('span.w-meta');
  const list = el('ul.tk-list.w-scroll');
  const footer = el('div.tk-foot');
  root.append(
    el('div.w-head', el('span.w-title', s.title || 'Tasks'), meta),
    el('div.tk-new', priBtn, input, el('button.btn.primary', { type: 'button', onclick: add, 'aria-label': 'Add task' }, 'Add')),
    list, footer,
  );

  function render(items) {
    const mine = items.filter((t) => (t.list || 'default') === listName);
    const open = mine.filter((t) => !t.done).sort((a, b) => a.priority - b.priority || String(a.createdAt).localeCompare(String(b.createdAt)));
    const done = mine.filter((t) => t.done).sort((a, b) => String(b.doneAt).localeCompare(String(a.doneAt)));
    meta.textContent = open.length ? `${open.length} open` : mine.length ? 'all done' : '';
    const rows = [...open, ...(s.showDone ? done : [])].map((t) => el('li.tk-row', { dataset: { p: String(t.priority), done: t.done ? '1' : '0' } },
      el('button.tk-check', { type: 'button', role: 'checkbox', 'aria-checked': t.done ? 'true' : 'false', 'aria-label': `${t.done ? 'Mark not done' : 'Mark done'}: ${t.text}`,
        onclick: () => col.update(t.id, { done: !t.done, doneAt: t.done ? null : new Date(ctx.now()).toISOString() }) }, t.done ? '✓' : ''),
      el('button.tk-pri', { type: 'button', title: `${PRI[t.priority]?.name || 'Normal'} priority — tap to change`, 'aria-label': `Priority ${PRI[t.priority]?.name}. Change`,
        onclick: () => col.update(t.id, { priority: ((Number(t.priority) || 2) % 3) + 1 }) }, PRI[t.priority]?.short || '!!'),
      el('span.tk-text', t.text),
      el('button.tk-del', { type: 'button', 'aria-label': `Delete ${t.text}`, title: 'Delete', onclick: () => col.remove(t.id) }, '✕')));
    list.replaceChildren(...(rows.length ? rows : [el('li.w-empty', 'Nothing to do. Add a task above.')]));
    footer.replaceChildren(done.length ? el('button.btn.small', { type: 'button', onclick: () => done.forEach((t) => col.remove(t.id)) }, `Clear ${done.length} done`) : '');
  }
  return col.subscribe(render);
}
