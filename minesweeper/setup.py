from setuptools import setup, find_packages


setup(
    name="minesweeper",
    version="0.1.0",
    description="Inefficient Minesweeper Solver",
    long_description="A very inefficient minesweeper solver.",
    author="rhdzmota",
    packages=find_packages(where="src"),
    package_dir={
        "": "src"
    },
    include_package_data=True,
    scripts=[
        "bin/minesweeper"
    ],
    python_requires=">3.5, <4"
)
