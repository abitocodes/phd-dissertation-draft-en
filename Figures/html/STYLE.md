# The look of the diagrams

The rules by which the diagrams of the thesis are drawn: the colours, the type, the marks and shapes, and how each kind of figure is built. The look follows a reference the author supplied; a trial of three figures came first, and on 2026-11-22 the author chose the palette of the reference for all 21 diagrams. On 2026-11-23 the author asked for the frames of the cards back, for cards of one width and one height, and for marks that sit exactly where they belong: the sections "Parts, cards and boxes" and "Exact in print" hold what followed from that.

The look lives in two files, `style.css` (colours, type, headings, tags, plates) and `fig.js` (the drawing helpers). A figure links both and names every colour by its token.

## The reference

Two JPEG boards on the Six Dynasties of Jinling (four infographic sheets and one long sheet). They carry no licence and no credit line. Their metadata, written by Adobe Illustrator in 2022, calls the document a graduation design, so they are someone else's work: they were looked at for style only. Nothing here is copied, cropped or traced from them, and every shape was drawn anew in HTML, CSS and SVG. Motifs that belong to the subject of the boards (lotus rosettes, fretwork corners, the Buddhist figures) were left out; only the graphic language was taken.

What the boards do:

- **Two colours and grey.** Ultramarine and sand gold on a pale grey board, with mid greys for rules and text; black only in the titles. Colour lies in flat masses, and where a blue and a gold shape overlap the mix is a lilac.
- **Two typefaces.** Titles in Palatino, regular weight, over a thick grey rule. Everything else in a DIN: bold for names, regular for text, set narrow and with open spacing. Section headings are bold DIN after a solid disc.
- **Circles.** Discs, concentric rings and arcs carry most marks: a pictogram is white on a solid disc inside a ring.
- **Flat bands and tags.** Quantities run as broad bands; a label of weight is a solid rectangle with white bold text; periods are thick bars with the name beneath.
- **Thin leaders.** Notes hang on thin dotted or dashed lines that end in a dot.
- **Air.** Few boxes: text stands on the board, and the board is two-thirds empty.

## The rules

What a caption says about a figure stays true: dashed stays dashed, hatched stays hatched, filled stays filled, an arrow stays an arrow, and a colour a caption names keeps its hue. The one word that changes is "orange", which is now gold.

### Colour

One colour per meaning; the hues are those of the reference where the meaning allows it. The two layers of the thesis take the two colours of the reference.

| Meaning | Token | Colour | Grey | Before | Grey |
|---|---|---|---|---|---|
| Allowance, thin line | `--allow` | `#B98A24` | 0.55 | `#D97706` | 0.53 |
| Allowance, band of 0.8 mm or more | `--allow-band` | `#CFA448` | 0.65 | | |
| Transfer | `--transfer` | `#2340C8` | 0.28 | `#2563EB` | 0.38 |
| C-PR, RQ4–5 | `--coupled`, `--rq45` | `#6A2C91` | 0.29 | `#7C3AED` | 0.38 |
| Contract | `--contract` | `#2A7A72` | 0.38 | `#0F766E` | 0.34 |
| User account (dashed) | `--user` | `#8A8A8A` | 0.54 | `#7A8594` | 0.52 |
| Neutral step, raw count | `--count` | `#5A5A5A` | 0.35 | `#475569` | 0.33 |
| RQ1; the web | `--rq1`, `--web` | `#2C8FB3` | 0.46 | `#0891B2` | 0.42 |
| RQ2 | `--rq2` | `#2F7D45` | 0.37 | `#059669` | 0.40 |
| RQ3; labels; a hot contract | `--rq3` | `#C23B5E` | 0.41 | `#DB2777` | 0.40 |

(Grey: the level a greyscale print gives, 0 black to 1 white.)

