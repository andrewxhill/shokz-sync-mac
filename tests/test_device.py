from collections import namedtuple

import pytest

from shokz_sync import device

Usage = namedtuple("Usage", "free")


@pytest.fixture
def vol(tmp_path):
    v = tmp_path / "SWIM PRO"
    (v / "SYSTEM").mkdir(parents=True)
    (v / "SYSTEM" / "allsong.lst").write_text("{}")
    (v / "System Volume Information").mkdir()
    return v


@pytest.fixture
def lib(tmp_path):
    d = tmp_path / "lib"
    d.mkdir()
    return d


def mk(d, name, size=10):
    p = d / name
    p.write_bytes(b"x" * size)
    return p


def run(files, vol, **kw):
    cleaned = []
    res = device.sync(files, vol, reserve=0, clean=cleaned.append, **kw)
    return res, cleaned


def test_copies_newest_first_then_deletes_unwanted(vol, lib):
    mk(vol, "old.mp3")
    mk(vol, "notes.txt")
    files = [mk(lib, "new.mp3"), mk(lib, "mid.mp3")]
    order = []
    res, cleaned = run(files, vol, on_copy=lambda p: order.append(p.name))
    assert order == ["new.mp3", "mid.mp3"]
    assert res.deleted == ["old.mp3"]
    assert sorted(p.name for p in device.tracks(vol)) == ["mid.mp3", "new.mp3"]
    assert (vol / "notes.txt").exists()
    assert (vol / "SYSTEM" / "allsong.lst").exists()
    assert (vol / "System Volume Information").is_dir()
    assert (vol / device.NEVER_INDEX).exists()
    assert cleaned == [vol]


def test_unchanged_files_are_not_recopied(vol, lib):
    f = mk(lib, "a.mp3")
    run([f], vol)
    res, _ = run([f], vol)
    assert res.copied == [] and res.deleted == []


def test_leftover_part_files_are_removed(vol, lib):
    mk(vol, "a.mp3.part")
    run([mk(lib, "a.mp3")], vol)
    assert not list(vol.glob("*.part"))


def test_no_space_keeps_existing_tracks(vol, lib, monkeypatch):
    mk(vol, "old.mp3")
    big = mk(lib, "big.mp3", 100)
    monkeypatch.setattr(device.shutil, "disk_usage", lambda p: Usage(50))
    res, _ = run([big], vol)
    assert res.no_space == ["big.mp3"]
    assert "big.mp3" not in {p.name for p in device.tracks(vol)}


def test_space_freed_by_deletes_is_used(vol, lib, monkeypatch):
    mk(vol, "old.mp3", 100)
    big = mk(lib, "big.mp3", 100)
    free = {"n": 50}
    real_unlink = type(vol).unlink

    def unlink(self, *a, **k):
        free["n"] += 100
        return real_unlink(self, *a, **k)

    monkeypatch.setattr(type(vol), "unlink", unlink)
    monkeypatch.setattr(device.shutil, "disk_usage", lambda p: Usage(free["n"]))
    res, _ = run([big], vol)
    assert res.copied == ["big.mp3"] and res.no_space == []


def test_find_requires_mount(tmp_path):
    (tmp_path / "SWIM PRO").mkdir()
    assert device.find("SWIM PRO", volumes=tmp_path) is None
