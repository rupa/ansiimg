#! /usr/bin/env python
"""
Images in B/W, Greyscale, 16 and 256 ANSI colors, delivered to STDOUT.

Demo: `curl https://raw.githubusercontent.com/rupa/ansiimg/master/demo.ansi`
"""

from itertools import product

from numpy import array, reshape
from PIL import Image
from scipy.cluster.vq import vq

# 16 colors
SYSTEM = [
    (0x00, 0x00, 0x00),
    (0x80, 0x00, 0x00),
    (0x00, 0x80, 0x00),
    (0x80, 0x80, 0x00),
    (0x00, 0x00, 0x80),
    (0x80, 0x00, 0x80),
    (0x00, 0x80, 0x80),
    (0xc0, 0xc0, 0xc0),
    (0x80, 0x80, 0x80),
    (0xff, 0x00, 0x00),
    (0x00, 0xff, 0x00),
    (0xff, 0xff, 0x00),
    (0x00, 0x00, 0xff),
    (0xff, 0x00, 0xff),
    (0x00, 0xff, 0xff),
    (0xff, 0xff, 0xff),
]
# Heres' how the 216 rgb colors are mapped
RGB_PARTITIONS = (0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff)
RGB = list(product(RGB_PARTITIONS, repeat=3))
# (8, 8, 8) ... (238, 238, 238) in increments of 10
GREYSCALE = [(i, i, i) for i in range(0x08, 0xef)[0::10]]

ANSI_RGB = list(enumerate(SYSTEM + RGB + GREYSCALE))
RGB_TO_ANSI = {rgb: i for i, rgb in ANSI_RGB}
ANSI_TO_RGB = {i: rgb for i, rgb in ANSI_RGB}
ANSI_TO_HEX = {
    ansi: ''.join('{0:02x}'.format(i) for i in ANSI_TO_RGB[ansi])
    for ansi in ANSI_TO_RGB
}

PALLETE_BW = array(((0, 0, 0), (255, 255, 255)))
PALLETE_16 = array(SYSTEM)
PALLETE_GREYSCALE = array(GREYSCALE + [(0, 0, 0), (255, 255, 255)])
PALLETE_256 = array(SYSTEM + RGB + GREYSCALE)
PALLETES = {
    'bw': PALLETE_BW,
    '16': PALLETE_16,
    'greyscale': PALLETE_GREYSCALE,
    '256': PALLETE_256,
}

def quantize(img, palette):
    """
    Quantize an image with a given color palette. Channels must match.
    """
    img = array(img)
    height, width, channels = img.shape
    # reshape to array of points
    pixels = reshape(img, (height * width, channels))
    # quantize
    qnt, _ = vq(pixels, palette)
    # reshape back to image
    return palette[reshape(qnt, (height, width))]

def ansi_pixel(ansi, close=False, text=False, nl=False):
    return '\033[38;5;{0:02};48;5;{0:02}m  {1}{2}{3}{4}'.format(
        ansi,
        '\033[m' if close is True else '',
        ' ' if text else '',
        text if text else '',
        '\n' if nl is True else ''
    )

def img_to_ansi(filename, max_size, alpha, palletes):

    img = Image.open(filename)
    img.thumbnail(max_size, Image.ANTIALIAS)
    width, height = img.size

    bands = img.getbands()
    if bands == ('R', 'G', 'B'):
        # RGB is all set
        pass
    elif bands == ('R', 'G', 'B', 'A'):
        # convert RGBA to RGB
        img2 = Image.new('RGB', (width, height), (alpha, alpha, alpha))
        img2.paste(img, mask=img.split()[3]) # 3 is the alpha channel
        img = img2
    elif bands == ('P',):
        # Needs work
        for y in xrange(height):
            for x in xrange(width):
                ansi = img.getpixel((x, y))
                yield ansi_pixel(ansi)
            yield '\033[m\n'
        return
    else:
        raise Exception('Weird image bands: {0}'.format(bands))

    for pallete in palletes:
        pixels = quantize(img, pallete)
        for x in xrange(height):
            for y in xrange(width):
                rgb = tuple(pixels[x][y])
                yield ansi_pixel(RGB_TO_ANSI[rgb])
            yield '\033[m\n'

def colorcubes():
    """
    Pretty.
    """
    for rgb in SYSTEM:
        yield ansi_pixel(RGB_TO_ANSI[rgb], close=True)
    yield '\n'
    for idx, rgb in enumerate(RGB):
        yield ansi_pixel(RGB_TO_ANSI[rgb], close=True)
        if (idx + 1) % 36 == 0:
            yield '\n'
    for rgb in GREYSCALE:
        yield ansi_pixel(RGB_TO_ANSI[rgb], close=True)
    yield '\n'

def ansicubes(ansis):
    """
    Show colorcube and values.
    """
    for ansi in ansis:
        yield ansi_pixel(
            ansi,
            close=True,
            text='{0:02} {1} {2}'.format(
                ansi, ANSI_TO_RGB[ansi], ANSI_TO_HEX[ansi],
            ),
            nl=True
        )

def ansifiles(filenames, max_size, alpha, palletes):
    """
    Pretty (image) files.
    """
    for filename in filenames:
        for char in img_to_ansi(filename, max_size, alpha, palletes):
            yield char

if __name__ == '__main__':
    import argparse
    import os
    import struct
    import sys
    from fcntl import ioctl
    from termios import TIOCGWINSZ

    def terminal_size(fd=1):
        try:
            return struct.unpack('hh', ioctl(fd, TIOCGWINSZ, '1234'))
        except:
            try:
                return (os.environ['LINES'], os.environ['COLUMNS'])
            except:
                return (25, 80)

    def valid_ansi(arg):
        if arg.isdigit() and 0 <= int(arg) <= 255:
            return int(arg)
        raise argparse.ArgumentTypeError('0-255 required')

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--alpha',
        type=valid_ansi,
        default=0,
        help='alpha value for RGBA images (0-255, default %(default)s)'
    )
    parser.add_argument(
        '--ansi',
        nargs='*',
        metavar='COLOR',
        type=valid_ansi,
        help='info for ANSI color (0-255)'
    )
    parser.add_argument('--colors', action='store_true', help='color cubes')
    parser.add_argument('files', nargs='*', metavar='file', help='image files')
    parser.add_argument(
        '-p', '--pallete',
        choices=sorted(PALLETES.keys()),
        action='append',
        help='pallete(s) to use',
    ),
    parser.add_argument(
        '--width',
        type=int,
        default=terminal_size()[1],
        help='default is terminal width (%(default)s)'
    )
    args = parser.parse_args()

    if args.pallete is None:
        args.pallete = [PALLETE_256]
    else:
        args.pallete = [PALLETES[x] for x in args.pallete]

    if args.colors:
        for x in colorcubes():
            sys.stdout.write(x)
    elif args.ansi:
        for x in ansicubes(args.ansi):
            sys.stdout.write(x)
    elif args.files:
        # divide width by 2 as each char is 2x1px, make height huge
        max_size = (args.width / 2, sys.maxint)
        for x in ansifiles(args.files, max_size, args.alpha, args.pallete):
            sys.stdout.write(x)
    else:
        parser.print_usage()

    # Don't complain about a pipe
    try:
        sys.stdout.close()
    except IOError:
        pass
