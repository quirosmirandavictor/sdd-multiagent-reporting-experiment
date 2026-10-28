"""Adaptador XlsxWriter para el dict normalizado del contrato v1."""

from io import BytesIO
from math import ceil

import xlsxwriter

from reporting import palette


def build_xlsx(report: dict) -> bytes:
    """Generar un libro completo sin modificar report ni realizar E/S."""
    try:
        output = BytesIO()
        with xlsxwriter.Workbook(output, {
            "in_memory": True, "strings_to_formulas": False,
            "strings_to_urls": False,
        }) as workbook:
            sheet = workbook.add_worksheet("Reporte")
            sheet.hide_gridlines(2)
            title = workbook.add_format({
                "font_color": palette.NAVY, "bold": True,
                "font_size": 20, "text_wrap": True, "valign": "top",
            })
            header = workbook.add_format({
                "bg_color": palette.AZURE, "font_color": palette.WHITE,
                "bold": True, "text_wrap": True, "valign": "top",
                "border": 1, "border_color": palette.BORDER,
            })
            formats = [workbook.add_format({
                "bg_color": color, "font_color": palette.NAVY,
                "border": 1, "border_color": palette.BORDER,
                "text_wrap": True, "valign": "top",
            }) for color in (palette.WHITE, palette.LIGHT_BLUE)]
            headers, rows = report["headers"], report["rows"]
            widths = []
            for col, name in enumerate(headers):
                width = min(48, max(16, len(name) + 2,
                                    max(len(str(row[col])) + 2 for row in rows)))
                widths.append(width)
                sheet.set_column(col, col, width)
            sheet.write_string(0, 0, report["title"], title)
            # Merge only when more than one column exists; write_string keeps
            # adversarial title text literal even in the merged range.
            if len(headers) > 1:
                sheet.merge_range(0, 0, 0, len(headers) - 1, "", title)
                sheet.write_string(0, 0, report["title"], title)
            sheet.set_row(0, max(30, 27 * ceil(len(report["title"]) / sum(widths))))
            sheet.set_row(2, max(30, 15 * max(ceil(len(h) / w) for h, w in zip(headers, widths))))
            sheet.add_table(2, 0, len(rows) + 2, len(headers) - 1, {
                "name": "Datos", "style": None, "banded_rows": False,
                "columns": [{"header": name, "header_format": header} for name in headers],
            })
            for index, row in enumerate(rows):
                sheet.set_row(index + 3, max(20, 15 * max(
                    sum(max(1, ceil(len(line) / widths[c])) for line in str(value).split("\n"))
                    for c, value in enumerate(row))))
                for col, value in enumerate(row):
                    fmt = formats[index % 2]
                    if isinstance(value, str):
                        sheet.write_string(index + 3, col, value, fmt)
                    else:
                        sheet.write_number(index + 3, col, value, fmt)
            chart = workbook.add_chart({"type": "column"})
            chart.set_style(10)
            for col in report["chart"]["value_columns"]:
                chart.add_series({
                    "name": ["Reporte", 2, col],
                    "categories": ["Reporte", 3, report["chart"]["category_column"],
                                   len(rows) + 2, report["chart"]["category_column"]],
                    "values": ["Reporte", 3, col, len(rows) + 2, col],
                    "fill": {"color": palette.AZURE},
                    "border": {"color": palette.AZURE},
                })
            chart.set_size({"width": 720, "height": 480})
            chart.set_chartarea({"fill": {"color": palette.WHITE}, "border": {"none": True}})
            chart.set_plotarea({"fill": {"color": palette.WHITE}, "border": {"none": True}})
            chart.set_x_axis({"num_font": {"color": palette.NAVY}})
            chart.set_y_axis({"num_font": {"color": palette.NAVY}})
            sheet.insert_chart(len(rows) + 4, 0, chart)
        return output.getvalue()
    except Exception as exc:
        raise RuntimeError("No se pudo generar el XLSX") from exc
