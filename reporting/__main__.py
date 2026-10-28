"""CLI local: python -m reporting --input reporte.yaml --output reporte.xlsx."""

import argparse
from pathlib import Path
import sys

from reporting.xlsx_output import build_xlsx


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Generar un reporte XLSX con identidad VQ")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.output.suffix.lower() != ".xlsx":
        parser.error("--output debe tener extensión .xlsx")
    path = args.input
    created = False
    try:
        text = args.input.read_text(encoding="utf-8")
        # Importación diferida: --help funciona antes de integrar el parser A.
        from reporting.yaml_input import parse_report
        report = parse_report(text)
        path = args.output
        content = build_xlsx(report)
        with args.output.open("xb") as stream:
            created = True
            stream.write(content)
    except (UnicodeError, ValueError) as exc:
        print(f"Error de validación: {exc}", file=sys.stderr)
        return 2
    except (OSError, RuntimeError) as exc:
        if created:
            try:
                args.output.unlink()
            except OSError as cleanup:
                print(f"Error de archivo: {args.output}: limpieza fallida: {cleanup}", file=sys.stderr)
        print(f"Error de archivo: {path}: {exc}", file=sys.stderr)
        return 1
    print(f"Reporte generado: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
