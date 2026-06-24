# F1 Race Prediction System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-FF6600.svg)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)

ML-powered Formula 1 race outcome predictions with a real-time React dashboard and a modular FastAPI backend.

---

## Features

- **Race Prediction** — predict finish positions, win probability, and podium probability for any driver/track/grid combination
- **Batch Prediction** — predict a full grid in one request, sorted by predicted finishing order
- **Three ML Models** — Random Forest, XGBoost, and Gradient Boosting trained and compared on every startup; best model is selected automatically
- **Feature Importance** — ranked breakdown of which factors drive predictions
- **Live Dashboard** — React frontend with a timing-tower layout, podium visualization, standings, and model tab; automatically switches between live API data and demo data
- **Modular API** — clean router-per-concern FastAPI structure with dependency injection
- **Docker ready** — single `docker compose up` starts the full stack

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| ML models | scikit-learn (Random Forest, Gradient Boosting), XGBoost |
| Data processing | Pandas, NumPy |
| Frontend | React 18 (no extra UI libraries) |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
f1-race-prediction/
│
├── src/
│   ├── config.py                ← all settings, env-var overridable
│   ├── api/
│   │   ├── main.py              ← FastAPI app entry point
│   │   ├── schemas.py           ← Pydantic request / response models
│   │   ├── dependencies.py      ← shared get_pipeline() dependency
│   │   └── routers/
│   │       ├── info.py          ← GET /  · /health  · /info
│   │       ├── data.py          ← GET /drivers  · /tracks  · /teams
│   │       ├── models.py        ← GET /models  · /models/features  · POST /models/train
│   │       └── predict.py       ← GET /predict/latest  · POST /predict  · /predict/batch
│   │
│   ├── data/
│   │   ├── data_loader.py       ← loads / generates race data
│   │   └── feature_engineer.py  ← feature engineering + label encoding
│   │
│   ├── models/
│   │   ├── train_models.py      ← Random Forest · XGBoost · Gradient Boosting
│   │   └── pipeline.py          ← training orchestration + inference helpers
│   │
│   └── utils/
│       └── helpers.py           ← get_logger() · @timed() decorator
│
├── artifacts/                   ← saved model artifacts (.pkl)
├── dataset/                     ← raw data files
├── dashboard/                   ← React frontend
│   └── src/
│       ├── App.jsx              ← full app (styles + data layer inline)
│       └── index.js
├── notebooks/
│   └── f1_analysis.ipynb
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### 1. Clone & set up Python environment

```bash
git clone https://github.com/DeepTaha/f1-race-prediction.git
cd f1-race-prediction

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Install frontend dependencies

```bash
cd dashboard
npm install
cd ..
```

### 3. Create the frontend environment file

```bash
# dashboard/.env
echo REACT_APP_API_URL=http://localhost:8000 > dashboard/.env
```

### 4. Run

Open two terminals from the project root:

**Terminal 1 — API**
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Dashboard**
```bash
cd dashboard
npm start
```

| Service | URL |
|---|---|
| React dashboard | http://localhost:3000 |
| FastAPI backend | http://localhost:8000 |
| Swagger UI (API docs) | http://localhost:8000/docs |

Models are trained automatically on API startup — no separate training step needed.

---

## Docker

```bash
docker compose up --build
```

Starts both services. The API is available on `:8000`, the dashboard on `:3000`.

---

## API Reference

### Info

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | API name, version, status |
| `GET` | `/health` | Health check + training status |
| `GET` | `/info` | Model metadata (accuracy, features, version) |

### Data

| Method | Path | Description |
|---|---|---|
| `GET` | `/drivers` | List of available drivers |
| `GET` | `/tracks` | List of available tracks |
| `GET` | `/teams` | List of available teams |

### Models

| Method | Path | Description |
|---|---|---|
| `GET` | `/models` | Per-model accuracy scores |
| `GET` | `/models/features` | Feature importances ranked by weight |
| `POST` | `/models/train` | Retrain all models and hot-swap the active pipeline |

### Prediction

| Method | Path | Description |
|---|---|---|
| `GET` | `/predict/latest` | Full-grid prediction for the default race (Abu Dhabi GP 2025) |
| `POST` | `/predict` | Single driver prediction |
| `POST` | `/predict/batch` | Full-grid prediction for any race + driver list |

#### POST /predict — request

```json
{
  "driver": "Verstappen",
  "team": "Red Bull",
  "track": "Monza",
  "grid_position": 1,
  "weather": "Dry",
  "temperature": 25
}
```

#### POST /predict — response

```json
{
  "driver": "Verstappen",
  "team": "Red Bull",
  "track": "Monza",
  "grid_position": 1,
  "predicted_position": 3,
  "win_probability": 0.0276,
  "podium_probability": 0.4362,
  "model_used": "Gradient Boosting",
  "timestamp": "2026-06-24T05:13:55.145900"
}
```

---

## ML Models

Three classifiers are trained on every startup and the best-performing one is used for all predictions.

| Model | Notes |
|---|---|
| Random Forest | 100 estimators, parallel fit |
| XGBoost | 100 estimators, learning rate 0.1, max depth 5 |
| Gradient Boosting | 100 estimators (scikit-learn) |

> **Note on accuracy:** the current dataset is synthetically generated (300 random races). Accuracy figures are low by design — plugging in real FastF1 historical data will substantially improve them. The pipeline is identical either way.

### Features used

| Feature | Description |
|---|---|
| `grid_position` | Starting position |
| `recent_form` | Rolling 5-race average finish position |
| `driver_win_rate` | Historical win rate |
| `driver_track_avg` | Driver's average finish at this track |
| `team_track_avg` | Team's average finish at this track |
| `quali_strength` | Driver's average qualifying position |
| `dnf_rate` | Historical DNF rate |
| `weather_encoded` | Dry / Wet |
| `temperature` | Track temperature (°C) |

---

## Configuration

All settings live in `src/config.py` and can be overridden with environment variables:

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | API bind host |
| `PORT` | `8000` | API port |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `ARTIFACTS_DIR` | `artifacts` | Path for saved model files |
| `DATASET_DIR` | `dataset` | Path for data files |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |
| `RF_N_ESTIMATORS` | `100` | Random Forest tree count |
| `XGB_N_ESTIMATORS` | `100` | XGBoost estimator count |
| `TEST_SIZE` | `0.2` | Train/test split ratio |

---

## Roadmap

- [ ] Integrate real FastF1 historical data (2018–2025)
- [ ] Add live qualifying data ingestion before race weekends
- [ ] Lap-by-lap race simulation mode
- [ ] Driver comparison view in the dashboard
- [ ] Real-time weather API integration
- [ ] LightGBM model + ensemble stacking
- [ ] Cloud deployment (AWS / GCP)

---

## Author

**DeepTaha** — [@DeepTaha](https://github.com/DeepTaha)
