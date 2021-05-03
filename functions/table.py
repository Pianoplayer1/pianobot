from math import ceil

def table(columns, rawData, seperator = 0, pageLen = 0, enum = False, label = ''):
    if enum:
        columns[list(columns.keys())[0]] -= 5
    message = []
    count = 0
    pageNum = 1 if pageLen == 0 else ceil(len(rawData) / pageLen)
    for page in range(pageNum):
        try:
            data = rawData[page * pageLen : (page+1) * pageLen]
        except IndexError:
            data = rawData[page * pageLen : ]
        if len(data) == 0:
            data = rawData[page * pageLen : ]
        message.append('```ml\n|')
        
        if enum:
            message[page] += '     '
        for column in columns:
            message[page] += f' {column.ljust(columns[column]-1)}|'
        
        for row in data:
            if count == 0 or seperator != 0 and (count - page * pageLen) % seperator == 0:
                message[page] += '\n+'
                if enum:
                    message[page] += '-----'
                for column in columns:
                    message[page] += '-' * (columns[column]) + '+'
            count += 1

            message[page] += '\n|'
            if enum:
                message[page] += f'{count}.'.rjust(5)
            for i in range(len(columns)):
                try:
                    message[page] += f' {str(row[i]).ljust(list(columns.values())[i]-1)}|'
                except IndexError:
                    message[page] += ' ' * (list(columns.values())[i]) + '|'
                    
        if pageNum > 1:
            message[page] += f'\n\nPage {page + 1} / {pageNum} {label}'
        message[page] += '```'
            
    return message