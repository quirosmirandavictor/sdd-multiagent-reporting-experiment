"""Agent A's contract tests; independent of XLSX generation and CLI."""

from decimal import localcontext

import pytest
import yaml

from reporting.yaml_input import _dimensions, parse_report


def definition():
    return {
        "schema_version": 1,
        "title": " Ventas por región ",
        "headers": ["Región", "Ventas", "Coste"],
        "rows": [["Norte", 120, 0.25], ["Sur", -90, 0]],
        "chart": {"type": "column", "category": "Región", "values": ["Coste", "Ventas"]},
    }


def dump(report):
    return yaml.safe_dump(report, allow_unicode=True, sort_keys=False)


def scalar_text(scalar):
    return ("schema_version: 1\ntitle: Reporte\nheaders: [Categoría, Valor]\n"
            f"rows: [[Norte, {scalar}]]\n"
            "chart: {type: column, category: Categoría, values: [Valor]}\n")


def test_exact_normalized_contract():
    report = definition()
    result = parse_report(dump(report))
    assert result == {**report, "chart": {"type": "column", "category_column": 0,
                                        "value_columns": [2, 1]}}
    assert type(result) is dict
    assert type(result["schema_version"]) is int
    assert type(result["rows"][0][1]) is int
    assert type(result["rows"][0][2]) is float
    assert all(type(index) is int for index in result["chart"]["value_columns"])


def test_category_can_follow_numeric_columns():
    report = definition()
    report["headers"] = ["Ventas", "Región", "Coste"]
    report["rows"] = [[120, "Norte", 0.25]]
    result = parse_report(dump(report))
    assert result["chart"] == {"type": "column", "category_column": 1,
                               "value_columns": [2, 0]}
    assert result["rows"] == report["rows"]


def test_nonrecursive_yaml_aliases_are_data():
    text = scalar_text("1").replace("[[Norte, 1]]", "[&row [Norte, 1], *row]")
    assert parse_report(text)["rows"] == [["Norte", 1], ["Norte", 1]]


@pytest.mark.parametrize("scalar, expected, kind", [
    ("1000000000", 1000000000, int), ("-1000000000", -1000000000, int),
    ("1000000000.0", 1e9, float), ("-1000000000.0", -1e9, float),
    ("0", 0, int), ("-0.0", -0.0, float), ("-12", -12, int),
    ("0.123456789012345", 0.123456789012345, float),
    ("1.2345678901234500000000000000000000", 1.23456789012345, float),
    ("1.0e+2", 100.0, float), ("1_000.25", 1000.25, float),
    ("0x10", 16, int), ("010", 8, int), ("0b11", 3, int), ("1:20", 80, int),
])
def test_original_numeric_scalars(scalar, expected, kind):
    result = parse_report(scalar_text(scalar))["rows"][0][1]
    assert result == expected
    assert type(result) is kind


@pytest.mark.parametrize("scalar", [
    "1.0000000000000001", "0.1234567890123456", "1000000001", "-1000000001",
    "1000000000.000001", "-1000000000.000001", ".nan", ".NaN", ".inf", "-.inf",
    "1.0e+1000", "1.0e-1000", "4.0e-324", "1:20.5", '!!float "nonsense"',
    '!!float "NaN"', '!!float "Infinity"',
])
def test_reject_original_invalid_numbers(scalar):
    with pytest.raises(ValueError, match=r"rows\[0\]\[1\]"):
        parse_report(scalar_text(scalar))


def test_significant_digits_independent_of_decimal_context():
    with localcontext() as context:
        context.prec = 2
        assert parse_report(scalar_text("1.23456789012345"))["rows"][0][1] == 1.23456789012345
        with pytest.raises(ValueError, match="15 significant"):
            parse_report(scalar_text("1.0000000000000001"))


@pytest.mark.parametrize("value", [None, 1, b"title: test", [], {}])
def test_python_argument_type(value):
    with pytest.raises(TypeError):
        parse_report(value)


@pytest.mark.parametrize("field, value", [
    ("schema_version", True), ("schema_version", 2), ("schema_version", 1.0),
    ("schema_version", "1"), ("title", " "), ("title", 1),
    ("title", "x" * 32768), ("title", "\ufffe"), ("title", "\ud800"),
    ("headers", []), ("headers", "A"), ("headers", ["A", "a"]),
    ("headers", ["Straße", "STRASSE"]), ("headers", [" "]),
    ("headers", [1]), ("headers", ["x" * 256]),
    ("rows", []), ("rows", "rows"), ("rows", [["Norte", 1]]),
    ("rows", ["abc"]), ("rows", [["Norte", 1, []]]),
    ("rows", [["Norte", 1, {}]]), ("rows", [["Norte", 1, None]]),
    ("rows", [["Norte", 1, True]]), ("rows", [["Norte", 1, "x" * 32768]]),
    ("chart", []),
], ids=lambda value: f"text-{len(value)}" if isinstance(value, str) and len(value) > 80 else None)
def test_invalid_report_fields(field, value):
    report = definition()
    report[field] = value
    with pytest.raises(ValueError, match=field):
        parse_report(dump(report))


