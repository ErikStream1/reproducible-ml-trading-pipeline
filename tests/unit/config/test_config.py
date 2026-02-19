from pathlib import Path

import pytest
from src.utils import deep_merge
from src.config import load_config, load_yaml


def test_load_yaml_raises_for_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileExistsError):
        load_yaml(tmp_path / "missing.yaml")


def test_deep_merge_merges_nested_dicts() -> None:
    left = {"a": {"x": 1, "y": 2}, "keep": 1}
    right = {"a": {"y": 9, "z": 3}, "new": 2}

    merged = deep_merge(left, right)

    assert merged == {"a": {"x": 1, "y": 9, "z": 3}, "keep": 1, "new": 2}


def test_load_config_merges_files_in_order(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    override = tmp_path / "override.yaml"
    base.write_text("model:\n  name: linear\n  alpha: 0.1\n", encoding="utf-8")
    override.write_text("model:\n  alpha: 0.4\n", encoding="utf-8")

    cfg = load_config(base, override)

    assert cfg == {"model": {"name": "linear", "alpha": 0.4}}