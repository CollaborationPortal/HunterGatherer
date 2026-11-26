# Porting the Hunter Gatherer setup screen to another game

This guide moves two features from Hunter Gatherer (`game-src.html` in
https://github.com/CollaborationPortal/HunterGatherer) into another browser game:

1. **Styled player-count dropdown**: a pill-shaped `<select>` with a custom chevron that matches the game's buttons.
2. **Tap-to-pick character selection with a sticky bar**: each player taps a character card to claim it, the turn passes automatically, and a bar pinned to the bottom of the screen always shows whose turn it is, everyone's picks, and the Play button. A "Scroll down for more options" hint floats in the middle of the screen until the player scrolls.

Everything below is plain HTML, CSS, and vanilla JavaScript with no libraries. The two features are independent, so you can port just one.

---

## How the selection works

Port this behavior, not just the code:

- The player count (1–4) creates that many players. Each player has an index and a colour class `p0`–`p3`.
- One player at a time is the **editor** (`state.selectingFor`). The banner says "Player N, tap a character to pick it!" in that player's colour.
- **Tapping a free card** assigns it to the editor right away, then hands the turn to the next player with no character. Nobody presses a confirm button.
- Tapping one of a card's **look thumbnails** picks the card with that look.
- A **claimed card** gets a coloured border and a "Player N" tag. Other players can't claim it, but its look thumbnails still change the owner's look. That way picking fast doesn't lock someone into an appearance.
- **Tapping a player chip** in the bar makes that player the editor again, so they can switch characters.
- When everyone has a character, `selectingFor` becomes `-1`: no editor. Free cards stop responding, the banner says "Everyone's ready!", and **Play Game** turns on and pulses.
- The sticky bar holds the banner, the chips, **Back**, and **Play Game**, so players never need to scroll to find them.
- The scroll hint shows when the setup screen opens and fades out once the player scrolls more than 60px. It never shows if the page doesn't scroll, and it hides whenever the game changes screens.

---

## Step 1: Theme tokens

All the CSS below uses these variables. If the target game already has a palette, map these names onto its colours instead of adding new ones.

```css
:root {
  --ui-ink: #2a1d12;        /* body text */
  --ui-dark: #3b2a1a;       /* text on bright hint */
  --ui-brown: #5c3d22;      /* dropdown text, chevron */
  --ui-edge: #8b5a2b;       /* dropdown border and 3D edge */
  --ui-gold: #e8c97a;       /* dropdown fill */
  --ui-panel: #f6ecd7;      /* sticky bar background */
  --ui-accent: #b5522a;     /* focus ring, active look */
}
```

The chevron is an inline SVG with its colour written into the data URI as `%235c3d22` (`#5c3d22`). If you change `--ui-brown`, change that hex too.

---

## Step 2: Player-count dropdown

### HTML

```html
<div style="display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;margin:.8rem 0">
  <label for="player-count"><strong>Number of players:</strong></label>
  <select id="player-count" class="count-select">
    <option value="1">1 player</option>
    <option value="2" selected>2 players</option>
    <option value="3">3 players</option>
    <option value="4">4 players</option>
  </select>
</div>
```

### CSS

```css
.count-select {
  appearance: none; -webkit-appearance: none;
  font: inherit; font-weight: 800; letter-spacing: .02em;
  color: var(--ui-brown);
  padding: .55rem 2.6rem .55rem 1.1rem;
  border: 2px solid var(--ui-edge);
  border-radius: 999px;
  background:
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='9' viewBox='0 0 14 9'%3E%3Cpath d='M1.5 1.5 7 7l5.5-5.5' fill='none' stroke='%235c3d22' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") right 1rem center / 14px 9px no-repeat,
    linear-gradient(180deg, #f6dc9c, var(--ui-gold));
  box-shadow: 0 4px 0 var(--ui-edge);
  cursor: pointer;
  transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}
.count-select:hover { transform: translateY(-1px); filter: brightness(1.05); }
.count-select:focus-visible { outline: 3px solid color-mix(in srgb, var(--ui-accent) 45%, transparent); outline-offset: 2px; }
.count-select option { background: var(--ui-panel); color: var(--ui-ink); font-weight: 700; }
```

Only the closed box is styled. The list that opens is drawn by the browser and can't be fully themed.

If you are porting only the dropdown, you're done. Wire `change` to whatever rebuilds your player list.

---

## Step 3: Setup screen markup

Put the sticky bar **inside** the scrolling panel, after the card grid, so it sticks to the bottom of the window while the panel scrolls past.

Put the scroll hint **outside** every screen container, as a direct child of `<body>`. It's `position: fixed`, and if any ancestor has a `transform` (Hunter Gatherer's screens slide in with a transform animation), the centring breaks.

