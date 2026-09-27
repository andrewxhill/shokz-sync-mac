from conftest import FakeAdapter, item

from shokz_sync.config import Config, Source
from shokz_sync.library import filename, refresh, skip
from shokz_sync.state import DROPPED, SKIPPED, WANTED, State


def setup(tmp_path, items, **kw):
    cfg = Config(library=tmp_path / "lib", sources=[Source(s, s, "rss") for s in items])
    return cfg, FakeAdapter(items, **kw)


def test_filename_is_ascii_fat_safe_and_unique():
    a = filename(item("Nate & Koa", "x", 1, 'SURFER？ WHEN / WAVES: "big"'))
    b = filename(item("Nate & Koa", "y", 1, 'SURFER？ WHEN / WAVES: "big"'))
    assert a.isascii() and not any(c in a for c in '/\\:*?"<>|')
    assert a.endswith(".mp3") and a != b


def test_filename_keeps_dashes_and_apostrophes():
    name = filename(item("Dwarkesh", "x", 1, "Noam Brown \u2013 Nate\u2019s swarms"))
    assert name.startswith("Dwarkesh - Noam Brown - Nate's swarms [")


def test_downloads_newest_and_prunes_displaced(tmp_path):
    items = {"a": [item("a", "1", 1)], "b": [item("b", "1", 2)]}
    cfg, fake = setup(tmp_path, items)
    refresh(cfg, {"rss": fake})
    assert State().keys(WANTED) == {"a:1", "b:1"}

    items["a"].append(item("a", "2", 9))
    report = refresh(cfg, {"rss": fake})
    st = State()
    assert st.keys(WANTED) == {"a:2", "b:1"}
    assert st.items["a:1"]["status"] == DROPPED
    assert len(report.removed) == 1
    assert sorted(p.name for p in cfg.library.iterdir()) == sorted(
        st.items[k]["file"] for k in ("a:2", "b:1")
    )


def test_failing_source_keeps_its_episode_and_others_continue(tmp_path):
    items = {"a": [item("a", "1", 1)], "b": [item("b", "1", 2)]}
    cfg, fake = setup(tmp_path, items)
    refresh(cfg, {"rss": fake})
    fake.fail_list = {"a"}
    items["b"].append(item("b", "2", 5))
    report = refresh(cfg, {"rss": fake})
    st = State()
    assert "a" in report.errors
    assert st.keys(WANTED) == {"a:1", "b:2"}
    assert st.sources["a"]["last_error"] == "feed down"
    assert st.sources["b"]["last_error"] is None


def test_failed_download_keeps_previous_episode(tmp_path):
    items = {"a": [item("a", "1", 1)]}
    cfg, fake = setup(tmp_path, items)
    refresh(cfg, {"rss": fake})
    items["a"].append(item("a", "2", 5))
    fake.fail_fetch = {"a:2"}
    report = refresh(cfg, {"rss": fake})
    assert State().keys(WANTED) == {"a:1"}
    assert "download failed" in report.errors["a"]


def test_skip_then_next_newest_fills_slot(tmp_path):
    items = {"a": [item("a", "1", 1, "older talk"), item("a", "2", 5, "Newest talk")]}
    cfg, fake = setup(tmp_path, items)
    refresh(cfg, {"rss": fake})
    st = State()
    assert [m["id"] for m in skip(st, cfg, "newest")] == ["2"]
    refresh(cfg, {"rss": fake})
    st = State()
    assert st.items["a:2"]["status"] == SKIPPED
    assert st.keys(WANTED) == {"a:1"}


def test_skip_ambiguous_changes_nothing(tmp_path):
    items = {"a": [item("a", "1", 1, "talk one")], "b": [item("b", "1", 2, "talk two")]}
    cfg, fake = setup(tmp_path, items)
    refresh(cfg, {"rss": fake})
    assert len(skip(State(), cfg, "talk")) == 2
    assert State().keys(SKIPPED) == set()


def test_disabled_source_leaves(tmp_path):
    items = {"a": [item("a", "1", 1)], "b": [item("b", "1", 2)]}
    cfg, fake = setup(tmp_path, items)
    refresh(cfg, {"rss": fake})
    cfg.sources[0].enabled = False
    refresh(cfg, {"rss": fake})
    assert State().keys(WANTED) == {"b:1"}


def test_renamed_file_is_reused_not_redownloaded(tmp_path):
    items = {"a": [item("a", "1", 1)]}
    cfg, fake = setup(tmp_path, items)
    refresh(cfg, {"rss": fake})
    st = State()
    old = cfg.library / st.items["a:1"]["file"]
    old.rename(cfg.library / "old-scheme.mp3")
    st.items["a:1"]["file"] = "old-scheme.mp3"
    st.save()
    fake.fetched.clear()
    refresh(cfg, {"rss": fake})
    assert fake.fetched == [] and old.exists()
