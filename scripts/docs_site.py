"""Prepare the isolated input and raw resources for the documentation site."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/marcoaureliomenezes/rand_engine"
SHA = re.compile(r"[0-9a-f]{40}")
MASTER_REF = "refs/heads/master"
PREVIEW_REF = "refs/heads/feature/0.8.0"


@dataclass(frozen=True)
class DeploymentEligibility:
  """State whether an event may deploy the prepared documentation artifact."""

  mode: str
  reason: str | None = None


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


def source_zip(sha: str) -> str:
  """Return the immutable source archive used by a preview reader."""
  return f"{REPOSITORY}/archive/{sha}.zip"


def preview_notice(sha: str) -> str:
  """Return the shared, visibly early preview install guidance."""
  return (
      "> **Unreleased preview.** This page describes the reviewed 0.8.0 source, not the stable PyPI release.\n"
      ">\n"
      "> Install this exact reviewed source:\n"
      ">\n"
      "> ```bash\n"
      f"> pip install \"{source_zip(sha)}\"\n"
      "> ```\n\n"
  )


def rewrite_project_routes(text: str, sha: str) -> str:
  """Bind project source links in a preview to its reviewed source revision."""
  return text.replace(f"{REPOSITORY}/blob/master/", f"{REPOSITORY}/blob/{sha}/").replace(
      f"{REPOSITORY}/raw/master/", f"{REPOSITORY}/raw/{sha}/")


def rewrite_preview_installs(text: str, sha: str) -> str:
  """Bind project installation guidance in a preview to its reviewed source."""
  archive = source_zip(sha)
  return text.replace(
      'pip install "rand-engine[faker]"',
      f'pip install "rand-engine[faker] @ {archive}"',
  ).replace("pip install rand-engine", f'pip install "{archive}"')


def add_preview_notice(text: str, sha: str, skill: bool = False) -> str:
  """Place preview guidance before installation while preserving skill front matter."""
  text = rewrite_preview_installs(rewrite_project_routes(text, sha), sha)
  notice = preview_notice(sha)
  if skill:
    match = re.match(r"(---\n.*?\n---\n)", text, re.S)
    if match is None:
      raise ValueError("canonical skill must begin with YAML front matter")
    return f"{match.group(1)}\n{notice}{text[match.end():]}"
  return f"{notice}{text}"


def prepared_text(text: str, mode: str, sha: str, skill: bool = False) -> str:
  """Render one public Markdown-like resource for the selected artifact mode."""
  return add_preview_notice(text, sha, skill) if mode == "preview" else text


def write_text(path: Path, text: str) -> None:
  """Write UTF-8 text after creating its parent directory."""
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(text, encoding="utf-8")


def prepare(mode: str, sha: str, output: Path) -> None:
  """Create build input and public raw resources without changing repository sources."""
  if output.exists():
    raise ValueError(f"output already exists: {output}")

  input_root = output / "input"
  public_root = output / "public"
  copy_input(input_root)

  config = input_root / "mkdocs.yml"
  config_text = config.read_text(encoding="utf-8")
  config.write_text(rewrite_project_routes(config_text, sha) if mode == "preview" else config_text, encoding="utf-8")

  source_documents = [input_root / "README.md", *(input_root / "docs").glob("**/*.md")]
  for path in source_documents:
    text = prepared_text(path.read_text(encoding="utf-8"), mode, sha)
    if path.name == "README.md":
      write_text(input_root / "docs" / "index.md", text)
    else:
      path.write_text(text, encoding="utf-8")

  source_llms = input_root / "llms.txt"
  source_llms.write_text(prepared_text(source_llms.read_text(encoding="utf-8"), mode, sha), encoding="utf-8")
  source_skill = input_root / "skills" / "rand-engine" / "SKILL.md"
  source_skill.write_text(prepared_text(source_skill.read_text(encoding="utf-8"), mode, sha, skill=True), encoding="utf-8")

  shutil.copytree(input_root / "docs", public_root / "docs")
  shutil.copy2(source_llms, public_root / "llms.txt")
  public_skill = public_root / "skills" / "rand-engine" / "SKILL.md"
  public_skill.parent.mkdir(parents=True, exist_ok=True)
  shutil.copy2(source_skill, public_skill)
  shutil.copytree(input_root / "rand_engine" / "cases", public_root / "rand_engine" / "cases")
  write_text(public_root / "README.md", prepared_text((ROOT / "README.md").read_text(encoding="utf-8"), mode, sha))


def deployment_eligibility(*, event_name: str, ref: str, sha: str, project_version: str,
                           read_remote_project_version: Callable[[str], str | None],
                           read_remote_ref: Callable[[str], str | None]) -> DeploymentEligibility:
  """Return the exact deploy mode or an explained successful skip."""
  if event_name != "push":
    return DeploymentEligibility("skip", "only push events may deploy Pages")
  if ref == MASTER_REF:
    return DeploymentEligibility("stable")
  if ref != PREVIEW_REF:
    return DeploymentEligibility("skip", "only master or feature/0.8.0 may deploy Pages")
  if project_version != "0.8.0":
    return DeploymentEligibility("skip", "preview source version is not 0.8.0")
  try:
    master_version = read_remote_project_version(MASTER_REF)
  except (KeyError, OSError, subprocess.SubprocessError, ValueError) as error:
    return DeploymentEligibility("skip", f"could not read remote master version: {error}")
  if master_version != "0.7.0":
    return DeploymentEligibility("skip", "remote master version is not 0.7.0")
  try:
    feature_sha = read_remote_ref(PREVIEW_REF)
  except (OSError, subprocess.SubprocessError, ValueError) as error:
    return DeploymentEligibility("skip", f"could not read remote feature head: {error}")
  if feature_sha != sha:
    return DeploymentEligibility("skip", "remote feature head no longer matches this event")
  return DeploymentEligibility("preview")


def remote_ref(ref: str) -> str:
  """Read one exact remote ref without moving the checked-out candidate."""
  result = subprocess.run(
      ["git", "ls-remote", "--refs", "origin", ref], cwd=ROOT, check=True,
      capture_output=True, text=True)
  lines = [line.split("\t", 1) for line in result.stdout.splitlines()]
  matches = [sha for sha, name in lines if name == ref and SHA.fullmatch(sha)]
  if len(matches) != 1:
    raise ValueError(f"remote ref is unavailable: {ref}")
  return matches[0]


def remote_project_version(ref: str) -> str | None:
  """Read project version from a freshly fetched exact remote revision."""
  remote_sha = remote_ref(ref)
  subprocess.run(
      ["git", "fetch", "--no-tags", "--depth=1", "origin", remote_sha], cwd=ROOT, check=True,
      capture_output=True, text=True)
  result = subprocess.run(
      ["git", "show", f"{remote_sha}:pyproject.toml"], cwd=ROOT, check=True,
      capture_output=True, text=True)
  return package_version(project_metadata(result.stdout))


def local_project_version() -> str | None:
  """Read the checked-out project's declared version."""
  return package_version(project_metadata((ROOT / "pyproject.toml").read_text(encoding="utf-8")))