```html
<div id="setup-screen" class="screen">
  <div class="panel">
    <h2>Choose Your Characters</h2>
    <!-- Step 2's player-count dropdown goes here -->
    <div id="char-grid" class="setup-grid"></div>
    <div class="setup-bar">
      <div class="setup-bar-status">
        <p id="pick-hint" class="pick-banner"></p>
        <div id="party-chips"></div>
      </div>
      <div class="row-actions">
        <button id="btn-back" type="button">Back</button>
        <button id="btn-begin" type="button" disabled>Play Game</button>
      </div>
    </div>
  </div>
</div>

<!-- Direct child of <body>, after all screens -->
<div class="scroll-hint gone" id="scroll-hint" aria-hidden="true">Scroll down for more options <span class="arrow">↓</span></div>
```

---

## Step 4: Setup screen CSS

```css
/* Player colours. Every coloured element reads --pc. */
:is(.player-chip, .pick-banner, .char-card, .owner-tag).p0 { --pc: #b5522a; }
:is(.player-chip, .pick-banner, .char-card, .owner-tag).p1 { --pc: #3f5e46; }
:is(.player-chip, .pick-banner, .char-card, .owner-tag).p2 { --pc: #3f7aa8; }
:is(.player-chip, .pick-banner, .char-card, .owner-tag).p3 { --pc: #8b5a2b; }

/* Card grid */
.setup-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.15rem 1.25rem; margin-top: 1rem; }
@media (max-width: 820px) { .setup-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }

.char-card {
  position: relative;
  background: #fff9ec;
  border: 3px solid transparent;
  border-radius: 18px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(42,29,18,.12);
  transition: border-color .15s, transform .15s;
}
.char-card:hover { transform: translateY(-3px); }
.char-card.owned { border-color: var(--pc); box-shadow: 0 0 0 3px color-mix(in srgb, var(--pc) 30%, transparent); }
.char-card.taken { opacity: .6; cursor: default; }
.char-card.taken:hover, .setup-grid.idle .char-card:not(.owned):hover { transform: none; }
.setup-grid.idle .char-card:not(.owned) { cursor: default; }
.char-card img.hero { width: 100%; aspect-ratio: 3 / 4; object-fit: contain; display: block; }
.owner-tag {
  position: absolute; top: .6rem; left: .6rem; z-index: 1;
  background: var(--pc); color: #fff8ef;
  border-radius: 999px; padding: .25rem .75rem;
  font-weight: 800; font-size: .9rem;
  box-shadow: 0 3px 8px rgba(42,29,18,.3);
}

/* Look thumbnails */
.look-row { display: flex; gap: 8px; flex-wrap: wrap; padding: .65rem .75rem 0; }
.look-btn {
  width: 56px; height: 56px; padding: 0; border-radius: 12px;
  border: 3px solid transparent; overflow: hidden; cursor: pointer;
}
.look-btn img { width: 100%; height: 100%; object-fit: cover; display: block; }
.look-btn.active { border-color: var(--ui-accent); }

/* Sticky bar */
.setup-bar {
  position: sticky; bottom: .75rem; z-index: 5;
  display: flex; gap: .75rem 1rem; flex-wrap: wrap;
  align-items: center; justify-content: space-between;
  margin-top: 1.2rem;
  padding: .75rem 1rem;
  background: var(--ui-panel);
  border: 3px solid rgba(92,61,34,.35);
  border-radius: 18px;
  box-shadow: 0 -6px 24px rgba(42,29,18,.25);
}
.setup-bar-status { flex: 1 1 22rem; min-width: 0; }
.pick-banner { margin: 0 0 .3rem; font-size: 1.2rem; font-weight: 800; color: var(--pc, var(--ui-brown)); }

/* Player chips */
.player-chip {
  display: inline-flex; align-items: center; gap: .45rem;
  background: #efe0c0; border-radius: 999px; padding: .35rem .7rem;
  margin: .2rem; font: inherit; font-weight: 700; font-size: .9rem;
  border: 3px solid transparent; cursor: pointer; color: inherit;
}
.player-chip.editing {
  border-color: var(--pc);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--pc) 25%, transparent);
  background: #ffe4c2;
}
.player-chip .check { color: var(--pc); font-weight: 900; }
.player-chip img { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }

/* Play button pulses once everyone is ready. Match the first shadow to the button's own 3D edge. */
#btn-begin.ready { animation: ready-pulse 1.6s ease-in-out infinite; }
@keyframes ready-pulse {
  0%, 100% { box-shadow: 0 8px 0 #7a3418, 0 0 0 0 rgba(217,120,58,.55); }
  50% { box-shadow: 0 8px 0 #7a3418, 0 0 0 10px rgba(217,120,58,0); }
}

/* Scroll hint, centred in the window */
.scroll-hint {
  position: fixed; left: 50%; top: 50%; z-index: 20;
  transform: translate(-50%, -50%);
  white-space: nowrap;
  background: linear-gradient(180deg, #ffe27a, #f5b93a);
  color: var(--ui-dark);
  border: 2px solid #c98a1c;
  border-radius: 999px;
  padding: .7rem 1.5rem;
  font-weight: 800; font-size: 1.3rem;
  box-shadow: 0 6px 18px rgba(42,29,18,.35);
  pointer-events: none;
  transition: opacity .35s ease, transform .35s ease;
}
.scroll-hint .arrow { display: inline-block; margin-left: .3rem; animation: hint-bounce 1s ease-in-out infinite; }
.scroll-hint.gone { opacity: 0; transform: translate(-50%, calc(-50% + 8px)); }
@keyframes hint-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(4px); }
}
```