- Each meaning has four tones in `style.css`: the mark (lines, tags, discs), `-ink` (small text on paper), `-fill` (broad surfaces) and `-bg` (pale surface). `fig.js` reads them from the stylesheet (`Fig.C.allow`, `Fig.C.allowInk`), so a colour is named in one place. A figure writes a colour as a token (`var(--allow)`, `Fig.C.allow`), never as a number; white is the one exception.
- Gold is the one hue with two marks. The gold of the reference is too light for a thin line, so a line under 0.8 mm takes the darker `--allow` and a band takes `--allow-band`.
- In greyscale an allowance (0.55 to 0.65) and a transfer (0.28) differ by lightness, which they did not before (0.53 and 0.38). Where two meanings are equally dark (transfer and C-PR; contract, RQ2 and RQ3) they are told apart by a second cue: dashes, shape, position or the label. A figure that draws C-PR edges beside transfer edges must give one of them a dash.
- The blend from blue to gold, the signature of the reference's pictures, is kept for the one thing that joins both layers, C-PR. Any other picture is shaded inside the tone of its own meaning.
- Surfaces are neutral: white, or the one pale grey `--plate`. Colour is carried by marks (bars, tags, discs, lines), not by tinted boxes. The exceptions are a layer drawn as a surface (the two planes of the contract graph), a score's tag (`.chip`), a verdict (`.pill`) and a bar of a period or an amount.
- Colours a figure had of its own:

| In the figure before | Now |
|---|---|
| slate and navy (`#334155`, `#475569`, `#1E3A5F`): a neutral step, a chapter, a badge | `--count`, or `--ink` for the darkest |
| the web (`#0E7490`) | `--web`, `--web-ink` for its text |
| dark orange (`#B45309`, `#7C3F00`): text about allowances, the token contract | `--allow-ink` |
| dark blue (`#1D4ED8`, `#1E3A8A`) | `--transfer-ink` |
| green of the discovery-order test (`#059669`, `#065F46`) | `--rq2` |
| pink of labels and of hot contracts (`#DB2777`, `#9D174D`) | `--rq3` |
| families of methods: web, restarts and trust (green), multilayer (purple), ledger (blue) | `--web`, `--good`, `--coupled`, `--transfer` |
| good, bad, mixed, tied | `--good`, `--bad`, `--mixed`, `--count` |
| grey of what is not yet seen or not read | `--user` (dashed outline) or `--plate-2` (fill) |
| grey of a dotted leader | `--leader` |

### Type

- Headings: Palatino Linotype, regular, 10.4 pt, near black, over a grey rule (`.h`; 0.45 mm in the stylesheet, 0.26 mm in print: see "Exact in print"); 9 pt in a narrow column or inside a drawing (`.h.s`); 8 pt where the longest heading of a row of cards would not fit otherwise, and then for every card of that row. A numbered heading has its number in a ringed disc (`.badge`, which `fig.js` draws as one SVG); an unnumbered one inside a drawing follows a solid dot; a heading with a pictogram follows its medal. A note after the title (`.sub`) stands on the title's baseline.
- All other text: Bahnschrift, the DIN that Windows carries, at its semi-condensed width with 0.045 em of spacing (measured against the reference: see the note in `style.css`). Names and titles bold in near black, text regular in `--muted`, group labels in spaced capitals (`.grp`, 0.1 em: at 0.12 em a PDF reader splits a word).
- Nothing under 7 pt on the page: 7.1 pt in CSS and 2.5 mm in a drawing, because a crop a little wider than 165 mm is scaled down. A subscript is 0.8 of its line, so at least 5.6 pt.
- Formulas and variables: Palatino, variables in its italic (`.m` with `<i>`, `i.v`, `Fig.rich`). Bahnschrift has no italic and lacks `‑ − ′ ⅓ → ≈ ≠ ≤ ⌈ ⌉ ★ √`; Palatino has all of these but `→ ⌈ ⌉ ★`. So a sign goes into Palatino (`.m`, `.pr`, `#…#` in `Fig.rich`), the two ceiling brackets come from Cambria Math (named last in the Palatino stack), and an arrow between two words and a star are drawn (`Fig.arrow`, `Fig.star`). A term such as C-PR is written with a plain hyphen inside `.nb`.
- Code: an identifier of the chain (`approve`, `Approval`, `eth_getCode`, `emit`, `LOG`, the crawl modes `out` and `both`) is set in Consolas (`.mono`, `mono: true`, or `` `code` `` in `Fig.rich`) at the size of its line.
- Numbers: lining and tabular, in Bahnschrift.

### Marks

