/* Drawing helpers of the thesis diagrams drawn in HTML (see README.md and STYLE.md in this folder).
   SVG coordinates are in millimetres when the <svg> has viewBox="0 0 W H" and width="Wmm" height="Hmm".

   Fig.C                                  the colours of style.css by name (Fig.C.allow, Fig.C.transfer, ...)
   Fig.edge(svg, [x1,y1], [x2,y2], opt)   arrow between two nodes, shortened to the node outlines
       opt: color, width (mm), dash ("1.1 0.8"), bend (mm), half (node half size), shape ("square" | "circle"),
            gap (extra mm at both ends), head (false: none), headSize (mm: a head of fixed size, for a band),
            label, labelPos (0..1), labelSize, labelColor, labelOffset, labelSerif / labelItalic (Palatino)
   Fig.graph(svg, {nodes, edges, kinds, node})   as in fig.js
   Fig.node(svg, x, y, opt)               a node: opt half, fill, shape, label, ring (a thin frame around it), glyph
   Fig.contract(svg, x, y, half, fill)    a contract: square with a "{}" glyph and a white keyline
   Fig.person(svg, x, y, s, color)        a user-account figure centred at (x, y), s = height in mm
   Fig.text(svg, x, y, str, opt)          opt: size (mm), weight, fill, anchor, serif (Palatino), italic (Palatino italic),
                                          mono (Consolas, for an identifier of the chain)
   Fig.rich(svg, x, y, str, opt)          text with marked parts: $x$ variable, #1 − # upright Palatino, _{obs} subscript,
                                          _{$q$} italic subscript, `code` monospace
   Fig.star(svg, x, y, r, color)          a five-pointed star (a hot contract)
   Fig.arrow(color, len, dir, dash)       an arrow between two parts of a figure, as HTML markup (dir: right, left, down, up)
   Fig.chevron(color, h, dir)             an open chevron ">" between two cards of a row, as HTML markup (dir: right, left)
   Fig.dots(svg, d, color, width)         a dotted leader (round dots) along the path d
   Fig.icon(name, color, size)            pictogram in a colour, inline SVG markup for HTML (size in mm)
   Fig.medal(name, color, size)           the pictogram in white on a solid disc with a ring, as HTML markup
   Fig.medalAt(svg, name, color, x, y, size)   the same inside an SVG, centred at (x, y)
   Fig.ramp(svg, id, stops, angle)        a linear gradient for an illustration (stops: [[offset, colour], ...])

   When the page has loaded, every <span data-icon>, <span data-medal>, <span data-arrow> and <span data-chevron> is replaced by its
   drawing, and every <span class="badge">1</span> by the numbered disc in its ring.
*/
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const SANS = "Bahnschrift, Segoe UI, Arial, sans-serif", SERIF = "Palatino Linotype, Book Antiqua, Palatino, Cambria Math, serif";
  const MONO = "Consolas, Cascadia Mono, monospace";
  // The colours are those of style.css, read from its custom properties (--allow-band becomes C.allowBand), so the
  // stylesheet is the one place that names a colour. The values here are used only if the stylesheet is missing.
  const C = {
    paper: "#FFFFFF", plate: "#F3F3F2", plate2: "#E6E6E4", rule: "#B4B4B4", hair: "#C4C4C2",
    ink: "#161616", text: "#333333", muted: "#575757",
    allow: "#B98A24", allowBand: "#CFA448", allowInk: "#6B4C0C", allowFill: "#DDBB76", allowBg: "#F4E9CF", allowPlane: "#F5EACB",
    transfer: "#2340C8", transferInk: "#162A8C", transferFill: "#97A6E3", transferBg: "#E2E6F8", transferPlane: "#D5DBF4",
    coupled: "#6A2C91", coupledInk: "#4A1D68", coupledFill: "#B79BCB", coupledBg: "#EFE7F4",
    contract: "#2A7A72", contractInk: "#1C544F", contractFill: "#8FC1BA", contractBg: "#E2F0EE",
    user: "#8A8A8A", userInk: "#4A4A4A", userFill: "#C9C9C7", userBg: "#F3F3F2",
    count: "#5A5A5A", countInk: "#333333", countFill: "#A9A9A7", countBg: "#ECECEA",
    web: "#2C8FB3", webInk: "#1C5F78", webBg: "#E1F0F5", leader: "#9A9A98",
    rq1: "#2C8FB3", rq2: "#2F7D45", rq3: "#C23B5E", rq45: "#6A2C91",
    rq1Bg: "#E1F0F5", rq2Bg: "#E3F0E6", rq3Bg: "#F8E4EA", rq45Bg: "#EFE7F4",
    good: "#2F7D45", bad: "#B3372B", mixed: "#8A6410", goodBg: "#E3F0E6", badBg: "#F7E3E0", mixedBg: "#F4E9CF",
  };
  {
    const css = getComputedStyle(document.documentElement);
    for (const k of Object.keys(C)) {
      const prop = "--" + k.replace(/[A-Z]/g, m => "-" + m.toLowerCase()).replace("plate2", "plate-2");
      const val = css.getPropertyValue(prop).trim();
      if (val) C[k] = val;
    }
  }
  const colour = (c, fallback) => C[c] || c || fallback;      // a name of C or a colour as it is
  const el = (parent, tag, attrs, text) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs || {}) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    parent.appendChild(e);
    return e;
  };
  const defs = (svg) => svg.querySelector("defs") || el(svg, "defs", {});
  // a slim arrow head with a notch at its back. Without a size it grows with the line (4.1 line widths long);
  // with a size (mm) it is that long whatever the line, which a broad band needs: the band ends inside the head.
  const HEAD_BACK = 5.2;                       // of the 10 units of the head, how many lie beyond the end of a band
  const marker = (svg, color, size) => {
    const id = "mk-" + color.replace(/[^0-9a-zA-Z]/g, "") + (size ? "-" + String(size).replace(".", "_") : "");
    if (!svg.querySelector("#" + id)) {
      const m = el(defs(svg), "marker", size
        ? { id, viewBox: "0 0 10 10", refX: 10 - HEAD_BACK, refY: 5, markerWidth: size, markerHeight: size, markerUnits: "userSpaceOnUse", orient: "auto" }
        : { id, viewBox: "0 0 10 10", refX: 8.4, refY: 5, markerWidth: 4.1, markerHeight: 4.1, orient: "auto" });
      el(m, "path", { d: "M0.2,1.3 L10,5 L0.2,8.7 L2.6,5 z", fill: color });
    }
    return `url(#${id})`;
  };
  const outline = (ux, uy, half, shape) => shape === "circle" ? half : half / Math.max(Math.abs(ux), Math.abs(uy));

  function edge(svg, a, b, o = {}) {
    const [x1, y1] = a, [x2, y2] = b, dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L;
    const half = o.half ?? 3, shape = o.shape || "square", gap = o.gap ?? 0.5, bend = o.bend || 0;
    const tip = o.head === false ? 0 : o.headSize ? o.headSize * HEAD_BACK / 10 : 0.35;   // head beyond the end of the line
    const s = outline(ux, uy, o.halfFrom ?? half, o.shapeFrom || shape) + gap;
    const e = outline(ux, uy, o.halfTo ?? half, o.shapeTo || shape) + gap + tip;
    const sx = x1 + ux * s, sy = y1 + uy * s, ex = x2 - ux * e, ey = y2 - uy * e;
    const mx = (sx + ex) / 2 - uy * bend, my = (sy + ey) / 2 + ux * bend;
    const color = o.color || C.count;
    const p = el(svg, "path", { d: `M${sx},${sy} Q${mx},${my} ${ex},${ey}`, fill: "none", stroke: color,
      "stroke-width": o.width ?? 0.45, "stroke-dasharray": o.dash, "stroke-linecap": "butt",
      "marker-end": o.head === false ? null : marker(svg, color, o.headSize) });
    if (o.label !== undefined) {
      const t = o.labelPos ?? 0.5, qx = (1 - t) * (1 - t) * sx + 2 * (1 - t) * t * mx + t * t * ex,
        qy = (1 - t) * (1 - t) * sy + 2 * (1 - t) * t * my + t * t * ey;
      const off = o.labelOffset ?? 1.6, lx = qx - uy * off * Math.sign(bend || 1), ly = qy + ux * off * Math.sign(bend || 1);
      // labelSerif / labelItalic: a number with a sign Bahnschrift lacks (⅓, 1 − λ) or a variable, in Palatino
      const serif = o.labelSerif || o.labelItalic;
      text(svg, lx, ly + 0.8, String(o.label), { size: o.labelSize || 2.5, fill: o.labelColor || color, anchor: "middle",
        weight: serif ? 400 : 600, serif: o.labelSerif, italic: o.labelItalic });
    }
    return p;
  }

  // a node: a flat square (or disc) on a white keyline; ring adds the thin frame of the reference's ringed marks
  function node(svg, x, y, o = {}) {
    const half = o.half ?? 3, fill = o.fill || C.contract, circle = o.shape === "circle";
    const key = o.keyline ?? 0.28, rx = o.rx ?? half * 0.2;
    const box = (h, attrs) => circle ? el(svg, "circle", Object.assign({ cx: x, cy: y, r: h }, attrs))
      : el(svg, "rect", Object.assign({ x: x - h, y: y - h, width: 2 * h, height: 2 * h, rx: Math.max(0, rx + (h - half) * 0.9) }, attrs));
    if (o.ring) box(half + (o.ringGap ?? 0.75), { fill: C.paper, stroke: o.ringColor || fill, "stroke-width": o.ringWidth ?? 0.2, "stroke-linejoin": "round" });
    else if (key) box(half + key, { fill: C.paper });
    box(half, { fill });
    if (o.glyph) {                               // the braces of a contract, drawn (a glyph would be text below 7 pt)
      const u = half / 5;                        // the pictogram's 12 x 12 box, its centre on the node
      el(svg, "path", { transform: `translate(${x - 6 * u} ${y - 6 * u}) scale(${u})`, fill: "none", stroke: "#fff",
        "stroke-width": 0.95, "stroke-linecap": "round", "stroke-linejoin": "round",
        d: "M5.3,3.2 c-0.9,0 -1.2,0.4 -1.2,1.1 v0.8 c0,0.6 -0.3,0.9 -0.9,0.9 c0.6,0 0.9,0.3 0.9,0.9 v0.8 c0,0.7 0.3,1.1 1.2,1.1 M6.7,3.2 c0.9,0 1.2,0.4 1.2,1.1 v0.8 c0,0.6 0.3,0.9 0.9,0.9 c-0.6,0 -0.9,0.3 -0.9,0.9 v0.8 c0,0.7 -0.3,1.1 -1.2,1.1" });
    }
    // the label: a name in bold Bahnschrift, or (labelItalic) a variable in Palatino italic
    if (o.label !== undefined) text(svg, x, y + (o.labelSize || 2.6) * (o.labelItalic ? 0.3 : 0.36), o.label,
      { size: o.labelSize || 2.6, weight: o.labelItalic ? 400 : 700, fill: o.labelColor || "#fff", anchor: "middle", italic: o.labelItalic });
  }
  const contract = (svg, x, y, half = 3, fill = C.contract, glyph = true) => node(svg, x, y, { half, fill, glyph });

  function person(svg, x, y, s = 6, color = C.user) {
    const r = s * 0.2, w = s * 0.36, base = y + s * 0.5;
    el(svg, "path", { d: `M${x - w},${base} a${w},${w * 0.95} 0 0 1 ${2 * w},0 z`, fill: color });
    el(svg, "circle", { cx: x, cy: y - s * 0.22, r: r + s * 0.045, fill: C.paper });
    el(svg, "circle", { cx: x, cy: y - s * 0.22, r, fill: color });
  }

  // Text in Bahnschrift at the width and spacing of style.css (87.5%, 0.05 em); serif or italic gives Palatino.
  // The spacing goes into the style, in user units: CSS would read an em of the page there, not of this text.
  // The spacing also follows the last glyph, and the anchor counts it: a centred text would stand half a spacing
  // left of its point and a right-aligned one a whole spacing. The x of such a text is moved by that much, so
  // that x is the centre, or the right end, of the glyphs.
  function text(svg, x, y, str, o = {}) {
    const serif = o.serif || o.italic, size = o.size || 2.6, plain = serif || o.mono;
    const anchor = o.anchor || "start", sp = plain ? 0 : size * (o.spacing ?? 0.05);
    const t = el(svg, "text", { x: anchor === "middle" ? x + sp / 2 : anchor === "end" ? x + sp : x, y, "font-size": size,
      "font-weight": o.weight || 400, fill: o.fill || C.text,
      "text-anchor": anchor, "font-style": o.italic ? "italic" : null, class: o.mono ? "mono" : serif ? "serif" : "sans",
      "font-family": o.family || (o.mono ? MONO : serif ? SERIF : SANS) }, str);
    if (!plain) t.style.letterSpacing = sp.toFixed(3) + "px";
    return t;
  }

  // Text with marked parts, for a label that holds a variable or an index:
  //   $x$      a variable: Palatino italic            #1 − #   upright Palatino (signs Bahnschrift lacks: − ≤ ≈ ≠ ′ ⅓)
  //   _{obs}   a subscript, 0.8 of the size           _{$q$}   a subscript that is a variable
  //   `code`   monospace
  // The rest is set as Fig.text sets it. opt as Fig.text (size, weight, fill, anchor).
  function rich(svg, x, y, str, o = {}) {
    const size = o.size || 2.5, t = text(svg, x, y, undefined, Object.assign({}, o, { size }));
    const serifSpan = (ts, s, italic, k = 1.06) => { ts.textContent = s; ts.setAttribute("class", "serif"); ts.setAttribute("font-family", SERIF);
      ts.setAttribute("font-size", (size * k).toFixed(3)); if (italic) ts.setAttribute("font-style", "italic"); };
    let shift = 0;
    for (const part of str.split(/(\$[^$]+\$|#[^#]+#|`[^`]+`|_\{[^}]+\})/).filter(Boolean)) {
      const ts = el(t, "tspan", {});
      if (part.startsWith("_{")) {
        const sub = part.slice(2, -1), d = size * 0.22;
        if (sub.startsWith("$")) serifSpan(ts, sub.slice(1, -1), true, 0.84); else { ts.textContent = sub; ts.setAttribute("font-size", (size * 0.8).toFixed(3)); }
        ts.setAttribute("dy", d.toFixed(3)); shift = d; continue;
      }
      if (shift) { ts.setAttribute("dy", (-shift).toFixed(3)); shift = 0; }
      if (part.startsWith("$")) serifSpan(ts, part.slice(1, -1), true);
      else if (part.startsWith("#")) serifSpan(ts, part.slice(1, -1), false);
      else if (part.startsWith("`")) { ts.textContent = part.slice(1, -1); ts.setAttribute("class", "mono"); ts.setAttribute("font-family", MONO); }
      else ts.textContent = part;
    }
    return t;
  }

  // a five-pointed star (a hot contract), centred at (x, y), r = outer radius in mm
  function star(svg, x, y, r = 1.7, color = C.rq3) {
    let d = "";
    for (let k = 0; k < 10; k++) {
      const q = k % 2 ? r * 0.44 : r, a = -Math.PI / 2 + k * Math.PI / 5;
      d += (k ? "L" : "M") + (x + q * Math.cos(a)).toFixed(2) + "," + (y + q * Math.sin(a)).toFixed(2);
    }
    return el(svg, "path", { d: d + "Z", fill: color });
  }

  // An arrow between two parts of a figure, as HTML markup: a thin line with the notched head.
  // len in mm; dir "right" | "left" | "down" | "up"; dash as a stroke-dasharray.
  function arrow(color = C.count, len = 6, dir = "right", dash) {
    const w = 0.42, hl = 1.75, hh = 0.66, m = 1.5;                 // line width, head length and half height, half the box
    // the ink runs from 0.1 to len - 0.1, so that an arrow centred in a gap stands as far from one side as from the other
    const b = len - hl - 0.05;                                      // the back of the head
    const body = `<path d="M0.1,${m} H${(b + 0.45).toFixed(2)}" fill="none" stroke="${color}" stroke-width="${w}"${dash ? ` stroke-dasharray="${dash}"${/^0[ ,]/.test(dash) ? ` stroke-linecap="round"` : ""}` : ""}/>` +
      `<path d="M${b.toFixed(2)},${m - hh} L${(len - 0.1).toFixed(2)},${m} L${b.toFixed(2)},${m + hh} L${(b + 0.42).toFixed(2)},${m} z" fill="${color}"/>`;
    const rot = { right: 0, down: 90, left: 180, up: 270 }[dir] || 0, vert = rot === 90 || rot === 270;
    const W = vert ? 2 * m : len, H = vert ? len : 2 * m;
    const tf = rot === 0 ? "" : rot === 180 ? ` transform="rotate(180 ${len / 2} ${m})"` :
      rot === 90 ? ` transform="translate(${2 * m} 0) rotate(90)"` : ` transform="translate(0 ${len}) rotate(-90)"`;
    return `<svg width="${W}mm" height="${H}mm" viewBox="0 0 ${W} ${H}" style="flex:none;display:block"><g${tf}>${body}</g></svg>`;
  }

  // An open chevron ">" between two cards of a row, as HTML markup: two strokes meeting at a point, for a gap too
  // short for an arrow with a line. h is the height of the ink in mm; the box adds half a stroke on every side, so a
  // chevron centred in a gap stands as far from one card as from the other.
  function chevron(color = C.count, h = 5.6, dir = "right", w = 0.55) {
    const d = h * 0.42, W = d + w, H = h + w, a = w / 2, b = w / 2 + d;
    const [x0, x1] = dir === "left" ? [b, a] : [a, b];
    const path = `M${x0.toFixed(3)},${a.toFixed(3)} L${x1.toFixed(3)},${(a + h / 2).toFixed(3)} L${x0.toFixed(3)},${(a + h).toFixed(3)}`;
    return `<svg width="${W.toFixed(3)}mm" height="${H.toFixed(3)}mm" viewBox="0 0 ${W.toFixed(3)} ${H.toFixed(3)}" style="flex:none;display:block">` +
      `<path d="${path}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  }

  // dotted leader: round dots, as the leader lines of the reference
  const dots = (svg, d, color = C.leader, width = 0.32, pitch = 0.95) =>
    el(svg, "path", { d, fill: "none", stroke: color, "stroke-width": width, "stroke-linecap": "round", "stroke-dasharray": `0 ${pitch}` });

  function graph(svg, spec) {
    const nd = Object.assign({ half: 3, shape: "square", fill: C.contract, labelColor: "#fff", labelSize: 2.6 }, spec.node || {});
    const N = {};
    for (const [id, v] of Object.entries(spec.nodes)) N[id] = Array.isArray(v) ? { x: v[0], y: v[1] } : v;
    for (const [from, to, kind, bend, label] of spec.edges || []) {
      const k = Object.assign({}, (spec.kinds || {})[kind] || {});
      const a = N[from], b = N[to];
      edge(svg, [a.x, a.y], [b.x, b.y], Object.assign(k, { bend, label, half: nd.half, shape: nd.shape,
        halfFrom: a.half ?? nd.half, halfTo: b.half ?? nd.half, shapeFrom: a.shape || nd.shape, shapeTo: b.shape || nd.shape }));
    }
    for (const n of Object.values(N))
      node(svg, n.x, n.y, { half: n.half ?? nd.half, shape: n.shape || nd.shape, fill: n.fill || nd.fill, ring: n.ring ?? nd.ring,
        glyph: n.shape !== "circle" && nd.shape !== "circle" && n.glyph !== false && n.label === undefined,
        label: n.label, labelSize: n.labelSize || nd.labelSize, labelColor: n.labelColor || nd.labelColor });
    return N;
  }

  // linear gradient for an illustration; angle in degrees (0 = left to right, 90 = top to bottom)
  function ramp(svg, id, stops, angle = 60) {
    const a = angle * Math.PI / 180, cx = Math.cos(a) / 2, cy = Math.sin(a) / 2;
    const g = el(defs(svg), "linearGradient", { id, x1: 0.5 - cx, y1: 0.5 - cy, x2: 0.5 + cx, y2: 0.5 + cy });
    for (const [offset, color] of stops) el(g, "stop", { offset, "stop-color": color });
    return `url(#${id})`;
  }

  // pictograms on a 12 x 12 box: c is the colour of the drawing, k the colour of what is cut out of it
  const ICONS = {
    bars: c => `<rect x="1.2" y="6.6" width="2.4" height="4.4" fill="${c}"/><rect x="4.8" y="3.8" width="2.4" height="7.2" fill="${c}"/><rect x="8.4" y="1" width="2.4" height="10" fill="${c}"/>`,
    search: c => `<circle cx="5" cy="5" r="3.3" fill="none" stroke="${c}" stroke-width="1.25"/><path d="M7.5,7.5 L10.8,10.8" stroke="${c}" stroke-width="1.6" stroke-linecap="round"/>`,
    calendar: c => `<rect x="1.2" y="2.2" width="9.6" height="8.6" rx="0.8" fill="none" stroke="${c}" stroke-width="1.1"/><path d="M1.2,4.9 H10.8" stroke="${c}" stroke-width="1.1"/><path d="M3.7,0.9 V3 M8.3,0.9 V3" stroke="${c}" stroke-width="1.1" stroke-linecap="round"/><rect x="6.5" y="6.5" width="2.5" height="2.5" fill="${c}"/>`,
    scale: c => `<path d="M6,1 V10.4 M3.2,10.7 H8.8" stroke="${c}" stroke-width="1.1" stroke-linecap="round"/><path d="M1.6,3 H10.4" stroke="${c}" stroke-width="1.1" stroke-linecap="round"/><path d="M1.6,3 L0.4,6.2 H2.8 Z M10.4,3 L9.2,6.2 H11.6 Z" fill="${c}"/>`,
    person: c => `<circle cx="6" cy="3.4" r="2.3" fill="${c}"/><path d="M1.8,11.2a4.2,4 0 0 1 8.4,0z" fill="${c}"/>`,
    people: (c, k = "#fff") => `<circle cx="2.9" cy="4.2" r="1.6" fill="${c}"/><path d="M0.2,10.2a2.7,2.6 0 0 1 5.4,0z" fill="${c}"/><circle cx="9.1" cy="4.2" r="1.6" fill="${c}"/><path d="M6.4,10.2a2.7,2.6 0 0 1 5.4,0z" fill="${c}"/><circle cx="6" cy="3.3" r="2.5" fill="${k}"/><path d="M2.2,11.2a3.8,3.6 0 0 1 7.6,0z" fill="${k}"/><circle cx="6" cy="3.3" r="1.95" fill="${c}"/><path d="M2.8,10.8a3.2,3 0 0 1 6.4,0z" fill="${c}"/>`,
    contract: (c, k = "#fff") => `<rect x="1" y="1" width="10" height="10" rx="1.3" fill="${c}"/><path d="M5.3,3.2 c-0.9,0 -1.2,0.4 -1.2,1.1 v0.8 c0,0.6 -0.3,0.9 -0.9,0.9 c0.6,0 0.9,0.3 0.9,0.9 v0.8 c0,0.7 0.3,1.1 1.2,1.1 M6.7,3.2 c0.9,0 1.2,0.4 1.2,1.1 v0.8 c0,0.6 0.3,0.9 0.9,0.9 c-0.6,0 -0.9,0.3 -0.9,0.9 v0.8 c0,0.7 -0.3,1.1 -1.2,1.1" fill="none" stroke="${k}" stroke-width="0.95" stroke-linecap="round" stroke-linejoin="round"/>`,
    coin: c => `<circle cx="6" cy="6" r="4.8" fill="none" stroke="${c}" stroke-width="1.2"/><path d="M6,3.2 V8.8 M4.4,4.6 H7.1 a1.1,1.1 0 0 1 0,2.2 H4.9 a1.1,1.1 0 0 0 0,2.2 H7.6" stroke="${c}" stroke-width="0.9" fill="none"/>`,
    key: c => `<circle cx="4" cy="6" r="2.6" fill="none" stroke="${c}" stroke-width="1.2"/><path d="M6.6,6 H11 M9.4,6 V8 M10.9,6 V7.6" stroke="${c}" stroke-width="1.2" stroke-linecap="round"/>`,
    web: c => `<circle cx="6" cy="6" r="4.8" fill="none" stroke="${c}" stroke-width="1"/><ellipse cx="6" cy="6" rx="2" ry="4.8" fill="none" stroke="${c}" stroke-width="0.9"/><path d="M1.2,6 H10.8 M2,3.5 H10 M2,8.5 H10" stroke="${c}" stroke-width="0.8"/>`,
    doc: c => `<path d="M2.6,1 H7.4 L9.8,3.4 V11 H2.6 Z" fill="none" stroke="${c}" stroke-width="1.1" stroke-linejoin="round"/><path d="M4.3,5.6 H8.1 M4.3,7.4 H8.1 M4.3,9.2 H6.8" stroke="${c}" stroke-width="0.9" stroke-linecap="round"/>`,
    database: c => `<ellipse cx="6" cy="2.7" rx="4.3" ry="1.7" fill="none" stroke="${c}" stroke-width="1.05"/><path d="M1.7,2.7 V9.3 a4.3,1.7 0 0 0 8.6,0 V2.7 M1.7,6 a4.3,1.7 0 0 0 8.6,0" fill="none" stroke="${c}" stroke-width="1.05"/>`,
    gear: c => `<circle cx="6" cy="6" r="2" fill="none" stroke="${c}" stroke-width="1.1"/><path d="M6,0.8 V2.6 M6,9.4 V11.2 M0.8,6 H2.6 M9.4,6 H11.2 M2.3,2.3 L3.6,3.6 M8.4,8.4 L9.7,9.7 M2.3,9.7 L3.6,8.4 M8.4,3.6 L9.7,2.3" stroke="${c}" stroke-width="1.3" stroke-linecap="round"/>`,
    check: (c, k = "#fff") => `<circle cx="6" cy="6" r="5.2" fill="${c}"/><path d="M3.4,6.2 L5.3,8 L8.7,4.2" stroke="${k}" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`,
    cross: (c, k = "#fff") => `<circle cx="6" cy="6" r="5.2" fill="${c}"/><path d="M4,4 L8,8 M8,4 L4,8" stroke="${k}" stroke-width="1.3" stroke-linecap="round"/>`,
    half: c => `<circle cx="6" cy="6" r="5.2" fill="none" stroke="${c}" stroke-width="1.1"/><path d="M6,0.8 A5.2,5.2 0 0 1 6,11.2 Z" fill="${c}"/>`,
    clock: c => `<circle cx="6" cy="6" r="4.8" fill="none" stroke="${c}" stroke-width="1.1"/><path d="M6,3 V6.2 L8.2,7.6" stroke="${c}" stroke-width="1.1" fill="none" stroke-linecap="round"/>`,
    crawl: c => `<circle cx="2.2" cy="6" r="1.5" fill="${c}"/><circle cx="6.2" cy="2.6" r="1.3" fill="${c}"/><circle cx="6.2" cy="9.4" r="1.3" fill="${c}"/><circle cx="10" cy="6" r="1.1" fill="${c}"/><path d="M3.4,5.2 L5.2,3.4 M3.4,6.8 L5.2,8.6 M7.3,3.3 L9.1,5.2" stroke="${c}" stroke-width="0.8"/>`,
    lock: c => `<rect x="2.2" y="5.2" width="7.6" height="5.8" rx="0.9" fill="${c}"/><path d="M3.8,5.2 V3.8 a2.2,2.2 0 0 1 4.4,0 V5.2" fill="none" stroke="${c}" stroke-width="1.1"/>`,
  };
  const icon = (name, color = C.text, size = 4.4) =>
    `<svg width="${size}mm" height="${size}mm" viewBox="0 0 12 12" style="flex:none">${ICONS[name](color, "#fff")}</svg>`;
  // the medal of the reference: a solid disc, the pictogram in white, one thin ring around it (16 x 16 box)
  const medalMarkup = (name, color) =>
    `<circle cx="8" cy="8" r="7.55" fill="none" stroke="${color}" stroke-width="0.5"/><circle cx="8" cy="8" r="6.35" fill="${color}"/>` +
    `<g transform="translate(3.74 3.74) scale(0.71)">${ICONS[name]("#fff", color)}</g>`;
  const medal = (name, color = C.count, size = 5.4) =>
    `<svg width="${size}mm" height="${size}mm" viewBox="0 0 16 16" style="flex:none">${medalMarkup(name, color)}</svg>`;
  function medalAt(svg, name, color, x, y, size = 5.4) {
    const g = el(svg, "svg", { x: x - size / 2, y: y - size / 2, width: size, height: size, viewBox: "0 0 16 16" });
    g.innerHTML = medalMarkup(name, color);
    return g;
  }

  window.Fig = { C, el, defs, marker, edge, graph, node, contract, person, text, rich, star, arrow, chevron, dots, ramp, icon, medal, medalAt, ICONS, SANS, SERIF, MONO };
  // Fill every <span data-icon="name" data-color="rq1" data-size="4.4"></span> with its icon,
  // every <span data-medal="name" data-color="rq1" data-size="5.4"></span> with its medal
  // and every <span data-arrow="right" data-color="count" data-len="6"></span> with an arrow between two parts
  // (data-color: a name of Fig.C, or a colour).
  // The class of the span passes to the drawing, so that the figure's CSS can place it.
  document.addEventListener("DOMContentLoaded", () => {
    const swap = (s, markup) => {
      const box = document.createElement("div");
      box.innerHTML = markup;
      const svg = box.firstElementChild;
      if (s.className) svg.setAttribute("class", s.className);
      s.replaceWith(svg);
    };
    for (const s of document.querySelectorAll("[data-icon]"))
      swap(s, icon(s.dataset.icon, colour(s.dataset.color, C.text), parseFloat(s.dataset.size || "4.4")));
    for (const s of document.querySelectorAll("[data-medal]"))
      swap(s, medal(s.dataset.medal, colour(s.dataset.color, C.count), parseFloat(s.dataset.size || "5.4")));
    for (const s of document.querySelectorAll("[data-arrow]"))
      swap(s, arrow(colour(s.dataset.color, C.count), parseFloat(s.dataset.len || "6"), s.dataset.arrow || "right", s.dataset.dash));
    for (const s of document.querySelectorAll("[data-chevron]"))
      swap(s, chevron(colour(s.dataset.color, C.count), parseFloat(s.dataset.h || "5.6"), s.dataset.chevron || "right"));
    // The pitch of the lines, in whole pixels. Chrome prints every baseline on a whole pixel, so lines 11.6 px apart
    // come out 11, 12 and 12 px apart. The line height of every element is rounded to the pixel here, unless its
    // figure gives it in whole px already (or as 0, for a sign set into a line of another face).
    {
      const todo = [];
      for (const e of document.querySelectorAll(".fig, .fig *")) {
        if (e.closest("svg")) continue;
        const lh = parseFloat(getComputedStyle(e).lineHeight);        // NaN for "normal"
        if (lh && Math.abs(lh - Math.round(lh)) > 0.01) todo.push([e, Math.round(lh)]);
      }
      for (const [e, px] of todo) e.style.lineHeight = px + "px";
    }
    // The title of a heading and the note after it (.sub) stand on one baseline: both go into one span, which the
    // heading then centres beside its disc. (As two flex items each was centred by itself, and the smaller note
    // stood higher than the title.)
    for (const sub of document.querySelectorAll(".h > .sub")) {
      const h = sub.parentNode, w = document.createElement("span");
      const mark = n => n.nodeType === 1 && n.matches("svg, .badge");
      const run = [...h.childNodes].filter(n => !mark(n));
      h.insertBefore(w, run[0]);
      for (const n of run) w.appendChild(n);
    }
    // The numbered disc of a heading, <span class="badge">1</span>, becomes one drawing: the disc, its ring and its
    // number share a centre. (As CSS boxes the disc and the ring were each set on whole pixels when the page was
    // printed, and the disc stood 0.13 mm off the centre of its ring.) The drawing keeps the box of the span, 4.3 mm,
    // and its class and style, so the margins and the colour (--c) of a figure still apply; the ring lies outside it.
    for (const s of document.querySelectorAll("span.badge")) {
      const svg = document.createElementNS(NS, "svg"), R = 2.15;
      svg.setAttribute("class", s.className);
      if (s.getAttribute("style")) svg.setAttribute("style", s.getAttribute("style"));
      svg.setAttribute("viewBox", `0 0 ${2 * R} ${2 * R}`);
      svg.setAttribute("width", `${2 * R}mm`); svg.setAttribute("height", `${2 * R}mm`);
      el(svg, "circle", { cx: R, cy: R, r: R + 0.52, fill: "none", "stroke-width": 0.22 }).style.stroke = "var(--c)";
      el(svg, "circle", { cx: R, cy: R, r: R }).style.fill = "var(--c)";
      text(svg, R, R + 2.61 * 0.356, s.textContent.trim(), { size: 2.61, weight: 700, fill: "#fff", anchor: "middle", spacing: 0 });
      s.replaceWith(svg);
    }
  });
})();
