# Porting the Hunter Gatherer setup screen to another game

This guide moves two features from Hunter Gatherer (`game-src.html` in
https://github.com/CollaborationPortal/HunterGatherer) into another browser game:

1. **Styled player-count dropdown**: a pill-shaped `<select>` with a custom chevron that matches the game's buttons.
2. **Try-then-confirm character selection**: each player taps character cards and look thumbnails to try them out, then presses **Confirm** on the card to lock in. A floating prompt tells each player when it's their turn, and a **Back to previous player** button lets the last player change their pick.

Everything below is plain HTML, CSS, and vanilla JavaScript with no libraries. The two features are independent, so you can port just one.

---

## How the selection works

Port this behavior, not just the code:

- The player count (1–4) creates that many players. Each player has an index and a colour class `p0`–`p3`.
- Players choose in order. The player choosing now is the **editor** (`state.selectingFor`). Every player before the editor has confirmed a character. No player after the editor has one yet.
- When the setup screen opens, a **floating prompt** in the middle of the window says "Player 1, select your character. Scroll down for more options ↓". It shows again whenever the turn changes ("Player 2, select your character."). Once everyone has confirmed, it says "Everyone's ready! Press Play Game." The scroll tip appears only when there are more cards below. The prompt fades when the player scrolls more than 60px or taps a card, and it never shows outside the setup screen.
- **Tapping a free card** doesn't claim it. It becomes the editor's **pending** pick (`state.pending`). The card gets a border in the editor's colour, and a panel appears right under the portrait with "Player N choose: The Hunter", a **✓ Confirm** button, and a tip to try other looks.
- Tapping a **look thumbnail** on a free card makes that card pending with that look. The player can switch cards and looks as often as they like.
- **Confirm** assigns the pending card to the editor and passes the turn to the next player with no character.
- A **confirmed card** is locked: it fades, keeps its coloured border, and gets a "Player N" tag. Nobody can tap it or change its look.
- **Back to previous player** shows from Player 2 onward, in the top button row and on the pending card's panel. It removes the previous player's character and makes it their pending pick again, so the old pick stays highlighted with its Confirm button. They can confirm it again or choose something else.
- When everyone has confirmed, `selectingFor` becomes `-1`. Free cards stop responding, the page scrolls to the top, and **Play Game** turns on and pulses. Back to previous player still works and reopens the last player's pick.
- Changing the player count clears every pick and starts again with Player 1.
- **Back**, **Back to previous player**, and **Play Game** sit in a row at the top of the setup panel, next to the player count. There's no sticky bar.

---

## Step 1: Theme tokens

All the CSS below uses these variables. If the target game already has a palette, map these names onto its colours instead of adding new ones.

```css
:root {
  --ui-ink: #2a1d12;        /* body text */
  --ui-dark: #3b2a1a;       /* text on the bright prompt */
  --ui-brown: #5c3d22;      /* dropdown text, chevron */
  --ui-edge: #8b5a2b;       /* dropdown border and 3D edge */
  --ui-gold: #e8c97a;       /* dropdown fill */
  --ui-panel: #f6ecd7;      /* dropdown list background */
  --ui-accent: #b5522a;     /* focus ring, active look */
}
```

The chevron is an inline SVG with its colour written into the data URI as `%235c3d22` (`#5c3d22`). If you change `--ui-brown`, change that hex too.

---

## Step 2: Player-count dropdown

### HTML

```html
<div class="count-row">
  <label for="player-count"><strong>Number of players:</strong></label>
  <select id="player-count" class="count-select">
    <option value="1">1 player</option>
    <option value="2" selected>2 players</option>
    <option value="3">3 players</option>
    <option value="4">4 players</option>
  </select>
</div>
```

If you port the whole setup screen, this goes inside `.setup-controls` (Step 3).

### CSS

```css
.count-row { display: flex; gap: .6rem; flex-wrap: wrap; align-items: center; }
.count-select {
  appearance: none; -webkit-appearance: none;
  min-width: 11.5rem; /* the browser sizes it from the lighter option text, which cuts off the label */
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

Keep the `min-width`. The browser works out the box's width from the option text, which is lighter than the box's own bold, letter-spaced text, so without it the last word gets clipped. If your labels are longer than "4 foragers", raise it.

Only the closed box is styled. The list that opens is drawn by the browser and can't be fully themed.

If you're porting only the dropdown, you're done. Wire `change` to whatever rebuilds your player list.

---

## Step 3: Setup screen markup

Put the controls row above the card grid. The pending card's panel is built by `renderSetup()` (Step 6), so it has no markup here.

Put the floating prompt **outside** every screen container, as a direct child of `<body>`. It's `position: fixed`, and if any ancestor has a `transform` (Hunter Gatherer's screens slide in with a transform animation), the centring breaks.

```html
<div id="setup-screen" class="screen">
  <div class="panel">
    <h2>Choose Your Characters</h2>
    <div class="setup-controls">
      <!-- Step 2's .count-row goes here -->
      <div class="row-actions">
        <button class="btn-soft" id="btn-back" type="button">Back</button>
        <button class="btn-soft" id="btn-prev-player" type="button" hidden>← Back to previous player</button>
        <button class="btn-primary" id="btn-begin" type="button" disabled>Play Game</button>
      </div>
    </div>
    <div id="char-grid" class="setup-grid"></div>
  </div>
</div>

<!-- Direct child of <body>, after all screens -->
<div class="turn-prompt gone" id="turn-prompt" role="status"><span id="turn-prompt-text"></span><span id="turn-prompt-scroll"> Scroll down for more options <span class="arrow">↓</span></span></div>
```

`role="status"` makes screen readers announce each new turn.

---

## Step 4: Setup screen CSS

The selectors `.btn-primary` and `.row-actions` are the game's existing button and button-row styles. The code below adds only what's new.

```css
/* Player colours. Every coloured element reads --pc. */
:is(.char-card, .owner-tag, .choose-panel).p0 { --pc: #b5522a; }
:is(.char-card, .owner-tag, .choose-panel).p1 { --pc: #3f5e46; }
:is(.char-card, .owner-tag, .choose-panel).p2 { --pc: #3f7aa8; }
:is(.char-card, .owner-tag, .choose-panel).p3 { --pc: #8b5a2b; }

/* Controls row: player count on the left, buttons on the right */
.setup-controls {
  display: flex; gap: .6rem 1rem; flex-wrap: wrap;
  align-items: center; justify-content: space-between;
  margin: .8rem 0;
}
.btn-soft {
  color: var(--ui-ink);
  background: #efe2c4;
  border: 2px solid rgba(92,61,34,.3);
  padding: .6rem 1rem;
}

/* Card grid */
.setup-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.15rem 1.25rem; margin-top: 1rem; }
@media (max-width: 820px) { .setup-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) { .setup-grid { grid-template-columns: minmax(0, 1fr); } }

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
.char-card.owned, .char-card.pending { border-color: var(--pc); box-shadow: 0 0 0 3px color-mix(in srgb, var(--pc) 30%, transparent); }
.char-card.pending:hover { transform: none; }
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

/* "Player N choose" panel under the pending card's portrait */
.choose-panel {
  display: flex; flex-direction: column; align-items: center; gap: .55rem;
  padding: .75rem .85rem .85rem;
  background: color-mix(in srgb, var(--pc) 14%, #fff9ec);
  border-bottom: 3px solid var(--pc);
  text-align: center;
  cursor: default;
}
.choose-panel .choose-title { margin: 0; font-size: 1.15rem; font-weight: 800; color: var(--pc); }
.choose-panel .choose-tip { margin: 0; font-size: .82rem; }
.choose-panel .row-actions { gap: .5rem; }
.choose-panel .btn-primary { padding: .65rem 1.3rem; box-shadow: 0 6px 0 #7a3418; }

/* Look thumbnails */
.look-row { display: flex; gap: 8px; flex-wrap: wrap; padding: .65rem .75rem 0; }
.look-btn {
  width: 3.5rem; height: 3.5rem; padding: 0; border-radius: 12px;
  border: 3px solid transparent; overflow: hidden; cursor: pointer;
}
.look-btn img { width: 100%; height: 100%; object-fit: cover; display: block; }
.look-btn.active { border-color: var(--ui-accent); }

/* Play button pulses once everyone is ready. Match the first shadow to the button's own 3D edge. */
#btn-begin.ready { animation: ready-pulse 1.6s ease-in-out infinite; }
@keyframes ready-pulse {
  0%, 100% { box-shadow: 0 8px 0 #7a3418, 0 0 0 0 rgba(217,120,58,.55); }
  50% { box-shadow: 0 8px 0 #7a3418, 0 0 0 10px rgba(217,120,58,0); }
}

/* Floating turn prompt, centred in the window */
.turn-prompt {
  position: fixed; left: 50%; top: 50%; z-index: 20;
  transform: translate(-50%, -50%);
  width: max-content; max-width: calc(100vw - 2rem);
  text-align: center;
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
.turn-prompt .arrow { display: inline-block; margin-left: .3rem; animation: hint-bounce 1s ease-in-out infinite; }
.turn-prompt.gone { opacity: 0; transform: translate(-50%, calc(-50% + 8px)); }
@keyframes hint-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(4px); }
}
```

`pointer-events: none` on the prompt matters: taps pass through it to the card underneath. `max-width` lets the text wrap on a phone instead of running off the screen.

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
  selectingFor: 0,      // index of the player choosing now; -1 when everyone has confirmed
  pending: null,        // { roleId, lookId } the chooser is trying out before confirming
  cardShowcase: {}      // characterId -> lookId shown on an unclaimed card
};

const $ = id => document.getElementById(id);
```

If a character has only one look, the thumbnail row shows a single button. You can hide `.look-row` in that case.

Hunter Gatherer turns image keys into embedded data URIs with `asset(key)`. The code below uses `look.img` directly as the `src`. If the target game has its own image helper, use it in the two places that build `<img src>`.

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
  state.pending = null;
  renderSetup();
  showTurnPrompt();
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

/** Try out a card (and look) for the current player without locking it in. */
function previewCard(roleId, lookId) {
  state.pending = { roleId, lookId };
  state.cardShowcase[roleId] = lookId;
  hideTurnPrompt();
  renderSetup();
}

/** Lock in the tried-out card, then hand over to the next player still choosing (-1 when all are set). */
function confirmPick() {
  const { roleId, lookId } = state.pending || {};
  if (!assignRole(state.selectingFor, roleId, lookId)) return;
  state.pending = null;
  state.selectingFor = state.players.findIndex(p => !p.character);
  // Play Game sits at the top of the page
  if (state.selectingFor < 0) window.scrollTo(0, 0);
  renderSetup();
  showTurnPrompt();
}

/** Reopen the previous player's choice; their old pick stays highlighted so they can keep or change it. */
function backToPreviousPlayer() {
  const prev = (state.selectingFor < 0 ? state.players.length : state.selectingFor) - 1;
  const player = state.players[prev];
  if (!player) return;
  state.pending = player.character ? { roleId: player.character.id, lookId: player.character.lookId } : null;
  player.character = null;
  state.selectingFor = prev;
  renderSetup();
  showTurnPrompt();
}

function renderSetup() {
  const editor = state.players[state.selectingFor] || null;
  const owners = new Map(state.players.filter(p => p.character).map(p => [p.character.id, p]));
  const allReady = state.players.every(p => p.character);
  const pendingId = editor && state.pending ? state.pending.roleId : null;
  const canGoBack = state.selectingFor !== 0 && state.players.some(p => p.character);
  const backBtn = `<button type="button" class="btn-soft prev-player-btn">← Back to previous player</button>`;

  $("char-grid").classList.toggle("idle", !editor);
  $("char-grid").innerHTML = CHARACTERS.map(c => {
    const owner = owners.get(c.id);
    const isPending = c.id === pendingId;
    const cls = owner ? `owned taken ${owner.colorClass}` : isPending ? `pending ${editor.colorClass}` : "";
    const previewLookId = owner ? owner.character.lookId : (state.cardShowcase[c.id] || c.looks[0].id);
    const choosePanel = isPending ? `<div class="choose-panel ${editor.colorClass}">
        <p class="choose-title">Player ${editor.id + 1} choose: ${c.name}</p>
        <p class="choose-tip">Try the other looks below, or tap a different character.</p>
        <div class="row-actions">
          ${canGoBack ? backBtn : ""}
          <button type="button" class="btn-primary confirm-btn">✓ Confirm</button>
        </div>
      </div>` : "";
    return `<div class="char-card ${cls}" data-id="${c.id}">
      ${owner ? `<span class="owner-tag ${owner.colorClass}">Player ${owner.id + 1}</span>` : ""}
      <img class="hero" src="${lookById(c, previewLookId).img}" alt="${c.name}" />
      ${choosePanel}
      <div class="look-row">
        ${c.looks.map(l => `<button type="button" class="look-btn ${previewLookId === l.id ? "active" : ""}" data-look="${l.id}" title="${l.label}"><img src="${l.img}" alt="${l.label}" /></button>`).join("")}
      </div>
      <div class="body">
        <h3>${c.name}</h3>
        <!-- game-specific card details here -->
      </div>
    </div>`;
  }).join("");

  $("char-grid").onclick = (e) => {
    if (e.target.closest(".prev-player-btn")) return backToPreviousPlayer();
    if (e.target.closest(".confirm-btn")) return confirmPick();
    const card = e.target.closest(".char-card");
    if (!card || !editor || e.target.closest(".choose-panel")) return;
    const ch = CHARACTERS.find(c => c.id === card.dataset.id);
    // Confirmed picks are locked; "Back to previous player" reopens them
    if (owners.has(ch.id)) return;
    const lookBtn = e.target.closest(".look-btn");
    if (!lookBtn && ch.id === pendingId) return;
    previewCard(ch.id, lookBtn ? lookBtn.dataset.look : (state.cardShowcase[ch.id] || ch.looks[0].id));
  };

  $("btn-prev-player").hidden = !canGoBack;
  $("btn-begin").disabled = !allReady;
  $("btn-begin").classList.toggle("ready", allReady);
}

let promptScrollY = 0;

/** Float "Player N, select your character" mid-screen; adds the scroll tip when more cards sit below. */
function showTurnPrompt() {
  // resetParty may run before the setup screen is open (for example on page load)
  if (!$("setup-screen").classList.contains("active")) return;
  const editor = state.players[state.selectingFor];
  $("turn-prompt-text").textContent = editor
    ? `Player ${editor.id + 1}, select your character.`
    : "Everyone's ready! Press Play Game.";
  const roomBelow = document.documentElement.scrollHeight - window.innerHeight - window.scrollY > 40;
  $("turn-prompt-scroll").hidden = !editor || !roomBelow;
  promptScrollY = window.scrollY;
  $("turn-prompt").classList.remove("gone");
}

function hideTurnPrompt() {
  $("turn-prompt").classList.add("gone");
}

window.addEventListener("scroll", () => {
  if (Math.abs(window.scrollY - promptScrollY) > 60) hideTurnPrompt();
}, { passive: true });
```

The card click handler is set on the grid, not on each card, because `renderSetup()` rebuilds every card on each change. The Confirm and Back buttons on the panel are found the same way, by class.

### Wiring

```js
function startSetup() {
  showScreen("setup-screen");     // the game's own screen switcher
  resetParty();                   // also shows the Player 1 prompt
}

$("player-count").onchange = resetParty;
$("btn-prev-player").onclick = backToPreviousPlayer;
$("btn-begin").onclick = () => {
  if (state.players.some(p => !p.character)) return;
  beginGame();                    // the game's own start function
};
```

`startSetup` must call `showScreen` before `resetParty`. `showTurnPrompt` does nothing unless the setup screen is active, which is what stops the prompt from appearing on a title screen.

In the game's screen switcher, hide the prompt so it can't float over gameplay:

```js
function showScreen(id) {
  // ...existing screen switching...
  hideTurnPrompt();
}
```

---

## Optional extras from Hunter Gatherer

- **Random card order and starting looks:** Hunter Gatherer shuffles the card order and picks a random look for each unclaimed card when setup opens (`randomShowcase()` and `state.characterOrder`). It keeps both when only the player count changes.
- **Rename players after picking:** Hunter Gatherer sets `player.name` to the character's short name ("Hunter") in `assignRole`, and resets it to "Forager N" in `backToPreviousPlayer`, so the rest of the game reads naturally.

---

## Things to adapt

- **Character data:** map the target game's roles onto `{ id, name, looks: [{ id, label, img }] }`, or change the field names in the logic.
- **Card body:** replace the `<!-- game-specific card details -->` block with whatever the game shows (story, powers, stats).
- **More than four players:** add `.p4`, `.p5`, … rules with new `--pc` colours, and more `<option>`s.
- **Wording:** the prompt, panel, and tag text all say "Player N". Change them in `showTurnPrompt()` and `renderSetup()`.
- **Where Play Game lives:** if the target game puts its Play button somewhere other than the top of the page, change or remove the `window.scrollTo(0, 0)` in `confirmPick()`.
- **Container that scrolls:** the prompt listens to `window`. If the target game scrolls inside an element instead, listen on that element and use its `scrollTop`, `scrollHeight`, and `clientHeight`.

## Checking it works

1. The prompt doesn't appear before the setup screen opens. When it opens, the prompt says "Player 1, select your character. Scroll down for more options ↓" and fades after a short scroll.
2. With 2 players, Player 1 taps a card: it gets a red border and a "Player 1 choose: …" panel with Confirm. Nothing is locked yet.
3. Tapping another card moves the panel there. Tapping a look thumbnail changes the portrait and keeps the panel.
4. Pressing Confirm fades the card, adds a "Player 1" tag, and shows "Player 2, select your character." Player 1's card no longer responds.
5. From Player 2 onward, Back to previous player shows in the top row and on the panel. Pressing it reopens Player 1's card with its panel and Confirm button.
6. Once both have confirmed, the page scrolls to the top, the prompt says "Everyone's ready! Press Play Game.", free cards don't react, and Play Game is enabled and pulsing.
7. Changing the player count clears all picks and returns to Player 1.
8. The prompt doesn't appear on the game screen.
9. At phone width the grid drops to one or two columns, the controls row wraps, and the prompt text wraps instead of running off the screen.
