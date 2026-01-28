import pytest
import numpy as np
import pandas as pd

from src.models import LinearModel, XGBoostModel

#Linear Model

@pytest.fixture
def trained_linear_model():
    X = pd.DataFrame({
        "Return" : np.random.randn(50),
        "MA7" : np.random.randn(50),
        "Volatility" : np.random.randn(50)
    })
    y = np.random.randn(50)
    
    model = LinearModel()
    model.fit(X,y)
    y_pred = model.predict(X)
    
    return model, X, y, y_pred

def test_fit_linear(trained_linear_model):
    model, _, _, _ = trained_linear_model
    assert model is not None
    
def test_predict_shape_linear(trained_linear_model):
    _, _, y, y_pred = trained_linear_model
    assert len(y) == len(y_pred)
    
def test_no_nan_linear(trained_linear_model):
    _, _, _, y_pred = trained_linear_model
    assert not np.isnan(y_pred).any()
    
# XGBoost model

@pytest.fixture
def trained_XGBoost_model():
    X = pd.DataFrame({
        "Return" : np.random.randn(50),
        "MA7" : np.random.randn(50),
        "Volatility" : np.random.randn(50)
        })
    y = np.random.randn(50)
    
    model = XGBoostModel()
    model.fit(X,y)
    
    y_pred = model.predict(X)
    
    return model, X, y, y_pred

def test_fit_XGB(trained_XGBoost_model):
    model, _, _, _ = trained_XGBoost_model
    assert model is not None
    
def test_predict_shape_XGB(trained_XGBoost_model):
    _, _, y, y_pred = trained_XGBoost_model
    assert len(y) == len(y_pred)
    
def test_no_nan_XGB(trained_XGBoost_model):
    _, _, _, y_pred = trained_XGBoost_model
    assert not np.isnan(y_pred).any()
    