from collections import namedtuple
from math import prod

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.patches as patches


Rectangle = namedtuple('Rectangle', ('xy', 'length', 'width', 'height', 'priority'))


def visualize(width, length, rectangles, with_borders=False):
    fig = plt.figure()
    axes = fig.add_subplot(1, 1, 1)
    axes.add_patch(
        patches.Rectangle((0, 0), width, length, hatch='x', fill=False)
    )
    for i, r in enumerate(rectangles):
        color = np.random.uniform(size=(3, ))
        axes.add_patch(
            patches.Rectangle(r.xy, r.width, r.length, color=color)
        )
        if with_borders:
            axes.add_patch(
                patches.Rectangle(r.xy, r.width, r.length,
                fill=False, edgecolor='black', linewidth=2)
            )
        x, y = r.xy
        axes.text(x + 0.48 * r.width, y + 0.48 * r.length, str(i))
    axes.set_xlim(0, width)
    axes.set_ylim(0, length)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


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


def write_txt(data, file_name, with_xy=False):
    print(f'Write to {file_name}')
    with open(file_name, 'w') as f:
        # size of ingot
        f.write(' '.join(map(str, data['ingot'])) + '\n')
        # number of bins
        f.write(f'{len(data["bins"])}\n')
        # sizes of bins
        for bin_size in data['bins']:
            f.write(f'{" ".join(map(str, bin_size))}\n')
        # number of rectangles
        f.write(f'{len(data["rectangles"])}\n')
        # parameters of rectangles
        for rectangle in data['rectangles']:
            if with_xy:
                xy = ' '.join(map(str, rectangle.xy)) + ' '
            else:
                xy = ''
            f.write(f'{xy}{" ".join(map(str, rectangle[1:]))}\n')


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


def recursive_generate(xy, size, rectangles, area_params, side_ratio_params):
    length, width, height = size

    area_alpha = area_params.get('alpha') or 2
    area_beta = area_params.get('beta') or 2
    min_area = area_params.get('min') or length * width / 10
    max_area = area_params.get('max') or length * width
    ratio_alpha = side_ratio_params.get('alpha') or 2
    ratio_beta = side_ratio_params.get('beta') or 2
    min_ratio = side_ratio_params.get('min') or 0.5
    max_ratio = side_ratio_params.get('max') or 2

    # priority = scipy.stats.beta.rvs(1, 5)
    # priority = np.around(1 + priority * (5 - 1))
    priority = np.random.randint(1, 4)

    area = sp.stats.beta.rvs(area_alpha, area_beta)
    area = np.around(min_area + area * (max_area - min_area))

    for _ in range(100):
        if 0 < area < length * width or min_area <= area <= max_area:
            break
        area = sp.stats.beta.rvs(area_alpha, area_beta)
        area = np.around(min_area + area * (max_area - min_area))
    else:
        area = length * width

    ratio = sp.stats.beta.rvs(ratio_alpha, ratio_beta)
    ratio = np.around(min_ratio + ratio * (max_ratio - min_ratio), 2)

    rect_width = np.around((area / ratio) ** 0.5)
    if rect_width > width or width - 1.5 * rect_width <= 0:
        rect_width = width

    rect_length = np.around(ratio * rect_width)
    if rect_length > length or length - 1.5*rect_length <= 0:
        rect_length = length

    rect = Rectangle(
        xy, int(rect_length), int(rect_width), int(height), int(priority)
    )
    rectangles.append(rect)

    if rect.length == length and rect.width != width:
        xy = xy[0] + rect.width, xy[1]
        recursive_generate(
            xy, (length, width - rect.width, height), rectangles,
            area_params, side_ratio_params
        )
    elif rect.length != length and rect.width == width:
        xy = xy[0], xy[1] + rect.length
        recursive_generate(
            xy, (length - rect.length, width, height), rectangles,
            area_params, side_ratio_params
        )
    else:
        cut_direction = np.random.choice((0, 1))
        if cut_direction == 0:
            # horizontal section
            recursive_generate(
                (xy[0], xy[1] + rect.length),
                (length - rect.length, width, height), rectangles,
                area_params, side_ratio_params
            )
            recursive_generate(
                (xy[0] + rect.width, xy[1]),
                (rect.length, width - rect.width, height), rectangles,
                area_params, side_ratio_params
            )
        else:
            # horizontal section
            recursive_generate(
                (xy[0], xy[1] + rect.length),
                (length - rect.length, rect.width, height), rectangles,
                area_params, side_ratio_params
            )
            recursive_generate(
                (xy[0] + rect.width, xy[1]),
                (length, width - rect.width, height), rectangles,
                area_params, side_ratio_params
            )


def generate_rectangles(length, width, height, **kwargs):
    start_xy = 0, 0

    x = int(np.random.normal(width / 2, width / 20))
    y = int(np.random.normal(length / 2, length / 20))
    
    while width / 30 < x <= width / 10:
        x = int(np.random.normal(width / 2, width / 20))
    while length / 30 < y <= length / 10:
        y = int(np.random.normal(length / 2, length / 20))

    size_1_a = (int(y / 2), x, height), start_xy
    size_1_b = (y - int(y / 2), x, height), (0, int(y / 2))
    size_2_a = (y, int((width - x) / 2), height), (x, 0)
    size_2_b = (y, width - x - size_2_a[1], height), (x + size_2_a[0][1], 0)
    size_3_a = (int((width - y) / 2), width - x, height), (x, y)
    size_3_b = (length - y - size_3_a[0], width - x, height), (x, y + size_3_a[0][0])
    size_4_a = (length - y, int(x / 2), height), (0, y)
    size_4_b = (length - y, x - size_4_a[0][1], height), (size_4_a[1], y)

    regions = (
        size_1_a, size_1_b, size_2_a, size_2_b,
        size_3_a, size_3_b, size_4_a, size_4_b
    )
    rectangles = []
    for xy, regin in regions:
        recursive_generate(xy, regin, rectangles, **kwargs)

    return rectangles
