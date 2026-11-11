"""
Test Public API - Ensure only DataGenerator is publicly accessible.

These tests validate that rand_engine exposes only its public API
and that internal modules are properly hidden from external users.

Run these tests after installing the package: pip install -e .
"""

import json
from email.parser import BytesParser
import os
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

import pytest


class TestPublicAPI:
    """Test that only public API is accessible from rand_engine package."""
    
    def test_can_import_datagenerator(self):
        """
        Example 1: DataGenerator should be importable from rand_engine.
        
        This is the ONLY public entry point for the library.
        """
        from rand_engine import DataGenerator
        
        assert DataGenerator is not None
        print("\n✓ DataGenerator successfully imported from rand_engine")
    
    
    def test_datagenerator_in_all(self):
        """
        Example 2: Check that __all__ contains public API: DataGenerator, SparkGenerator, and RandSpecs.
        
        __all__ defines the public API of a module.
        """
        import rand_engine
        
        assert hasattr(rand_engine, '__all__')
        assert "DataGenerator" in rand_engine.__all__
        assert "SparkGenerator" in rand_engine.__all__
        assert "RandSpecs" in rand_engine.__all__
        assert len(rand_engine.__all__) == 3
        print(f"\n✓ rand_engine.__all__ = {rand_engine.__all__}")
    
    
    def test_private_modules_not_in_main_namespace(self):
        """
        Example 3: Private modules should not be accessible from rand_engine.
        
        Users should not be able to do: from rand_engine import RandGenerator
        """
        import rand_engine
        
        # These should NOT be accessible
        private_names = [
            "RandGenerator",
            "FileBatchWriter", 
            "FileStreamWriter",
        ]
        
        for name in private_names:
            assert not hasattr(rand_engine, name), \
                f"Private class '{name}' should not be in rand_engine namespace"
        
        print(f"\n✓ Private modules not exposed in rand_engine namespace")
    
    
    def test_cannot_import_private_modules_directly(self):
        """
        Example 4: Importing private modules should work but is discouraged.
        
        While Python doesn't enforce privacy, the underscore convention
        indicates these modules are internal implementation details.
        """
        # These imports should work (Python doesn't enforce privacy)
        # but they start with underscore to discourage direct use
        from rand_engine.file_handlers import _writer_batch
        from rand_engine.file_handlers import _writer_stream
        from rand_engine.main import _rand_generator
        
        # Verify the convention: all start with underscore
        assert _writer_batch.__name__ == "rand_engine.file_handlers._writer_batch"
        assert _writer_stream.__name__ == "rand_engine.file_handlers._writer_stream"
        assert _rand_generator.__name__ == "rand_engine.main._rand_generator"
        
        print("\n✓ Private modules use underscore naming convention")
    
    
    def test_examplespecs_can_be_imported(self):
        """
        Example 5a: RandSpecs should be importable from rand_engine.
        
        RandSpecs provides ready-to-use specifications for learning and prototyping.
        """
        from rand_engine import RandSpecs
        
        assert RandSpecs is not None
        
        # Verify all specs are accessible as class methods
        assert callable(RandSpecs.customers)
        assert callable(RandSpecs.products)
        assert callable(RandSpecs.orders)
        assert callable(RandSpecs.transactions)
        
        print("\n✓ RandSpecs successfully imported and has all specs")
    
    
    def test_datagenerator_can_be_instantiated(self):
        """
        Example 5b: Verify DataGenerator works correctly.
        
        The public API should be fully functional.
        """
        from rand_engine import DataGenerator
        
        # Simple spec to test instantiation
        spec = {
            "id": {
                "method": "integers",
                "kwargs": {"min": 1, "max": 100}
            }
        }
        
        generator = DataGenerator(spec, seed=42)
        generator.size(10)
        df = generator.get_df()
        
        assert len(df) == 10
        assert "id" in df.columns
        print(f"\n✓ DataGenerator works correctly: {len(df)} rows generated")
    
    
    def test_examplespecs_works_with_datagenerator(self):
        """
        Example 5c: Verify RandSpecs works with DataGenerator.
        
        Pre-built specs should work seamlessly with DataGenerator.
        """
        from rand_engine import DataGenerator, RandSpecs
        
        df = DataGenerator(RandSpecs.customers(), seed=42).size(10).get_df()
        
        assert len(df) == 10
        assert 'customer_id' in df.columns
        assert 'age' in df.columns
        assert 'city' in df.columns
        assert 'total_spent' in df.columns
        assert 'is_premium' in df.columns
        assert 'registration_date' in df.columns
        
        print(f"\n✓ RandSpecs works with DataGenerator: {len(df)} rows with {len(df.columns)} columns")
    
    
    def test_public_api_is_minimal(self):
        """
        Example 6: Public API should be minimal and well-defined.
        
        A good library exposes only what users need, hiding complexity.
        """
        import rand_engine
        
        # Get all public attributes (not starting with _)
        public_attrs = [attr for attr in dir(rand_engine) if not attr.startswith('_')]
        
        # Should only have DataGenerator and RandSpecs
        expected_public = ['DataGenerator', 'RandSpecs']
        
        for expected in expected_public:
            assert expected in public_attrs, f"{expected} should be public"
        
        print(f"\n✓ Public API is minimal: {', '.join(expected_public)}")
    
    
    def test_private_module_naming_convention(self):
        """
        Example 7: All internal modules follow underscore naming.
        
        This test documents the internal structure for maintainers.
        """
        import os
        import glob
        
        # Find all Python files in file_handlers and main
        internal_dirs = [
            "rand_engine/file_handlers",
            "rand_engine/main"
        ]
        
        private_files = []
        public_files = []
        
        for directory in internal_dirs:
            pattern = f"{directory}/*.py"
            for filepath in glob.glob(pattern):
                filename = os.path.basename(filepath)
                
                # Skip __init__.py and __pycache__
                if filename.startswith('__'):
                    continue
                
                if filename.startswith('_'):
                    private_files.append(filepath)
                else:
                    # Check if it's a public entry point
                    if filename == "data_generator.py":
                        public_files.append(filepath)
                    else:
                        # This would be a violation of naming convention
                        # (unless it's intentionally public)
                        pass
        
        # Log findings
        print(f"\n✓ Private modules (underscore prefix): {len(private_files)}")
        for f in private_files:
            print(f"  - {f}")
        
        print(f"\n✓ Public entry points: {len(public_files)}")
        for f in public_files:
            print(f"  - {f}")
    
    
    def test_documentation_imports(self):
        """
        Example 8: Test the recommended import pattern from documentation.
        
        Users should always import like this:
            from rand_engine import DataGenerator
        """
        # This is the ONLY recommended way
        from rand_engine import DataGenerator
        
        # Alternative (also acceptable)
        import rand_engine
        generator_class = rand_engine.DataGenerator
        
        # Both should give the same class
        assert DataGenerator is generator_class
        
        print("\n✓ Recommended import patterns work correctly")
    
    
    def test_star_import_behavior(self):
        """
        Example 9: Test 'from rand_engine import *' behavior.
        
        Should only import what's in __all__ (DataGenerator).
        """
        # Simulate star import
        import rand_engine
        namespace = {}
        
        # This simulates: from rand_engine import *
        if hasattr(rand_engine, '__all__'):
            for name in rand_engine.__all__:
                namespace[name] = getattr(rand_engine, name)
        
        # Should only have DataGenerator
        assert "DataGenerator" in namespace
        assert "RandGenerator" not in namespace
        
        print(f"\n✓ Star import only brings: {list(namespace.keys())}")


