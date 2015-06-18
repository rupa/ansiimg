from setuptools import setup

setup(
    name='ansiimg',
    version='0.1',
    description=(
        'Images in B/W, Greyscale, 16 and 256 ANSI colors, delivered to STDOUT'
    ),
    url='http://github.com/rupa/ansiimg',
    author='rupa',
    author_email='rupa@lrrr.us',
    license='MIT',
    packages=['ansiimg'],
    package_data={'ansiimg': ['Impact.ttf']},
    entry_points={
        'console_scripts': ['ansi=ansiimg.ansi:main'],
    },
    zip_safe=False
)
