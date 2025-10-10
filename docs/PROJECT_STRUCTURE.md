# Project Structure

## Root Directory
```
unified-ids-and-iot-security-system/
├── src/                          # Source code
│   ├── api/                      # FastAPI backend
│   │   ├── main.py              # API entry point with CORS
│   │   └── endpoints.py         # API route handlers
│   ├── data_processing/         # Data processing modules
│   │   ├── data_loader.py       # Load and process data
│   │   ├── feature_engineer.py  # CICIDS feature engineering
│   │   └── preprocessor.py      # Data preprocessing
│   ├── frontend/                # React dashboard
│   │   ├── src/
│   │   │   ├── App.jsx          # Main app component
│   │   │   ├── components/      # React components
│   │   │   │   ├── Alerts.jsx   # Alert display
│   │   │   │   └── Flows.jsx    # Network flows
│   │   │   └── main.jsx         # Entry point
│   │   ├── package.json         # Frontend dependencies
│   │   └── vite.config.js       # Vite configuration
│   ├── iot_security/            # IoT security modules
│   │   ├── device_profiler.py   # Device profiling
│   │   └── mqtt_security.py     # MQTT security
│   ├── models/                  # ML models
│   │   ├── model_utils.py       # Model utilities
│   │   ├── predict.py           # Prediction logic
│   │   └── train.py             # Training logic
│   ├── network/                 # Network monitoring
│   │   ├── packet_sniffer.py    # Packet capture
│   │   └── traffic_analyzer.py  # Traffic analysis & ML
│   └── utils/                   # Utility modules
│       ├── alert_manager.py     # Alert management
│       ├── config_loader.py     # Configuration
│       ├── helpers.py           # Helper functions
│       ├── notification_service.py  # Email/SMS alerts
│       ├── response_actions.py  # Automated responses
│       └── statistics_tracker.py    # Statistics tracking
│
├── notebooks/                   # Jupyter notebooks for ML development
│   ├── 01_data_consolidation_and_label_engineering.ipynb
│   ├── 02_advanced_preprocessing_and_feature_engineering.ipynb
│   ├── 03_addressing_class_imbalance.ipynb
│   ├── 04_baseline_model_and_evaluation.ipynb
│   ├── 05_deep_learning_model_development.ipynb
│   ├── 06_hyperparameter_tuning_and_optimization.ipynb
│   └── 07_model_comparison_dashboard.ipynb
│
├── trained_models/              # Pre-trained ML models (gitignored)
│   ├── best_baseline.pkl        # RandomForest classifier
│   ├── encoder.pkl              # Label encoder
│   ├── scaler_standard.pkl      # Feature scaler
│   └── dl_models/               # Deep learning models
│       ├── anomaly_autoencoder.keras
│       ├── anomaly_threshold.npy
│       └── anormaly_scaler.joblib
│
├── logs/                        # Runtime logs (gitignored)
│   ├── .gitkeep                 # Preserve directory
│   ├── alerts.jsonl             # Alert logs
│   ├── alert_tracking.json      # Alert tracking
│   └── statistics.json          # Statistics
│
├── data/                        # Training data (gitignored)
│
├── config.yaml                  # System configuration
├── requirements.txt             # Python dependencies
├── generate_anomalies.py        # Traffic generation tool
├── Dockerfile                   # Docker container config
├── .dockerignore               # Docker ignore rules
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # Project overview
├── ENHANCEMENTS.md             # Feature documentation
├── IMPLEMENTATION_SUMMARY.md   # Implementation details
├── VERIFICATION.md             # Testing & verification
└── TODO.md                     # Development tasks
```

## Key Components

### Backend (FastAPI)
- **Entry**: `src/api/main.py`
- **Endpoints**: `/api/alerts`, `/api/flows`, `/api/statistics/*`, `/api/response/*`
- **WebSockets**: `/ws/alerts`, `/ws/flows`

### Frontend (React + Vite)
- **Entry**: `src/frontend/src/main.jsx`
- **Dashboard**: Real-time threat monitoring
- **Components**: Alerts, Flows, Statistics

### ML Pipeline
- **Training**: Jupyter notebooks in `notebooks/`
- **Models**: RandomForest + Autoencoder
- **Prediction**: Real-time threat classification

### Network Monitoring
- **Packet Capture**: Scapy-based sniffer (requires root)
- **Analysis**: Flow-based feature engineering
- **Detection**: Dual ML model approach

## Running the System

### Development
```bash
# Backend (requires sudo for packet capture)
sudo venv/bin/python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd src/frontend
npm run dev
```

### Production (Docker)
```bash
docker build -t ids-system .
docker run --cap-add=NET_RAW --cap-add=NET_ADMIN -p 8000:8000 -p 5173:5173 ids-system
```

## Ports
- **Backend API**: 8000
- **Frontend Dashboard**: 5173