@pytest.mark.parametrize("field, value", [
    ("type", "bar"), ("type", []), ("category", "región"),
    ("category", 0), ("category", "Missing"), ("values", []),
    ("values", "Ventas"), ("values", [1]), ("values", ["Missing"]),
    ("values", ["Ventas", "Ventas"]), ("values", ["Región"]),
])
def test_invalid_chart_fields(field, value):
    report = definition()
    report["chart"][field] = value
    with pytest.raises(ValueError, match="chart"):
        parse_report(dump(report))


@pytest.mark.parametrize("value", ["", " ", 1, 1.0])
def test_category_requires_nonempty_text(value):
    report = definition()
    report["rows"][0][0] = value
    with pytest.raises(ValueError, match=r"rows\[0\]\[0\]"):
        parse_report(dump(report))


def test_numeric_strings_are_not_coerced():
    with pytest.raises(ValueError, match="numeric"):
        parse_report(scalar_text('"120"'))


@pytest.mark.parametrize("scope", ["report", "chart"])
def test_missing_unknown_and_duplicate_keys(scope):
    for operation in ("missing", "unknown", "duplicate"):
        report = definition()
        obj = report if scope == "report" else report["chart"]
        key = "title" if scope == "report" else "type"
        if operation == "missing":
            del obj[key]
        elif operation == "unknown":
            obj["color"] = "azure"
        text = dump(report)
        if operation == "duplicate":
            text += "title: duplicate\n" if scope == "report" else "  type: column\n"
        with pytest.raises(ValueError, match=scope):
            parse_report(text)


@pytest.mark.parametrize("text", [
    "", "# empty", "[]", "null", "title: [", "a: 1\n---\nb: 2",
    "!!python/object/apply:os.system ['echo unsafe']", "!custom foo",
    "&root [*root]", "{[a, b]: value}", "{<<: {title: merged}}",
])
def test_invalid_yaml(text):
    with pytest.raises(ValueError):
        parse_report(text)


@pytest.mark.parametrize("scalar", ["true", "null", "2026-10-27", "[1]", "{a: 1}"])
def test_unsupported_cell_types(scalar):
    with pytest.raises(ValueError, match=r"rows\[0\]\[1\]"):
        parse_report(scalar_text(scalar))


def test_executable_tag_is_never_constructed(tmp_path):
    target = tmp_path / "must-not-exist"
    text = f'!!python/object/apply:builtins.open ["{target.as_posix()}", "w"]'
    with pytest.raises(ValueError):
        parse_report(text)
    assert not target.exists()


@pytest.mark.parametrize("literal", ["=1+1", "+SUM(A1:A2)", "-SUM(A1:A2)",
                                     "@SUM(A1:A2)", "https://example.com", "00120"])
def test_text_is_preserved_everywhere(literal):
    report = definition()
    report["title"] = literal
    report["headers"][0] = literal
    report["chart"]["category"] = literal
    report["rows"][0][0] = literal
    result = parse_report(dump(report))
    assert result["title"] == result["headers"][0] == result["rows"][0][0] == literal


def test_repeated_categories_and_empty_non_chart_text_are_allowed():
    report = definition()
    report["headers"].append("Nota")
    for row in report["rows"]:
        row[0] = "Repetida"
        row.append("")
    assert parse_report(dump(report))["rows"] == report["rows"]


def test_text_boundaries_and_xml_whitespace():
    report = definition()
    report["title"] = "x" * 32767
    report["headers"][0] = "h" * 255
    report["chart"]["category"] = report["headers"][0]
    report["rows"][0][0] = "\t\n\r á😀"
    assert parse_report(dump(report))["rows"] == report["rows"]


@pytest.mark.parametrize("columns, rows, series", [
    (16384, 1048548, 255), (1, 1, 1),
])
def test_dimension_boundaries(columns, rows, series):
    _dimensions(columns, rows, series)


@pytest.mark.parametrize("columns, rows, series, field", [
    (16385, 1, 1, "headers"), (1, 1048549, 1, "rows"), (256, 1, 256, "chart.values"),
])
def test_dimensions_outside_boundaries(columns, rows, series, field):
    with pytest.raises(ValueError, match=field):
        _dimensions(columns, rows, series)


@pytest.mark.parametrize("count", [255, 256, 16384, 16385])
def test_dimensions_through_parser(count):
    report = definition()
    report["headers"] = ["Category"] + [f"V{i}" for i in range(count - 1)]
    report["rows"] = [["Norte"] + [0] * (count - 1)]
    report["chart"] = {"type": "column", "category": "Category",
                       "values": report["headers"][1: min(count, 256)]}
    if count == 256:  # Exactly 255 series.
        assert len(parse_report(dump(report))["chart"]["value_columns"]) == 255
    elif count == 16385:
        with pytest.raises(ValueError, match="headers"):
            parse_report(dump(report))
    else:
        assert len(parse_report(dump(report))["headers"]) == count


def test_too_many_series_through_parser():
    report = definition()
    report["headers"] = ["Category"] + [f"V{i}" for i in range(256)]
    report["rows"] = [["Norte"] + [0] * 256]
    report["chart"] = {"type": "column", "category": "Category",
                       "values": report["headers"][1:]}
    with pytest.raises(ValueError, match="255 series"):
        parse_report(dump(report))
