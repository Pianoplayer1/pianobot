"""Table-rendering helpers."""

from collections.abc import Sequence
from math import ceil


def render_page(
    columns: Sequence[tuple[str, int]],
    rows: Sequence[Sequence[str]],
    *,
    start_index: int,
    enum: bool,
    separator_rows: int,
    label: str | None,
    page_num: int,
    total_pages: int,
    leading_text: str | None,
) -> str:
    """Render one paginated page of a bordered ASCII table as a single string."""
    effective_cols = list(columns)
    if enum:
        name, width = effective_cols[0]
        effective_cols[0] = (name, max(1, width - 5))
    out: list[str] = []
    if leading_text:
        out.append(leading_text)
    out.append("```ml")
    header = "│"
    if enum:
        header += "     "
    for name, width in effective_cols:
        header += f" {name.ljust(width - 1)}│"
    out.append(header)
    for i, row in enumerate(rows):
        abs_index = start_index + i
        if i == 0 or (separator_rows and i % separator_rows == 0):
            sep = "├"
            if enum:
                sep += "─────"
            for pos, (_, width) in enumerate(effective_cols):
                sep += "─" * width + ("┼" if pos != len(effective_cols) - 1 else "┤")
            out.append(sep)
        line = "│"
        if enum:
            line += f"{abs_index + 1}.".rjust(5)
        for j, (_, width) in enumerate(effective_cols):
            value = row[j] if j < len(row) else ""
            line += f" {str(value).ljust(width - 1)}│"
        out.append(line)
    footer = ""
    if total_pages > 1:
        footer += f"\nPage {page_num} / {total_pages}"
        if label:
            footer += f" {label}"
    if footer:
        out.append(footer)
    out.append("```")
    return "\n".join(out)


def paginate(
    columns: Sequence[tuple[str, int]],
    rows: Sequence[Sequence[str]],
    *,
    page_size: int,
    enum: bool,
    separator_rows: int,
    label: str | None,
    leading_text: str | None,
) -> list[str]:
    """Split rows into `page_size` chunks and render each via `render_page`."""
    if not rows:
        return [
            render_page(
                columns,
                [],
                start_index=0,
                enum=enum,
                separator_rows=separator_rows,
                label=label,
                page_num=1,
                total_pages=1,
                leading_text=leading_text,
            )
        ]
    total_pages = max(1, ceil(len(rows) / page_size))
    pages: list[str] = []
    for page in range(total_pages):
        chunk = rows[page * page_size : (page + 1) * page_size]
        pages.append(
            render_page(
                columns,
                chunk,
                start_index=page * page_size,
                enum=enum,
                separator_rows=separator_rows,
                label=label,
                page_num=page + 1,
                total_pages=total_pages,
                leading_text=leading_text,
            )
        )
    return pages
