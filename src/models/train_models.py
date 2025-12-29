"""
Model Training Pipeline
Train and evaluate multiple ML models
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import joblib

class F1PredictionModel:
    """Multi-model ensemble for F1 race predictions"""
    
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.models = {}
        self.results = {}
        self.best_model = None
        
    def prepare_data(self, test_size=0.2):
        """Split and scale data"""
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=test_size, random_state=42
        )
        
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print(f"✓ Train set: {len(self.X_train)}, Test set: {len(self.X_test)}")
        
    def train_random_forest(self):
        """Train Random Forest classifier"""
        print("\nTraining Random Forest...")
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(self.X_train_scaled, self.y_train)
        
        y_pred = rf.predict(self.X_test_scaled)
        accuracy = accuracy_score(self.y_test, y_pred)
        
        self.models['Random Forest'] = rf
        self.results['Random Forest'] = accuracy
        
        print(f"✓ Random Forest Accuracy: {accuracy:.4f}")
        return rf
        
    def train_xgboost(self):
        """Train XGBoost classifier"""
        print("\nTraining XGBoost...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            n_jobs=-1
        )
        xgb_model.fit(self.X_train_scaled, self.y_train)
        
        y_pred = xgb_model.predict(self.X_test_scaled)
        accuracy = accuracy_score(self.y_test, y_pred)
        
        self.models['XGBoost'] = xgb_model
        self.results['XGBoost'] = accuracy
        
        print(f"✓ XGBoost Accuracy: {accuracy:.4f}")
        return xgb_model
        
    def train_gradient_boosting(self):
        """Train Gradient Boosting classifier"""
        print("\nTraining Gradient Boosting...")
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        gb.fit(self.X_train_scaled, self.y_train)
        
        y_pred = gb.predict(self.X_test_scaled)
        accuracy = accuracy_score(self.y_test, y_pred)
        
        self.models['Gradient Boosting'] = gb
        self.results['Gradient Boosting'] = accuracy
        
        print(f"✓ Gradient Boosting Accuracy: {accuracy:.4f}")
        return gb
    
    def train_all_models(self):
        """Train all models and compare"""
        print("\n" + "="*80)
        print("TRAINING MULTIPLE MODELS")
        print("="*80)
        
        self.prepare_data()
        self.train_random_forest()
        self.train_xgboost()
        self.train_gradient_boosting()
        
        # Select best model
        self.best_model_name = max(self.results, key=self.results.get)
        self.best_model = self.models[self.best_model_name]
        
        print(f"\n✓ Best Model: {self.best_model_name} ({self.results[self.best_model_name]:.4f})")
        
    def save_models(self, path='models/trained_models/'):
        """Save trained models"""
        for name, model in self.models.items():
            filename = f"{path}{name.lower().replace(' ', '_')}.pkl"
            joblib.dump(model, filename)
            print(f"✓ Saved {name} to {filename}")
        
        # Save scaler
        joblib.dump(self.scaler, f"{path}scaler.pkl")
        print(f"✓ Saved scaler")