- Edge of a small graph: 0.42 to 0.6 mm, with the slim notched head of `Fig.marker`. Edge of a graph whose nodes are 6 mm or more: a band of about 1 mm with a head of fixed size (`Fig.edge` with `width: 1.05` and `headSize: 3.1`).
- An allowance edge is solid gold, a transfer edge blue. Where the two stand in one drawing and the caption calls the transfer edge dashed, it is a thin dashed line (`1.2 0.75`) beside the gold band.
- Dashed (`1.1 0.8`): user accounts, teleportation, and what is not yet seen. Dotted with round dots (`Fig.dots`, or `stroke-linecap: round` with a dash of `0 1.1`): a leader, the same thing shown twice, or an arrow the caption calls dotted.
- Connector between boxes and arrow between parts: 0.42 mm in `--count`, a dot 1.2 mm across where a connector branches or joins.
- Nothing thinner than 0.15 mm, and nothing thinner than 0.2 mm that carries meaning.

### Shapes

- Contract: a flat square with a small radius on a white keyline (`Fig.node`, `Fig.contract`). In a worked example whose nodes carry a name the node also has a thin frame (`ring: true`) and its name in white: a letter of the text in bold Bahnschrift, a variable in Palatino italic (`labelItalic: true`). The one node that differs takes a frame of its own colour (`ringColor`).
- Score or term: a flat tag with a 0.5 mm radius (`.chip`). The method of the thesis is the solid one.
- Solid label: a research question, a claim, a window, a family (`.tag`), white bold text on the colour.
- Evaluation or step: a neutral surface behind a solid bar of its colour on the left (`.card`, `.rowp`; the `box` of `pipeline-architecture.html`). The bar is 4 px (1.06 mm) where it is a CSS border, which is what a border of 1.3 mm came to in print (a border width is rounded down to the pixel), and 1.3 mm where it is drawn in SVG.
- Pictogram: white on a solid disc of the meaning's colour inside one thin ring (`Fig.medal`, `Fig.medalAt`, `data-medal`), 4.3 to 5.4 mm. The open form (white disc, pictogram in the colour) marks what is not there or not tested.
- Bar of a value: flat, square ends.

### Pictures

The author asked for the way the reference draws its figures (the seated Buddha, the horses, the vase) to be analysed, for use where a diagram needs a picture. `illustration-sampler.html` shows the result on the thesis's own objects.

How the reference draws a figure:

1. **One silhouette.** The figure is a single flat shape with no outline. There is no black anywhere and no drawn shadow.
2. **A blend, not shading.** The silhouette is filled with a soft blend between the two colours of the board, ultramarine through a lilac to sand gold, running across the whole figure in one direction. Form comes from the change of hue, not from light and dark.
3. **A white keyline.** A thin white contour runs around the silhouette and parts it from whatever lies behind (the blue wall, another figure, a gold band).
4. **White lines for all detail.** Features, folds, fingers and manes are thin white lines of one weight, in places doubled. Pattern is white too: stippling for the hair, sprigs on a cup.
5. **A halo of rings.** The main figure sits before a broad ring blended from gold to grey, with a thin white ring and a blue ring inside it.
6. **A flat ground.** Architecture behind the figures is flat blue and gold blocks ruled with white lines.

Simpler objects on the boards are drawn in two further ways: flat shapes of blue, gold and dark grey that overlap with transparency (the instrument), and the medal (a white pictogram on a blue disc inside a gold ring).

The rules for the thesis:

- A picture is a silhouette with a linear blend inside the tone of its meaning (dark to light), a white keyline of 0.3 to 0.4 mm, and its detail in white lines of one weight, at least 0.2 mm. No outline in a dark colour.
- Size decides the form. From about 10 mm: blend, keyline and four or five white lines. At 8 mm: the two or three lines that name the object. At 5 mm and below: the medal.
- A halo (a ring around a picture) marks at most one thing in a figure.
- Not taken over: the brush texture and soft edges, the stippling, the figurative drawing itself. They are raster effects or hand drawing, they would not stay vector, and at the sizes of a thesis figure they would not print.

## Patterns for the kinds of figure

### Size on the page

- Every chapter includes a figure with `width=\textwidth`, so it prints 165 mm wide whatever the width of its PDF, and its height and its text scale with it.
- A figure is no taller on the page than the one it replaces: a taller figure can move a page break.
- All strokes of a drawing have round joins (`style.css`). The crop widens the box of a mitred stroke by about 1 mm a side, which made a PDF wider than its drawing and the figure smaller on the page.

### Parts, cards and boxes

