# -*- coding: utf-8 -*-
import os, sys, time, subprocess, hashlib
from datetime import datetime

WATCH_FILES = ['index.html', 'app.html', 'landing.html']
CHECK_INTERVAL = 3

def get_hash(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def run_git(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, r.stdout.strip(), r.stderr.strip()

def git_push(fname):
    now = datetime.now().strftime("%H:%M:%S")
    print("\n[" + now + "] Degisiklik: " + fname)
    run_git('git add .')
    code, out, err = run_git('git commit -m "auto: ' + fname + ' ' + now + '"')
    if code != 0 and 'nothing to commit' not in out + err:
        print("  HATA commit: " + err); return
    code, out, err = run_git('git push')
    if code != 0:
        print("  HATA push: " + err); return
    print("  PUSHED! Vercel ~30 saniyede deploy eder.")

def main():
    print("=" * 40)
    print("  DEPTHPULSE - Auto Deploy")
    print("=" * 40)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    code, out, _ = run_git('git --version')
    if code != 0: print("Git bulunamadi!"); sys.exit(1)
    print("OK: " + out)
    
    code, _, _ = run_git('git status')
    if code != 0: print("Git repo degil! GitHub Desktop ile clone yap."); sys.exit(1)
    
    code, out, _ = run_git('git remote -v')
    print("Remote: " + (out.split()[1] if out.split() else '?'))
    print()
    
    hashes = {}
    for f in WATCH_FILES:
        h = get_hash(f)
        if h: hashes[f] = h; print("Izleniyor: " + f)
        else: print("Beklenecek: " + f)
    
    print()
    print("HAZIR! Dosyayi klasore kopyala -> otomatik push.")
    print("Durdurmak: Ctrl+C")
    print("-" * 40)
    
    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            for fname in WATCH_FILES:
                nh = get_hash(fname)
                if nh is None:
                    hashes.pop(fname, None); continue
                oh = hashes.get(fname)
                if oh != nh:
                    hashes[fname] = nh
                    git_push(fname)
        except KeyboardInterrupt:
            print("\nDurduruldu."); sys.exit(0)
        except Exception as e:
            print("Hata: " + str(e)); time.sleep(5)

if __name__ == '__main__':
    main()
