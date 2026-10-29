"""Push the whole local git repo to GitHub through the REST API only.

Why this exists: in this sandbox github.com is blocked (git-over-HTTPS fails),
while api.github.com is reachable. So instead of `git push` we replay the
working tree through the Git Data API (blob -> tree -> commit -> ref).

Usage:
    python scripts/13_push_via_api.py                # token from env GH_TOKEN or ../token.txt
    python scripts/13_push_via_api.py --dry-run      # build the payload only, no network
"""

import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OWNER = "cho1eeee"
REPO = "spacex-capstone"
BRANCH = "main"
API = "https://api.github.com"
TOKEN_FILE = os.path.join(BASE, "..", "token.txt")


def read_token():
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok and os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, encoding="utf-8") as fh:
            tok = fh.read()
    if not tok:
        return None
    tok = tok.strip().splitlines()[0].strip() if tok.strip() else ""
    # ignore placeholder / instruction text left in the file
    prefixes = ("ghp_", "github_pat_", "gho_", "ghu_", "ghs_")
    if not tok.startswith(prefixes) or len(tok) < 20:
        return None
    return tok


def api(path, token, method="GET", payload=None):
    url = API + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "spacex-capstone-pusher")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read()
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body[:400].decode("utf-8", "replace")}
        return exc.code, parsed


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=BASE, capture_output=True, check=True
    ).stdout
    paths = [p for p in out.decode("utf-8").split("\0") if p]
    # skip files that git ignores on disk but may be missing
    return [p for p in paths if os.path.isfile(os.path.join(BASE, p))]


def main():
    dry = "--dry-run" in sys.argv
    files = tracked_files()
    total = sum(os.path.getsize(os.path.join(BASE, p)) for p in files)
    print(f"files to push : {len(files)}")
    print(f"total size    : {total / 1024 / 1024:.1f} MB")
    print(f"target        : https://github.com/{OWNER}/{REPO} ({BRANCH})")

    if dry:
        big = sorted(files, key=lambda p: -os.path.getsize(os.path.join(BASE, p)))[:5]
        print("\ntop 5 largest files:")
        for p in big:
            print(f"  {os.path.getsize(os.path.join(BASE, p)) / 1024:8.1f} KB  {p}")
        print("\ndry-run only, nothing sent.")
        return

    token = read_token()
    if not token:
        path = os.path.normpath(TOKEN_FILE)
        if os.path.exists(path):
            print("\n[!] token.txt exists but does not contain a token yet.")
            print("    open it, delete the Chinese instructions, paste the token")
            print("    (starts with ghp_ or github_pat_) on the first line, save, retry.")
        else:
            print(f"\n[!] no token file. create {path} and paste the token inside.")
        sys.exit(2)

    status, me = api("/user", token)
    if status != 200:
        print(f"[!] token rejected (HTTP {status}): {me}")
        sys.exit(3)
    print(f"authenticated : {me.get('login')}")

    status, repo = api(f"/repos/{OWNER}/{REPO}", token)
    if status != 200:
        print(f"[!] repo not accessible (HTTP {status}): {repo}")
        sys.exit(4)

    # 0) an empty repo refuses POST /git/blobs (409 "Git Repository is empty"),
    #    so seed one commit through the Contents API first.
    status, ref = api(f"/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}", token)
    if status != 200:
        print(f"bootstrap     : ref lookup HTTP {status} -> treating as empty repo")
        seed = base64.b64encode(b"# spacex-capstone\n\nbootstrap commit\n").decode()
        status, res = api(f"/repos/{OWNER}/{REPO}/contents/README.md", token, "POST",
                          {"message": "Initialize repository", "content": seed,
                           "branch": BRANCH})
        if status not in (200, 201):
            print(f"[!] bootstrap failed (HTTP {status}): {res}")
            sys.exit(4)
        print("bootstrap     : ok")

    # 1) blobs (only files whose content differs from what is already remote)
    remote_sha = {}
    base_tree = None
    status, rtree = api(f"/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1", token)
    if status == 200 and not rtree.get("truncated"):
        base_tree = rtree["sha"]
        remote_sha = {i["path"]: i["sha"] for i in rtree.get("tree", [])
                      if i.get("type") == "blob"}
        print(f"remote tree   : {base_tree} ({len(remote_sha)} files)")

    def local_blob_sha(rel):
        out = subprocess.run(["git", "hash-object", rel], cwd=BASE,
                             capture_output=True, check=True).stdout
        return out.decode().strip()

    tree_items = []
    skipped = 0
    for idx, rel in enumerate(files, 1):
        relposix = rel.replace("\\", "/")
        lsha = local_blob_sha(rel)
        if remote_sha.get(relposix) == lsha:
            skipped += 1
            continue
        with open(os.path.join(BASE, rel), "rb") as fh:
            content = base64.b64encode(fh.read()).decode()
        status, blob = api(f"/repos/{OWNER}/{REPO}/git/blobs", token, "POST",
                           {"content": content, "encoding": "base64"})
        if status not in (200, 201):
            print(f"[!] blob failed for {rel} (HTTP {status}): {blob}")
            sys.exit(5)
        tree_items.append({"path": relposix, "mode": "100644",
                           "type": "blob", "sha": blob["sha"]})
        print(f"  [{idx}/{len(files)}] blob {blob['sha'][:8]}  {rel}")

    # drop remote files that no longer exist locally
    for path in remote_sha:
        if path not in {f.replace("\\", "/") for f in files}:
            tree_items.append({"path": path, "mode": "100644",
                               "type": "blob", "sha": None})
            print(f"  delete  {path}")

    print(f"unchanged     : {skipped} files, {len(tree_items)} to send")
    if not tree_items:
        print("\nSUCCESS (already up to date)")
        return

    # 2) tree
    tree_payload = {"tree": tree_items}
    if base_tree:
        tree_payload["base_tree"] = base_tree
    status, tree = api(f"/repos/{OWNER}/{REPO}/git/trees", token, "POST", tree_payload)
    if status not in (200, 201):
        print(f"[!] tree failed (HTTP {status}): {tree}")
        sys.exit(6)
    print(f"tree          : {tree['sha']}")

    # 3) parent commit (empty repo -> none)
    status, ref = api(f"/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}", token)
    parent = None
    if status == 200:
        parent = ref["object"]["sha"]
        print(f"parent commit : {parent}")
    else:
        print("parent commit : none (first push)")

    commit_payload = {"message": "SpaceX Falcon 9 capstone: full pipeline, notebooks and report",
                      "tree": tree["sha"]}
    if parent:
        commit_payload["parents"] = [parent]
    status, commit = api(f"/repos/{OWNER}/{REPO}/git/commits", token, "POST", commit_payload)
    if status not in (200, 201):
        print(f"[!] commit failed (HTTP {status}): {commit}")
        sys.exit(7)
    print(f"commit        : {commit['sha']}")

    # 4) ref
    if parent:
        status, res = api(f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}", token,
                          "PATCH", {"sha": commit["sha"], "force": False})
    else:
        status, res = api(f"/repos/{OWNER}/{REPO}/git/refs", token, "POST",
                          {"ref": f"refs/heads/{BRANCH}", "sha": commit["sha"]})
    if status not in (200, 201):
        print(f"[!] ref update failed (HTTP {status}): {res}")
        sys.exit(8)

    print("\nSUCCESS")
    print(f"https://github.com/{OWNER}/{REPO}")


if __name__ == "__main__":
    main()
