"""Safe YAML validation and normalization for the report-v1 contract."""

import math
import re
from decimal import Decimal, InvalidOperation

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


_TAG = "tag:yaml.org,2002:"
_DECIMAL = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


def _number(node: ScalarNode, path: str) -> int | float:
    """Validate exact digits before allowing any binary floating conversion."""
    is_integer = node.tag == _TAG + "int"
    try:
        if is_integer:
            # SafeLoader's integer constructor uses exact integer arithmetic,
            # including YAML integer bases; it never passes through float.
            loader = yaml.SafeLoader("")
            try:
                integer = loader.construct_yaml_int(node)
            finally:
                loader.dispose()
            original = Decimal(integer)
        else:
            spelling = node.value.replace("_", "")
            if not _DECIMAL.fullmatch(spelling):
                raise ValueError(f"{path}: unsupported or non-finite numeric scalar")
            original = Decimal(spelling)
    except (InvalidOperation, ValueError, OverflowError) as exc:
        raise ValueError(f"{path}: invalid numeric scalar {node.value!r}") from exc
    if not original.is_finite():
        raise ValueError(f"{path}: number must be finite")
    if not -1_000_000_000 <= original <= 1_000_000_000:
        raise ValueError(f"{path}: number outside [-1000000000, 1000000000]")
    digits = original.as_tuple().digits
    significant = len(digits)
    while significant > 1 and digits[significant - 1] == 0:
        significant -= 1
    if significant > 15:
        raise ValueError(f"{path}: number exceeds 15 significant digits")
    if is_integer:
        return integer
    result = float(original)
    if not math.isfinite(result) or Decimal(str(result)) != original:
        raise ValueError(f"{path}: numeric conversion loses precision")
    return result


def _read_node(node, path: str, active: set[int]):
    if id(node) in active:
        raise ValueError(f"{path}: recursive YAML structure")
    active.add(id(node))
    try:
        if isinstance(node, ScalarNode):
            if node.tag == _TAG + "str":
                return node.value
            if node.tag in (_TAG + "int", _TAG + "float"):
                return _number(node, path)
            raise ValueError(f"{path}: unsupported scalar type {node.tag}")
        if isinstance(node, SequenceNode) and node.tag == _TAG + "seq":
            return [_read_node(child, f"{path}[{i}]", active)
                    for i, child in enumerate(node.value)]
        if isinstance(node, MappingNode) and node.tag == _TAG + "map":
            result = {}
            for key, value in node.value:
                if not isinstance(key, ScalarNode) or key.tag != _TAG + "str":
                    raise ValueError(f"{path}: object keys must be strings")
                if key.value in result:
                    raise ValueError(f"{path}.{key.value}: duplicate key")
                result[key.value] = _read_node(value, f"{path}.{key.value}", active)
            return result
        raise ValueError(f"{path}: unsupported YAML tag {node.tag}")
    finally:
        active.remove(id(node))


def _object(value, keys: set[str], path: str) -> None:
    if type(value) is not dict:
        raise ValueError(f"{path}: expected object")
    missing = keys - value.keys()
    unknown = value.keys() - keys
    if missing or unknown:
        raise ValueError(f"{path}: missing fields {sorted(missing)}; unknown fields {sorted(unknown)}")


def _text(value, path: str, *, nonempty=False, limit=32767) -> None:
    if type(value) is not str:
        raise ValueError(f"{path}: expected text")
    if nonempty and not value.strip():
        raise ValueError(f"{path}: text must not be empty")
    if len(value) > limit:
        raise ValueError(f"{path}: text exceeds {limit} characters")
    for char in value:
        code = ord(char)
        if not (code in (9, 10, 13) or 0x20 <= code <= 0xD7FF
                or 0xE000 <= code <= 0xFFFD or 0x10000 <= code <= 0x10FFFF):
            raise ValueError(f"{path}: character not representable in XML 1.0")


def _list(value, path: str) -> None:
    if type(value) is not list or not value:
        raise ValueError(f"{path}: expected nonempty list")


def _dimensions(columns: int, rows: int, series: int) -> None:
    if columns > 16384:
        raise ValueError("headers: exceeds 16384 columns")
    if rows + 28 > 1048576:
        raise ValueError("rows: exceeds worksheet capacity including chart")
    if series > 255:
        raise ValueError("chart.values: exceeds 255 series")


def parse_report(text: str) -> dict:
    """Return the normalized v1 dict, or a contextual ValueError.

    File reading belongs to the caller. Composition with SafeLoader retains
    original numeric spelling and never constructs executable YAML objects.
    """
    if not isinstance(text, str):
        raise TypeError("text must be str")
    try:
        root = yaml.compose(text, Loader=yaml.SafeLoader)
        if root is None:
            raise ValueError("report: empty YAML document")
        report = _read_node(root, "report", set())
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML: {exc}") from exc
    except RecursionError as exc:
        raise ValueError("YAML: structure too deeply nested") from exc

    _object(report, {"schema_version", "title", "headers", "rows", "chart"}, "report")
    if type(report["schema_version"]) is not int or report["schema_version"] != 1:
        raise ValueError("schema_version: expected integer 1")
    _text(report["title"], "title", nonempty=True)
    headers, rows, chart = report["headers"], report["rows"], report["chart"]
    _list(headers, "headers")
    _list(rows, "rows")
    _object(chart, {"type", "category", "values"}, "chart")
    if chart["type"] != "column":
        raise ValueError("chart.type: expected column")
    _list(chart["values"], "chart.values")
    _dimensions(len(headers), len(rows), len(chart["values"]))
    seen = set()
    for i, header in enumerate(headers):
        _text(header, f"headers[{i}]", nonempty=True, limit=255)
        if header.casefold() in seen:
            raise ValueError(f"headers[{i}]: duplicate header according to casefold")
        seen.add(header.casefold())
    for i, row in enumerate(rows):
        if type(row) is not list or len(row) != len(headers):
            raise ValueError(f"rows[{i}]: expected {len(headers)} cells")
        for j, cell in enumerate(row):
            if type(cell) is str:
                _text(cell, f"rows[{i}][{j}]")
            elif type(cell) not in (int, float):
                raise ValueError(f"rows[{i}][{j}]: expected text or number")

    def column(name, path):
        _text(name, path, nonempty=True, limit=255)
        if name not in headers:
            raise ValueError(f"{path}: unknown column {name!r}")
        return headers.index(name)

    category = column(chart["category"], "chart.category")
    values = [column(name, f"chart.values[{i}]") for i, name in enumerate(chart["values"])]
    if len(set(values)) != len(values) or category in values:
        raise ValueError("chart.values: series must be unique and distinct from category")
    for i, row in enumerate(rows):
        _text(row[category], f"rows[{i}][{category}] category", nonempty=True)
        for j in values:
            if type(row[j]) not in (int, float):
                raise ValueError(f"rows[{i}][{j}]: chart series must be numeric")
    return {"schema_version": report["schema_version"], "title": report["title"],
            "headers": headers, "rows": rows,
            "chart": {"type": "column", "category_column": category, "value_columns": values}}
