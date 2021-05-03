from collections import Counter
from operator import itemgetter

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def cutting_chart(width, length, rectangles, with_borders=False):
    fig = plt.figure()
    axes = fig.add_subplot(1, 1, 1)
    axes.add_patch(
        patches.Rectangle((0, 0), width, length, hatch='x', fill=False)
    )
    for _, r in enumerate(rectangles):
        color = np.random.uniform(size=(3, ))
        axes.add_patch(
            patches.Rectangle(r.xy, r.width, r.length, color=color)
        )
        if with_borders:
            axes.add_patch(
                patches.Rectangle(r.xy, r.width, r.length,
                fill=False, edgecolor='black', linewidth=1)
            )
        # x, y = r.xy
        # axes.text(x + 0.48 * r.width, y + 0.48 * r.length, str(i))
    axes.set_xlim(0, width)
    axes.set_ylim(0, length)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


def dataset_parameters(examples):
    _, axes = plt.subplots(1, 3)
    count = Counter([len(item["bins"]) for item in examples]).items()
    axes[0].bar(
        list(map(itemgetter(0), count)),
        list(map(itemgetter(1), count)),
        label='Number of groups'
    )
    axes[1].hist(
        [len(item["rectangles"]) / len(item["bins"]) for item in examples],
        label='Instances per bin'
    )
    axes[2].hist(
        [len(item["rectangles"]) for item in examples],
        label='Number of instances per example'
    )
    for axis in axes:
        axis.legend()
        axis.grid()
    plt.show()


def example_parameters(rectangles):
    ratio = [r.length / r.width for r in rectangles]
    squares = [r.length * r.width for r in rectangles]
    _, axes = plt.subplots(1, 3)
    axes[0].hist(ratio, label=r'$\frac{L}{W}$ ratio')
    axes[1].hist(squares, label='Square')
    axes[2].hist([r.priority for r in rectangles], label='Priority')

    for axis in axes:
        axis.legend()
        axis.grid()
    plt.show()
