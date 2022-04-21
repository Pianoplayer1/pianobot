from math import ceil


def table(
    columns: dict[str, int],
    raw_data: list[list[str]],
    seperator: int = 0,
    page_len: int = 0,
    enum: bool = False,
    label: str = '',
    start_text: str | None = None,
) -> list[str]:
    if enum:
        columns[list(columns.keys())[0]] -= 5
    message = []
    count = 0
    page_num = 1 if page_len == 0 else ceil(len(raw_data) / page_len)
    for page in range(page_num):
        try:
            data = raw_data[page * page_len : (page + 1) * page_len]
        except IndexError:
            data = raw_data[page * page_len :]
        if len(data) == 0:
            data = raw_data[page * page_len :]
        message.append((start_text + '\n' if start_text else '') + '```ml\n│')

        if enum:
            message[page] += '     '
        for column in columns:
            message[page] += f' {column.ljust(columns[column]-1)}│'

        for row in data:
            if count == 0 or seperator != 0 and (count - page * page_len) % seperator == 0:
                message[page] += '\n├'
                if enum:
                    message[page] += '─────'
                for pos, column in enumerate(columns):
                    message[page] += '─' * (columns[column]) + (
                        '┼' if pos != len(columns) - 1 else '┤'
                    )
            count += 1

            message[page] += '\n│'
            if enum:
                message[page] += f'{count}.'.rjust(5)
            for i in range(len(columns)):
                try:
                    message[page] += f' {str(row[i]).ljust(list(columns.values())[i]-1)}│'
                except IndexError:
                    message[page] += ' ' * (list(columns.values())[i]) + '│'

        if page_num > 1:
            message[page] += f'\n\nPage {page + 1} / {page_num} {label}'
        message[page] += '```'

    return message
