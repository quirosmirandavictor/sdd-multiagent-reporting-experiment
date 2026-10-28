"""Integración real pendiente hasta recibir el parser A; sin reemplazos."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys

import pytest

from reporting.xlsx_output import build_xlsx
from test_xlsx_output import xml_parts, NS

parser = pytest.importorskip("reporting.yaml_input", reason="Pendiente integración del parser A")
ROOT = Path(__file__).resolve().parents[1]


def test_real_example_and_cli(tmp_path):
    source = ROOT / "examples/report.yaml"
    report = parser.parse_report(source.read_text(encoding="utf-8"))
    original = deepcopy(report)
    parts = xml_parts(build_xlsx(report))
    assert report == original
    assert parts["xl/tables/table1.xml"].attrib["ref"] == "A3:B5"
    assert parts["xl/charts/chart1.xml"].find(".//c:barDir", NS).attrib["val"] == "col"
    target = tmp_path / "report.xlsx"
    result = subprocess.run([sys.executable, "-m", "reporting", "--input", str(source),
                             "--output", str(target)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    xml_parts(target.read_bytes())
    assert str(target.resolve()) in result.stdout


@pytest.mark.parametrize("text", ["schema_version: 2", "styles: {color: red}", "rows: ["])
def test_real_invalid_input(tmp_path, text):
    source = tmp_path / "invalid.yaml"
    source.write_text(text, encoding="utf-8")
    target = tmp_path / "invalid.xlsx"
    result = subprocess.run([sys.executable, "-m", "reporting", "--input", str(source),
                             "--output", str(target)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 2
    assert not target.exists()


def test_real_literal_text_and_existing_target(tmp_path):
    text = (ROOT / "examples/report.yaml").read_text(encoding="utf-8")
    text = text.replace('"Ventas por región"', '"=1+1"').replace('"Norte"', '"https://example.com"')
    report = parser.parse_report(text)
    parts = xml_parts(build_xlsx(report))
    sheet = parts["xl/worksheets/sheet1.xml"]
    assert not sheet.findall(".//s:f", NS)
    assert not sheet.findall(".//s:hyperlink", NS)
    source = tmp_path / "literal.yaml"
    source.write_text(text, encoding="utf-8")
    target = tmp_path / "existing.xlsx"
    target.write_bytes(b"original")
    result = subprocess.run([sys.executable, "-m", "reporting", "--input", str(source),
                             "--output", str(target)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 1
    assert target.read_bytes() == b"original"