- Where a figure sets like parts side by side (the chapters of the thesis, the steps of a flow, the three parts of an explanation), each part is a card: a hairline frame around its heading and its content (`<div class="part panel">`). A first version stood such parts on the page without a frame; the author asked for the frames back.
- The cards of one figure have one width and one height. Their grid gives the columns and the gaps in whole pixels (see "Exact in print") and stretches its row. A card that holds plainly less than its neighbours may keep a narrower width (the three parts of `defi-risk`), and a card over the whole width (Chapter 1 of `thesis-roadmap`) is a banner, not one of the row.
- Inside the cards of a row like things stand on one line: the headings, the drawings, the first line of a list (`web-to-ledger` lets its cards share the rows of the grid, `grid-template-rows:subgrid`). What ends a card stands at its foot (`margin-top:auto`), and a card with less in it spreads its groups over its height rather than leave a hole at the bottom.
- Between two cards that lead on, a short arrow in `--count` stands in the middle of the gap (`data-arrow`), at the height of the numbered discs or of the middle of the drawings.
- A part that is not one of a row of like parts stays a column under its heading (`.part` with `.h`): the two unequal parts of a worked example (`depth-one`), the columns of `conceptual-model`.
- The pale plate (`.panel.soft`) holds what the figure sets apart: a result, a formula, the contract graph as a thing, the closing statement of a figure (then behind a solid bar, with its medal). Where a boundary matters, as that of the contract graph, the plate also has a thin solid line, so that nothing depends on the tint.
- A hairline box (`.panel`) is also one of a list of like things: a method, a risk layer, a counterpart. Boxes of one list have one width where their text allows it, or stand on one grid of equal columns, a box one or two columns wide.
- The dashed frame (`.panel.users`) is for user accounts and for what leaves the graph, and for nothing else.
- A row of a table of rows is the plate behind a solid bar of its colour (`.rowp`); a head row is spaced capitals. A row for what is not tested is drawn open: white inside a hairline, an open bar, an open medal.
- No tinted box, no rounded corner above 0.6 mm, no gradient, no drop shadow (the hairline frame is drawn with `box-shadow` without blur: see "Exact in print").

### Exact in print

Chrome prints the page and PyMuPDF crops it, and both round in ways that show at the size of a thesis figure.

- **Whole pixels.** Chrome sets the edges of every CSS box on whole CSS pixels (1 px = 0.2646 mm). A column of 51.7 mm comes out 195 or 196 px wide according to where it stands. The width of a border is rounded down to the pixel: anything under 0.53 mm prints 1 px (0.26 mm), so the hairlines, the dashed frame and the rule under a heading are all 0.26 mm on paper, and a bar of 1.3 mm is 4 px (1.06 mm). Boxes that must be equal side by side get their widths and the gaps between them in whole px (`grid-template-columns:repeat(3, 200px); column-gap:12px`), and the figure is then as wide as their sum (`.fig { width:624px }`, 165.1 mm). Boxes one above the other at one left edge print equal anyway.
- **One edge for a rule, a text and a drawing.** A box is rounded to the pixel, the origin of an SVG too, and text is not; from a fractional start each goes its own way, and the rule under a heading, the list and the drawing of one card begin up to a pixel apart. So the padding of a card is whole px (`.part.panel`: 6 px, 8 px), a drawing that fills a card is as wide as the inside of the card in px (`width:182px`, its `viewBox` that width in mm, 1 px = 0.264583 mm), and the figure stands 23 px from the corner of the page. An arrow between two cards is a whole number of px long (`data-len="2.117"` is 8 px), so that it stands in the middle of its gap.
- **Baselines.** The baseline of a line is printed on a whole pixel too, rounded by itself. A tag with paddings in mm and a line height given as a number came out 13 or 14 px high, with its text 9 or 10 px below its top, according to where it stood; two chips side by side held their names 0.26 mm apart in height. So every length inside a small box with a line of text is a whole number of px (`.tag` 15 px, `.chip` 20 px, `.pill` 14 px, the tags of a list, the lettered discs: the recipes are in `style.css`), and the text then lies the same distance below the top of each. For Bahnschrift at 7.1 to 7.9 pt the baseline lies floor((line-height − 10) / 2) + 8 px below the top of its line.
- **The pitch of lines.** For the same reason lines 11.6 px apart print 11, 12 and 12 px apart. `fig.js` rounds the line height of every element to the pixel when the page loads; a figure that needs a certain pitch gives it in px.
- **One drawing for marks that share a centre.** A disc in a ring or a square in a frame made of two CSS boxes prints up to 0.13 mm off its centre, each box being rounded by itself. Such a pair is drawn in one SVG, where nothing is rounded: the numbered disc of a heading (`fig.js`), the medals, the nodes.
- **Frames as shadows.** Chrome prints a CSS border with rounded corners as a stroked path, and the crop takes a stroked path with corners to be about 1 mm wider on every side than it is. A frame at the edge of a figure then makes the PDF wider than the figure, and the figure smaller on the page. So a hairline frame is `box-shadow:inset 0 0 0 0.25mm` with no border (`.panel`): a shadow without blur prints as a filled shape of exactly its size. A dashed frame stays a border (the crop takes it 0.29 mm wider), and so may a square-cornered one (taken at its size).
- **Text is measured wide.** The crop takes a line of text about 0.3 mm wider on its left than its glyphs. A name that starts at the left edge of a figure is set 0.5 mm in.
- **Centred text.** The spacing of the DIN follows the last glyph too, and SVG counts it when it centres or right-aligns a text. `Fig.text` moves such a text by half the spacing, or the whole of it, so that its glyphs are centred on, or end at, the point given.
- `check_layout.py` reads all of this from the page and from the PDF: text or a drawing that runs past the padding of its box, a heading wider than its line, boxes side by side that are alike but not whole pixels, a card whose inside does not start on a whole pixel, small boxes of one kind that hold their text at different heights, a disc off the centre of its ring, a crop wider than the figure.

