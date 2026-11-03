"""Reference: reads the installed rand_engine/llms.txt and writes the URL of its writing-files page."""
import re
from pathlib import Path

import rand_engine

text = (Path(rand_engine.__file__).parent / "llms.txt").read_text(encoding="utf-8")
url = next(u for u in re.findall(r"\]\((https?://[^)\s]+)\)", text) if "WRITING_FILES" in u)
Path("answer.txt").write_text(url + "\n", encoding="utf-8")
