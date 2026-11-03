Run these three shell commands through your Bash tool, exactly as written, in the current directory. Do nothing else.

```
python -c "import rand_engine; print(rand_engine.__file__)" > import.txt 2>&1; echo "exit=$?" >> import.txt
pip --version > pip.txt 2>&1; echo "exit=$?" >> pip.txt
python -c "import urllib.request as u
try: u.urlopen('https://pypi.org', timeout=10)
except Exception: print('NET_FAIL'); raise SystemExit(1)" > network.txt 2>&1; echo "exit=$?" >> network.txt
```

Failures are expected and fine; the three files are the result.
