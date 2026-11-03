"""Reference: scaffold the lake starter with the package CLI."""
import subprocess
import sys

subprocess.run([sys.executable, "-c", "import sys; from rand_engine.cli import main; sys.exit(main())",
                "get-started", "lake", "--out", "starter"], check=True)
