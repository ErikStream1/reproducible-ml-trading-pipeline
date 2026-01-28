import pandas as pd
import pytest
from src.data import validate_btc_data

@pytest.mark.parametrize("missing_column",
                         ["Date", "Open", "High", "Low", "Close", "Volume"])

def test_missing_columns(missing_column:str):
    data = {
        "Date": ["2023-01-01"],
        "Open": [10000],
        "High": [20000],
        "Low": [10203],
        "Close": [10000],
        "Volume": [1244]
    }
    data.pop(missing_column)
    df = pd.DataFrame(data)
    
    with pytest.raises(ValueError):
        validate_btc_data(df)

def test_data_valid():
    data = {
        "Date": ["2023-01-01"],
        "Open": [10000],
        "High": [20000],
        "Low": [10203],
        "Close": [10000],
        "Volume": [1244]
    }
    
    df = pd.DataFrame(data)
    validate_btc_data(df)

@pytest.mark.parametrize("dates, result",
                         [(["2023-01-01", "2023-01-02"], True),
                          (["2023-01-02", "2023-01-01"], False),
                          (["2023-01-01", "2023-01-01"], False)
                          ])

def test_valid_data(dates:list[str], result:bool):
    
    data = {
        "Date": dates,
        "Open": [10000,11234],
        "High": [20000,1235213],
        "Low": [10203,13123],
        "Close": [10000,123123],
        "Volume": [1244,123123]
    }
    
    df = pd.DataFrame(data)
    
    if not result:
        with pytest.raises(ValueError):
            validate_btc_data(df)
    else:
        validate_btc_data(df)
        
@pytest.mark.parametrize("current_missing", 
                         ["Date","Open", "High", "Low", "Close", "Volume"])        
def test_null_values(current_missing:str):
    data = {
        "Date": ["2023-01-01"],
        "Open": [10000],
        "High": [20000],
        "Low": [10203],
        "Close": [10000],
        "Volume": [1244]
        }
    
    data[current_missing] = float("nan")
    df = pd.DataFrame(data)
    
    with pytest.raises(ValueError):
        validate_btc_data(df)

@pytest.mark.parametrize("col,value,result",
                         [("Open", -12, False),
                         ("High", -4, False),
                         ("Low", -45, False),
                         ("Open",1 , True)
                         ])

def test_nonpositive_prices(col:str, value:int, result:bool):
    data = {
        "Date": ["2023-01-01"],
        "Open": [10000],
        "High": [20000],
        "Low": [10203],
        "Close": [10000],
        "Volume": [1244]
        }
    
    data[col] = value
    df = pd.DataFrame(data)
    
    if not result:
        with pytest.raises(ValueError):
            validate_btc_data(df)
    else:
        validate_btc_data(df)
@pytest.mark.parametrize("volume, result",
                         [(10, True),
                          (0, True),
                          (-1, False)])       
def test_negative_volume(volume:int, result:bool):
    data = {
        "Date": ["2023-01-01"],
        "Open": [10000],
        "High": [20000],
        "Low": [10203],
        "Close": [10000],
        "Volume": volume
        }
    
    df = pd.DataFrame(data)
    
    if not result:
        with pytest.raises(ValueError):
            validate_btc_data(df)
    else:
        validate_btc_data(df)