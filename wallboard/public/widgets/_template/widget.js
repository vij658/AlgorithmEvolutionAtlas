// Widget template. Copy the whole folder (e.g. to public/widgets/hello or, on the NAS,
// to /data/widgets/hello), rename nothing else, edit, reload the screen.
//
// mount(root, ctx) is called once per widget instance. `root` is an empty element that
// fills the card. Return a cleanup function (or nothing). When the user changes the
// settings the widget is unmounted and mounted again with the new ctx.settings.
export function mount(root, ctx) {
  const { el } = ctx.util; // el('div.class#id', {props}, ...children) — text is never parsed as HTML
  const s = ctx.settings; // manifest defaults merged with this instance's settings

  root.classList.add('my-widget'); // a class of your own to scope the CSS in style.css
  root.style.setProperty('--accent', s.color);
  const time = el('div.tpl-time.tabular');
  const clicks = el('span');
  root.append(
    el('div.w-head', el('span.w-title', ctx.manifest.name), el('span.w-meta', clicks)),
    el('div.tpl-msg', s.message),
    s.showTime ? time : null,
    el('button.btn.small', { type: 'button', onclick: bump }, 'Click me'),
  );

  // ctx.every(ms, fn) runs fn on an interval that is cleared automatically on unmount.
  if (s.showTime) ctx.every(1000, () => { time.textContent = new Date(ctx.now()).toLocaleTimeString(); });

  // ctx.collection(name) is a live, offline-first list stored on the server and synced
  // to every screen. Use your widget id as a prefix for the name.
  const counter = ctx.collection('template-demo');
  function bump() {
    const cur = counter.get('clicks');
    if (cur) counter.update('clicks', { n: cur.n + 1 }); else counter.add({ id: 'clicks', n: 1 });
  }
  const off = counter.subscribe(() => { clicks.textContent = `${counter.get('clicks')?.n || 0} clicks`; });

  // Other helpers: ctx.api.get('/api/...'), ctx.on('crawl', fn), ctx.onVisible(fn),
  // ctx.isVisible(), ctx.tv, ctx.saveSettings({...}), ctx.util.toast('...'). See WIDGETS.md.
  return () => off();
}