`pointer-events: none` on the hint matters: taps pass through it to the card underneath.

---

## Step 5: Data the logic expects

```js
// Each character has an id, a display name, and one or more looks (portrait variants).
const CHARACTERS = [
  {
    id: "hunter",
    name: "The Hunter",
    looks: [
      { id: "k1", label: "Look 1", img: "images/hunter-1.jpg" },
      { id: "k2", label: "Look 2", img: "images/hunter-2.jpg" }
    ]
  },
  // ...
];

const state = {
  players: [],          // built by resetParty()
  selectingFor: 0,      // index of the player picking now; -1 when everyone has picked
  cardShowcase: {}      // characterId -> lookId shown on an unclaimed card
};

const $ = id => document.getElementById(id);
```

If a character has only one look, the thumbnail row shows a single button. You can hide `.look-row` in that case.

Hunter Gatherer turns image keys into embedded data URIs with `asset(key)`. The code below uses `look.img` directly as the `src`. If the target game has its own image helper, use it in the three places that build `<img src>`.

---

## Step 6: Logic

```js
function resetParty() {
  const n = Number($("player-count").value);
  state.players = Array.from({ length: n }, (_, i) => ({
    id: i,
    name: `Player ${i + 1}`,
    character: null,
    colorClass: `p${i}`
    // ...plus any per-player game state (score, position, etc.)
  }));
  state.selectingFor = 0;
  renderSetup();
}

function lookById(ch, lookId) {
  return ch.looks.find(l => l.id === lookId) || ch.looks[0];
}

/** Give a character and look to a player. Returns true if assigned. */
function assignRole(playerIndex, roleId, lookId) {
  const player = state.players[playerIndex];
  const ch = CHARACTERS.find(c => c.id === roleId);
  if (!player || !ch) return false;
  const heldByOther = state.players.find(p => p.id !== player.id && p.character && p.character.id === ch.id);
  if (heldByOther) return false;
  const look = lookById(ch, lookId);
  player.character = { ...ch, img: look.img, lookId: look.id, lookLabel: look.label };
  state.cardShowcase[ch.id] = look.id;
  return true;
}

/** Claim a card for the current player, then hand over to the next player still choosing (-1 when all are set). */
function pickCard(roleId, lookId) {
  if (!assignRole(state.selectingFor, roleId, lookId)) return;
  state.selectingFor = state.players.findIndex(p => !p.character);
  renderSetup();
}

function renderSetup() {
  const editor = state.players[state.selectingFor] || null;
  const owners = new Map(state.players.filter(p => p.character).map(p => [p.character.id, p]));
  const allReady = state.players.every(p => p.character);
  const shortName = c => c.name.replace(/^The /, "");

  const chips = $("party-chips");
  chips.innerHTML = state.players.map((p, i) => {
    const editing = p === editor ? "editing" : "";
    if (!p.character) {
      return `<button type="button" class="player-chip ${p.colorClass} ${editing}" data-player="${i}">Player ${i + 1}: ${editing ? "picking now…" : "waiting"}</button>`;
    }
    return `<button type="button" class="player-chip ${p.colorClass} ${editing}" data-player="${i}" title="Tap to change Player ${i + 1}'s pick"><img src="${p.character.img}" alt="" /> <span class="check">✓</span> Player ${i + 1}: ${shortName(p.character)}</button>`;
  }).join("");

  const banner = $("pick-hint");
  banner.className = `pick-banner ${editor ? editor.colorClass : ""}`;
  if (!editor) banner.textContent = "Everyone's ready! Press Play Game — or tap a player below to change.";
  else if (editor.character) banner.textContent = `Player ${editor.id + 1}, tap a different character to switch.`;
  else banner.textContent = `Player ${editor.id + 1}, tap a character to pick it!`;

  $("char-grid").classList.toggle("idle", !editor);
  $("char-grid").innerHTML = CHARACTERS.map(c => {
    const owner = owners.get(c.id);
    const cls = owner ? `owned ${owner.colorClass} ${owner === editor ? "" : "taken"}` : "";
    const previewLookId = owner ? owner.character.lookId : (state.cardShowcase[c.id] || c.looks[0].id);
    return `<div class="char-card ${cls}" data-id="${c.id}">
      ${owner ? `<span class="owner-tag ${owner.colorClass}">Player ${owner.id + 1}</span>` : ""}
      <img class="hero" src="${lookById(c, previewLookId).img}" alt="${c.name}" />
      <div class="look-row">
        ${c.looks.map(l => `<button type="button" class="look-btn ${previewLookId === l.id ? "active" : ""}" data-look="${l.id}" title="${l.label}"><img src="${l.img}" alt="${l.label}" /></button>`).join("")}
      </div>
      <div class="body">
        <h3>${c.name}</h3>
        <!-- game-specific card details here -->
      </div>
    </div>`;
  }).join("");

  chips.onclick = (e) => {
    const chip = e.target.closest("[data-player]");
    if (!chip) return;
    state.selectingFor = Number(chip.dataset.player);
    renderSetup();
  };

  $("char-grid").onclick = (e) => {
    const card = e.target.closest(".char-card");
    if (!card) return;
    const ch = CHARACTERS.find(c => c.id === card.dataset.id);
    const lookBtn = e.target.closest(".look-btn");
    const owner = owners.get(ch.id);
    if (owner && owner !== editor) {
      // A claimed card stays with its player; its looks still restyle that player
      if (lookBtn && assignRole(owner.id, ch.id, lookBtn.dataset.look)) renderSetup();
      return;
    }
    if (!editor) return;
    pickCard(ch.id, lookBtn ? lookBtn.dataset.look : (state.cardShowcase[ch.id] || ch.looks[0].id));
  };

  $("btn-begin").disabled = !allReady;
  $("btn-begin").classList.toggle("ready", allReady);
}

/** Hide the "scroll down" hint once the player scrolls, or when there is nothing below the fold. */
function updateScrollHint() {
  const hint = $("scroll-hint");
  if (hint.classList.contains("gone")) return;
  const roomBelow = document.documentElement.scrollHeight - window.innerHeight > 40;
  if (window.scrollY > 60 || !roomBelow) hint.classList.add("gone");
}
window.addEventListener("scroll", updateScrollHint, { passive: true });
```

