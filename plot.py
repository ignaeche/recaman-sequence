from recaman import recaman, recaman_circles, Quadrant, Direction

import argparse, os, itertools

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import patches, animation
from matplotlib.axes import Axes

from tqdm import tqdm

DEFAULT_FPS = 240
DEFAULT_DPI = 100
PLOT_MARGIN = 1
LINE_WIDTH = 0.2

def save_filepath(directory, filename):
    dirpath = os.path.join(os.path.dirname(__file__), directory)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    return os.path.join(dirpath, filename)

def make_semicircle(center_x, diameter, angles):
    return patches.Arc((center_x, 0), diameter, diameter, theta1=angles[0], theta2=angles[1], linewidth=LINE_WIDTH)

def add_circles(axes: Axes, circles: list):
    for circle in circles:
        angles = (180, 0) if circle['quadrant'] == Quadrant.NEG else (0, 180)
        arc = make_semicircle(circle['center'], circle['diameter'], angles)
        axes.add_patch(arc)

def prepare_figure(sequence: list, circles: list):
    # Get diameter of the biggest circle
    max_diameter = max(circles, key=lambda x: x['diameter'])['diameter']
    
    fig, ax = plt.subplots()
    # Hide axes
    ax.set_frame_on(False)
    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    # Set plot limits
    ax.set_xlim(0 - PLOT_MARGIN, max(sequence) + PLOT_MARGIN)
    ax.set_ylim(-(max_diameter / 2 + PLOT_MARGIN), max_diameter / 2 + PLOT_MARGIN)
    # Make axes equal
    ax.set_aspect('equal', adjustable='box')

    return fig, ax

def save_figure(fig, filename: str, dpi):
    # Save figure
    # Remove bbox_inches='tight' if you need all generated images to be the same size
    fig.savefig(filename, dpi=dpi, bbox_inches='tight')

def animate_frame(frame, axes, circles, patch_list):
    (n, deg) = frame
    circle = circles[n]
    if deg == 0:
        # First frame on new semicircle
        angle = 180 if circle['direction'] == Direction.RIGHT else 0
        arc = make_semicircle(circle['center'], circle['diameter'], (angle, angle))
        axes.add_patch(arc)
        patch_list.append(arc)
        return arc,
    else:
        # Change start or end angle according to quadrant and direction
        arc = patch_list[n]
        if circle['quadrant'] == Quadrant.NEG:
            if circle['direction'] == Direction.RIGHT:
                arc.theta2 = 180 + deg
            else:
                arc.theta1 = 360 - deg
        else:
            if circle['direction'] == Direction.RIGHT:
                arc.theta1 = 180 - deg
            else:
                arc.theta2 = deg
        return arc,

def animate(fig, axes, circles: list, degree_skip: int = 1):
    # Generate iterable for animation
    frames = [(circle, degrees)
        for circle in range(len(circles))
        for degrees in itertools.chain(range(0, 180, degree_skip), [180]) # Add 180 to end of range to ensure full semicircle
    ]

    # Empty init
    def init_frame():
        return []
    
    return animation.FuncAnimation(
        fig,
        animate_frame,
        init_func=init_frame,
        frames=tqdm(frames, desc='Animating'),
        fargs=(axes, circles, [],),
        interval=1,
        blit=True)

def save_animation(anim: animation.FuncAnimation, filename: str, dpi: int, fps: int):
    anim.save(filename, dpi=dpi, fps=fps)

def remove_patches(axes: Axes):
    [p.remove() for p in reversed(axes.patches)]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot the first N numbers of the Recamán sequence')
    parser.add_argument('N', type=int)
    parser.add_argument('--start', type=int, default=0, metavar='M', help='Start the sequence with M')
    parser.add_argument('--format', choices=['png', 'svg'], default='png', help='Choose a format for the plot')
    parser.add_argument('--dpi', type=int, default=DEFAULT_DPI, help='Set DPI for the plot')
    parser.add_argument('--line-width', type=float, default=LINE_WIDTH, metavar='WIDTH', help='Set line width of circles')
    parser.add_argument('--anim', action='store_true', help='Animate plot')
    parser.add_argument('--fps', type=int, default=DEFAULT_FPS, help='Set frames per second of animation')
    parser.add_argument('--anim-dpi', type=int, default=DEFAULT_DPI, metavar='DPI', help='Set DPI for the animation')
    parser.add_argument('--degree-skip', type=int, default=1, metavar='SKIP', help='Set degrees to skip in circle animation')

    args = parser.parse_args()

    sequence = recaman(args.N, args.start)
    circles = recaman_circles(sequence)
    if not circles:
        print('Not enough circles to plot')
        exit(-1)

    # Set line width for plot and animation
    LINE_WIDTH = args.line_width

    # Make plot
    fig, ax = prepare_figure(sequence, circles)
    add_circles(ax, circles)
    filename = save_filepath('plots', 'recaman_{0}_start_{1}.{2}'.format(args.N, args.start, args.format))
    save_figure(fig, filename, args.dpi)

    # Make animation if requested
    if args.anim:
        # Remove patches instead of creating new figure and axes
        # fig, ax = prepare_figure(sequence, circles)
        remove_patches(ax)
        anim = animate(fig, ax, circles, degree_skip=args.degree_skip)
        filename = save_filepath('animations', 'recaman_{0}_start_{1}.mp4'.format(args.N, args.start))
        save_animation(anim, filename, args.anim_dpi, args.fps)