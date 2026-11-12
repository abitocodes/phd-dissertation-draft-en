/* Drawing helpers shared by the thesis diagrams drawn in HTML (see README.md in this folder).
   SVG coordinates are in millimetres when the <svg> has viewBox="0 0 W H" and width="Wmm" height="Hmm".

   Fig.edge(svg, [x1,y1], [x2,y2], opt)   arrow between two nodes, shortened to the node outlines
       opt: color, width (mm), dash ("1 0.7"), bend (mm, + bends to the left of the direction), half (node half size),
            shape ("square" | "circle"), gap (extra mm at both ends), head (true: arrow head), label, labelPos (0..1)
   Fig.graph(svg, {nodes, edges, kinds, node})
       nodes: {id: [x, y] | {x, y, label, fill, shape, half}}
       edges: [[from, to, kind, bend, label], ...]      kinds: {kind: edge options}
       node:  defaults for nodes {half, shape, fill, label, labelColor, labelSize}
   Fig.contract(svg, x, y, half, fill)   rounded square with a "{}" glyph (a contract)
   Fig.person(svg, x, y, s, color)       a user-account icon centred at (x, y), s = height in mm
   Fig.text(svg, x, y, str, opt)         opt: size (mm), weight, fill, anchor, italic, family
   Fig.icon(name, color, size)           inline SVG markup for HTML (size in mm); names in Fig.ICONS
*/
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const el = (parent, tag, attrs, text) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs || {}) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    parent.appendChild(e);
    return e;
  };
  const defs = (svg) => svg.querySelector("defs") || el(svg, "defs", {});
  const marker = (svg, color) => {
    const id = "mk-" + color.replace(/[^0-9a-zA-Z]/g, "");
    if (!svg.querySelector("#" + id)) {
      const m = el(defs(svg), "marker", { id, viewBox: "0 0 10 10", refX: 8.6, refY: 5, markerWidth: 3.6, markerHeight: 3.6, orient: "auto" });
      el(m, "path", { d: "M0,0.6 L10,5 L0,9.4 z", fill: color });
    }
    return `url(#${id})`;
  };
  const outline = (ux, uy, half, shape) => shape === "circle" ? half : half / Math.max(Math.abs(ux), Math.abs(uy));

  function edge(svg, a, b, o = {}) {
    const [x1, y1] = a, [x2, y2] = b, dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L;
    const half = o.half ?? 3, shape = o.shape || "square", gap = o.gap ?? 0.5, bend = o.bend || 0;
    const s = outline(ux, uy, o.halfFrom ?? half, o.shapeFrom || shape) + gap;
    const e = outline(ux, uy, o.halfTo ?? half, o.shapeTo || shape) + gap + (o.head === false ? 0 : 0.35);
    const sx = x1 + ux * s, sy = y1 + uy * s, ex = x2 - ux * e, ey = y2 - uy * e;
    const mx = (sx + ex) / 2 - uy * bend, my = (sy + ey) / 2 + ux * bend;
    const color = o.color || "#334155";
    const p = el(svg, "path", { d: `M${sx},${sy} Q${mx},${my} ${ex},${ey}`, fill: "none", stroke: color,
      "stroke-width": o.width ?? 0.45, "stroke-dasharray": o.dash, "stroke-linecap": "round",
      "marker-end": o.head === false ? null : marker(svg, color) });
    if (o.label !== undefined) {
      const t = o.labelPos ?? 0.5, qx = (1 - t) * (1 - t) * sx + 2 * (1 - t) * t * mx + t * t * ex,
        qy = (1 - t) * (1 - t) * sy + 2 * (1 - t) * t * my + t * t * ey;
      const off = o.labelOffset ?? 1.6, lx = qx - uy * off * Math.sign(bend || 1), ly = qy + ux * off * Math.sign(bend || 1);
      text(svg, lx, ly + 0.8, String(o.label), { size: o.labelSize || 2.5, fill: o.labelColor || color, anchor: "middle", weight: 600 });
    }
    return p;
  }

  function contract(svg, x, y, half = 3, fill = "#0F766E", glyph = true) {
    el(svg, "rect", { x: x - half, y: y - half, width: 2 * half, height: 2 * half, rx: half * 0.42, fill });
    if (glyph) text(svg, x, y + half * 0.3, "{}", { size: half * 0.88, weight: 700, fill: "#fff", anchor: "middle", family: "Consolas, monospace" });
  }

  function person(svg, x, y, s = 6, color = "#7A8594") {
    const r = s * 0.2;
    el(svg, "circle", { cx: x, cy: y - s * 0.22, r, fill: color });
    const w = s * 0.36, base = y + s * 0.5;
    el(svg, "path", { d: `M${x - w},${base} a${w},${w * 0.95} 0 0 1 ${2 * w},0 z`, fill: color });
  }

  function text(svg, x, y, str, o = {}) {
    return el(svg, "text", { x, y, "font-size": o.size || 2.6, "font-weight": o.weight || 400, fill: o.fill || "#1F2937",
      "text-anchor": o.anchor || "start", "font-style": o.italic ? "italic" : null,
      "font-family": o.family || "Segoe UI, Arial, sans-serif" }, str);
  }

  function graph(svg, spec) {
    const nd = Object.assign({ half: 3, shape: "square", fill: "#0F766E", labelColor: "#fff", labelSize: 2.6 }, spec.node || {});
    const N = {};
    for (const [id, v] of Object.entries(spec.nodes)) N[id] = Array.isArray(v) ? { x: v[0], y: v[1] } : v;
    for (const [from, to, kind, bend, label] of spec.edges || []) {
      const k = Object.assign({}, (spec.kinds || {})[kind] || {});
      const a = N[from], b = N[to];
      edge(svg, [a.x, a.y], [b.x, b.y], Object.assign(k, { bend, label, half: nd.half, shape: nd.shape,
        halfFrom: a.half ?? nd.half, halfTo: b.half ?? nd.half, shapeFrom: a.shape || nd.shape, shapeTo: b.shape || nd.shape }));
    }
    for (const [id, n] of Object.entries(N)) {
      const half = n.half ?? nd.half, shape = n.shape || nd.shape, fill = n.fill || nd.fill;
      if (shape === "circle") el(svg, "circle", { cx: n.x, cy: n.y, r: half, fill, stroke: n.stroke, "stroke-width": n.strokeWidth });
      else if (n.glyph !== false && n.label === undefined) contract(svg, n.x, n.y, half, fill);
      else el(svg, "rect", { x: n.x - half, y: n.y - half, width: 2 * half, height: 2 * half, rx: half * 0.42, fill });
      if (n.label !== undefined) text(svg, n.x, n.y + (n.labelSize || nd.labelSize) * 0.36, n.label,
        { size: n.labelSize || nd.labelSize, weight: 700, fill: n.labelColor || nd.labelColor, anchor: "middle" });
    }
    return N;
  }

  const ICONS = {
    bars: c => `<rect x="1" y="6.5" width="2.4" height="4.5" rx="0.5" fill="${c}"/><rect x="4.8" y="3.5" width="2.4" height="7.5" rx="0.5" fill="${c}" opacity="0.75"/><rect x="8.6" y="1" width="2.4" height="10" rx="0.5" fill="${c}" opacity="0.5"/>`,
    search: c => `<circle cx="5" cy="5" r="3.3" fill="none" stroke="${c}" stroke-width="1.3"/><path d="M7.4,7.4 L10.8,10.8" stroke="${c}" stroke-width="1.6" stroke-linecap="round"/>`,
    calendar: c => `<rect x="1" y="2" width="10" height="9" rx="1.2" fill="none" stroke="${c}" stroke-width="1.1"/><path d="M1,4.8 H11" stroke="${c}" stroke-width="1.1"/><path d="M3.6,0.8 V3 M8.4,0.8 V3" stroke="${c}" stroke-width="1.1" stroke-linecap="round"/><rect x="6.6" y="6.6" width="2.6" height="2.6" rx="0.4" fill="${c}"/>`,
    scale: c => `<path d="M6,1 V10.5 M3,10.8 H9" stroke="${c}" stroke-width="1.1" stroke-linecap="round"/><path d="M1.5,3 H10.5" stroke="${c}" stroke-width="1.1"/><path d="M1.5,3 L0.5,6.3 H2.5 Z M10.5,3 L9.5,6.3 H11.5 Z" fill="${c}"/>`,
    person: c => `<circle cx="6" cy="3.4" r="2.3" fill="${c}"/><path d="M1.8,11.2a4.2,4 0 0 1 8.4,0z" fill="${c}"/>`,
    people: c => `<circle cx="3.2" cy="4" r="1.6" fill="${c}" opacity="0.7"/><path d="M0.4,10a2.8,2.6 0 0 1 5.6,0z" fill="${c}" opacity="0.7"/><circle cx="8.8" cy="4" r="1.6" fill="${c}" opacity="0.7"/><path d="M6,10a2.8,2.6 0 0 1 5.6,0z" fill="${c}" opacity="0.7"/><circle cx="6" cy="3.2" r="1.9" fill="${c}"/><path d="M2.8,10.6a3.2,3 0 0 1 6.4,0z" fill="${c}"/>`,
    contract: c => `<rect x="1" y="1" width="10" height="10" rx="2.2" fill="${c}"/><text x="6" y="8.2" font-size="6" font-weight="700" fill="#fff" text-anchor="middle" font-family="Consolas,monospace">{}</text>`,
    coin: c => `<circle cx="6" cy="6" r="4.8" fill="none" stroke="${c}" stroke-width="1.2"/><path d="M6,3.2 V8.8 M4.4,4.6 H7.1 a1.1,1.1 0 0 1 0,2.2 H4.9 a1.1,1.1 0 0 0 0,2.2 H7.6" stroke="${c}" stroke-width="0.9" fill="none"/>`,
    key: c => `<circle cx="4" cy="6" r="2.6" fill="none" stroke="${c}" stroke-width="1.2"/><path d="M6.6,6 H11 M9.4,6 V8 M10.9,6 V7.6" stroke="${c}" stroke-width="1.2" stroke-linecap="round"/>`,
    web: c => `<circle cx="6" cy="6" r="4.8" fill="none" stroke="${c}" stroke-width="1"/><ellipse cx="6" cy="6" rx="2" ry="4.8" fill="none" stroke="${c}" stroke-width="0.9"/><path d="M1.2,6 H10.8 M2,3.5 H10 M2,8.5 H10" stroke="${c}" stroke-width="0.8"/>`,
    doc: c => `<path d="M2.5,1 H7.5 L10,3.5 V11 H2.5 Z" fill="none" stroke="${c}" stroke-width="1.1" stroke-linejoin="round"/><path d="M4.2,5.5 H8.3 M4.2,7.4 H8.3 M4.2,9.2 H7" stroke="${c}" stroke-width="0.9"/>`,
    database: c => `<ellipse cx="6" cy="2.6" rx="4.4" ry="1.6" fill="none" stroke="${c}" stroke-width="1"/><path d="M1.6,2.6 V9.4 a4.4,1.6 0 0 0 8.8,0 V2.6 M1.6,6 a4.4,1.6 0 0 0 8.8,0" fill="none" stroke="${c}" stroke-width="1"/>`,
    gear: c => `<circle cx="6" cy="6" r="2" fill="none" stroke="${c}" stroke-width="1.1"/><path d="M6,0.8 V2.6 M6,9.4 V11.2 M0.8,6 H2.6 M9.4,6 H11.2 M2.3,2.3 L3.6,3.6 M8.4,8.4 L9.7,9.7 M2.3,9.7 L3.6,8.4 M8.4,3.6 L9.7,2.3" stroke="${c}" stroke-width="1.3" stroke-linecap="round"/>`,
    check: c => `<circle cx="6" cy="6" r="5.2" fill="${c}"/><path d="M3.4,6.2 L5.3,8 L8.7,4.2" stroke="#fff" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`,
    cross: c => `<circle cx="6" cy="6" r="5.2" fill="${c}"/><path d="M4,4 L8,8 M8,4 L4,8" stroke="#fff" stroke-width="1.3" stroke-linecap="round"/>`,
    half: c => `<circle cx="6" cy="6" r="5.2" fill="none" stroke="${c}" stroke-width="1.1"/><path d="M6,0.8 A5.2,5.2 0 0 1 6,11.2 Z" fill="${c}"/>`,
    clock: c => `<circle cx="6" cy="6" r="4.8" fill="none" stroke="${c}" stroke-width="1.1"/><path d="M6,3 V6.2 L8.2,7.6" stroke="${c}" stroke-width="1.1" fill="none" stroke-linecap="round"/>`,
    crawl: c => `<circle cx="2.2" cy="6" r="1.5" fill="${c}"/><circle cx="6.2" cy="2.6" r="1.3" fill="${c}" opacity="0.75"/><circle cx="6.2" cy="9.4" r="1.3" fill="${c}" opacity="0.75"/><circle cx="10" cy="6" r="1.1" fill="${c}" opacity="0.5"/><path d="M3.4,5.2 L5.2,3.4 M3.4,6.8 L5.2,8.6 M7.3,3.3 L9.1,5.2" stroke="${c}" stroke-width="0.8"/>`,
    lock: c => `<rect x="2.2" y="5.2" width="7.6" height="5.8" rx="1.2" fill="${c}"/><path d="M3.8,5.2 V3.8 a2.2,2.2 0 0 1 4.4,0 V5.2" fill="none" stroke="${c}" stroke-width="1.1"/>`,
  };
  const icon = (name, color = "#1F2937", size = 4.4) =>
    `<svg width="${size}mm" height="${size}mm" viewBox="0 0 12 12" style="flex:none">${ICONS[name](color)}</svg>`;

  window.Fig = { el, defs, marker, edge, graph, contract, person, text, icon, ICONS };
  // Fill every <span data-icon="name" data-color="#hex" data-size="4.4"></span> with its icon.
  document.addEventListener("DOMContentLoaded", () => {
    for (const s of document.querySelectorAll("[data-icon]"))
      s.outerHTML = icon(s.dataset.icon, s.dataset.color || "#1F2937", parseFloat(s.dataset.size || "4.4"));
  });
})();
