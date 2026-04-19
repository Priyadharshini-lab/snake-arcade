# 🐍 Snake Arcade – Full Stack Web Application

A cinematic, full-stack browser Snake game with a real-time leaderboard.

```
Frontend (HTML/CSS/JS)  ──fetch──►  Backend (Flask REST API)  ──SQL──►  Database (SQLite / PostgreSQL)
```

---

## 📁 Folder Structure

```
snake-arcade/
├── frontend/
│   ├── index.html       ← Single-page game UI + leaderboard
│   └── netlify.toml     ← Netlify deploy config
│
├── backend/
│   ├── app.py           ← Flask REST API
│   ├── requirements.txt ← Python dependencies
│   └── render.yaml      ← Render deploy config
│
└── README.md
```

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🎮 Gameplay | Arrow keys / WASD / swipe / D-pad |
| 📈 Scoring | 10 pts × level; level up every 5 foods |
| 👤 Name input | Enter name before playing; reused on submit |
| 🏆 Leaderboard | Top 10 global scores, refreshed live |
| 💾 Persistent | SQLite (dev) / PostgreSQL (prod) |
| 📱 Responsive | Desktop + mobile |

---

## 🛠 Local Development

### 1 – Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# → API running at http://localhost:5000
```

### 2 – Frontend

Open `frontend/index.html` in your browser **OR** serve it:

```bash
cd frontend
python -m http.server 8080
# → http://localhost:8080
```

Edit the `API_BASE_URL` constant near the top of the `<script>` in `index.html`:

```js
const API_BASE_URL = "http://localhost:5000";
```

---

## 🌐 Deployment

### Backend → Render

1. Push the entire repo to GitHub.
2. Go to [render.com](https://render.com) → **New Web Service**.
3. Connect your GitHub repo and set the **Root Directory** to `backend`.
4. Render auto-detects `render.yaml` – click **Deploy**.
5. Copy your Render service URL, e.g. `https://snake-arcade-api.onrender.com`.

### Frontend → Netlify

1. Go to [netlify.com](https://netlify.com) → **Add new site → Import from Git**.
2. Select your GitHub repo and set the **Publish directory** to `frontend`.
3. Click **Deploy site**.
4. In `frontend/index.html`, update:

```js
const API_BASE_URL = "https://snake-arcade-api.onrender.com"; // ← your Render URL
```

5. Commit and push – Netlify rebuilds automatically.

---

## 🔌 REST API

| Method | Endpoint | Body / Params | Response |
|---|---|---|---|
| GET | `/` | – | `{ status: "ok" }` |
| POST | `/submit` | `{ name, score, level }` | `{ message, entry }` |
| GET | `/leaderboard` | `?limit=10` | `{ leaderboard: [...] }` |
| GET | `/leaderboard/:name` | – | `{ player, entries }` |

---

## 🚀 Future Enhancements

- [ ] Authentication (JWT login/signup)
- [ ] Real-time multiplayer (WebSockets)
- [ ] Sound effects
- [ ] AI difficulty scaling
- [ ] PostgreSQL via `DATABASE_URL` env var
