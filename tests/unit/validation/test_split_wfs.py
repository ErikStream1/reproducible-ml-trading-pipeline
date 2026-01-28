import pytest

import numpy as np

from src.validation import walk_forward_splits

SIZE = 500

def test_basic_wfs():
    n = SIZE
    cfg ={
        "training":{
            "random_seed": 42,
            "split":{
                "method": "walk_forward_splits",
                "train_size": 200,
                "test_size": 50,
                "step": 50,
            },
        }
    }

    train_size = cfg["training"]["split"]["train_size"]
    test_size = cfg["training"]["split"]["test_size"]

    folds = list(walk_forward_splits(n, cfg))
    assert len(folds)>0
    
    for tr_idx, te_idx in folds:
        assert len(tr_idx) >= train_size
        assert len(te_idx) == test_size 
        
        assert np.all(np.diff(tr_idx) == 1)
        assert np.all(np.diff(te_idx) == 1)
        
        assert tr_idx.max() < te_idx.min()
        
def test_wfs_step_overlap_ok():
    n = SIZE
    cfg ={
        "training":{
            "random_seed": 42,
            "split":{
                "method": "walk_forward_splits",
                "train_size": 200,
                "test_size": 50,
                "step": 10,
            },
        }
    }
    
    folds = list(walk_forward_splits(n,cfg))
    
    assert len(folds) > 1
    for tr_idx, te_idx in folds:
        assert tr_idx.max() < te_idx.min()
        
def test_wfs_not_enough_data():
    n = SIZE
    cfg ={
        "training":{
            "random_seed": 42,
            "split":{
                "method": "walk_forward_splits",
                "train_size": n,
                "test_size": 50,
                "step": 50,
            },
        }
    }
    
    folds = list(walk_forward_splits(n, cfg))
    
    assert len(folds) == 0
    

def test_wfs_invalid_sizes():
    n = SIZE
    cfg ={
        "training":{
            "random_seed": 42,
            "split":{
                "method": "walk_forward_splits",
                "train_size": 0,
                "test_size": 50,
                "step": 50,
            },
        }
    }
    
    with pytest.raises(ValueError):
        list(walk_forward_splits(n, cfg))
        
def test_wfs_invalid_step():
    n = SIZE
    cfg ={
        "training":{
            "random_seed": 42,
            "split":{
                "method": "walk_forward_splits",
                "train_size": 200,
                "test_size": 50,
                "step": 0,
            },
        }
    }
    
    with pytest.raises(ValueError):
        list(walk_forward_splits(n, cfg))
