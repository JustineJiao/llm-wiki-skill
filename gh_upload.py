"""Upload files to GitHub repo via API using gh auth"""
import pathlib, base64, json, subprocess, os, sys

REPO = "JustineJiao/llm-wiki-skill"
ROOT = r"D:\WorkDir\llm-wiki-github"

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
PATH = r"C:\Program Files\GitHub CLI;C:\Program Files\Git\bin;" + os.environ.get("PATH", "")

def gh_api(method, endpoint, data=None):
    cmd = [r"C:\Program Files\GitHub CLI\gh.exe", "api", f"/repos/{REPO}/{endpoint}", "--method", method]
    if data:
        cmd.extend(["--input", "-"])
    env = os.environ.copy()
    env["PATH"] = PATH
    r = subprocess.run(cmd, input=json.dumps(data) if data else None,
                       capture_output=True, text=True, env=env, timeout=30)
    if r.returncode != 0:
        print(f"ERROR {endpoint}: {r.stderr[:200]}")
        return None
    return json.loads(r.stdout) if r.stdout else {}

# Get the latest commit SHA on the default branch
default_branch = gh_api("GET", "") or {}
default_branch_name = default_branch.get("default_branch", "main")
print(f"Default branch: {default_branch_name}")

# Get the ref of the branch (it's empty, so we'll create initial commit)
# For empty repo, we need to create the initial commit via blobs + trees + commits
files_to_upload = []
for f in sorted(pathlib.Path(ROOT).rglob("*")):
    if f.is_file() and ".git" not in str(f):
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        content = f.read_bytes()
        b64 = base64.b64encode(content).decode()
        files_to_upload.append({"path": rel, "content": b64, "encoding": "base64"})

print(f"Uploading {len(files_to_upload)} files...")

# Upload files via GitHub Contents API (one by one is safer for empty repos)
for i, f in enumerate(files_to_upload):
    data = {
        "message": f"Add {f['path']}",
        "content": f["content"],
        "branch": default_branch_name
    }
    result = gh_api("PUT", f"contents/{f['path']}", data)
    status = "OK" if result else "FAIL"
    print(f"[{i+1}/{len(files_to_upload)}] {f['path']} -> {status}")

print("Done!")
