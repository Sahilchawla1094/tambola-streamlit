# 🎱 Tambola Party — Streamlit App

Multiplayer Tambola (Housie / Indian Bingo) built with Python + Streamlit.
Play with friends over the same Wi-Fi **or** over the internet.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py

# 3. Open in browser
#    → http://localhost:8501
```

---

## 🎮 How to Play

### Host
1. Open `http://localhost:8501` → click **Host a Game**
2. Enter your name → **Create Room**
3. Share the **6-letter code** (e.g. `TK4RXZ`) with all players
4. Wait for players to join → click **▶ Start Game**
5. Click **Call Next Number 🎲** to draw numbers
6. The app auto-detects all claims — winners are validated server-side!

### Players
1. Open `http://<host-ip>:8501` → click **Join a Game**
2. Enter your name + the **room code**
3. Wait for the host to start — your ticket appears automatically
4. Watch for green numbers on your ticket
5. When a prize completes → click **🎉 Claim [Prize Name]!**

> **Sharing over the internet?**
> Run with `streamlit run app.py --server.address 0.0.0.0`
> then use a tunnel like [ngrok](https://ngrok.com): `ngrok http 8501`

---

## 🏆 Prizes

| Prize | Rule |
|---|---|
| 🏃 Early Five | First to mark any 5 numbers |
| 🔝 Top Line | All 5 in the top row |
| ➡️ Middle Line | All 5 in the middle row |
| ⬇️ Bottom Line | All 5 in the bottom row |
| 🔲 Four Corners | All 4 corner numbers |
| 🏠 Full House | All 15 numbers — Grand Prize! |

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| Language | Python 3.10+ |
| Framework | Streamlit |
| Realtime sync | `streamlit-autorefresh` (polls every 1.2s) |
| Shared state | SQLite (`tambola.db`) — all sessions share one DB |
| Ticket gen | Pure Python (valid 3×9 Tambola layout) |
| Prize check | Server-side validation (no cheating) |

---

## 📁 Project Structure

```
tambola-streamlit/
├── app.py              # Main Streamlit app (all screens)
├── game.py             # Ticket generator + prize logic
├── db.py               # SQLite shared state layer
├── requirements.txt    # streamlit + streamlit-autorefresh
├── .streamlit/
│   └── config.toml     # Dark theme + server config
└── tambola.db          # Auto-created on first run
```

---

## 🌐 Deploying Online (Free)

### Streamlit Community Cloud (easiest)
1. Push this folder to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → deploy!
4. Share the generated URL with friends

### Railway / Render
```bash
# Procfile (create this file)
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

## ⚠️ Notes

- `tambola.db` is created automatically in the project folder on first run
- The SQLite DB persists between runs — old rooms stay until the host ends them
- For production, replace SQLite with PostgreSQL (e.g. via `psycopg2`)
- Auto-refresh polls every 1.2 seconds — works great on LAN; fine over internet too
