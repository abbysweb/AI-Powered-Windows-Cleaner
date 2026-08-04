from pathlib import Path

from ai_health_copilot.core.duplicate.scanner import find_duplicates


def test_find_duplicates(tmp_path):
    # Unique file
    f1 = tmp_path / "unique.txt"
    f1.write_text("Hello World")

    # Duplicate files
    f2 = tmp_path / "dupe1.txt"
    f2.write_text("Duplicate content")

    f3 = tmp_path / "dupe2.txt"
    f3.write_text("Duplicate content")

    # Same size, different content
    f4 = tmp_path / "diff.txt"
    f4.write_text("Different content")

    results = find_duplicates(tmp_path)

    assert len(results) == 1
    group = results[0]
    assert len(group) == 2

    names = [Path(p).name for p in group]
    assert "dupe1.txt" in names
    assert "dupe2.txt" in names
    assert "unique.txt" not in names
    assert "diff.txt" not in names


def test_find_duplicates_empty_dir(tmp_path):
    results = find_duplicates(tmp_path)
    assert results == []
