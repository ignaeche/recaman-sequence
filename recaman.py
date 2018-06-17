import argparse
from enum import Enum

def recaman(n: int, start: int = 0):
    sequence = []
    for i in range(n):
        if (i == 0):
            x = start
        else:
            x = sequence[i - 1] - i
        if (x >= 0 and x not in sequence):
            sequence.append(x)
        else:
            sequence.append(sequence[i - 1] + i)
    return sequence

Quadrant = Enum('Quadrant', 'POS NEG')
Direction = Enum('Direction', 'RIGHT LEFT')

def recaman_circles(sequence: list):
    circles = []
    start = sequence[0]
    for index, number in enumerate(sequence[1:]):
        circles.append({
            'quadrant': Quadrant.NEG if index % 2 == 0 else Quadrant.POS,
            'center': (start + number) / 2,
            'diameter': index + 1,
            'direction': Direction.RIGHT if number - start > 0 else Direction.LEFT
        })
        start = number
    return circles

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Returns the first N numbers of the Recamán sequence')
    parser.add_argument('N', type=int)
    parser.add_argument('--start', type=int, default=0, metavar='M', help='Start the sequence with M')

    args = parser.parse_args()

    print(recaman(args.N, args.start))