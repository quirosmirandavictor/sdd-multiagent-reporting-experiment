import pytest

from reporting.xlsx_output import build_xlsx
from test_xlsx_output import NS, xml_parts, report


@pytest.mark.parametrize("text", ["=1+1", "+SUM(A1:A2)", "-SUM(A1:A2)",
                                 "@SUM(A1:A2)", "https://example.com", "mailto:test@example.com"])
def test_literal_text_everywhere(report, text):
    report["title"] = text
    report["headers"][1] = text
    report["rows"][0][0] = text
    parts = xml_parts(build_xlsx(report))
    sheet = parts["xl/worksheets/sheet1.xml"]
    assert sheet.findall(".//s:f", NS) == []
    assert sheet.findall(".//s:hyperlink", NS) == []
    cells = {c.attrib["r"]: c for c in sheet.findall(".//s:c", NS)}
    strings = ["".join(s.itertext()) for s in parts["xl/sharedStrings.xml"].findall("s:si", NS)]
    for ref in ("A1", "B3", "A4"):
        assert cells[ref].attrib["t"] == "s"
        assert strings[int(cells[ref].find("s:v", NS).text)] == text
    assert cells["B5"].find("s:v", NS).text == "-90"


def test_generation_failure_chains_cause(report, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("simulated")
    monkeypatch.setattr("reporting.xlsx_output.xlsxwriter.Workbook", fail)
    with pytest.raises(RuntimeError) as error:
        build_xlsx(report)
    assert isinstance(error.value.__cause__, OSError)


def test_close_failure_chains_cause(report, monkeypatch):
    def fail(self):
        raise OSError("simulated close failure")
    monkeypatch.setattr("reporting.xlsx_output.xlsxwriter.Workbook.close", fail)
    with pytest.raises(RuntimeError) as error:
        build_xlsx(report)
    assert isinstance(error.value.__cause__, OSError)
