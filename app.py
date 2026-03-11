"""
app.py — Tambola Party  🎱
Run:  streamlit run app.py

Features:
  • Players tap/click ticket cells to manually mark called numbers
  • Host browser announces each number TWICE via Web Speech API
  • Server-side prize validation (cheat-proof)
"""

import streamlit as st
import streamlit.components.v1 as components
import uuid
from streamlit_autorefresh import st_autorefresh

import db, game

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tambola Party 🎱",
    page_icon="🎱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Nunito:wght@600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: #08061a; color: #e8e0f8; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 860px; }
h1,h2,h3 { font-family: 'Cinzel', serif !important; color: #f5a623 !important; }

.tambola-card {
    background: #110e28; border: 1px solid rgba(245,166,35,.25);
    border-radius: 18px; padding: 28px; margin-bottom: 16px;
    box-shadow: 0 0 50px rgba(245,166,35,.05), 0 16px 32px rgba(0,0,0,.4);
}
.code-box {
    background: #0a0815; border: 2px solid #f5a623; border-radius: 14px;
    padding: 20px; text-align: center; margin: 12px 0;
    box-shadow: 0 0 30px rgba(245,166,35,.12);
}
.code-value {
    font-family: 'Cinzel', serif; font-size: 3rem; font-weight: 900;
    color: #f5a623; letter-spacing: 12px; text-shadow: 0 0 24px rgba(245,166,35,.45);
}
.code-hint { color: #5550a0; font-size: 0.8rem; margin-top: 4px; }
.num-display {
    font-family: 'Cinzel', serif; font-size: 5rem; font-weight: 900;
    color: #f5a623; text-align: center; text-shadow: 0 0 40px rgba(245,166,35,.55);
    line-height: 1; padding: 10px 0;
}
.num-label    { color: #5550a0; font-size: .75rem; letter-spacing: 2px; text-transform: uppercase; text-align: center; }
.num-progress { color: #5550a0; font-size: .8rem; text-align: center; margin-top: 4px; }

/* Ticket cell buttons are styled via JavaScript injection in render_interactive_ticket */

.numboard { display:grid; grid-template-columns:repeat(10,1fr); gap:4px; background:#110e28; border:1px solid rgba(245,166,35,.18); border-radius:12px; padding:10px; }
.n-chip     { aspect-ratio:1; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:clamp(8px,1.5vw,11px); font-weight:700; }
.n-uncalled { background:rgba(255,255,255,.04); color:#4a4480; }
.n-called   { background:#f5a623; color:#1a0800; box-shadow:0 0 8px rgba(245,166,35,.35); }

.prize-row   { display:flex; align-items:center; gap:12px; background:#13102a; border:1px solid #2a2445; border-radius:10px; padding:10px 14px; margin-bottom:7px; transition:all .2s; }
.prize-won   { border-color:#2ecc71!important; background:rgba(46,204,113,.07)!important; }
.prize-claim { border-color:#f5a623!important; background:rgba(245,166,35,.1)!important; }
.prize-emoji { font-size:1.4rem; }
.prize-name  { font-weight:800; font-size:.95rem; }
.prize-desc  { font-size:.75rem; color:#5550a0; }
.prize-winner{ margin-left:auto; color:#2ecc71; font-size:.8rem; font-weight:700; white-space:nowrap; }
.prize-tag   { margin-left:auto; background:rgba(245,166,35,.15); color:#f5a623; border-radius:6px; padding:2px 9px; font-size:.75rem; font-weight:700; }

.player-chip   { display:flex; align-items:center; gap:10px; background:#13102a; border:1px solid #2a2445; border-radius:10px; padding:9px 14px; margin-bottom:6px; }
.player-avatar { width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#9b59b6,#3498db); display:flex; align-items:center; justify-content:center; font-size:.9rem; font-weight:900; color:#fff; flex-shrink:0; }

.section-label { font-size:.7rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#4a4480; margin-bottom:8px; margin-top:4px; }
.winner-row    { display:flex; align-items:center; gap:12px; background:#1a1530; border:1px solid rgba(46,204,113,.3); border-radius:12px; padding:12px 16px; margin-bottom:8px; }
.ticket-hint   { font-size:.7rem; color:#5550a0; text-align:center; margin-top:4px; }
.speech-badge  { display:inline-flex; align-items:center; gap:5px; background:rgba(46,204,113,.12); border:1px solid #2ecc71; border-radius:6px; padding:3px 9px; font-size:.7rem; font-weight:700; color:#2ecc71; }

div.stButton > button { font-family:'Nunito',sans-serif!important; font-weight:800!important; border-radius:12px!important; transition:all .15s!important; }
.stTextInput > div > div > input { background:#0a0815!important; border:1.5px solid rgba(245,166,35,.25)!important; border-radius:12px!important; color:#e8e0f8!important; font-family:'Nunito',sans-serif!important; font-weight:700!important; }
.stTextInput > div > div > input:focus { border-color:#f5a623!important; box-shadow:0 0 0 2px rgba(245,166,35,.15)!important; }
hr { border-color:rgba(245,166,35,.12)!important; }
.stAlert { border-radius:12px!important; }

/* ── Mobile responsive ── */
@media (max-width: 640px) {
    .block-container { padding-left: 0.6rem !important; padding-right: 0.6rem !important; padding-top: 1rem !important; }
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.4rem !important; }
    .num-display { font-size: 3rem !important; }
    .code-value  { font-size: 2rem !important; letter-spacing: 6px !important; }
    .tambola-card { padding: 16px !important; border-radius: 12px !important; }
    .code-box { padding: 14px !important; }
    .numboard { gap: 3px !important; padding: 7px !important; }
    .n-chip   { font-size: clamp(9px, 2.8vw, 12px) !important; }

    /* Stack all column layouts vertically.
       Ticket rows (9 cols) are restored to horizontal by the JS tighten() call. */
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 6px !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: 100% !important;
        flex: none !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* Full-width buttons on mobile */
    div.stButton > button { width: 100% !important; }

    /* Prize row: wrap long winner names */
    .prize-winner { white-space: normal !important; font-size: .75rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
def _init():
    for k, v in {
        "player_id":       str(uuid.uuid4())[:8],
        "screen":          "home",
        "room_code":       "",
        "player_name":     "",
        "is_host":         False,
        "marked_numbers":  set(),
        "last_spoken_num": None,
        "speech_enabled":  True,
        "ticket_fs":       False,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()
ss = st.session_state


# ── Speech helper ──────────────────────────────────────────────────────────────
def announce_number(num, enabled: bool = True):
    """Speak the number twice via browser Web Speech API (host device only)."""
    if not enabled or num is None or ss.last_spoken_num == num:
        return
    ss.last_spoken_num = num
    components.html(f"""
    <script>
    (function() {{
        window.speechSynthesis.cancel();
        function say(text, onDone) {{
            var u = new SpeechSynthesisUtterance(text);
            u.lang = 'en-IN'; u.rate = 0.78; u.pitch = 1.05; u.volume = 1.0;
            if (onDone) u.onend = onDone;
            window.speechSynthesis.speak(u);
        }}
        // Say "Number X" then after a pause say "X" again
        say("Number {num}", function() {{
            setTimeout(function() {{ say("{num}"); }}, 650);
        }});
    }})();
    </script>
    """, height=0)


# ── Helpers ────────────────────────────────────────────────────────────────────
def go(screen):
    ss.screen = screen; st.rerun()

def room():
    return db.load_room(ss.room_code) if ss.room_code else None

def save(r):
    db.save_room(r["code"], r)


# ── Interactive ticket ─────────────────────────────────────────────────────────
def render_interactive_ticket(grid, called_set: set, marked_set: set, pid: str):
    corners = set(game.corner_numbers(grid))
    marked_cnt = len(marked_set)
    called_on_ticket = sum(1 for n in game.all_numbers(grid) if n in called_set)

    # ── Ticket header ────────────────────────────────────────────────────────────
    col_headers = "".join(
        f'<div style="text-align:center;font-size:9px;color:#4a4080;font-weight:700;padding:2px 0">{h}</div>'
        for h in ["1–9","10–19","20–29","30–39","40–49","50–59","60–69","70–79","80–90"]
    )
    st.markdown(f"""
    <div style="border:2px solid #f5a623;border-radius:14px;overflow:hidden;margin:8px 0 4px">
      <div style="background:linear-gradient(90deg,#f5a623,#e84545);padding:8px 16px;
                  display:flex;justify-content:space-between;align-items:center;
                  font-weight:800;font-size:.85rem;color:#1a0800;">
        <span>🎟 MY TICKET</span>
        <span>✅ {marked_cnt} marked &nbsp;|&nbsp; 📢 {called_on_ticket} called</span>
      </div>
      <div style="background:#0d0a20;padding:4px 6px 2px;
                  display:grid;grid-template-columns:repeat(9,1fr);gap:3px">
        {col_headers}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Per-button CSS using Streamlit's automatic st-key-{key} class ───────────
    # Streamlit adds class="... st-key-{key} ..." to every keyed widget's container,
    # so [class*="st-key-tc_..."] button reliably targets exactly that button.
    BASE = ("width:100%!important;padding:0!important;min-height:48px!important;"
            "font-size:clamp(10px,2.8vw,15px)!important;font-weight:800!important;"
            "border-radius:6px!important;white-space:nowrap!important;"
            "overflow:hidden!important;line-height:1!important;")
    css = []
    for ri, row in enumerate(grid):
        for ci, num in enumerate(row):
            k = f"tc_{pid}_{ri}_{ci}"
            sel = f'[class*="st-key-{k}"] button'
            is_corner = num in corners
            if num == 0:
                color = "background:#06040f!important;border:1px solid rgba(255,255,255,.04)!important;color:transparent!important;pointer-events:none!important;cursor:default!important;"
            elif num in marked_set:
                ex = "outline:2px solid #f5a623!important;outline-offset:-3px!important;" if is_corner else ""
                color = f"background:#2ecc71!important;border:2px solid #27ae60!important;color:#fff!important;box-shadow:0 0 10px rgba(46,204,113,.5)!important;{ex}"
            elif num in called_set:
                color = "background:#1e1a40!important;border:2px solid #f5a623!important;color:#f5a623!important;cursor:pointer!important;"
            else:
                color = "background:#13102a!important;border:1px solid rgba(255,255,255,.07)!important;color:#5050a0!important;cursor:not-allowed!important;"
            css.append(f"{sel}{{{BASE}{color}}}")
    st.markdown(f"<style>{''.join(css)}</style>", unsafe_allow_html=True)

    # ── Button rows ──────────────────────────────────────────────────────────────
    for ri, row in enumerate(grid):
        cols = st.columns(9, gap="small")
        for ci, num in enumerate(row):
            with cols[ci]:
                if num == 0:
                    st.button(" ", key=f"tc_{pid}_{ri}_{ci}", disabled=True)
                elif num in marked_set:
                    if st.button(str(num), key=f"tc_{pid}_{ri}_{ci}"):
                        ss.marked_numbers.discard(num); st.rerun()
                elif num in called_set:
                    if st.button(str(num), key=f"tc_{pid}_{ri}_{ci}"):
                        ss.marked_numbers.add(num); st.rerun()
                else:
                    st.button(str(num), key=f"tc_{pid}_{ri}_{ci}", disabled=True)

    st.markdown('<p class="ticket-hint">💡 <b style="color:#f5a623">Gold border</b> = tap to mark &nbsp;·&nbsp; <b style="color:#2ecc71">Green</b> = tap to unmark &nbsp;·&nbsp; Dim = not called yet</p>', unsafe_allow_html=True)

    # ── JS: tighten column gaps only (styling is handled by CSS above) ───────────
    components.html("""<script>
    (function(){
        try {
            var doc = window.parent.document;
            function tighten(){
                doc.querySelectorAll('[data-testid="stHorizontalBlock"]').forEach(function(blk){
                    var cols = blk.querySelectorAll(':scope>[data-testid="column"]');
                    if(cols.length !== 9) return;
                    /* Override the mobile flex-direction:column rule for ticket rows */
                    blk.style.flexDirection = 'row';
                    blk.style.flexWrap = 'nowrap';
                    blk.style.gap = '3px';
                    blk.style.padding = '0 4px 4px';
                    cols.forEach(function(c){
                        c.style.paddingLeft='1px'; c.style.paddingRight='1px';
                        c.style.minWidth='0'; c.style.width='auto'; c.style.flex='1';
                    });
                });
            }
            tighten(); setTimeout(tighten,300); setTimeout(tighten,800);
        } catch(e) {}
    })();
    </script>""", height=0)


def render_number_board(called_nums):
    called_set = set(called_nums)
    chips = "".join(
        f'<div class="n-chip {"n-called" if n in called_set else "n-uncalled"}">{n}</div>'
        for n in range(1, 91)
    )
    st.markdown(f'<div class="numboard">{chips}</div>', unsafe_allow_html=True)


def render_prizes(awarded, claimable_ids=None, show_claim_btn=False):
    for pid, emoji, name, desc in game.PRIZES:
        won = pid in awarded
        can = claimable_ids and pid in claimable_ids
        cls = "prize-row" + (" prize-won" if won else " prize-claim" if can else "")
        right = (f'<span class="prize-winner">🏅 {awarded[pid]}</span>' if won
                 else '<span class="prize-tag">CLAIM!</span>' if can else "")
        st.markdown(f'<div class="{cls}"><span class="prize-emoji">{emoji}</span><div><div class="prize-name">{name}</div><div class="prize-desc">{desc}</div></div>{right}</div>', unsafe_allow_html=True)
        if show_claim_btn and can:
            if st.button(f"🎉 Claim {name}!", key=f"claim_{pid}", use_container_width=True, type="primary"):
                r = room()
                if r and r["game_state"] == "playing" and pid not in r["awarded_prizes"]:
                    grid = r["tickets"].get(ss.player_id)
                    if grid and game.check_prize(pid, grid, set(r["called_numbers"])):
                        r["awarded_prizes"][pid] = ss.player_name
                        r["winners"].append({"player_name": ss.player_name, "prize_id": pid})
                        if len(r["awarded_prizes"]) >= len(game.PRIZE_IDS):
                            r["game_state"] = "over"
                        save(r); st.rerun()
                    else:
                        st.error("❌ Bogie! Numbers haven't all been called yet.")


def render_players(players, my_id=""):
    for p in players:
        badge = " &nbsp;<b style='color:#f5a623'>← You</b>" if p["id"] == my_id else ""
        st.markdown(f'<div class="player-chip"><div class="player-avatar">{p["name"][0].upper()}</div><span style="font-weight:700">{p["name"]}{badge}</span><span style="margin-left:auto;color:#2ecc71;font-size:.8rem;font-weight:700">✓ Ready</span></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCREENS
# ══════════════════════════════════════════════════════════════════════════════

# HOME
if ss.screen == "home":
    st.markdown('<div style="text-align:center;padding:20px 0 10px"><div style="font-size:5rem">🎱</div><h1 style="font-size:2.8rem;margin:8px 0 4px">Tambola Party</h1><p style="color:#5550a0;font-size:1rem;margin-bottom:32px">Play Housie with friends — tap to mark your numbers!</p></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown('<div class="tambola-card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown("### 🎙️ Host")
        st.caption("Create a room — browser announces each number twice via speaker.")
        if st.button("Host a Game", use_container_width=True, type="primary"): go("host_setup")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="tambola-card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown("### 🎟️ Join")
        st.caption("Get your ticket and tap numbers as the host calls them out.")
        if st.button("Join a Game", use_container_width=True): go("join")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#3a3460;font-size:.8rem;margin-top:24px">🔊 Numbers announced twice on host · 👆 Tap to mark · ✅ Server-side validation</p>', unsafe_allow_html=True)


# HOST SETUP
elif ss.screen == "host_setup":
    st.markdown('<div class="tambola-card">', unsafe_allow_html=True)
    st.markdown("## 🎙️ Host a Game")
    st.caption("Keep your device volume UP — the app will announce each number twice through your speaker.")
    st.divider()
    name = st.text_input("Your Name", placeholder="e.g. Priya", max_chars=30)
    c1, c2 = st.columns([2, 1])
    with c1:
        if st.button("✨ Create Room", use_container_width=True, type="primary", disabled=not name.strip()):
            code = db.gen_code()
            r = game.new_room(code, name.strip())
            db.save_room(code, r)
            ss.room_code = code; ss.player_name = name.strip()
            ss.is_host = True; ss.last_spoken_num = None
            go("host_lobby")
    with c2:
        if st.button("← Back", use_container_width=True): go("home")
    st.markdown('</div>', unsafe_allow_html=True)


# HOST LOBBY
elif ss.screen == "host_lobby":
    st_autorefresh(interval=1500, key="hlr")
    r = room()
    if not r: st.error("Room not found."); go("home")
    st.markdown("## 🎉 Waiting Room")
    st.markdown(f'<div class="code-box"><div class="section-label">Share this code with players</div><div class="code-value">{r["code"]}</div><div class="code-hint">They open this app and click "Join a Game"</div></div>', unsafe_allow_html=True)
    st.code(r["code"], language=None)
    st.divider()
    st.markdown('<div class="section-label">Active Prizes</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (pid, emoji, name, desc) in enumerate(game.PRIZES):
        with cols[i % 2]:
            st.markdown(f'<div class="prize-row" style="margin-bottom:6px"><span class="prize-emoji">{emoji}</span><div><div class="prize-name">{name}</div><div class="prize-desc">{desc}</div></div></div>', unsafe_allow_html=True)
    st.divider()
    players = r.get("players", [])
    st.markdown(f'<div class="section-label">Players Joined ({len(players)})</div>', unsafe_allow_html=True)
    if players: render_players(players)
    else: st.info("Waiting for players… share the code above!")
    st.divider()
    c1, c2 = st.columns([3, 1])
    with c1:
        if st.button(f"▶ Start Game ({len(players)} player{'s' if len(players)!=1 else ''})",
                     use_container_width=True, type="primary", disabled=len(players)==0):
            r = room(); r["game_state"] = "playing"
            r["tickets"] = {p["id"]: game.generate_ticket() for p in r["players"]}
            save(r); go("host_game")
    with c2:
        if st.button("🗑 End", use_container_width=True):
            db.delete_room(ss.room_code); ss.room_code = ""; go("home")


# HOST GAME
elif ss.screen == "host_game":
    st_autorefresh(interval=1200, key="hgr")
    r = room()
    if not r: st.error("Room ended."); go("home")
    if r["game_state"] == "over": go("over")

    called = r["called_numbers"]
    current_num = called[-1] if called else None

    # ── Announce number twice ──────────────────────────────────────────────────
    announce_number(current_num, enabled=ss.speech_enabled)

    st.markdown("## 🎙️ Caller Board")

    # Speech toggle in top-right
    _, col_tog = st.columns([4, 1])
    with col_tog:
        ss.speech_enabled = st.toggle("🔊", value=ss.speech_enabled,
                                      help="Announce each number twice through your device speaker")

    speech_badge = '<span class="speech-badge">🔊 Announced twice</span>' if (ss.speech_enabled and current_num) else ""
    st.markdown(f"""
    <div class="tambola-card" style="text-align:center;padding:24px">
        <div class="num-label">Current Number</div>
        <div class="num-display">{current_num if current_num else "—"}</div>
        <div class="num-progress">
            {len(called)} of 90 called &nbsp;·&nbsp; {len(r['number_bag'])} remaining
            {"&nbsp;&nbsp;" + speech_badge if speech_badge else ""}
        </div>
    </div>""", unsafe_allow_html=True)

    # Last 5 numbers strip
    if len(called) > 1:
        prev = " &nbsp;·&nbsp; ".join(f'<span style="color:#6660a0">{n}</span>' for n in reversed(called[-6:-1]))
        st.markdown(f'<p style="text-align:center;font-size:.8rem;color:#4a4480">Previous: {prev}</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c1:
        label = "Call First Number 🎲" if not called else "Call Next Number 🎲"
        all_done = len(r["awarded_prizes"]) >= len(game.PRIZE_IDS)
        if st.button(label, use_container_width=True, type="primary", disabled=len(called)>=90 or all_done):
            r = room()
            if r["number_bag"]:
                n = r["number_bag"].pop(); r["called_numbers"].append(n); save(r); st.rerun()
    with c2:
        if st.button("🏁 End Game", use_container_width=True):
            r = room(); r["game_state"] = "over"; save(r); go("over")

    st.divider()
    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown('<div class="section-label">Players</div>', unsafe_allow_html=True)
        for p in r["players"]:
            st.markdown(f'<div class="player-chip"><div class="player-avatar">{p["name"][0].upper()}</div><span style="font-weight:700">{p["name"]}</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label" style="margin-top:14px">Called Numbers</div>', unsafe_allow_html=True)
        render_number_board(called)
    with right:
        st.markdown('<div class="section-label">Prizes</div>', unsafe_allow_html=True)
        render_prizes(r["awarded_prizes"])


# PLAYER JOIN
elif ss.screen == "join":
    st.markdown('<div class="tambola-card">', unsafe_allow_html=True)
    st.markdown("## 🎟️ Join a Game")
    st.caption("Ask the host for the 6-letter room code.")
    st.divider()
    name = st.text_input("Your Name", placeholder="e.g. Rahul", max_chars=30)
    code = st.text_input("Room Code", placeholder="e.g. TK4RXZ", max_chars=6).strip().upper()
    c1, c2 = st.columns([2, 1])
    with c1:
        if st.button("🚀 Join Game", use_container_width=True, type="primary",
                     disabled=not name.strip() or len(code)<6):
            r = db.load_room(code)
            if not r: st.error("❌ Room not found. Check the code.")
            elif r["game_state"] != "lobby": st.error("⚠️ Game already started!")
            else:
                if not any(p["id"] == ss.player_id for p in r["players"]):
                    r["players"].append({"id": ss.player_id, "name": name.strip()})
                    db.save_room(code, r)
                ss.room_code = code; ss.player_name = name.strip()
                ss.is_host = False; ss.marked_numbers = set()
                go("lobby")
    with c2:
        if st.button("← Back", use_container_width=True): go("home")
    st.markdown('</div>', unsafe_allow_html=True)


# PLAYER LOBBY
elif ss.screen == "lobby":
    st_autorefresh(interval=1500, key="plr")
    r = room()
    if not r: st.error("Room not found."); go("home")
    if r["game_state"] == "playing": ss.marked_numbers = set(); go("game")
    players = r["players"]
    st.markdown("## 🎉 You're In!")
    st.markdown(f"<p style='color:#6660a0'>Waiting for <b style='color:#f5a623'>{r['host_name']}</b> to start…</p>", unsafe_allow_html=True)
    st.markdown(f'<div class="code-box"><div class="section-label">Room Code</div><div class="code-value" style="font-size:2rem;letter-spacing:8px">{r["code"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">Players ({len(players)})</div>', unsafe_allow_html=True)
    render_players(players, ss.player_id)
    st.info("⏳ Waiting for host to start… auto-refreshes every 1.5s")
    if st.button("← Leave Room"):
        r = room(); r["players"] = [p for p in r["players"] if p["id"] != ss.player_id]
        save(r); ss.room_code = ""; go("home")


# PLAYER GAME
elif ss.screen == "game":
    st_autorefresh(interval=1200, key="pgr")
    r = room()
    if not r: st.error("Room ended."); go("home")
    if r["game_state"] == "over": go("over")

    called     = r["called_numbers"]
    called_set = set(called)
    awarded    = r["awarded_prizes"]
    grid       = r["tickets"].get(ss.player_id)
    current_num = called[-1] if called else None

    # Keep marked_numbers as a proper set
    if not isinstance(ss.marked_numbers, set):
        ss.marked_numbers = set(ss.marked_numbers)
    ss.marked_numbers &= called_set   # remove any invalid marks
    marked_set = ss.marked_numbers

    st.markdown(f"## 🎱 {ss.player_name}'s Ticket")

    st.markdown(f"""
    <div class="tambola-card" style="text-align:center;padding:20px">
        <div class="num-label">Current Number</div>
        <div class="num-display">{current_num if current_num else "—"}</div>
        <div class="num-progress">{len(called)} of 90 called</div>
    </div>""", unsafe_allow_html=True)

    # Alert if new number is on their ticket and not yet marked
    if current_num and grid:
        ticket_nums = [n for row in grid for n in row if n > 0]
        if current_num in ticket_nums and current_num not in marked_set:
            st.success(f"🎯 **{current_num}** is on your ticket! Tap it to mark.")

    claimable = game.claimable_prizes(grid, marked_set, awarded) if grid else []

    if ss.ticket_fs:
        # ── Fullscreen ticket ─────────────────────────────────────────────────
        st.markdown("""<style>
        div[data-testid="column"] div.stButton > button {
            min-height: 68px !important;
            font-size: clamp(16px, 4vw, 26px) !important;
        }
        </style>""", unsafe_allow_html=True)
        _, exit_col = st.columns([5, 1])
        with exit_col:
            if st.button("Collapse", use_container_width=True, key="exit_fs"):
                ss.ticket_fs = False; st.rerun()
        if grid:
            render_interactive_ticket(grid, called_set, marked_set, ss.player_id)
        if claimable:
            st.success(f"🎉 You can claim **{len(claimable)}** prize(s)!")
            render_prizes(awarded, claimable_ids=claimable, show_claim_btn=True)
        with st.expander("Number Board"):
            render_number_board(called)
        with st.expander("Prizes"):
            render_prizes(awarded, claimable_ids=claimable, show_claim_btn=True)
    else:
        # ── Normal split view ─────────────────────────────────────────────────
        left, right = st.columns([1, 1], gap="medium")
        with left:
            if grid:
                _, fs_col = st.columns([5, 1])
                with fs_col:
                    if st.button("Expand", key="enter_fs",
                                 use_container_width=True):
                        ss.ticket_fs = True; st.rerun()
                render_interactive_ticket(grid, called_set, marked_set, ss.player_id)
            st.markdown('<div class="section-label" style="margin-top:12px">Number Board</div>', unsafe_allow_html=True)
            render_number_board(called)
        with right:
            if claimable:
                st.success(f"🎉 You can claim **{len(claimable)}** prize(s)! Tap below.")
            elif grid:
                total = len([n for row in grid for n in row if n > 0])
                st.markdown(f'<p style="color:#5550a0;font-size:.85rem">Marked {len(marked_set)} / {total} numbers</p>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Prizes</div>', unsafe_allow_html=True)
            render_prizes(awarded, claimable_ids=claimable, show_claim_btn=True)


# GAME OVER
elif ss.screen == "over":
    r = room()
    winners = r["winners"] if r else []
    st.markdown('<div style="text-align:center;padding:16px 0"><div style="font-size:5rem">🏆</div><h1 style="font-size:2.5rem;margin:8px 0 4px">Game Over!</h1><p style="color:#5550a0;margin-bottom:24px">Here are the winners</p></div>', unsafe_allow_html=True)
    for w in winners:
        m = game.PRIZE_MAP.get(w["prize_id"], {})
        st.markdown(f'<div class="winner-row"><span style="font-size:1.8rem">{m.get("emoji","🏆")}</span><div><div style="color:#f5a623;font-weight:700;font-size:.85rem">{m.get("name","Prize")}</div><div style="font-weight:800;font-size:1.1rem">{w["player_name"]}</div></div></div>', unsafe_allow_html=True)
    if not winners:
        st.info("No prizes were claimed this round.")
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
            if ss.is_host and ss.room_code: db.delete_room(ss.room_code)
            ss.room_code = ""; go("home")
    with c2:
        if ss.is_host and st.button("🔁 New Round (same players)", use_container_width=True):
            r = room()
            if r:
                import random
                r.update({"game_state":"lobby","called_numbers":[],"awarded_prizes":{},"winners":[],"tickets":{}})
                r["number_bag"] = list(range(1, 91)); random.shuffle(r["number_bag"])
                save(r); ss.marked_numbers = set(); ss.last_spoken_num = None; go("host_lobby")

else:
    go("home")
