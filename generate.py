from collections import namedtuple


Rectangle = namedtuple('Rectangle', ('xy', 'length', 'width', 'height', 'priority'))


def to_json(obj, level=0):
    SPACE = ' '
    SEPARATOR = ':'
    NEWLINE = '\n'
    INDENT = 4
    result = ''
    if isinstance(obj, dict):
        result += f'{{{NEWLINE}'
        comma = ''
        for key, value in obj.items():
            result += comma
            comma = f',{NEWLINE}'
            result += f'{SPACE * INDENT * (level + 1)}'
            result += f'"{str(key)}"{SEPARATOR}{SPACE}'
            result += to_json(value, level=level + 1)
        result += f'{NEWLINE}{SPACE * INDENT * level}}}'
    if isinstance(obj, (list, tuple)):
        list_newline, list_endline = '', ''
        list_separator = ', '
        nested = False
        if obj and isinstance(obj[0], (list, tuple)):
            nested = True
        if nested:
            list_newline = f'{NEWLINE}{SPACE * INDENT * (level + 1)}'
            list_endline = f'{NEWLINE}{SPACE * INDENT * level}'
            level += 1
            list_separator = f',{NEWLINE}{SPACE * INDENT * level}'
        result += f'[{list_newline}'
        result += list_separator.join([to_json(item, level + 1) for item in obj])
        result += f'{list_endline}]'
    if isinstance(obj, (int, float)):
        result += str(obj)
    if isinstance(obj, str):
        result += f'"{obj}"'
    return result


def write_json_file(data, file_name: str):
    print(f'Write to {file_name}')
    with open(file_name, 'w') as f:
        f.write(to_json(data))


def write_txt(data, file_name):
    print(f'Write to {file_name}')
    with open(file_name, 'w') as f:
        # size of ingot
        f.write(' '.join(map(str, data['ingot'])) + '\n')
        # number of bins
        f.write(f'{len(data["bins"])}\n')
        # sizes of bins
        for bin_size in data["bins"]:
            f.write(f'{" ".join(map(str, bin_size))}\n')
        # number of rectangles
        f.write(f'{len(data["rectangles"])}\n')
        # parameters of rectangles
        for rectangle in data["rectangles"]:
            f.write(f'{" ".join(map(str, rectangle))}\n')
