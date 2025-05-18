import os
import subprocess
from datetime import datetime

# Step 1: Run generate_static.py
print(f"🕒 Starting at {datetime.now()}")
try:
    subprocess.run(["python", "generate_static.py"], check=True)
    print("✅ generate_static.py ran successfully.")
except subprocess.CalledProcessError:
    print("❌ Error in generate_static.py")
    exit(1)

# Step 2: Git commit & push
def run_git(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("⚠️", result.stderr)

print("📦 Committing and pushing to main...")
run_git("git add docs/index.html")
run_git("git commit -m \"Auto: update dashboard from Task Scheduler\"")
run_git("git push origin main")

print("🌍 Pushing to gh-pages...")
run_git("git subtree push --prefix docs origin gh-pages")

print(f"✅ Done at {datetime.now()}")