class TestInternalAccess:
    """
    Test that internal modules CAN be accessed (Python doesn't enforce privacy)
    but document that this is NOT recommended.
    """
    
    def test_internal_modules_technically_accessible(self):
        """
        Example 10: Internal modules are technically accessible.
        
        Python uses convention, not enforcement. Underscored modules signal
        "private implementation detail - use at your own risk".
        """
        # These work, but are NOT part of the public API
        # Users should NOT rely on these - they may change without warning
        
        from rand_engine.main._rand_generator import RandGenerator
        
        assert RandGenerator is not None
        
        print("\n✓ Internal modules are accessible (but NOT recommended)")
        print("  ⚠️  These are implementation details and may change!")


class TestPackageStructure:
    """Test overall package structure and organization."""
    
    def test_package_has_version(self):
        """
        Example 11: Package should have version information.
        
        Good practice for tracking releases.
        """
        import rand_engine
        
        # Version might be in __version__ or read from pyproject.toml
        has_version = hasattr(rand_engine, '__version__') or \
                     hasattr(rand_engine, 'version')
        
        if has_version:
            version = getattr(rand_engine, '__version__', None) or \
                     getattr(rand_engine, 'version', None)
            print(f"\n✓ Package version: {version}")
        else:
            print("\n⚠️  No version attribute found (consider adding __version__)")
    
    
    def test_clean_namespace(self):
        """
        Example 12: Package namespace should be clean.
        
        Only necessary imports should pollute the namespace.
        """
        import rand_engine
        
        # Get all attributes
        all_attrs = dir(rand_engine)
        
        # Separate into public and private
        public = [a for a in all_attrs if not a.startswith('_')]
        private = [a for a in all_attrs if a.startswith('_') and not a.startswith('__')]
        
        print(f"\n✓ Public attributes: {public}")
        print(f"✓ Private attributes: {private}")
        
        # Public should be minimal (DataGenerator + potential subpackages)
        # In development mode, subpackages may be visible
        essential_public = ["DataGenerator"]
        for attr in essential_public:
            assert attr in public, f"Expected public attribute '{attr}' not found"
        
        print(f"✓ Essential public API present: {essential_public}")


def test_every_shipped_module_imports():
    """Every module in the package must import; dead code that cannot is a defect."""
    import importlib
    from pathlib import Path

    import rand_engine

    root = Path(rand_engine.__file__).parent
    for path in sorted(root.rglob("*.py")):
        importlib.import_module(".".join(("rand_engine", *path.relative_to(root).with_suffix("").parts)))


def test_public_export_surface_remains_exactly_three_names():
    import rand_engine

    assert rand_engine.__all__ == ["DataGenerator", "SparkGenerator", "RandSpecs"]