def project_metadata(text: str) -> dict | None:
  """Read TOML metadata when the deployed interpreter provides its parser."""
  try:
    import tomllib
  except ModuleNotFoundError:
    return None
  try:
    metadata = tomllib.loads(text)
  except tomllib.TOMLDecodeError:
    return None
  return metadata if isinstance(metadata, dict) else None


def package_version(metadata: object) -> str | None:
  """Read either supported project metadata version declaration."""
  project = metadata.get("project") if isinstance(metadata, dict) else None
  version = project.get("version") if isinstance(project, dict) else None
  if isinstance(version, str):
    return version
  tool = metadata.get("tool") if isinstance(metadata, dict) else None
  poetry = tool.get("poetry") if isinstance(tool, dict) else None
  version = poetry.get("version") if isinstance(poetry, dict) else None
  return version if isinstance(version, str) else None


def write_github_output(path: Path, decision: DeploymentEligibility) -> None:
  """Write the deployment result for a GitHub Actions step."""
  with path.open("a", encoding="utf-8") as output:
    output.write(f"mode={decision.mode}\n")
    output.write(f"reason={decision.reason or ''}\n")


def check_deployment(args: argparse.Namespace) -> int:
  """Evaluate the live checkout and remote refs for a pending deployment."""
  project_version = (
      local_project_version()
      if args.event_name == "push" and args.ref == PREVIEW_REF
      else ""
  )
  decision = deployment_eligibility(
      event_name=args.event_name,
      ref=args.ref,
      sha=args.sha,
      project_version=project_version or "",
      read_remote_project_version=remote_project_version,
      read_remote_ref=remote_ref,
  )
  if args.github_output is not None:
    write_github_output(args.github_output, decision)
  print(decision.mode if decision.reason is None else f"{decision.mode}: {decision.reason}")
  return 0


def main() -> int:
  """Parse the preparation command and create its selected artifact."""
  parser = argparse.ArgumentParser(description=__doc__)
  commands = parser.add_subparsers(dest="command", required=True)
  command = commands.add_parser("prepare")
  command.add_argument("--mode", choices=("preview", "stable"), required=True)
  command.add_argument("--sha", required=True)
  command.add_argument("--output", type=Path, required=True)
  eligibility = commands.add_parser("deployment-eligibility")
  eligibility.add_argument("--event-name", required=True)
  eligibility.add_argument("--ref", required=True)
  eligibility.add_argument("--sha", required=True)
  eligibility.add_argument("--github-output", type=Path)
  args = parser.parse_args()
  if SHA.fullmatch(args.sha) is None:
    parser.error("--sha must be a 40-character lowercase hexadecimal revision")
  try:
    if args.command == "prepare":
      prepare(args.mode, args.sha, args.output)
    else:
      return check_deployment(args)
  except (OSError, subprocess.CalledProcessError, ValueError) as error:
    parser.error(str(error))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
