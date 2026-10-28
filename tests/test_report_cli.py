import sys
from types import ModuleType
from pathlib import Path

import pytest

from reporting import __main__ as cli


@pytest.fixture
def setup_cli(tmp_path, monkeypatch):
    source = tmp_path / "report.yaml"
    source.write_text("entrada", encoding="utf-8")
    target = tmp_path / "report.xlsx"
    events = []
    module = ModuleType("reporting.yaml_input")
    def parse(text):
        events.append(("parse", text))
        return {"normalized": True}
    def build(report):
        assert not target.exists()
        events.append(("build", report))
        return b"complete bytes"
    module.parse_report = parse
    monkeypatch.setitem(sys.modules, "reporting.yaml_input", module)
    monkeypatch.setattr(cli, "build_xlsx", build)
    return source, target, events, module


def run(source, target):
    return cli.main(["--input", str(source), "--output", str(target)])


def test_success(setup_cli, capsys):
    source, target, events, _ = setup_cli
    assert run(source, target) == 0
    assert target.read_bytes() == b"complete bytes"
    assert events == [("parse", "entrada"), ("build", {"normalized": True})]
    assert capsys.readouterr().out == f"Reporte generado: {target.resolve()}\n"


@pytest.mark.parametrize("args", [[], ["--input", "x"], ["--input", "x", "--output", "x.txt"]])
def test_arguments(args):
    with pytest.raises(SystemExit) as error:
        cli.main(args)
    assert error.value.code == 2


def test_help(capsys):
    with pytest.raises(SystemExit) as error:
        cli.main(["--help"])
    assert error.value.code == 0
    assert "--input" in capsys.readouterr().out


def test_validation_stops_generation(setup_cli, capsys):
    source, target, events, module = setup_cli
    def invalid(text):
        raise ValueError("rows: fila incorrecta")
    module.parse_report = invalid
    assert run(source, target) == 2
    assert not events and not target.exists()
    assert "rows" in capsys.readouterr().err


@pytest.mark.parametrize("failure", ["missing", "utf8", "parent", "existing", "generation", "write", "permission"])
def test_errors(setup_cli, monkeypatch, capsys, failure):
    source, target, events, module = setup_cli
    if failure == "missing":
        source.unlink()
    elif failure == "utf8":
        source.write_bytes(b"\xff")
    elif failure == "parent":
        target = target.parent / "missing" / "report.xlsx"
    elif failure == "existing":
        target.write_bytes(b"original")
        monkeypatch.setattr(cli, "build_xlsx", lambda report: b"new")
    elif failure == "generation":
        def fail(report):
            raise RuntimeError("generation failed")
        monkeypatch.setattr(cli, "build_xlsx", fail)
    elif failure in ("write", "permission"):
        original = Path.open
        class BrokenWriter:
            def __enter__(self):
                self.stream = original(target, "xb")
                return self
            def write(self, data):
                self.stream.write(b"partial")
                raise OSError("disk full")
            def __exit__(self, *args):
                self.stream.close()
        def open_file(path, mode="r", *args, **kwargs):
            if path == target and mode == "xb":
                if failure == "permission":
                    raise PermissionError("denied")
                return BrokenWriter()
            return original(path, mode, *args, **kwargs)
        monkeypatch.setattr(Path, "open", open_file)
    assert run(source, target) == (2 if failure == "utf8" else 1)
    result = capsys.readouterr()
    assert not result.out and "Traceback" not in result.err
    assert "Error de" in result.err
    if failure == "existing":
        assert target.read_bytes() == b"original"
    else:
        assert not target.exists()
