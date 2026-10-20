"""Prepare the isolated input and raw resources for the documentation site."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tracked_files() -> list[Path]:
  """Return every tracked file needed to build documentation from an isolated tree."""
  result = subprocess.run(
      ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True, text=False)
  return [Path(name.decode()) for name in result.stdout.split(b"\0") if name]


def copy_input(destination: Path) -> None:
  """Copy tracked project files to the isolated documentation build input."""
  for relative in tracked_files():
    source = ROOT / relative
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def write_text(path: Path, text: str) -> None:
  """Write UTF-8 text after creating its parent directory."""
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(text, encoding="utf-8")


def prepare(output: Path) -> None:
  """Create build input and public raw resources without changing repository sources."""
  if output.exists():
    raise ValueError(f"output already exists: {output}")

  input_root = output / "input"
  public_root = output / "public"
  copy_input(input_root)
  write_text(input_root / "docs" / "index.md", (input_root / "README.md").read_text(encoding="utf-8"))

  shutil.copytree(input_root / "docs", public_root / "docs")
  shutil.copy2(input_root / "llms.txt", public_root / "llms.txt")
  public_skill = public_root / "skills" / "rand-engine" / "SKILL.md"
  public_skill.parent.mkdir(parents=True, exist_ok=True)
  shutil.copy2(input_root / "skills" / "rand-engine" / "SKILL.md", public_skill)
  shutil.copytree(input_root / "rand_engine" / "cases", public_root / "rand_engine" / "cases")
  shutil.copy2(ROOT / "README.md", public_root / "README.md")


def main() -> int:
  """Parse the output path and prepare the documentation site input."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--output", type=Path, required=True)
  args = parser.parse_args()
  try:
    prepare(args.output)
  except (OSError, subprocess.CalledProcessError, ValueError) as error:
    parser.error(str(error))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
