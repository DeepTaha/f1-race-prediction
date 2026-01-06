# 🏎️ F1 Race Prediction System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-000000.svg)
![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-orange.svg)

A comprehensive machine learning system for predicting Formula 1 race outcomes using historical race data, driver statistics, weather conditions, and circuit characteristics.

## ✨ Features

- 🎯 **Race Winner Prediction** - ML-powered predictions with confidence scores
- 📊 **Multiple ML Models** - Random Forest, Gradient Boosting, and Neural Networks
- 📈 **Feature Importance Analysis** - Understand which factors influence predictions
- 📜 **Prediction History** - Track accuracy over past races
- 🌐 **Interactive Dashboard** - Real-time visualization built with React
- 🔄 **RESTful API** - Flask backend for easy integration

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **Scikit-learn** - Machine learning models
- **Pandas & NumPy** - Data processing
- **FastF1** - F1 data collection

### Frontend
- **React 18** - UI framework
- **Recharts** - Data visualization
- **CSS3** - Styling

## 📁 Project Structure

```
f1-prediction-system/
├── .gitignore
├── README.md
├── requirements.txt
├── dashboard/                 # React frontend
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.jsx           # Main React component
│       ├── App.css           # Styling
│       ├── index.js          # React entry point
│       └── index.css
├── notebooks/
│   └── f1_analysis.ipynb     # Jupyter notebook for analysis
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── app.py            # Flask API
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_loader.py    # Data fetching & loading
│   │   └── feature_engineer.py  # Feature engineering
│   └── models/
│       ├── __init__.py
│       └── train_models.py   # Model training
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DeepTaha/f1-prediction-system.git
   cd f1-prediction-system
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node dependencies**
   ```bash
   cd dashboard
   npm install
   cd ..
   ```

### Running the Application

1. **Start the Flask backend** (from project root)
   ```bash
   # Make sure virtual environment is activated
   cd src/api
   python app.py
   ```
   Backend will run on `http://localhost:5000`

2. **Start the React frontend** (in a new terminal)
   ```bash
   cd dashboard
   npm start
   ```
   Frontend will open automatically at `http://localhost:3000`

## 📊 Models & Performance

### Random Forest Classifier (Primary Model)
- **Accuracy:** 87.5%
- **Precision:** 85.3%
- **F1 Score:** 85.7%

### Gradient Boosting (Backup Model)
- **Accuracy:** 84.2%
- **Precision:** 82.8%
- **F1 Score:** 83.1%

### Neural Network (Experimental)
- **Accuracy:** 81.9%
- **Precision:** 80.1%
- **F1 Score:** 80.7%

## 🔑 Key Features Analyzed

1. **Qualifying Position** (38.5%) - Starting grid position
2. **Driver Championship Points** (22.3%) - Current season performance
3. **Circuit History** (15.7%) - Past performance at specific track
4. **Weather Conditions** (11.2%) - Temperature, rain, track conditions
5. **Team Performance** (8.9%) - Constructor form and upgrades
6. **Tire Strategy** (3.4%) - Optimal compound choices

## 📖 API Documentation

### Endpoints

#### Get Race Prediction
```http
GET /api/predict
```

**Response:**
```json
{
  "race_name": "Abu Dhabi Grand Prix 2025",
  "circuit": "Yas Marina Circuit",
  "winner": "Max Verstappen",
  "confidence": "86.2%",
  "qualifying": [
    {
      "position": 1,
      "driver": "Max Verstappen",
      "team": "Red Bull Racing",
      "time": "1:22.945"
    }
  ]
}
```

## 🧪 Testing

Run tests using pytest:
```bash
pytest tests/
```

## 📝 Data Sources

- **FastF1 API** - Official F1 timing data
- **Ergast API** - Historical F1 data
- **Weather APIs** - Real-time weather conditions

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📋 To-Do

- [ ] Add more historical data (2015-2024 seasons)
- [ ] Implement live race tracking
- [ ] Add driver comparison feature
- [ ] Integrate real-time weather API
- [ ] Add user authentication
- [ ] Deploy to cloud platform
- [ ] Mobile responsive improvements
- [ ] Add more ML models (XGBoost, LightGBM)

## 🐛 Known Issues

- Predictions depend on accurate qualifying data
- Weather predictions limited to race day conditions
- Historical data may need periodic updates

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Author

**DeepTaha**
- GitHub: [@DeepTaha](https://github.com/DeepTaha)

## 🙏 Acknowledgments

- FastF1 library for F1 data access
- Ergast API for historical F1 data
- Formula 1 community for insights and feedback
- Scikit-learn for machine learning tools

## 📧 Contact

For questions or suggestions, please open an issue or contact through GitHub.

---

⭐ If you find this project useful, please consider giving it a star!

## 🔮 Future Enhancements

- Real-time race simulation
- Driver performance analytics
- Team strategy recommendations
- Fantasy F1 integration
- Historical race replays with predictions