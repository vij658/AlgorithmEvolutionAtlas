/* ---------------- the board ---------------- */
function stagesOf(a, b) {            // the squares cut from an a-by-b rectangle, stage by stage
  let x = 0, y = 0, w = a, h = b; const out = [];
  while (w > 0 && h > 0) {
    const s = Math.min(w, h), n = Math.floor(Math.max(w, h) / s);
    out.push({side: s, count: n, x, y, horizontal: w >= h, piece: {x, y, w, h}});
    if (w >= h) { x += n * s; w -= n * s; } else { y += n * s; h -= n * s; }
  }
  return out;
}
const board = {a: 1071, b: 462, stages: [], shown: 0, timer: null, view: null, anim: null};
const rect = document.getElementById("rect");
function setView(target, animate) {
  const cur = board.view || target;
  board.view = target;
  if (board.anim) cancelAnimationFrame(board.anim);
  if (!animate || reduceMotion) { rect.setAttribute("viewBox", `${target.x} ${target.y} ${target.w} ${target.h}`); return; }
  const t0 = performance.now(), dur = 650;
  const step = now => {
    const k = Math.min(1, (now - t0) / dur), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
    const v = ["x", "y", "w", "h"].map(p => cur[p] + (target[p] - cur[p]) * e);
    rect.setAttribute("viewBox", v.join(" "));
    if (k < 1) board.anim = requestAnimationFrame(step);
  };
  board.anim = requestAnimationFrame(step);
}
function fitBox(p) {                 // a viewBox around a piece, with the board's aspect ratio
  const ar = board.a / board.b, pad = 1.25;
  let w = p.w * pad, h = p.h * pad;
  if (w / h > ar) h = w / ar; else w = h * ar;
  return {x: p.x + p.w / 2 - w / 2, y: p.y + p.h / 2 - h / 2, w, h};
}
function drawBoard(animateZoom) {
  const {a, b, stages, shown} = board;
  rect.replaceChildren();
  sv("rect", {x: 0, y: 0, width: a, height: b, fill: "var(--wash)", stroke: "var(--ink)", "stroke-width": 1.5, "vector-effect": "non-scaling-stroke"}, rect);
  for (let k = 0; k < shown; k++) {
    const st = stages[k], color = COLORS[k % 3], on = ON[k % 3];
    if (st.count > 400) {            // too many squares to draw one by one: draw the block they fill
      const p = st.piece, w = st.horizontal ? st.count * st.side : p.w, h = st.horizontal ? p.h : st.count * st.side;
      sv("rect", {x: st.x, y: st.y, width: w, height: h, fill: color, opacity: .85}, rect);
      continue;
    }
    for (let i = 0; i < st.count; i++) {
      const x = st.horizontal ? st.x + i * st.side : st.x, y = st.horizontal ? st.y : st.y + i * st.side;
      sv("rect", {x, y, width: st.side, height: st.side, fill: color, stroke: "var(--paper)", "stroke-width": 1.5, "vector-effect": "non-scaling-stroke"}, rect);
      if (st.count <= 40) sv("text", {x: x + st.side / 2, y: y + st.side / 2, "text-anchor": "middle", "dominant-baseline": "central", fill: on,
        "font-size": st.side * 0.3, "font-family": "var(--mono)", "font-weight": 600}, rect, fmt(st.side));
    }
  }
  // the zoom target: the piece still to be filled, or the last one filled
  let target = {x: 0, y: 0, w: a, h: b}, note = "";
  const idx = shown < stages.length ? shown : stages.length - 1;
  const piece = shown === 0 ? null : stages[idx].piece;
  if (piece && Math.max(piece.w / a, piece.h / b) < 0.18 && !board.whole) {
    target = fitBox(piece);
    note = `Zoomed in ×${(a / target.w).toFixed(1)} on the ${fmt(piece.w)} × ${fmt(piece.h)} piece.`;
  } else if (shown === 0) note = "Press Step to cut the first squares.";
  else if (shown === stages.length) note = "Done: the last squares fill their piece exactly.";
  document.getElementById("zoomnote").textContent = note;
  setView(target, animateZoom);
  renderSteps();
}
function gcdInfo(a, b) {
  // quotients, remainders and Bezout coefficients with BigInt so large inputs stay exact
  let r0 = BigInt(a), r1 = BigInt(b), s0 = 1n, s1 = 0n, t0 = 0n, t1 = 1n; const rows = [];
  while (r1 !== 0n) {
    const q = r0 / r1, r2 = r0 - q * r1;
    rows.push({big: r0, q, small: r1, r: r2});
    [r0, r1] = [r1, r2]; [s0, s1] = [s1, s0 - q * s1]; [t0, t1] = [t1, t0 - q * t1];
  }
  return {rows, g: r0, x: s0, y: t0};
}
function renderSteps() {
  const info = gcdInfo(board.a, board.b), ol = document.getElementById("steps");
  ol.replaceChildren();
  const max = 12;
  info.rows.forEach((row, i) => {
    if (i >= max && i !== info.rows.length - 1) { if (i === max) el("li", {class: "pending"}, ol, `… ${info.rows.length - max - 1} more …`); return; }
    const li = el("li", {class: i < board.shown ? (i === board.shown - 1 ? "current" : "") : "pending"}, ol);
    const sw = el("span", {class: "sw"}, li); sw.style.background = COLORS[i % 3];
    el("span", {}, li, `${fmt(row.big)} = ${fmt(row.q)} × ${fmt(row.small)} + ${fmt(row.r)}`);
  });
  const res = document.getElementById("result");
  res.replaceChildren();
  if (board.shown === board.stages.length) {
    const qs = info.rows.map(r => fmt(r.q));
    const p1 = el("p", {}, res); p1.append("gcd = "); el("b", {}, p1, fmt(info.g));
    p1.append(` · continued fraction [${qs[0]}${qs.length > 1 ? "; " + qs.slice(1).join(", ") : ""}]`);
    const p2 = el("p", {}, res); p2.append("Bézout: "); el("b", {}, p2, `${fmt(info.g)} = ${info.x} × ${fmt(board.a)} + ${info.y} × ${fmt(board.b)}`);
  } else {
    el("p", {}, res, `${board.shown} of ${board.stages.length} stages cut.`);
  }
  // work done by each method
  const g = info.g, subtractions = info.rows.reduce((s, r) => s + r.q, 0n);
  const trying = BigInt(Math.min(board.a, board.b)) - g + 1n;
  const work = [["Trying candidates", trying], ["Subtracting (Euclid)", subtractions], ["Dividing", BigInt(info.rows.length)]];
  const maxLog = Math.max(...work.map(w => Math.log10(Number(w[1]) + 1)));
  const box = document.getElementById("work"); box.replaceChildren();
  el("div", {class: "eyebrow"}, box, "Work done, on a log scale");
  for (const [name, v] of work) {
    const row = el("div", {class: "row"}, box);
    el("span", {}, row, name);
    const cell = el("div", {}, row);
    const bar = el("div", {class: "bar"}, cell); bar.style.width = `${Math.max(1, Math.log10(Number(v) + 1) / (maxLog || 1) * 100)}%`;
    el("span", {class: "val"}, cell, `${fmt(v)} ${name.startsWith("Div") ? "divisions" : name.startsWith("Sub") ? "subtractions" : "candidates"}`);
  }
}
function load(a, b) {
  stop();
  a = Math.max(1, Math.min(1e12, Math.floor(a))); b = Math.max(1, Math.min(1e12, Math.floor(b)));
  if (b > a) [a, b] = [b, a];
  board.a = a; board.b = b; board.stages = stagesOf(a, b); board.whole = false;
  document.getElementById("in-a").value = a; document.getElementById("in-b").value = b;
  board.view = null; board.shown = 0;
  drawBoard(false);
}
function stepOnce() { if (board.shown < board.stages.length) { board.shown++; board.whole = false; drawBoard(true); } if (board.shown >= board.stages.length) stop(); }
function stop() { if (board.timer) { clearInterval(board.timer); board.timer = null; } document.getElementById("btn-play").textContent = "Play"; }
document.getElementById("btn-step").addEventListener("click", () => {
  stop();
  if (board.shown >= board.stages.length) { board.shown = 0; board.view = null; }   // start again from the empty rectangle
  board.whole = false; document.getElementById("btn-whole").textContent = "Whole rectangle";
  stepOnce();
});
document.getElementById("btn-play").addEventListener("click", e => {
  if (board.timer) return stop();
  board.whole = false; document.getElementById("btn-whole").textContent = "Whole rectangle";
  if (board.shown >= board.stages.length) { board.shown = 0; board.view = null; drawBoard(false); }
  e.target.textContent = "Pause";
  board.timer = setInterval(stepOnce, reduceMotion ? 400 : 1100);
});
document.getElementById("btn-reset").addEventListener("click", () => load(+document.getElementById("in-a").value, +document.getElementById("in-b").value));
document.getElementById("btn-whole").addEventListener("click", () => { board.whole = !board.whole; drawBoard(true); document.getElementById("btn-whole").textContent = board.whole ? "Follow the pieces" : "Whole rectangle"; });
for (const id of ["in-a", "in-b"]) document.getElementById(id).addEventListener("change", () => load(+document.getElementById("in-a").value, +document.getElementById("in-b").value));
document.querySelectorAll(".presets button").forEach(btn => btn.addEventListener("click", () => load(+btn.dataset.a, +btn.dataset.b)));
// at rest: 1071 and 462, fully cut
load(1071, 462); board.shown = board.stages.length; board.whole = true; drawBoard(false);
document.getElementById("btn-whole").textContent = "Follow the pieces";
document.getElementById("zoomnote").textContent = "All three stages are cut. Press Step to replay, and the view follows the pieces as they shrink.";