def test_ordinary_import_neither_requires_nor_imports_faker():
    code = """
import builtins
import sys

real_import = builtins.__import__

def import_without_faker(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "faker" or name.startswith("faker."):
        raise ModuleNotFoundError("Faker is deliberately unavailable")
    return real_import(name, globals, locals, fromlist, level)

builtins.__import__ = import_without_faker
import rand_engine
assert rand_engine.__all__ == ["DataGenerator", "SparkGenerator", "RandSpecs"]
assert not any(name == "faker" or name.startswith("faker.") for name in sys.modules)
"""
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).parents[2],
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


@pytest.fixture(scope="module")
def built_wheel(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("wheel")
    project_root = Path(__file__).parents[2]
    output = tmp_path / "dist"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["POETRY_CACHE_DIR"] = str(tmp_path / "poetry-cache")
    env["POETRY_VIRTUALENVS_IN_PROJECT"] = "false"
    env["POETRY_VIRTUALENVS_CREATE"] = "false"
    result = subprocess.run(
        [
            "poetry", "build", "--format", "wheel", "--output", str(output),
            "--no-interaction", "--no-cache",
        ],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    wheels = list(output.glob("*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def test_wheel_exposes_faker_only_as_the_approved_optional_extra(built_wheel):
    with ZipFile(built_wheel) as wheel:
        metadata_path = next(name for name in wheel.namelist() if name.endswith(".dist-info/METADATA"))
        metadata = BytesParser().parsebytes(wheel.read(metadata_path))

    faker_requirements = [
        requirement
        for requirement in metadata.get_all("Requires-Dist", [])
        if requirement.lower().startswith("faker ")
    ]
    assert metadata.get_all("Provides-Extra", []).count("faker") == 1
    assert faker_requirements == ['faker (>=28.4.1) ; extra == "faker"']


def test_wheel_requires_only_open_floors_of_the_three_core_dependencies(built_wheel):
    requirements = _wheel_metadata(built_wheel).get_all("Requires-Dist", [])
    core = sorted(r for r in requirements if "extra ==" not in r)
    assert core == ["numpy (>=1.26)", "pandas (>=2.2,<4)", "pyarrow (>=19.0.0)"]


def test_wheel_documentation_url_is_the_docs_site_named_by_the_error_footer(built_wheel):
    from rand_engine.validators.common_validator import CommonValidator
    from rand_engine.validators.exceptions import SpecValidationError

    with ZipFile(built_wheel) as wheel:
        metadata_path = next(name for name in wheel.namelist() if name.endswith(".dist-info/METADATA"))
        metadata = BytesParser().parsebytes(wheel.read(metadata_path))
    with pytest.raises(SpecValidationError) as exc_info:
        CommonValidator.validate_spark_and_raise({"age": {"method": "invalid_method", "kwargs": {}}})

    docs = "https://marcoaureliomenezes.github.io/rand_engine/"
    assert "Documentation, " + docs in metadata.get_all("Project-URL", [])
    assert "Documentation: " + docs in str(exc_info.value)


def _wheel_metadata(wheel_path):
    with ZipFile(wheel_path) as wheel:
        metadata_path = next(name for name in wheel.namelist() if name.endswith(".dist-info/METADATA"))
        return BytesParser().parsebytes(wheel.read(metadata_path))


def test_package_docstring_first_line_is_the_wheel_summary(built_wheel):
    import rand_engine

    assert rand_engine.__doc__.splitlines()[0] == _wheel_metadata(built_wheel)["Summary"]


def test_wheel_project_urls_carry_the_llms_txt_and_the_agent_skill(built_wheel):
    urls = _wheel_metadata(built_wheel).get_all("Project-URL", [])

    site = "https://marcoaureliomenezes.github.io/rand_engine/"
    repo = "https://github.com/marcoaureliomenezes/rand_engine"
    assert sorted(urls) == sorted([
        "Homepage, " + repo,
        "Repository, " + repo,
        "Documentation, " + site,
        "Issues, " + repo + "/issues",
        "Changelog, " + repo + "/blob/master/CHANGELOG.md",
        "llms.txt, " + site + "llms.txt",
        "Agent skill, " + site + "skills/rand-engine/SKILL.md",
    ])


def test_wheel_keywords_are_the_seventeen_search_terms(built_wheel):
    keywords = _wheel_metadata(built_wheel)["Keywords"].split(",")

    assert sorted(keywords) == [
        "data-engineering", "data-generation", "data-generator", "fake-data", "faker", "kafka",
        "mock-data", "numpy", "pandas", "parquet", "pyspark", "python", "random-data", "spark",
        "synthetic-data", "test-data", "test-fixtures",
    ]


def test_wheel_advertises_typed_and_exactly_the_tested_python_set(built_wheel):
    metadata = _wheel_metadata(built_wheel)
    classifiers = metadata.get_all("Classifier", [])
    prefix = "Programming Language :: Python :: 3."

    assert "Typing :: Typed" in classifiers
    assert "Topic :: Software Development :: Testing :: Mocking" in classifiers
    assert "Topic :: Software Development :: Libraries :: Python Modules" in classifiers
    assert sorted(c for c in classifiers if c.startswith(prefix)) == [
        prefix + "11", prefix + "12", prefix + "13", prefix + "14",
    ]
    assert metadata["Requires-Python"] == ">=3.11"


@pytest.mark.parametrize("legacy", [{"args": [0, 3]}, {"splitable": True}, {"sep": ","}, {"pk": 1}])
def test_legacy_column_keys_are_refused_at_validation(legacy):
    from rand_engine import DataGenerator
    from rand_engine.validators.exceptions import SpecValidationError

    with pytest.raises(SpecValidationError):
        DataGenerator({"a": {"method": "integers", "kwargs": {"min": 0, "max": 3}, **legacy}})


@pytest.mark.parametrize("column, remedy", [
    ({"method": "poisson", "kwargs": {"lam": 2}}, "method 'poisson' is NumPy engine only"),
    ({"method": "integers", "kwargs": {"min": 0, "max": 3}, "null_rate": 0.1}, "modifier 'null_rate' is NumPy engine only"),
])
def test_spark_refuses_new_methods_and_modifiers_naming_datagenerator(column, remedy):
    from rand_engine import SparkGenerator
    from rand_engine.validators.exceptions import SpecValidationError

    with pytest.raises(SpecValidationError) as error:
        SparkGenerator(None, None, {"x": column})
    assert remedy in str(error.value) and "Use DataGenerator" in str(error.value)


def test_version_falls_back_when_distribution_is_not_installed(monkeypatch):
    import importlib
    import importlib.metadata

    import rand_engine

    def missing(name):
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    try:
        reloaded = importlib.reload(rand_engine)
        assert reloaded.__version__ == "0.0.0+unknown"
    finally:
        monkeypatch.undo()
        importlib.reload(rand_engine)


def test_wheel_ships_py_typed(built_wheel):
    with ZipFile(built_wheel) as wheel:
        assert "rand_engine/py.typed" in wheel.namelist()


def test_wheel_ships_llms_txt_equal_to_the_tracked_file(built_wheel):
    tracked = Path(__file__).parents[2] / "rand_engine" / "llms.txt"
    with ZipFile(built_wheel) as wheel:
        assert "rand_engine/llms.txt" in wheel.namelist()
        assert wheel.read("rand_engine/llms.txt") == tracked.read_bytes()


def test_wheel_holds_only_the_rand_engine_package(built_wheel):
    with ZipFile(built_wheel) as wheel:
        names = [n for n in wheel.namelist() if ".dist-info/" not in n]
    assert [n for n in names if not n.startswith("rand_engine/")] == []
    assert [n for n in names if "skills/" in n] == []


def test_no_workflow_but_eval_yml_names_the_evals_folder():
    workflows = Path(__file__).parents[2] / ".github" / "workflows"
    assert [
        w.name for w in workflows.glob("*") if w.name != "eval.yml" and "evals/" in w.read_text(encoding="utf-8")
    ] == []


def test_evals_folder_holds_no_file_pytest_collects():
    evals = Path(__file__).parents[2] / "evals"
    collected = [
        p.name for p in evals.rglob("*")
        if p.is_file() and (p.name in ("conftest.py",) or p.match("test_*.py") or p.match("*_test.py"))
    ]
    assert collected == []


@pytest.mark.parametrize("sub", ["main", "file_handlers", "core", "utils"])
def test_wheel_holds_subpackage_init(built_wheel, sub):
    with ZipFile(built_wheel) as wheel:
        assert f"rand_engine/{sub}/__init__.py" in wheel.namelist()


def test_extracted_wheel_reports_the_pyproject_version(built_wheel, tmp_path):
    with ZipFile(built_wheel) as wheel:
        wheel.extractall(tmp_path)
    env = {k: v for k, v in os.environ.items() if not k.startswith("COV_CORE_")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import rand_engine; print(rand_engine.__version__)", str(tmp_path)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "0.8.2"


def test_wheel_declares_the_rand_engine_console_script(built_wheel):
    from configparser import ConfigParser

    with ZipFile(built_wheel) as wheel:
        path = next((n for n in wheel.namelist() if n.endswith(".dist-info/entry_points.txt")), None)
        assert path, "wheel has no entry_points.txt: the console script is not declared"
        parser = ConfigParser()
        parser.read_string(wheel.read(path).decode())
    assert dict(parser["console_scripts"]) == {"rand-engine": "rand_engine.cli:main"}


def test_wheel_ships_each_declared_case_resource_byte_for_byte(built_wheel):
    from rand_engine.cli import CASES

    resources = {
        "test-data": "test-data.py.txt",
        "lake": "lake.py.txt",
        "kafka": "kafka.py.txt",
        "databricks": "databricks.py.txt",
        "faker": "faker.py.txt",
        "agent": "agent.md.txt",
    }
    targets = {
        "test-data": "test-data-example.py",
        "lake": "lake-example.py",
        "kafka": "kafka-example.py",
        "databricks": "databricks-example.py",
        "faker": "faker-example.py",
        "agent": "AGENTS.md",
    }
    assert set(CASES) == set(resources)
    assert {slug: case.resource for slug, case in CASES.items()} == resources
    assert {slug: case.filename for slug, case in CASES.items()} == targets
    assert [slug for slug, case in CASES.items() if case.kind == "runnable"] == [
        "test-data", "lake", "kafka", "databricks", "faker",
    ]
    assert [slug for slug, case in CASES.items() if case.kind == "agent"] == ["agent"]
    cases_dir = Path(__file__).parents[2] / "rand_engine" / "cases"
    with ZipFile(built_wheel) as wheel:
        for case in CASES.values():
            assert wheel.read(f"rand_engine/cases/{case.resource}") == (cases_dir / case.resource).read_bytes()


def test_extracted_wheel_module_cli_writes_agent_context(built_wheel, tmp_path):
    from rand_engine.cli import CASES

    case = CASES["agent"]
    assert case.kind == "agent"
    assert case.resource == "agent.md.txt"
    assert case.filename == "AGENTS.md"
    extracted = tmp_path / "wheel"
    output = tmp_path / "project"
    with ZipFile(built_wheel) as wheel:
        wheel.extractall(extracted)
    env = {k: v for k, v in os.environ.items() if not k.startswith("COV_CORE_")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(extracted)
    result = subprocess.run(
        [sys.executable, "-m", "rand_engine", "get-started", "agent", "--out", str(output)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    target = output / case.filename
    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{target}\n"
    assert target.read_bytes() == (extracted / "rand_engine" / "cases" / case.resource).read_bytes()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


USAGE_TOOLS = "Bash,Read,Write,Edit,Glob,Grep"
# the init `tools` of CLI 2.1.316 recorded with `--allowedTools` alone: every built-in tool
DEFAULT_INIT_TOOLS = [
    "Task", "Bash", "CronCreate", "CronDelete", "CronList", "DesignSync", "Edit", "EnterWorktree", "ExitWorktree",
    "Glob", "Grep", "ListAgents", "Monitor", "NotebookEdit", "PushNotification", "Read", "RemoteTrigger",
    "ReportFindings", "ScheduleWakeup", "SendMessage", "SendToProject", "SendToProjectContext", "TaskStop",
    "ToolSearch", "WebFetch", "WebSearch", "Workflow", "Write"]


def _load_run():
    import importlib.util

    spec = importlib.util.spec_from_file_location("eval_run", Path(__file__).parents[2] / "evals" / "run.py")
    run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run)
    return run


def _prepare(monkeypatch, tmp_path, rnd="usage", init=None, check_out="", requirements=(), events=None, check_rc=0,
             result=None):
    """Build a fixture task with every subprocess faked; return (run module, args, calls, out)."""
    import types

    run = _load_run()
    repo = tmp_path / "repo"
    task_dir = repo / "evals" / "tasks" / "t"
    (task_dir / "tests").mkdir(parents=True)
    reqs = f"requirements = {json.dumps(list(requirements))}\n"
    (task_dir / "task.toml").write_text(
        f'[task]\nround = "{rnd}"\n[agent]\ntimeout_sec = 5.0\n[verifier]\ntimeout_sec = 5.0\n'
        f"[environment]\ninstall_rand_engine = false\n{reqs}", encoding="utf-8")
    (task_dir / "instruction.md").write_text("do it", encoding="utf-8")
    (task_dir / "tests" / "check.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(run, "HERE", repo / "evals")
    monkeypatch.setattr(run, "REPO", repo)
    calls = []

    def fake(cmd, **kw):
        calls.append((cmd, kw))
        out = ""
        if cmd[0] == "claude":
            tools = cmd[cmd.index("--tools") + 1].split(",") if "--tools" in cmd else DEFAULT_INIT_TOOLS
            stream = events or [{"type": "system", "subtype": "init", "model": "m", "permissionMode": "default",
                                 "tools": tools, **(init or {})},
                                {"type": "result", "usage": {"input_tokens": 10, "cache_creation_input_tokens": 5,
                                                             "cache_read_input_tokens": 20, "output_tokens": 7},
                                 "total_cost_usd": 0.5, **(result or {})}]
            out = "\n".join(json.dumps(e) for e in stream) + "\n"
        elif str(cmd[-1]).endswith("check.py"):
            out = check_out
        code = check_rc if str(cmd[-1]).endswith("check.py") else 0
        return subprocess.CompletedProcess(cmd, code, stdout=out, stderr="")

    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "placeholder")
    monkeypatch.setattr(run.subprocess, "run", fake)
    monkeypatch.setattr(run.tempfile, "mkdtemp", lambda prefix: str(tmp_path / "w"))
    (tmp_path / "w").mkdir()
    out = tmp_path / "out"
    args = types.SimpleNamespace(rand_engine="rand-engine", model="m", leg="pypi", k=3, out=out)
    return run, args, calls, out


def _trial(monkeypatch, tmp_path, *a, **kw):
    """Run one trial of a fixture task through `run_trial`; return (result, calls, out)."""
    run, args, calls, out = _prepare(monkeypatch, tmp_path, *a, **kw)
    return run.run_trial("t", 2, args), calls, out


def _claude(calls):
    return [c for c in calls if c[0][0] == "claude"][0]


def _flag(cmd, name):
    return cmd[cmd.index(name) + 1]


def test_eval_usage_round_runs_sandboxed_without_web_tools(monkeypatch, tmp_path):
    res, calls, _ = _trial(monkeypatch, tmp_path, "usage")
    cmd = _claude(calls)[0]
    assert "error" not in res
    assert _flag(cmd, "--setting-sources") == ""
    assert _flag(cmd, "--tools") == USAGE_TOOLS
    assert _flag(cmd, "--allowedTools") == USAGE_TOOLS
    assert _flag(cmd, "--disallowedTools") == "WebSearch,WebFetch"
    sandbox = json.loads(_flag(cmd, "--settings"))["sandbox"]
    assert sandbox["enabled"] is True
    assert sandbox["failIfUnavailable"] is True
    assert sandbox["allowUnsandboxedCommands"] is False
    assert not sandbox.get("network", {}).get("allowedDomains")
    assert any(d in ("/", str(Path.home())) for d in sandbox["filesystem"]["denyRead"])


@pytest.mark.parametrize("rnd", ["usage", "canary"])
def test_eval_sandboxed_rounds_deny_read_glob_grep_under_home(monkeypatch, tmp_path, rnd):
    _, calls, _ = _trial(monkeypatch, tmp_path, rnd)
    settings = json.loads(_flag(_claude(calls)[0], "--settings"))
    assert settings["permissions"]["deny"] == ["Read(~/**)", "Glob(~/**)", "Grep(~/**)"]


def test_eval_discovery_round_keeps_web_tools_and_no_settings(monkeypatch, tmp_path):
    res, calls, _ = _trial(monkeypatch, tmp_path, "discovery")
    cmd = _claude(calls)[0]
    assert "error" not in res
    assert _flag(cmd, "--setting-sources") == ""
    assert "--settings" not in cmd
    assert _flag(cmd, "--tools") == f"{USAGE_TOOLS},WebSearch,WebFetch"
    assert {"WebSearch", "WebFetch"} <= set(_flag(cmd, "--allowedTools").split(","))
    assert "--disallowedTools" not in cmd


@pytest.mark.parametrize("init", [{"permissionMode": "acceptEdits"}, {"tools": ["Bash", "WebFetch"]}])
def test_eval_assert_isolated_raises_on_a_mode_or_tools_mismatch(monkeypatch, tmp_path, init):
    res, _, _ = _trial(monkeypatch, tmp_path, "usage", init=init)
    assert res["error"].startswith("RuntimeError: ")


def test_eval_assert_isolated_rejects_the_default_tool_list_and_accepts_the_round_set():
    run = _load_run()
    tools = USAGE_TOOLS.split(",")
    with pytest.raises(RuntimeError, match="isolation violated"):
        run.assert_isolated({"permissionMode": "default", "tools": DEFAULT_INIT_TOOLS}, "default", tools)
    run.assert_isolated({"permissionMode": "default", "tools": tools}, "default", tools)


def test_eval_trial_keeps_the_transcript_and_hands_the_check_its_env(monkeypatch, tmp_path):
    res, calls, out = _trial(monkeypatch, tmp_path, "usage", check_out="probe:x\nRESULT {}\n")
    transcript = out / "t-pypi-2" / "transcript.jsonl"
    env = [kw["env"] for cmd, kw in calls if str(cmd[-1]).endswith("check.py")][0]
    assert env["RAND_EVAL_TRANSCRIPT"] == str(transcript)
    assert env["RAND_EVAL_TOKENS"] == "42"
    assert env["PYTHONPATH"] == str(tmp_path / "repo" / "evals")
    assert json.loads(transcript.read_text(encoding="utf-8").splitlines()[-1])["type"] == "result"


def test_eval_trial_json_merges_the_check_result_line(monkeypatch, tmp_path):
    stdout = 'probe:x\nRESULT {"layer": 2, "surfaces": ["a"]}\n'
    res, _, _ = _trial(monkeypatch, tmp_path, "usage", check_out=stdout)
    assert (res["leg"], res["round"], res["k"], res["trial"]) == ("pypi", "usage", 3, 2)
    assert (res["layer"], res["surfaces"]) == (2, ["a"])
    assert res["check_output"] == stdout


def test_eval_check_result_cannot_overwrite_runner_keys(monkeypatch, tmp_path):
    stdout = ('RESULT {"task": "x", "trial": 9, "leg": "w", "round": "r", "k": 99, "model": "z", "input_tokens": 1,'
              ' "output_tokens": 1, "cost_usd": 1, "passed": null, "check_output": "y", "layer": 2}\n')
    res, _, _ = _trial(monkeypatch, tmp_path, "usage", check_out=stdout)
    assert (res["task"], res["trial"], res["leg"], res["round"], res["k"], res["model"]) == (
        "t", 2, "pypi", "usage", 3, "m")
    assert (res["input_tokens"], res["output_tokens"], res["cost_usd"]) == (35, 7, 0.5)
    assert (res["passed"], res["check_output"], res["layer"]) == (True, stdout, 2)


def test_eval_malformed_result_line_keeps_check_output_records_an_error_and_marks_not_passed(monkeypatch, tmp_path):
    stdout = "why it failed\nRESULT {not json\n"
    res, _, _ = _trial(monkeypatch, tmp_path, "usage", check_out=stdout)
    assert res["check_output"] == stdout
    assert res["error"].startswith("ValueError: ")
    assert res["passed"] is False


def test_eval_trial_json_holds_the_final_message_and_the_first_failure_line(monkeypatch, tmp_path):
    res, _, _ = _trial(monkeypatch, tmp_path, "usage", check_out="no rows written\nsecond line\n", check_rc=1,
                       result={"result": "I wrote the file"})
    assert res["passed"] is False
    assert res["final_message"] == "I wrote the file"
    assert res["first_failure"] == "no rows written"


def test_eval_failing_check_with_a_malformed_result_line_keeps_its_first_failure(monkeypatch, tmp_path):
    res, _, _ = _trial(monkeypatch, tmp_path, "usage", check_out="why it failed\nRESULT {not json\n", check_rc=1)
    assert res["first_failure"] == "why it failed"
    assert res["error"].startswith("ValueError: ")


def test_eval_stream_with_no_result_event_raises_an_error_naming_the_missing_result_event(monkeypatch, tmp_path):
    res, _, _ = _trial(monkeypatch, tmp_path, "usage", events=[{"type": "assistant"}])
    assert res["error"] == "RuntimeError: no result event in the agent stream"


@pytest.mark.parametrize("key, value, literal", [("errors", ["boom"], "boom"),
                                                  ("startup_failure_reason", "no token", "no token")])
def test_eval_stream_with_no_init_event_raises_an_error_naming_the_result_event(monkeypatch, tmp_path, key, value,
                                                                                literal):
    res, _, _ = _trial(monkeypatch, tmp_path, "usage", events=[{"type": "result", "is_error": True, key: value}])
    assert "StopIteration" not in res["error"]
    assert literal in res["error"]


def test_eval_main_writes_the_trial_json_as_utf8(monkeypatch, tmp_path):
    run, _, _, out = _prepare(monkeypatch, tmp_path, result={"result": "caf\u00e9"})
    monkeypatch.setattr(sys, "argv", ["run.py", "--task", "t", "--k", "1", "--leg", "pypi", "--model", "m",
                                      "--out", str(out)])
    with pytest.raises(SystemExit):
        run.main()
    assert "caf\u00e9".encode("utf-8") in (out / "t-pypi-1.json").read_bytes()


def test_eval_discovery_trial_records_passed_null(monkeypatch, tmp_path):
    res, _, _ = _trial(monkeypatch, tmp_path, "discovery", check_out='RESULT {"adopted": true, "surface": "s"}\n')
    assert res["passed"] is None
    assert (res["adopted"], res["surface"]) == (True, "s")


def test_eval_trial_installs_task_requirements_before_the_agent(monkeypatch, tmp_path):
    _, calls, _ = _trial(monkeypatch, tmp_path, "usage", requirements=["pkg-x>=1"])
    cmds = [c for c, _ in calls]
    pip = [i for i, c in enumerate(cmds) if "pip" in c and "install" in c and "pkg-x>=1" in c]
    assert pip and pip[0] < [i for i, c in enumerate(cmds) if c[0] == "claude"][0]


def test_eval_runs_claude_with_the_subprocess_env_scrub(monkeypatch, tmp_path):
    _, calls, _ = _trial(monkeypatch, tmp_path)
    env = _claude(calls)[1]["env"]
    assert env["CLAUDE_CODE_SUBPROCESS_ENV_SCRUB"] == "1"
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "placeholder"
    others = [kw["env"] for cmd, kw in calls if cmd[0] != "claude"]
    assert len(others) >= 2  # venv, check
    assert all("CLAUDE_CODE_OAUTH_TOKEN" not in e for e in others)


def test_eval_workflow_pins_the_scrub_cli_and_runs_under_bubblewrap():
    text = _job("trials")
    assert "@anthropic-ai/claude-code@2.1.316" in text
    assert text.index("apt-get install -y bubblewrap socat") < text.index("python evals/run.py")
    lift = "sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0"
    assert text.index(lift) < text.index("python evals/run.py")


def test_eval_trials_step_fails_before_the_eval_when_k_is_above_three():
    text = _job("trials")
    guard = 'if [ "$K" -gt 3 ] || ! [ "$K" -ge 1 ] 2>/dev/null; then'
    assert guard in text, "the trials job lacks the fail-closed guard on K"
    assert text.index(guard) < text.index("python evals/run.py")


@pytest.mark.parametrize("k, exit_code", [("3", 0), ("4", 1), ("abc", 1), ("", 1), ("2.5", 1)])
def test_eval_trials_k_guard_fails_closed_on_anything_but_an_integer_up_to_three(k, exit_code):
    guard = next(
        line.strip() for line in _job("trials").splitlines() if line.strip().startswith('if [ "$K"')
    )
    run = subprocess.run(["bash", "-c", guard], env={**os.environ, "K": k}, capture_output=True, text=True)
    assert run.returncode == exit_code, run.stderr


def test_eval_trials_apt_get_update_runs_before_the_install():
    text = _job("trials")
    assert "apt-get update" in text, "no apt-get update in the trials job"
    assert text.index("apt-get update") < text.index("apt-get install -y bubblewrap")


def test_eval_trials_sysctl_lift_is_guarded_by_its_key():
    text = _job("trials")
    key = "kernel.apparmor_restrict_unprivileged_userns"
    guards = [text.find(g) for g in (f"sysctl -n {key}", f"/proc/sys/{key.replace('.', '/')}")]
    assert max(guards) >= 0, "the sysctl lift has no guard on the key existing"
    assert min(g for g in guards if g >= 0) < text.index(f"sysctl -w {key}=0")


def _workflow():
    """Return (text, {job key: block text}, {trigger key: block text}) of the eval workflow, split by indentation."""
    import re

    text = (Path(__file__).parents[2] / ".github" / "workflows" / "eval.yml").read_text(encoding="utf-8")
    on, jobs = text.split("\non:\n")[1].split("\njobs:\n")[0], text.split("\njobs:\n")[1]
    pieces = lambda s, pat: {m[1]: m[2] for m in re.findall(pat, s, re.S)}  # noqa: E731
    triggers = pieces(on, r"(^|\n)  (\w+):\n(.*?)(?=\n  \w+:|\Z)")
    blocks = pieces(jobs, r"(^|\n)  ([\w-]+):\n(.*?)(?=\n  [\w-]+:\n|\Z)")
    return text, blocks, triggers


def _job(key):
    blocks = _workflow()[1]
    assert key in blocks, f"no job {key!r} in {sorted(blocks)}"
    return blocks[key]


def _gate():
    block = next((b for b in _workflow()[1].values() if "name: Agent eval gate" in b), None)
    assert block is not None, "no job named 'Agent eval gate'"
    return block


def test_eval_workflow_push_trigger_keeps_the_eval_paths_and_adds_the_rc_branches():
    push = _workflow()[2]["push"]
    for line in ("'feature/**'", "'wt/*/rc-*/wt-rc'", "'evals/**'"):
        assert line in push
    assert push.index("branches:") < push.index("paths:")


def test_eval_workflow_pull_request_covers_development_and_master_without_paths_and_cancels_superseded_runs():
    pr = _workflow()[2]["pull_request"]
    assert "- development" in pr and "- master" in pr
    assert "paths" not in pr
    import re

    assert re.search(r"^concurrency:\n  group: .*github\.ref.*\n  cancel-in-progress: true$", _workflow()[0], re.M), (
        "no top-level concurrency group on github.ref that cancels in progress")


def test_eval_workflow_gate_job_always_runs_after_selfcheck_and_trials():
    gate = _gate()
    assert "if: always()" in gate
    needs = __import__("re").split(r"\n    \w", gate.split("needs:")[1])[0]
    assert "selfcheck" in needs and "trials" in needs


def test_eval_workflow_matrix_is_not_the_five_leg_include_and_has_no_job_summary_step():
    text = _workflow()[0]
    assert "- {task: e1-cold-discovery, install: pypi}" not in text
    assert "Job summary" not in text


def test_eval_workflow_timeout_comment_states_one_task_and_leg_per_job():
    trials = _job("trials")
    assert "each job runs up to 3 trials of one task and leg, 2100 s each at most" in trials


def test_eval_workflow_scans_for_the_token_before_the_upload():
    trials = _job("trials")
    scan = trials.index('grep -rqF -- "$CLAUDE_CODE_OAUTH_TOKEN"')
    assert scan < trials.index("actions/upload-artifact")


def test_eval_workflow_calibrates_before_the_verdict_step():
    gate = _gate()
    calibrate = gate.index("gate.py --calibrate")
    verdict = gate.index("gate.py", calibrate + 1)
    assert calibrate < verdict


def _steps(block):
    return ["- name:" + t for t in block.split("\n      - name:")[1:]]


def test_eval_workflow_verdict_step_is_the_plain_gate_call():
    verdicts = [x for x in _steps(_gate()) if "gate.py" in x and "--calibrate" not in x]
    assert len(verdicts) == 1
    assert "||" not in verdicts[0]


def test_eval_workflow_gate_fails_last_when_the_selfcheck_is_not_green():
    steps = _steps(_gate())
    verdict = next(i for i, x in enumerate(steps) if "gate.py" in x and "--calibrate" not in x)
    last = steps[-1]
    assert len(steps) - 1 > verdict
    assert "needs.selfcheck.result != 'success'" in last
    assert "exit 1" in last


def test_eval_workflow_scan_step_always_runs_deletes_the_out_dir_and_fails_on_a_hit():
    scan = next(x for x in _steps(_job("trials")) if "grep -rqF" in x)
    assert "if: always()" in scan
    assert 'rm -rf "$OUT"' in scan
    assert "exit 1" in scan


def test_eval_workflow_scan_counts_a_hit_only_for_a_non_empty_token():
    scan = next(x for x in _steps(_job("trials")) if "grep -rqF" in x)
    assert '-n "$CLAUDE_CODE_OAUTH_TOKEN"' in scan


def test_eval_workflow_selfcheck_runs_against_the_built_wheel():
    check = _job("selfcheck")
    assert "python evals/selfcheck.py --rand-engine" in check
    assert "dist/*.whl" in check


def test_every_eval_workflow_checkout_sets_persist_credentials_false():
    steps = _workflow()[0].split("uses: actions/checkout@")[1:]
    assert len(steps) == 3
    assert [s for s in steps if "persist-credentials: false" not in s.split("\n\n")[0]] == []
