"""Build one standalone test page per mini-game from the built game.

Each page is a full copy of hunter-gatherer.html that starts a 1-player game
and opens the mini-game over the board, replaying it after every Continue.
Re-run after rebuilding hunter-gatherer.html:  python3 minigame-tests/build.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = {"mammoth": "Mammoth Hunt", "river": "River Crossing", "tiger": "Saber-Tooth Attack"}
ANCHOR = "resetParty();\n</script>"

HARNESS = """resetParty();

/* ---------- Mini-game test harness ---------- */
(async () => {
  $("player-count").value = "1";
  resetParty();
  const ch = CHARACTERS[0];
  state.selectingFor = 0;
  state.draft = { roleId: ch.id, lookId: ch.looks[0].id };
  applyDraft();
  beginGame();
  await sleep(400);
  for (;;) {
    const p = state.players[0];
    await playMiniGame(%r, p);
    p.skip = 0;
    await sleep(300);
  }
})();
</script>"""

src = (ROOT / "hunter-gatherer.html").read_text(encoding="utf-8")
assert src.count(ANCHOR) == 1, "could not find end of game script"
for kind, name in GAMES.items():
    page = src.replace(ANCHOR, HARNESS % kind)
    page = page.replace("<title>", f"<title>TEST {name} – ", 1)
    out = ROOT / "minigame-tests" / f"minigame-{kind}.html"
    out.write_text(page, encoding="utf-8")
    print("wrote", out.relative_to(ROOT))
