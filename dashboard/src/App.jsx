import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('prediction');

  useEffect(() => {
    // Simulate fetching prediction from Flask API
    // Replace this with actual fetch when your backend is ready
    setTimeout(() => {
      setPrediction({
        race_name: 'Abu Dhabi Grand Prix 2025',
        circuit: 'Yas Marina Circuit',
        race_date: 'Dec 8, 2025',
        conditions: '29°C | Clear',
        model_status: 'Active',
        winner: 'Max Verstappen',
        confidence: '86.2%',
        timestamp: '1/4/2026, 4:55:54 PM',
        qualifying: [
          { position: 1, driver: 'Max Verstappen', team: 'Red Bull Racing', time: '1:22.945' },
          { position: 2, driver: 'Lando Norris', team: 'McLaren', time: '1:23.056' },
          { position: 3, driver: 'Oscar Piastri', team: 'McLaren', time: '1:23.104' },
          { position: 4, driver: 'Carlos Sainz', team: 'Ferrari', time: '1:23.287' },
          { position: 5, driver: 'Charles Leclerc', team: 'Ferrari', time: '1:23.401' }
        ]
      });
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading predictions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🏎️ F1 RACE PREDICTOR</h1>
        <p className="race-info">
          📍 {prediction?.race_name} | {prediction?.circuit}
        </p>
      </header>

      <div className="container">
        <div className="info-grid">
          <div className="info-card">
            <span className="icon">🏁</span>
            <div>
              <p className="label">Race Date</p>
              <p className="value">{prediction?.race_date}</p>
            </div>
          </div>

          <div className="info-card">
            <span className="icon">🌡️</span>
            <div>
              <p className="label">Conditions</p>
              <p className="value">{prediction?.conditions}</p>
            </div>
          </div>

          <div className="info-card">
            <span className="icon">⚡</span>
            <div>
              <p className="label">Model Status</p>
              <p className="value status-active">{prediction?.model_status}</p>
            </div>
          </div>
        </div>

        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'prediction' ? 'active' : ''}`}
            onClick={() => setActiveTab('prediction')}
          >
            Prediction
          </button>
          <button 
            className={`tab ${activeTab === 'models' ? 'active' : ''}`}
            onClick={() => setActiveTab('models')}
          >
            Models
          </button>
          <button 
            className={`tab ${activeTab === 'features' ? 'active' : ''}`}
            onClick={() => setActiveTab('features')}
          >
            Features
          </button>
          <button 
            className={`tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            History
          </button>
        </div>

        {activeTab === 'prediction' && (
          <div className="content">
            <div className="winner-card">
              <h2>🏆 PREDICTED RACE WINNER</h2>
              <div className="winner-name">{prediction?.winner}</div>
              <p className="confidence">Confidence: {prediction?.confidence}</p>
              <p className="timestamp">
                🕐 Prediction generated: {prediction?.timestamp}
              </p>
            </div>

            <div className="qualifying-section">
              <h3>🎯 Qualifying Results</h3>
              <div className="results-list">
                {prediction?.qualifying.map((result, idx) => (
                  <div key={idx} className="result-item">
                    <span className="position">{result.position}</span>
                    <div className="driver-info">
                      <p className="driver-name">{result.driver}</p>
                      <p className="team-name">{result.team}</p>
                    </div>
                    <span className="lap-time">{result.time}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'models' && (
          <div className="content">
            <h3>🤖 Machine Learning Models</h3>
            <div className="models-grid">
              <div className="model-card">
                <div className="model-header">
                  <h4>Random Forest Classifier</h4>
                  <span className="model-badge active">Active</span>
                </div>
                <div className="model-stats">
                  <div className="stat">
                    <span className="stat-label">Accuracy</span>
                    <span className="stat-value">87.5%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Precision</span>
                    <span className="stat-value">85.3%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Recall</span>
                    <span className="stat-value">86.1%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">F1 Score</span>
                    <span className="stat-value">85.7%</span>
                  </div>
                </div>
                <p className="model-description">
                  Primary model using ensemble learning with 100 decision trees. 
                  Trained on historical race data including qualifying positions, weather, and driver performance.
                </p>
              </div>

              <div className="model-card">
                <div className="model-header">
                  <h4>Gradient Boosting</h4>
                  <span className="model-badge">Backup</span>
                </div>
                <div className="model-stats">
                  <div className="stat">
                    <span className="stat-label">Accuracy</span>
                    <span className="stat-value">84.2%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Precision</span>
                    <span className="stat-value">82.8%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Recall</span>
                    <span className="stat-value">83.5%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">F1 Score</span>
                    <span className="stat-value">83.1%</span>
                  </div>
                </div>
                <p className="model-description">
                  Sequential boosting model with learning rate optimization. 
                  Used for cross-validation and ensemble predictions.
                </p>
              </div>

              <div className="model-card">
                <div className="model-header">
                  <h4>Neural Network</h4>
                  <span className="model-badge experimental">Experimental</span>
                </div>
                <div className="model-stats">
                  <div className="stat">
                    <span className="stat-label">Accuracy</span>
                    <span className="stat-value">81.9%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Precision</span>
                    <span className="stat-value">80.1%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Recall</span>
                    <span className="stat-value">81.3%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">F1 Score</span>
                    <span className="stat-value">80.7%</span>
                  </div>
                </div>
                <p className="model-description">
                  Deep learning model with 3 hidden layers. 
                  Currently in testing phase for complex pattern recognition.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'features' && (
          <div className="content">
            <h3>📊 Feature Importance Analysis</h3>
            <p className="section-description">
              Key factors influencing race predictions, ranked by importance in our model.
            </p>
            <div className="features-list">
              <div className="feature-item">
                <div className="feature-header">
                  <span className="feature-name">Qualifying Position</span>
                  <span className="feature-importance">38.5%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: '38.5%'}}></div>
                </div>
                <p className="feature-description">
                  Starting grid position from qualifying session - strongest predictor of race outcome
                </p>
              </div>

              <div className="feature-item">
                <div className="feature-header">
                  <span className="feature-name">Driver Championship Points</span>
                  <span className="feature-importance">22.3%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: '22.3%'}}></div>
                </div>
                <p className="feature-description">
                  Current season points indicating overall driver performance and consistency
                </p>
              </div>

              <div className="feature-item">
                <div className="feature-header">
                  <span className="feature-name">Circuit History</span>
                  <span className="feature-importance">15.7%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: '15.7%'}}></div>
                </div>
                <p className="feature-description">
                  Driver's past performance at this specific circuit over previous seasons
                </p>
              </div>

              <div className="feature-item">
                <div className="feature-header">
                  <span className="feature-name">Weather Conditions</span>
                  <span className="feature-importance">11.2%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: '11.2%'}}></div>
                </div>
                <p className="feature-description">
                  Temperature, rain probability, and track conditions
                </p>
              </div>

              <div className="feature-item">
                <div className="feature-header">
                  <span className="feature-name">Team Performance</span>
                  <span className="feature-importance">8.9%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: '8.9%'}}></div>
                </div>
                <p className="feature-description">
                  Constructor's recent form and technical upgrades
                </p>
              </div>

              <div className="feature-item">
                <div className="feature-header">
                  <span className="feature-name">Tire Strategy</span>
                  <span className="feature-importance">3.4%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: '3.4%'}}></div>
                </div>
                <p className="feature-description">
                  Predicted optimal tire compound choices and pit stop windows
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="content">
            <h3>📜 Prediction History</h3>
            <p className="section-description">
              Past race predictions and accuracy tracking
            </p>
            <div className="history-list">
              <div className="history-item">
                <div className="history-header">
                  <div>
                    <h4>Las Vegas Grand Prix 2024</h4>
                    <p className="history-date">November 23, 2024</p>
                  </div>
                  <span className="accuracy-badge correct">✓ Correct</span>
                </div>
                <div className="history-details">
                  <div className="history-stat">
                    <span className="stat-label">Predicted Winner</span>
                    <span className="stat-value">Max Verstappen</span>
                  </div>
                  <div className="history-stat">
                    <span className="stat-label">Actual Winner</span>
                    <span className="stat-value">Max Verstappen</span>
                  </div>
                  <div className="history-stat">
                    <span className="stat-label">Confidence</span>
                    <span className="stat-value">82.1%</span>
                  </div>
                </div>
              </div>

              <div className="history-item">
                <div className="history-header">
                  <div>
                    <h4>São Paulo Grand Prix 2024</h4>
                    <p className="history-date">November 3, 2024</p>
                  </div>
                  <span className="accuracy-badge correct">✓ Correct</span>
                </div>
                <div className="history-details">
                  <div className="history-stat">
                    <span className="stat-label">Predicted Winner</span>
                    <span className="stat-value">Max Verstappen</span>
                  </div>
                  <div className="history-stat">
                    <span className="stat-label">Actual Winner</span>
                    <span className="stat-value">Max Verstappen</span>
                  </div>
                  <div className="history-stat">
                    <span className="stat-label">Confidence</span>
                    <span className="stat-value">79.4%</span>
                  </div>
                </div>
              </div>

              <div className="history-item">
                <div className="history-header">
                  <div>
                    <h4>Mexico City Grand Prix 2024</h4>
                    <p className="history-date">October 27, 2024</p>
                  </div>
                  <span className="accuracy-badge incorrect">✗ Incorrect</span>
                </div>
                <div className="history-details">
                  <div className="history-stat">
                    <span className="stat-label">Predicted Winner</span>
                    <span className="stat-value">Max Verstappen</span>
                  </div>
                  <div className="history-stat">
                    <span className="stat-label">Actual Winner</span>
                    <span className="stat-value">Carlos Sainz</span>
                  </div>
                  <div className="history-stat">
                    <span className="stat-label">Confidence</span>
                    <span className="stat-value">75.8%</span>
                  </div>
                </div>
              </div>

              <div className="history-item">
                <div className="history-header">
                  <div>
                    <h4>United States Grand Prix 2024</h4>
                    <p className="history-date">October 20, 2024</p>
                  </div>
                  <span className="accuracy-badge correct">✓ Correct</span>
                </div>
                <div className="history-details">
                  <div className="history-stat">
                    <span className="stat-label">Predicted Winner</span>
                    <span className="stat-value">Charles Leclerc</span>
                  </div>
                  <div className="history-stat">
                    <span className="stat-label">Actual Winner</span>
                    <span className="stat-value">Charles Leclerc</span>
                  </div>
                  <div className="history-stat">
                    <span className="stat-label">Confidence</span>
                    <span className="stat-value">71.2%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="overall-stats">
              <h4>Overall Accuracy</h4>
              <div className="overall-stat-grid">
                <div className="overall-stat">
                  <span className="big-number">75%</span>
                  <span className="stat-label">Prediction Accuracy</span>
                </div>
                <div className="overall-stat">
                  <span className="big-number">3/4</span>
                  <span className="stat-label">Recent Correct</span>
                </div>
                <div className="overall-stat">
                  <span className="big-number">77.1%</span>
                  <span className="stat-label">Avg Confidence</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;