### Wiring

```js
function startSetup() {
  showScreen("setup-screen");     // the game's own screen switcher
  resetParty();
  $("scroll-hint").classList.remove("gone");
  updateScrollHint();             // hides it at once if nothing scrolls
}

$("player-count").onchange = resetParty;
$("btn-begin").onclick = () => {
  if (state.players.some(p => !p.character)) return;
  beginGame();                    // the game's own start function
};
```

In the game's screen switcher, hide the hint so it can't float over gameplay:

```js
function showScreen(id) {
  // ...existing screen switching...
  $("scroll-hint").classList.add("gone");
}
```

`startSetup` calls `showScreen` first and then removes `gone`, so the order matters.

---

## Optional extras from Hunter Gatherer

- **Random card order and starting looks:** Hunter Gatherer shuffles the card order and picks a random look for each unclaimed card when setup opens (`randomShowcase()` and `state.characterOrder`). It keeps both when only the player count changes.
- **Rename players after picking:** Hunter Gatherer sets `player.name` to the character's short name ("Hunter") so the rest of the game reads naturally.

---

## Things to adapt

- **Character data:** map the target game's roles onto `{ id, name, looks: [{ id, label, img }] }`, or change the field names in the logic.
- **Card body:** replace the `<!-- game-specific card details -->` block with whatever the game shows (story, powers, stats).
- **More than four players:** add `.p4`, `.p5`, … rules with new `--pc` colours, and more `<option>`s.
- **Wording:** the banner, chip, and tag text all say "Player N". Change them in `renderSetup()`.
- **Container that scrolls:** the scroll hint listens to `window`. If the target game scrolls inside an element instead, listen on that element and use its `scrollTop`, `scrollHeight`, and `clientHeight`.

## Checking it works

1. With 2 players, Player 1 taps a card: it gets a red border and a "Player 1" tag, and the banner turns green: "Player 2, tap a character to pick it!"
2. Player 2 can't claim Player 1's card, but tapping a look thumbnail on it changes Player 1's look.
3. Once both have picked, the banner says "Everyone's ready!", free cards don't react, and Play Game is enabled and pulsing.
4. Tapping a chip lets that player switch characters.
5. Changing the player count resets all picks.
6. The scroll hint is centred when setup opens, fades after a short scroll, and doesn't appear on the game screen.
7. At phone width the grid drops to two columns and the bar wraps without overflowing.