### Calendars and periods

- Months: their letters in `--muted`, 2.5 mm; years bold in `--ink`; month lines 0.2 mm in `--plate-2`; the axis 0.3 mm in `--rule`.
- A period is a flat bar with square ends, its name inside: a score window of the contract graph in `--contract-fill` with `--contract-ink` text; a label window in the tint of `--rq3` inside a 0.3 mm line of `--rq3`.
- Where both layers matter the score window is two bands without text, `--allow-band` over `--transfer`.
- A bar that names a record kind and carries text: Approval in `--allow-fill` with `--allow-ink` text, Transfer solid `--transfer` with white text (the two `-fill` tints are nearly the same grey, so the transfer bar is the solid one), neither layer in `--count-bg` inside a 0.25 mm line of `--count`.
- A freeze is a dashed line in `--ink`, 0.4 mm, dashes `0.9 0.6`, with its name in bold at its foot.
- A hatched bar (held out of the scores) is white with thin diagonal lines of its colour and a line around it; its name stands on a white box as high as the inside of the bar. The lines are drawn and clipped (`hatch()` in `data-overview.html`): an SVG pattern prints as an image.

### Bars of an amount

Flat, square ends. Where the amount has a maximum (a share, a count of a total) the bar stands on a track of `--count-bg`; where it has none (a balance, an allowance) there is no track. The part that counts is solid in the mark of its meaning; a part that is shown but does not count is the `-bg` tint inside a 0.25 mm line of the mark.

### Small graphs

- States of a crawl: read or visited is solid; the frontier is white with a 0.45 mm line of the colour; not yet seen is white with a dashed line of `--user`; the one chosen next has a frame in `--coupled`.
- A page of the web is a white upright rectangle with a line of `--web` and three hairlines; the page many link to is larger and tinted. A contract is a square, so the two crawls differ by shape.
- A user account is `Fig.person` in `--user`.
- A hot contract is a star in `--rq3` (`Fig.star`); a seed carries a small flag in `--rq2`.
- A schematic curve: axes 0.3 mm in `--count`, the curve of interest 0.6 mm in its colour, the ideal order in round dots of `--ink`, the random order dashed in `--user`, every label clear of every line.
- Two edges do not share a point of a node's side: one of them meets the node a little off its centre.

### Lanes of a sequence

A lane head is a solid flat rectangle with its name in white bold and a second line in white; a lifeline is a hairline in `--hair`. A message is an arrow in the colour of what it does, with a dot on the sender's lifeline where it starts, its call above it in Consolas in the `-ink` of that colour, its note below in `--muted`.

## What does not carry over to a printed thesis

