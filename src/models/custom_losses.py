"""
Custom loss functions for Keras models.
These need to be registered for model loading to work.
"""
import os

# Suppress TensorFlow messages BEFORE importing tensorflow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from tensorflow import keras
import tensorflow.keras.backend as K

# Try to import the correct registration decorator based on TensorFlow version
try:
    from tensorflow.keras.saving import register_keras_serializable
except ImportError:
    try:
        from tensorflow.keras.utils import register_keras_serializable
    except ImportError:
        # Fallback for older TensorFlow versions
        def register_keras_serializable(package=None, name=None):
            def decorator(func):
                return func
            return decorator


@register_keras_serializable(package="Custom", name="focal_loss_fixed")
def focal_loss_fixed(y_true, y_pred, gamma=2.0, alpha=0.25):
    """
    Focal Loss for handling class imbalance.

    Args:
        y_true: True labels
        y_pred: Predicted probabilities
        gamma: Focusing parameter (default: 2.0)
        alpha: Weighting factor (default: 0.25)

    Returns:
        Focal loss value
    """
    # Clip predictions to prevent log(0)
    epsilon = K.epsilon()
    y_pred = K.clip(y_pred, epsilon, 1.0 - epsilon)

    # Calculate cross entropy
    cross_entropy = -y_true * K.log(y_pred)

    # Calculate focal loss
    loss = alpha * K.pow(1 - y_pred, gamma) * cross_entropy

    return K.mean(K.sum(loss, axis=-1))


@register_keras_serializable(package="Custom", name="focal_loss")
def focal_loss(y_true, y_pred, gamma=2.0, alpha=0.25):
    """
    Focal Loss function (registered for model loading).
    This is an alias to focal_loss_fixed for backward compatibility.

    Args:
        y_true: True labels
        y_pred: Predicted probabilities
        gamma: Focusing parameter
        alpha: Weighting factor

    Returns:
        Focal loss value
    """
    return focal_loss_fixed(y_true, y_pred, gamma=gamma, alpha=alpha)


def focal_loss_factory(gamma=2.0, alpha=0.25):
    """
    Factory function for focal loss with configurable parameters.

    Args:
        gamma: Focusing parameter
        alpha: Weighting factor

    Returns:
        Focal loss function
    """
    def focal_loss_inner(y_true, y_pred):
        return focal_loss_fixed(y_true, y_pred, gamma=gamma, alpha=alpha)

    # Set the function name for Keras to recognize it
    focal_loss_inner.__name__ = 'focal_loss'

    return focal_loss_inner
