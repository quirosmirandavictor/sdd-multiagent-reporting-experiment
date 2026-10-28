from copy import deepcopy
from io import BytesIO
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import pytest

from reporting import palette
from reporting.xlsx_output import build_xlsx

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


@pytest.fixture
def report():
    return {"schema_version": 1, "title": "Ventas por región",
            "headers": ["Región", "Ventas", "Margen"],
            "rows": [["Norte", 120, 2.5], ["Sur", -90, 0]],
            "chart": {"type": "column", "category_column": 0, "value_columns": [2, 1]}}


def xml_parts(content):
    with ZipFile(BytesIO(content)) as archive:
        assert archive.testzip() is None
        return {name: ET.fromstring(archive.read(name))
                for name in archive.namelist() if name.endswith(".xml")}


def test_structure_data_styles_and_chart(report):
    original = deepcopy(report)
    parts = xml_parts(build_xlsx(report))
    assert report == original
    workbook = parts["xl/workbook.xml"]
    assert [s.attrib["name"] for s in workbook.findall("s:sheets/s:sheet", NS)] == ["Reporte"]
    table = parts["xl/tables/table1.xml"]
    assert table.attrib["name"] == "Datos"
    assert table.attrib["ref"] == "A3:C5"
    assert table.attrib.get("totalsRowShown") == "0"
    sheet = parts["xl/worksheets/sheet1.xml"]
    cells = {c.attrib["r"]: c for c in sheet.findall(".//s:c", NS)}
    strings = ["".join(s.itertext()) for s in parts["xl/sharedStrings.xml"].findall("s:si", NS)]
    assert strings[int(cells["A1"].find("s:v", NS).text)] == report["title"]
    for r, row in enumerate([report["headers"], *report["rows"]], 3):
        for col, expected in zip("ABC", row):
            cell = cells[f"{col}{r}"]
            value = cell.find("s:v", NS).text
            assert (strings[int(value)] if cell.attrib.get("t") == "s" else float(value)) == expected
    assert not any(c.attrib["r"].endswith("2") for c in cells.values())
    styles = parts["xl/styles.xml"]
    xfs = styles.find("s:cellXfs", NS)
    def style(ref):
        return xfs[int(cells[ref].attrib["s"])]
    def color(ref, kind):
        xf = style(ref)
        if kind == "font":
            return styles.find("s:fonts", NS)[int(xf.attrib["fontId"])].find("s:color", NS).attrib["rgb"]
        return styles.find("s:fills", NS)[int(xf.attrib["fillId"])].find("s:patternFill/s:fgColor", NS).attrib["rgb"]
    assert color("A1", "font") == "FF" + palette.NAVY[1:]
    assert color("A3", "fill") == "FF" + palette.AZURE[1:]
    assert color("A3", "font") == "FF" + palette.WHITE[1:]
    assert color("A4", "fill") == "FF" + palette.WHITE[1:]
    assert color("A5", "fill") == "FF" + palette.LIGHT_BLUE[1:]
    border = styles.find("s:borders", NS)[int(style("A4").attrib["borderId"])]
    assert border.find("s:left/s:color", NS).attrib["rgb"] == "FF" + palette.BORDER[1:]
    chart = parts["xl/charts/chart1.xml"]
    assert chart.find(".//c:barDir", NS).attrib["val"] == "col"
    assert chart.find(".//c:bar3DChart", NS) is None
    series = chart.findall(".//c:ser", NS)
    for ser, col in zip(series, "CB"):
        assert [f.text for f in ser.findall(".//c:f", NS)] == [
            f"Reporte!${col}$3", "Reporte!$A$4:$A$5", f"Reporte!${col}$4:${col}$5"]
        assert ser.find(".//a:solidFill/a:srgbClr", NS).attrib["val"] == palette.AZURE[1:]
    drawing = parts["xl/drawings/drawing1.xml"]
    dns = {"d": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"}
    assert drawing.find(".//d:from/d:row", dns).text == "6"
