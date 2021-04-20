from collections import namedtuple
from math import prod

import numpy as np


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


def rolling(length, width, height, new_height):
    new_length = length * height / new_height
    new_width = width * height / new_height
    if new_length == int(new_length) and new_width == int(new_width):
        k = length / width
        if k < 0.3:
            length = new_length
        elif k > 3:
            width = new_width
        else:
            if np.random.uniform() < 0.5:
                length = new_length
            else:
                width = new_width
    elif new_length == int(new_length):
        length = new_length
    elif new_width == int(new_width):
        width = new_width
    else:
        msg = (
            f'Rolling operation from ({length, width, height}) to '
            f'({new_height}) does not result in integer size'
        )
        raise ValueError(msg)
    return int(length), int(width), new_height


def cutting(length, width, height):
    if length > width:
        new_length = np.around(np.random.normal(length/20, length/60))
        for _ in range(100):
            if 0 <= new_length < length:
                break
            new_length = np.around(np.random.normal(length/20, length/60))
        else:
            raise ValueError('Failed to generate integer length')
        new_length *= 10
        size_a = int(new_length), int(width), height
        size_b = int(length - new_length), int(width), height
    else:
        new_width = np.around(np.random.normal(width/20, width/60))
        for _ in range(100):
            if 0 <= new_width < width:
                break
            new_width = np.around(np.random.normal(width/20, width/60))
        else:
            raise ValueError('Failed to generate integer width')
        new_width *= 10
        size_a = int(length), int(new_width), height
        size_b = int(length), int(width - new_width), height
    return size_a, size_b


def generate_bins(length, width, height, heights):
    sizes = []
    size = length, width, height
    for i, height in enumerate(heights):
        if i != len(heights) - 1:
            if np.random.uniform() < 0.5:
                size = rolling(*size, height)
                size, size_b = cutting(*size)
                sizes.append(size_b)
            else:
                size, size_b = cutting(*size)
                size_b = rolling(*size_b, height)
                sizes.append(size_b)
        else:
            if size[-1] != height:
                size = rolling(*size, height)
            sizes.append(size)

    if prod((length, width, height)) != sum(map(prod, sizes)):
        msg = 'The sizes of the original bin and the resulting bins do not match'
        raise ValueError(msg)
    return sizes
