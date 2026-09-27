"""shokz-sync command line."""

from __future__ import annotations

import shutil
from datetime import datetime
from importlib.metadata import version as pkg_version
from typing import NoReturn

import typer
from rich.console import Console
from rich.table import Table

from . import config as config_mod
from . import device, launchd, library, notify, state
from .config import Config, Source
from .sources import adapters

app = typer.Typer(
    help="Keep your Shokz OpenSwim Pro loaded with the newest episode from each source.",
    no_args_is_help=True,
    add_completion=False,
)
sources_app = typer.Typer(help="Manage sources.", no_args_is_help=True)
app.add_typer(sources_app, name="sources")
out = Console()
err = Console(stderr=True)


def _cfg() -> Config:
    try:
        return config_mod.load()
    except Exception as e:
        err.print(f"[red]config error[/] in {config_mod.config_path()}: {e}")
        raise typer.Exit(2) from e


def _fail(msg: str, code: int = 1) -> NoReturn:
    err.print(f"[red]✗[/] {msg}")
    raise typer.Exit(code)


def _hm(seconds: float) -> str:
    m = int(seconds // 60)
    return f"{m // 60}h{m % 60:02d}" if m >= 60 else f"{m}m"


def _age(iso: str | None) -> str:
    if not iso:
        return "never"
    delta = datetime.now().astimezone() - datetime.fromisoformat(iso)
    mins = int(delta.total_seconds() // 60)
    if mins < 60:
        return f"{mins}m ago"
    if mins < 48 * 60:
        return f"{mins // 60}h ago"
    return f"{mins // 1440}d ago"


# ---------------------------------------------------------------- sources


@sources_app.command("list")
def sources_list() -> None:
    """List sources."""
    cfg = _cfg()
    if not cfg.sources:
        out.print("No sources yet. Add one: [bold]shokz-sync sources add NAME URL[/]")
        return
    st = state.State()
    t = Table(box=None, pad_edge=False)
    for col in ("", "name", "kind", "last ok", "url"):
        t.add_column(col)
    for s in cfg.sources:
        info = st.sources.get(s.name, {})
        mark = "[green]●[/]" if s.enabled else "[dim]○[/]"
        if s.enabled and info.get("last_error"):
            mark = "[red]●[/]"
        t.add_row(mark, s.name, s.kind, _age(info.get("last_ok")), f"[dim]{s.url}[/]")
    out.print(t)


@sources_app.command("add")
def sources_add(
    name: str,
    url: str,
    kind: str = typer.Option(None, help="rss or youtube (inferred from the URL)."),
) -> None:
    """Add a podcast feed or YouTube channel/playlist."""
    cfg = _cfg()
    if cfg.find(name):
        _fail(f"a source named {name!r} already exists")
    kind = kind or config_mod.infer_kind(url)
    if kind not in config_mod.KINDS:
        _fail(f"kind must be one of {', '.join(config_mod.KINDS)}")
    cfg.sources.append(Source(name, url, kind))
    config_mod.save(cfg)
    out.print(f"[green]✓[/] added [bold]{name}[/] ({kind})")


@sources_app.command("rm")
def sources_rm(name: str) -> None:
    """Remove a source."""
    cfg = _cfg()
    src = cfg.find(name) or _fail(f"no source named {name!r}")
    cfg.sources.remove(src)
    config_mod.save(cfg)
    out.print(f"[green]✓[/] removed {src.name}; its episode leaves on the next download")


def _set_enabled(name: str, enabled: bool) -> None:
    cfg = _cfg()
    src = cfg.find(name) or _fail(f"no source named {name!r}")
    src.enabled = enabled
    config_mod.save(cfg)
    out.print(f"[green]✓[/] {src.name} {'enabled' if enabled else 'disabled'}")


@sources_app.command("enable")
def sources_enable(name: str) -> None:
    """Enable a source."""
    _set_enabled(name, True)


@sources_app.command("disable")
def sources_disable(name: str) -> None:
    """Disable a source without removing it."""
    _set_enabled(name, False)


# ---------------------------------------------------------------- download / sync


def _download(quiet: bool = False) -> library.Report:
    cfg = _cfg()
    if not cfg.enabled_sources:
        _fail("no enabled sources; add one with: shokz-sync sources add NAME URL")
    try:
        with state.lock("download"):
            report = library.refresh(
                cfg,
                adapters(cfg.youtube_cookies_from),
                commit_lock=lambda: state.lock("commit", wait=300),
                on_fetch=lambda item: out.print(f"[cyan]↓[/] {item.source}: {item.title}"),
            )
    except state.Busy as e:
        _fail(str(e))
    for name in report.removed:
        out.print(f"[dim]− {name}[/]")
    for src, msg in report.errors.items():
        err.print(f"[red]✗ {src}:[/] {msg}")
    if not quiet and not report.errors:
        out.print(f"[green]✓[/] library up to date ({len(report.downloaded)} new)")
    return report


@app.command()
def download() -> None:
    """Fetch the newest episode from each source into the library."""
    report = _download()
    if report.errors:
        raise typer.Exit(1)


@app.command()
def sync(
    auto: bool = typer.Option(False, "--auto", help="For launchd: quiet if no device, notify."),
) -> None:
    """Mirror the library onto the headphones."""
    cfg = _cfg()
    vol = device.find(cfg.device)
    if vol is None:
        if auto:
            return
        _fail(f"headphones not connected (looking for /Volumes/{cfg.device})")
    try:
        with state.lock("commit", wait=60 if auto else 5):
            st = state.State()
            rows = [r for r in st.wanted() if r["file"] and (cfg.library / r["file"]).exists()]
            if not rows:
                # never wipe the device just because the library is empty
                _fail("library is empty; run: shokz-sync download")
            res = device.sync(
                [cfg.library / r["file"] for r in rows],
                vol,
                on_copy=lambda p: out.print(f"[cyan]→[/] {p.name}"),
            )
    except state.Busy as e:
        _fail(str(e))
    for name in res.deleted:
        out.print(f"[dim]− {name}[/]")
    for name in res.no_space:
        err.print(f"[yellow]! no space for[/] {name}")
    on_device = [r for r in rows if r["file"] not in set(res.no_space)]
    total = sum(r.get("duration") or 0 for r in on_device)
    summary = f"{len(on_device)} on device · {_hm(total)}"
    if res.copied:
        summary = f"Loaded {len(res.copied)} new · " + summary
    out.print(f"[green]✓[/] {summary}")
    if auto:
        notify.notify(summary + " · safe to unplug")


@app.command()
def run() -> None:
    """Download, then sync if the headphones are connected."""
    report = _download()
    if device.find(_cfg().device):
        sync(auto=False)
    else:
        out.print("[dim]headphones not connected; they'll sync when plugged in[/]")
    if report.errors:
        raise typer.Exit(1)


@app.command()
def skip(query: str = typer.Argument(..., help="Part of the episode title.")) -> None:
    """Never put this episode on the device again; the next-newest takes its place."""
    cfg = _cfg()
    with state.lock("commit", wait=30):
        st = state.State()
        matches = library.skip(st, cfg, query)
    if not matches:
        _fail(f"no wanted episode matches {query!r}")
    if len(matches) > 1:
        err.print(f"[yellow]{len(matches)} episodes match; be more specific:[/]")
        for m in matches:
            err.print(f"  {m['source']}: {m['title']}")
        raise typer.Exit(1)
    m = matches[0]
    out.print(f"[green]✓[/] skipped {m['source']}: {m['title']}")
    out.print("[dim]run [bold]shokz-sync run[/bold] to fetch its replacement now[/]")


# ---------------------------------------------------------------- status / doctor


@app.command()
def status() -> None:
    """What's on the headphones, what's queued, and how each source is doing."""
    cfg = _cfg()
    st = state.State()
    vol = device.find(cfg.device)
    on_dev = {p.name for p in device.tracks(vol)} if vol else set()

    if vol:
        free = shutil.disk_usage(vol).free / 1e9
        out.print(f"[green]●[/] headphones connected · {free:.1f} GB free")
    else:
        out.print(f"[dim]○ headphones not connected[/] [dim](/Volumes/{cfg.device})[/]")

    rows = st.wanted()
    out.print(f"\n[bold]Episodes[/] [dim](newest {cfg.per_source}/source, max {cfg.total})[/]")
    if not rows:
        out.print("  [dim]none yet; run: shokz-sync download[/]")
    for r in rows:
        if not vol:
            mark = " "
        elif r["file"] in on_dev:
            mark = "[green]✓[/]"
        else:
            mark = "[yellow]↑[/]"
        dur = f" [dim]{_hm(r['duration'])}[/]" if r.get("duration") else ""
        day = r["published"][:10]
        out.print(f"  {mark} [bold]{r['source']}[/] · {r['title']} [dim]{day}[/]{dur}")
    extra = sorted(on_dev - {r["file"] for r in rows})
    for name in extra:
        out.print(f"  [red]−[/] [dim]{name} (removed on next sync)[/]")

    if cfg.sources:
        out.print("\n[bold]Sources[/]")
        for s in cfg.sources:
            info = st.sources.get(s.name, {})
            if not s.enabled:
                out.print(f"  [dim]○ {s.name} (disabled)[/]")
            elif info.get("last_error"):
                last = _age(info.get("last_run"))
                out.print(f"  [red]●[/] {s.name} · {info['last_error']} [dim]({last})[/]")
            else:
                out.print(f"  [green]●[/] {s.name} [dim]checked {_age(info.get('last_ok'))}[/]")

    agents = all(launchd.loaded(label) for label in (launchd.DOWNLOAD, launchd.MOUNT))
    if not agents:
        out.print("\n[yellow]![/] automation off; run [bold]shokz-sync install[/]")


@app.command()
def doctor() -> None:
    """Check tools, config, device, and automation."""
    ok = True

    def check(passed: bool, label: str, hint: str = "") -> None:
        nonlocal ok
        ok &= passed
        mark = "[green]✓[/]" if passed else "[red]✗[/]"
        out.print(f"{mark} {label}" + (f" [dim]— {hint}[/]" if hint and not passed else ""))

    for tool, hint in (("ffmpeg", "brew install ffmpeg"), ("deno", "brew install deno")):
        check(shutil.which(tool) is not None, tool, hint)
    check(shutil.which("dot_clean") is not None, "dot_clean")
    check(True, f"yt-dlp {pkg_version('yt-dlp')}")
    try:
        cfg = config_mod.load()
        check(
            bool(cfg.enabled_sources),
            f"config ({len(cfg.enabled_sources)} enabled sources)",
            "add one: shokz-sync sources add NAME URL",
        )
    except Exception as e:
        check(False, "config", str(e))
        cfg = Config()
    vol = device.find(cfg.device)
    if vol:
        probe = vol / ".shokz-sync-probe"
        try:
            probe.write_text("ok")
            probe.unlink()
            check(True, f"headphones writable at {vol}")
        except OSError as e:
            check(False, f"headphones at {vol}", f"not writable: {e}")
    else:
        out.print(f"[dim]○ headphones not connected (/Volumes/{cfg.device})[/]")
    for label in (launchd.DOWNLOAD, launchd.MOUNT):
        check(launchd.loaded(label), f"launchd {label}", "run: shokz-sync install")
    if not ok:
        raise typer.Exit(1)


# ---------------------------------------------------------------- install


@app.command()
def install() -> None:
    """Download on a schedule (default daily) and sync whenever the headphones are plugged in."""
    program = shutil.which("shokz-sync")
    if not program:
        _fail("shokz-sync is not on PATH; install it first: uv tool install .")
    hours = _cfg().download_every_hours
    for path in launchd.install(program, hours):
        out.print(f"[green]✓[/] {path}")
    out.print(f"[dim]downloads every {hours}h · logs: {launchd.log_path()}[/]")
    out.print("A first download is running now. Plug in the headphones to sync.")


@app.command()
def uninstall() -> None:
    """Remove the launchd agents (keeps config, state, and library)."""
    removed = launchd.uninstall()
    out.print(f"[green]✓[/] removed {len(removed)} agent(s)")


@app.command()
def version() -> None:
    """Print the version."""
    out.print(pkg_version("shokz-sync-mac"))
