import json
from collections import namedtuple
from itertools import chain
from math import prod
from operator import itemgetter
from pathlib import Path

from visualize import cutting_chart, example_parameters
from generate import Rectangle


def read_json_file(file_name: str):
    path = Path(file_name)
    try:
        path = path.resolve(strict=True)
    except FileNotFoundError:
        print('Could not open file')
    else:
        print(f'Read from {path}')
        with open(path, 'r') as f:
            data = json.load(f)
        return data


def read_txt_file(file_name: str):
    path = Path(file_name)
    try:
        path = path.resolve(strict=True)
    except FileNotFoundError:
        print('Could not open file')
    else:
        print(f'Read from {path}')
        data = {}
        with open(path, 'r') as f:
            data['ingot'] = tuple(map(int, f.readline().split()))
            m = int(f.readline())
            data['bins'] = []
            for _ in range(m):
                data['bins'].append(tuple(map(float, f.readline().split())))
            n = int(f.readline())
            data['rectangles'] = []
            for _ in range(n):
                parameters = f.readline().split()
                x, y, l, w = tuple(map(int, parameters[:4]))
                h = float(parameters[4])
                if len(parameters) == 6:
                    p = int(parameters[-1])
                else:
                    p = 0
                data['rectangles'].append(
                    Rectangle((x, y), l, w, h, p)
                )
        return data


def print_example_parameters(data):
    m = len(data['bins'])
    n = len(data['rectangles'])
    area = tuple(map(prod, map(itemgetter(1, 2), data['rectangles'])))
    ratio = tuple(map(lambda item: item[0] / item[1], map(itemgetter(1, 2), data['rectangles'])))
    heights = sorted(list(set(map(itemgetter(-2), data['rectangles']))), reverse=True)
    print('-' * 50)
    print(f'1)   Number of groups                  : {m}')
    print(f'2)   Number of rectangles              : {n}')
    print(f'3)   Average number of elements per bin: {n / m:.4f}')
    print(f'4.1) Min area                          : {min(area):.4f}')
    print(f'4.2) Max area                          : {max(area):.4f}')
    print(f'4.3) Average area                      : {sum(area) / n:.4f}')
    print(f'5.1) Min aspect ratio                  : {min(ratio):.4f}')
    print(f'5.2) Max aspect ratio                  : {max(ratio):.4f}')
    print(f'5.3) Average aspect ratio              : {sum(ratio) / n:.4f}')
    print(f'6)   All heights                       : {heights}')
    print('-' * 50)


def visualize_example(containers, rectangles):
    answers = {
        ('y', 'yes'): True,
        ('n', 'no'): False,
    }
    msg = 'Visualize? [yes/no]: '
    while (s := input(msg).lower()):
        if s in tuple(chain.from_iterable(answers.keys())):
            break
    is_visualize = answers[tuple(filter(lambda x: s in x, answers.keys()))[0]]
    if is_visualize:
        for length, width, height in containers:
            rect = list(filter(lambda x: x[-2] == height, rectangles))
            cutting_chart(width, length, rect, with_borders=True)
        
        example_parameters(rectangles)


def main():
    msg = 'Enter the number of the example (or exit): '
    while (number := input(msg)) != 'exit' and number.isdigit():
        number = int(number)
        file_name = f'txt_coordinates/problem_{number}.txt'
        data = read_txt_file(file_name)
        print_example_parameters(data)
        rectangles = data['rectangles']
        visualize_example(data['bins'], rectangles)


if __name__ == '__main__':
    main()
