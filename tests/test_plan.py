from conftest import item

from shokz_sync.plan import choose


def test_newest_per_source_then_total_newest_first():
    c = {
        "a": [item("a", "1", 1), item("a", "2", 5)],
        "b": [item("b", "1", 3)],
        "c": [item("c", "1", 9), item("c", "2", 8)],
    }
    got = choose(c, set(), per_source=1, total=5)
    assert [i.key for i in got] == ["c:1", "a:2", "b:1"]


def test_total_cap_keeps_most_recent_sources():
    c = {s: [item(s, "1", d)] for s, d in (("a", 1), ("b", 2), ("c", 3))}
    assert [i.key for i in choose(c, set(), 1, 2)] == ["c:1", "b:1"]


def test_skipped_item_is_replaced_by_next_newest():
    c = {"a": [item("a", "old", 1), item("a", "new", 5)]}
    assert [i.key for i in choose(c, {"a:new"}, 1, 5)] == ["a:old"]


def test_per_source_more_than_one():
    c = {"a": [item("a", str(d), d) for d in (1, 2, 3)]}
    assert [i.key for i in choose(c, set(), 2, 5)] == ["a:3", "a:2"]