| In the reference | Why not | Instead |
|---|---|---|
| The pale grey board under everything | On a white page it is a grey slab; a 5% tint prints unevenly and can drop out in a copy; and a board inside the 165 mm would shrink the drawing, taking 7 pt text below 7 pt | White ground. The grey is used for the parts of a figure only, and nothing depends on it: bars, borders and headings still mark every part if the tint is lost. |
| Sand gold for thin lines and for text | Too light on white (grey 0.74): it fades in print | A darker gold for lines and a dark bronze for text; the gold of the reference only in bands and surfaces |
| Pure RGB blue `#0A00FF` | Outside what a printer reaches; it turns violet, towards the colour of C-PR | Ultramarine `#2340C8`, a little towards cyan |
| Two hues for everything | The thesis has ten meanings to tell apart | Four companion hues of the same muted family (verdigris, violet, a cyan, a green, a rose), the four research questions darkening in order |
| Blue headings after a blue disc | Blue means transfer here | Headings in Palatino, near black; the disc carries the number or the pictogram, or stays neutral |
| Text of 4 to 6 pt, hairlines, dotted lines of 0.1 mm | Below what prints at thesis size | 7 pt floor; lines from 0.2 mm |
| Translucent overlaps | The mixed colour would be a colour without a meaning; transparency is also the least reliable part of a PDF in print | Flat fills; the one overlap (C-PR in the sampler) is drawn as a shape of its own |
| Bands whose width is a quantity | The arrows of these figures are relations, not quantities | Bands of one width, only where the nodes are large |
| DIN | A commercial family, not on this machine | Bahnschrift; see below |

## Fonts, as they are in the PDF

- Palatino Linotype, Bahnschrift, Consolas and Cambria Math come with Windows and all allow embedding (the same permission as Segoe UI, which the figures embedded before). If the author licenses a DIN (FF DIN, DIN Pro), name it first in `--sans` and remove `font-stretch` and `letter-spacing` from `body`.
- Chrome embeds Bahnschrift, a variable font, as a Type 3 font: outlines, with the text kept as text (the content check reads the same words from the new PDFs as from the old ones). The other faces are embedded as ordinary subsets.
- A PDF holds Bahnschrift (Type 3), Palatino, Consolas where there is code and Cambria Math for `⌈ ⌉`. Any other face is a fallback for a glyph that a face lacks.
- Another machine without these fonts substitutes the next one in the list; render on Windows.
- The thesis is set in Times New Roman, so a Palatino heading inside a figure is a second serif on the page.
- The Korean edition (`overleaf-github-ko`) keeps these faces for Latin letters, digits, formulas and code. Hangul comes from Noto Sans KR where the text is Bahnschrift and from Noto Serif KR where it is Palatino, both installed as variable fonts (`NotoSansKR-VF.ttf`, `NotoSerifKR-VF.ttf`, SIL Open Font License), so a weight is always given: 400, or 700 where the text is bold. Hangul gets no added letter spacing (it is not condensed), and Korean lines break between words (`word-break: keep-all`). Chrome embeds the two as Type 3 fonts under the name of their default instance (`NotoSansKR-Thin`, `NotoSerifKR-ExtraLight`) whatever weight it drew; the outlines are those of the weight drawn.

## Drawing or changing a figure

1. Link `style.css` and `fig.js`. Open the file with a comment that says in words what the figure shows and, in a last paragraph, how it is drawn.
2. Build it from the patterns above; take a finished figure of the same kind as the model (columns: `conceptual-model`; boxes and connectors: `pipeline-architecture`; a worked example: `random-surfer`, `cpr-schematic`; a calendar: `study-timeline`; rows: `practical-uses`; parts and arrows: `accounts-logs`; a crawl: `crawl-ordering`).
3. Render it and read the check that the renderer prints: its height on the page, its smallest text, its fonts, no embedded image.
4. Run `check_layout.py` on it: nothing may run out of its box, cards that are alike must be whole pixels, and the PDF must be as wide as the figure.
5. Look at the picture in colour and in grey: nothing overlaps, every label stands clear of every line, like things are one size and stand on one line, and two meanings that touch still differ in grey.

Things that went wrong once:

- A Palatino variable inside running text widens the pitch of its line: give `.m`, `i.v` and `.pr` a `line-height` of 0 there (not where the formula is a block of its own).
- A space next to a sign set in another face is lost in the text of the PDF: keep it inside the span (`<span class="pr"> ≈ </span>`; `"#≠ #$c$"` in `Fig.rich`).
- A prime after a word inside a `.chip` must share a span with the word: the gap of the chip otherwise parts them.
- `.grp` turns its text into capitals, also in the text of the PDF. A group label that must stay as written is semi-bold in `--muted` instead.
- A `.tag` inside running text needs `line-height: 1` and a little less padding, or it pushes the lines apart.
- `.badge` is the numbered disc of a heading and nothing else: `fig.js` redraws every `.badge` at one size. A mark of another size (the score `c` in the key of `depth-one`) is drawn by the function that draws it in the figure.
- Code inside a sentence widens the pitch of its line as a Palatino variable does: `.mono` gets a `line-height` of 0 there.
- A short note that ends in one word on a line of its own: `text-wrap:balance` (`text-wrap:pretty` for a paragraph).
- A heading does not wrap (`white-space:nowrap`): one that is too long for its card runs out of it, and the crop then makes the whole figure smaller. `check_layout.py` names it.
- An SVG `<pattern>` prints as a page-sized image and a CSS gradient as an unbounded shading; both defeat the crop.
- The `.m` of `style.css` is the formula class: a figure may not use `.m` for something else.

## The data plots

The seven plots in `Figures/generated/` are not drawn here: `experiments/scripts/export_latex.py` writes them, with the colours of `PAL` and the type of its `_style()`. Since 2026-11-24 they take the values below, which follow the tokens; the bars of the EndorseRank histogram are an area and take the band gold (`er_area`).

| `PAL` | Before | Now | Token |
|---|---|---|---|
| `er` | `#D97706` | `#B98A24` (a line), `#CFA448` (an area) | `--allow`, `--allow-band` |
| `awp` | `#2563EB` | `#2340C8` | `--transfer` |
| `cpr` | `#7C3AED` | `#6A2C91` | `--coupled` |
| `spr` | `#A78BFA` | `#B79BCB` | `--coupled-fill` |
| `count`, `equal` | `#334155`, `#475569` | `#5A5A5A` | `--count` |
| `bfs` | `#8A94A3` | `#8A8A8A` | `--user` |
| `random` | `#C3CAD3` | `#C9C9C7` | `--user-fill` |
| `ideal` | `#374151` | `#333333` | `--text` |
| `point`, `decay` | `#0F766E` | `#2A7A72` | `--contract` |
| `band`, `divider` | `#CBD5E1` | `#C4C4C2` | `--hair` |
| `ref` | `#64748B` | `#575757` | `--muted` |
| `w0` | `#DB2777` | `#C23B5E` | `--rq3` |

In `_style()`: text and axis labels `#333333`, axis line `#B4B4B4`, ticks `#575757`, grid `#E6E6E4`.

The faces are those of the diagrams too (since 2026-11-24). matplotlib reads only the default instance of a variable font and sets no letter spacing, so `_plot_face()` in `export_latex.py` makes the face on the machine that draws the plots: it cuts the semi-condensed instance of the installed Bahnschrift with fontTools (wght 400, wdth 87.5), adds the 0.045 em of spacing to every advance, gives it a minus sign (Bahnschrift has none: the horizontal bar of its own plus, on the advance of the plus), and keeps it as `experiments/data/_work/fonts/bahnschrift-semicondensed-plot-v2.ttf` under the family name "Bahnschrift SemiCondensed". That folder is ignored by git: the font may not be put into the repository. Formulas and variables are set in Palatino (mathtext `custom`, its italic for the variables, STIX as the fallback), and the panel titles of the discovery curves in Palatino, as the headings of the diagrams. Where Bahnschrift or Palatino is not installed the plots fall back to Segoe UI and STIX sans, and the script says so.

The Korean plots (`overleaf-github-ko/scripts/make_ko_figures.py`) are drawn by the same functions with these colours and faces. Their Hangul comes from static weight-400 cuts of Noto Sans KR (text) and Noto Serif KR (panel titles), made from the installed variable fonts with fontTools, kept in the same folder and given no added spacing. A text that holds a formula is laid out whole by mathtext, which has no per-glyph fallback, so the script takes the Hangul of such a text from the Noto cut itself.
