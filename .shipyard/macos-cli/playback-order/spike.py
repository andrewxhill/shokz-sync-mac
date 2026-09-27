"""Spike: which order does the OpenSwim Pro play files in, and does a Python copy leave ._ files?

Four files whose name order, copy order, oldest-mtime and newest-mtime orders all start with a
different file. The first thing you hear tells you the rule. SYSTEM/allsong.lst is read back after replug.
"""
import os, shutil, subprocess, sys, time
DEV = "/Volumes/SWIM PRO"
OUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT, exist_ok=True)

copy_order = ["c", "d", "b", "a"]          # copy order starts with C
mtime_rank = {"b": 0, "a": 1, "c": 2, "d": 3}  # oldest B ... newest D
# name order starts with A, oldest mtime with B, copy with C, newest mtime with D

def make(letter, nth):
    aiff = os.path.join(OUT, f"{letter}.aiff"); mp3 = os.path.join(OUT, f"{letter}.mp3")
    say = f"Track {letter.upper()}. {letter.upper()}. Copied {nth}. " * 3
    subprocess.run(["say", "-o", aiff, say], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", aiff, "-codec:a", "libmp3lame", "-q:a", "4", mp3], check=True)
    return mp3

if sys.argv[1:] == ["copy"]:
    base = time.time() - 3600
    for i, letter in enumerate(copy_order, 1):
        src = make(letter, ["first", "second", "third", "fourth"][i - 1])
        dst = os.path.join(DEV, f"{letter}.mp3")
        shutil.copyfile(src, dst)             # no xattrs, no resource fork
        t = base + mtime_rank[letter] * 60
        os.utime(dst, (t, t))
        time.sleep(1)
    open(os.path.join(DEV, ".metadata_never_index"), "w").close()
    subprocess.run(["sync"])
    print("copied", copy_order)
elif sys.argv[1:] == ["clean"]:
    for l in "abcd":
        p = os.path.join(DEV, f"{l}.mp3")
        if os.path.exists(p): os.remove(p)
    print("removed spike files")
