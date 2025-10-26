"""
Model Ensemble Module for Network IDS

Combines predictions from multiple models (ML and DL) to improve detection accuracy.
Supports different ensemble strategies: voting, weighted voting, confidence-based.
Loads and uses retrained models from trained_models/retrained/
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import joblib
import json
import os
import threading

# Suppress TensorFlow messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.models import load_model

logger = logging.getLogger(__name__)


class ModelEnsemble:
    """
    Ensemble of multiple models for threat detection using retrained models.

    Supports:
    - Random Forest (ML classifier)
    - Deep Learning FFNN (optimized for false positive reduction)
    - Ensemble strategies: voting, weighted voting, confidence-based

    Loads models from trained_models/retrained/ directory.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the ensemble with retrained models.

        Args:
            config: Configuration dictionary with model weights and thresholds
        """
        self.config = config or self._default_config()
        self.prediction_history = []
        self.performance_metrics = {
            'ml_classifier': {'correct': 0, 'total': 0},
            'dl_ffnn': {'correct': 0, 'total': 0}
        }

        # Model paths - using retrained models
        self.retrained_dir = Path('trained_models/retrained')
        self.dl_model_path = self.retrained_dir / 'dl_model_retrained_fp_optimized.keras'
        self.rf_model_path = self.retrained_dir / 'random_forest_calibrated.pkl'
        self.scaler_path = self.retrained_dir / 'scaler_standard_retrained.pkl'
        self.class_mapping_path = self.retrained_dir / 'class_mapping.json'
        self.optimal_threshold_path = self.retrained_dir / 'optimal_threshold.json'

        # Load models and configuration
        self._load_models()
        self._load_config()

        # Expected feature count for retrained models
        self.expected_features = 37
        self.model_feature_names = [
            'flow_duration', 'Header_Length', 'Protocol Type', 'Duration',
            'Rate', 'Drate', 'fin_flag_number', 'syn_flag_number',
            'psh_flag_number', 'ack_flag_number', 'ece_flag_number', 'cwr_flag_number',
            'syn_count', 'fin_count', 'urg_count', 'rst_count',
            'HTTP', 'HTTPS', 'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC',
            'TCP', 'UDP', 'DHCP', 'ARP', 'ICMP', 'IPv',
            'Tot sum', 'Min', 'Max', 'AVG', 'Tot size', 'IAT',
            'Covariance', 'Variance'
        ]

        # Model cache
        self._model_cache = {}
        self._model_cache_lock = threading.Lock()

        # Clipping configuration (mirrors behavior in src.models.predict)
        self.clip_enabled = os.getenv('PREDICTION_CLIP_ENABLED', '1') == '1'
        try:
            self.clip_z = float(os.getenv('PREDICTION_CLIP_Z', '5.0'))
        except Exception:
            self.clip_z = 5.0

    def _default_config(self) -> Dict:
        """Default configuration for the ensemble."""
        return {
            'ensemble_mode': 'weighted_voting',  # 'voting', 'weighted_voting', 'confidence'
            'model_weights': {
                'ml_classifier': 0.6,  # Random Forest weight
                'dl_ffnn': 0.4,  # Deep Learning weight
            },
            'confidence_threshold': 0.35,  # Optimal threshold from training
            'enable_models': {
                'ml_classifier': True,
                'dl_ffnn': True,
            },
            'optimal_threshold': 0.55  # From training config
        }

    def _load_models(self):
        """Load retrained models and scaler."""
        try:
            # Import custom losses for DL model
            from src.models.custom_losses import focal_loss_fixed, focal_loss

            # Load models
            self.rf_model = joblib.load(self.rf_model_path)
            self.dl_model = load_model(self.dl_model_path, custom_objects={
                'focal_loss_fixed': focal_loss_fixed,
                'focal_loss': focal_loss
            })
            self.scaler = joblib.load(self.scaler_path)

            logger.info("Successfully loaded retrained models")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise

    def _load_config(self):
        """Load class mapping and optimal threshold."""
        try:
            # Load class mapping
            with open(self.class_mapping_path, 'r') as f:
                self.class_mapping = json.load(f)
            # Convert string keys to integers
            self.class_mapping = {int(k): v for k, v in self.class_mapping.items()}

            # Load optimal threshold
            with open(self.optimal_threshold_path, 'r') as f:
                threshold_data = json.load(f)
                self.optimal_threshold = threshold_data.get('optimal_threshold', 0.35)

            logger.info("Successfully loaded model configuration")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def _validate_features(self, features):
        """
        Ensure correct shape for model input and select required features.

        Args:
            features: Either DataFrame or numpy array with features

        Returns:
            DataFrame with exactly expected_features in correct order
        """
        # Convert DataFrame to select only required features
        if isinstance(features, pd.DataFrame):
            # Select only the features the model expects, in the correct order
            try:
                X_df = features[self.model_feature_names]
            except KeyError as e:
                logger.error(f"Missing required features: {e}")
                # Fallback: use whatever features are available
                X_df = features
        else:
            X = np.asarray(features)
            if X.ndim == 1:
                X = X.reshape(1, -1)
            # Convert to DataFrame with feature names
            X_df = pd.DataFrame(X, columns=self.model_feature_names)

        if X_df.shape[1] != self.expected_features:
            raise ValueError(f"Expected {self.expected_features} features, got {X_df.shape[1]}")

        return X_df

    def _get_cached_model(self, key, loader_fn):
        """Thread-safe cache models or scalers to speed up repeated inference."""
        if key not in self._model_cache:
            with self._model_cache_lock:
                if key not in self._model_cache:
                    self._model_cache[key] = loader_fn()
        return self._model_cache[key]

    def predict_with_rf(self, features):
        """Predict using Random Forest model."""
        try:
            X_df = self._validate_features(features)
            X_scaled = self.scaler.transform(X_df)
            if self.clip_enabled:
                X_scaled = np.clip(X_scaled, -self.clip_z, self.clip_z)

            # Get predictions
            preds = self.rf_model.predict(X_scaled)
            proba = self.rf_model.predict_proba(X_scaled)

            class_index = preds[0]
            confidence = float(np.max(proba[0]))

            # Decode label using class mapping
            label = self.class_mapping.get(class_index, 'Unknown')

            # Determine severity
            if label == 'BenignTraffic':
                severity = 'low'
            elif any(x in label for x in ['DDoS', 'DoS', 'Flood']):
                severity = 'medium'
            elif any(x in label for x in ['Backdoor', 'Malware', 'Injection', 'Mirai']):
                severity = 'high'
            elif any(x in label for x in ['Recon', 'Scan', 'Discovery']):
                severity = 'medium'
            else:
                severity = 'high'

            return {
                'attack': label,
                'severity': severity,
                'confidence': confidence
            }

        except Exception as e:
            logger.error(f"Random Forest prediction failed: {e}")
            return {
                'attack': 'BenignTraffic',
                'severity': 'low',
                'confidence': 0.0
            }

    def predict_with_dl(self, features):
        """Predict using Deep Learning model."""
        try:
            X_df = self._validate_features(features)
            X_scaled = self.scaler.transform(X_df)
            if self.clip_enabled:
                X_scaled = np.clip(X_scaled, -self.clip_z, self.clip_z)

            # Get predictions
            predictions = self.dl_model.predict(X_scaled, verbose=0)
            class_index = np.argmax(predictions, axis=1)[0]
            confidence = float(np.max(predictions[0]))

            # Decode label using class mapping
            label = self.class_mapping.get(class_index, 'Unknown')

            # Determine severity
            if label == 'BenignTraffic':
                severity = 'low'
            elif any(x in label for x in ['DDoS', 'DoS', 'Flood']):
                severity = 'medium'
            elif any(x in label for x in ['Backdoor', 'Malware', 'Injection', 'Mirai']):
                severity = 'high'
            elif any(x in label for x in ['Recon', 'Scan', 'Discovery']):
                severity = 'medium'
            else:
                severity = 'high'

            return {
                'attack': label,
                'severity': severity,
                'confidence': confidence
            }

        except Exception as e:
            logger.error(f"Deep Learning prediction failed: {e}")
            return {
                'attack': 'BenignTraffic',
                'severity': 'low',
                'confidence': 0.0
            }

    def predict_threat(self, features, use_ensemble=True):
        """
        Predict threat using ensemble of Random Forest and Deep Learning models.

        Args:
            features: Feature array or DataFrame
            use_ensemble: Whether to use ensemble or individual models

        Returns:
            dict with attack type, severity, confidence, and detection method
        """
        try:
            if use_ensemble:
                # Use combine_predictions for ensemble logic
                attack, confidence, method = self.combine_predictions(features)

                # Get individual model results for return
                rf_result = self.predict_with_rf(features)
                dl_result = self.predict_with_dl(features)

                # Determine severity based on attack type
                if attack == 'BenignTraffic':
                    severity = 'low'
                elif any(x in attack for x in ['DDoS', 'DoS', 'Flood']):
                    severity = 'medium'
                elif any(x in attack for x in ['Backdoor', 'Malware', 'Injection', 'Mirai']):
                    severity = 'high'
                elif any(x in attack for x in ['Recon', 'Scan', 'Discovery']):
                    severity = 'medium'
                else:
                    severity = 'high'

                return {
                    'attack': attack,
                    'severity': severity,
                    'confidence': float(confidence),
                    'method': method,
                    'threshold': self.optimal_threshold,
                    'models': {
                        'ml': rf_result,
                        'dl': dl_result
                    }
                }
            else:
                # Use Random Forest only (more accurate based on training)
                rf_result = self.predict_with_rf(features)
                return {
                    'attack': rf_result['attack'],
                    'severity': rf_result['severity'],
                    'confidence': float(rf_result['confidence']),
                    'method': 'random_forest_only',
                    'threshold': self.optimal_threshold,
                    'models': {
                        'ml': rf_result,
                        'dl': self.predict_with_dl(features)
                    }
                }

        except Exception as e:
            logger.error(f"Ensemble prediction failed: {e}")
            return {
                'attack': 'BenignTraffic',
                'severity': 'unknown',
                'confidence': 0.0,
                'method': 'error',
                'error': str(e),
                'models': {
                    'ml': {'attack': 'BenignTraffic', 'severity': 'low', 'confidence': 0.0},
                    'dl': {'attack': 'BenignTraffic', 'severity': 'low', 'confidence': 0.0}
                }
            }

    def combine_predictions(self,
                           features,
                           mode: Optional[str] = None) -> Tuple[str, float, str]:
        """
        Combine predictions from retrained models.

        Args:
            features: Feature array or DataFrame to predict on
            mode: Ensemble mode override

        Returns:
            Tuple of (attack_type, confidence, method)
        """
        mode = mode or self.config['ensemble_mode']

        # Generate predictions from retrained models
        predictions = {}
        if self.config['enable_models'].get('ml_classifier', True):
            predictions['ml_classifier'] = self.predict_with_rf(features)
        if self.config['enable_models'].get('dl_ffnn', True):
            predictions['dl_ffnn'] = self.predict_with_dl(features)

        if not predictions:
            return 'BenignTraffic', 0.0, 'no_models'

        if mode == 'voting':
            return self._simple_voting(predictions)
        elif mode == 'weighted_voting':
            return self._weighted_voting(predictions)
        elif mode == 'confidence':
            return self._confidence_based(predictions)
        else:
            logger.warning(f"Unknown ensemble mode: {mode}, using weighted_voting")
            return self._weighted_voting(predictions)

    def _simple_voting(self, predictions: Dict) -> Tuple[str, float, str]:
        """Simple majority voting."""
        votes = {}
        confidences = {}

        for model_name, pred in predictions.items():
            attack = pred.get('attack', 'BenignTraffic')
            conf = pred.get('confidence', 0.5)

            votes[attack] = votes.get(attack, 0) + 1
            if attack not in confidences:
                confidences[attack] = []
            confidences[attack].append(conf)

        # Get most voted attack
        winner = max(votes, key=votes.get)
        avg_confidence = np.mean(confidences[winner])

        return winner, avg_confidence, 'simple_voting'

    def _weighted_voting(self, predictions: Dict) -> Tuple[str, float, str]:
        """Weighted voting based on model performance."""
        weighted_votes = {}
        weighted_confidences = {}

        for model_name, pred in predictions.items():
            attack = pred.get('attack', 'BenignTraffic')
            conf = pred.get('confidence', 0.5)
            weight = self.config['model_weights'].get(model_name, 1.0)

            # Apply performance-based weight adjustment
            if self.performance_metrics[model_name]['total'] > 10:
                accuracy = (self.performance_metrics[model_name]['correct'] /
                           self.performance_metrics[model_name]['total'])
                weight *= accuracy

            weighted_votes[attack] = weighted_votes.get(attack, 0) + weight
            if attack not in weighted_confidences:
                weighted_confidences[attack] = []
            weighted_confidences[attack].append(conf * weight)

        # Get attack with highest weighted vote
        winner = max(weighted_votes, key=weighted_votes.get)
        avg_confidence = (sum(weighted_confidences[winner]) /
                         len(weighted_confidences[winner]))

        return winner, avg_confidence, 'weighted_voting'

    def _confidence_based(self, predictions: Dict) -> Tuple[str, float, str]:
        """Use prediction with highest confidence."""
        best_model = None
        best_attack = 'BenignTraffic'
        best_confidence = 0.0

        for model_name, pred in predictions.items():
            conf = pred.get('confidence', 0.0)
            if conf > best_confidence:
                best_confidence = conf
                best_attack = pred.get('attack', 'BenignTraffic')
                best_model = model_name

        return best_attack, best_confidence, f'confidence:{best_model}'

    def update_performance(self, model_name: str, correct: bool):
        """
        Update performance metrics for a model.

        Args:
            model_name: Name of the model
            correct: Whether the prediction was correct
        """
        if model_name in self.performance_metrics:
            self.performance_metrics[model_name]['total'] += 1
            if correct:
                self.performance_metrics[model_name]['correct'] += 1

    def get_model_accuracy(self, model_name: str) -> float:
        """Get accuracy for a specific model."""
        metrics = self.performance_metrics.get(model_name, {'correct': 0, 'total': 0})
        if metrics['total'] == 0:
            return 0.0
        return metrics['correct'] / metrics['total']

    def get_all_accuracies(self) -> Dict[str, float]:
        """Get accuracies for all models."""
        return {
            name: self.get_model_accuracy(name)
            for name in self.performance_metrics.keys()
        }

    def save_history(self, filepath: Path):
        """Save prediction history to file."""
        df = pd.DataFrame(self.prediction_history)
        df.to_csv(filepath, index=False)
        logger.info(f"Saved prediction history to {filepath}")

    def load_history(self, filepath: Path):
        """Load prediction history from file."""
        df = pd.read_csv(filepath)
        self.prediction_history = df.to_dict('records')
        logger.info(f"Loaded {len(self.prediction_history)} predictions from {filepath}")


def create_ensemble_from_config(config_path: Path) -> ModelEnsemble:
    """
    Create ensemble from configuration file.

    Args:
        config_path: Path to config file (JSON or YAML)

    Returns:
        ModelEnsemble instance
    """
    import json

    with open(config_path, 'r') as f:
        config = json.load(f)

    return ModelEnsemble(config)
