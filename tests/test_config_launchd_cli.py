import plistlib

from typer.testing import CliRunner

from shokz_sync import config, launchd
from shokz_sync.cli import app

runner = CliRunner()


def test_infer_kind():
    assert config.infer_kind("https://www.youtube.com/@x") == "youtube"
    assert config.infer_kind("https://youtu.be/abc") == "youtube"
    assert config.infer_kind("https://anchor.fm/s/1/podcast/rss") == "rss"
    assert config.infer_kind("https://notyoutube.com/feed") == "rss"


def test_config_round_trip(tmp_path):
    cfg = config.Config(sources=[config.Source("Pod", "https://ex.com/rss", "rss", False)])
    p = tmp_path / "c.toml"
    config.save(cfg, p)
    back = config.load(p)
    assert back.sources == cfg.sources and back.per_source == 1 and back.total == 5
    assert back.download_every_hours == 24
    assert back.library == cfg.library


def test_cli_sources_add_list_disable_rm():
    r = runner.invoke(app, ["sources", "add", "Nate & Koa", "https://www.youtube.com/@nk"])
    assert r.exit_code == 0 and "youtube" in r.output
    assert runner.invoke(app, ["sources", "add", "nate & koa", "https://x"]).exit_code == 1
    assert runner.invoke(app, ["sources", "disable", "nate & koa"]).exit_code == 0
    assert config.load().sources[0].enabled is False
    assert "Nate & Koa" in runner.invoke(app, ["sources", "list"]).output
    assert runner.invoke(app, ["sources", "rm", "Nate & Koa"]).exit_code == 0
    assert config.load().sources == []


def test_sync_without_device_is_quiet_in_auto_mode(monkeypatch):
    monkeypatch.setattr("shokz_sync.device.find", lambda name: None)
    assert runner.invoke(app, ["sync", "--auto"]).exit_code == 0
    assert runner.invoke(app, ["sync"]).exit_code == 1


def test_sync_refuses_to_wipe_device_when_library_empty(tmp_path, monkeypatch):
    vol = tmp_path / "vol"
    vol.mkdir()
    (vol / "keep.mp3").write_bytes(b"x")
    monkeypatch.setattr("shokz_sync.device.find", lambda name: vol)
    r = runner.invoke(app, ["sync"])
    assert r.exit_code == 1 and (vol / "keep.mp3").exists()


def test_launchd_render():
    assert launchd.render("/bin/shokz-sync")[launchd.DOWNLOAD]["StartInterval"] == 86400
    agents = launchd.render("/bin/shokz-sync", every_hours=6)
    dl, mount = agents[launchd.DOWNLOAD], agents[launchd.MOUNT]
    assert dl["ProgramArguments"] == ["/bin/shokz-sync", "download"]
    assert dl["StartInterval"] == 21600
    assert mount["ProgramArguments"] == ["/bin/shokz-sync", "sync", "--auto"]
    assert mount["StartOnMount"] is True
    assert "/opt/homebrew/bin" in mount["EnvironmentVariables"]["PATH"]
    plistlib.dumps(dl), plistlib.dumps(mount)  # both serialise
