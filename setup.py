from setuptools import setup, find_packages

setup(
    name="scd-parser-visualizer",
    version="1.0.0",
    description="SCD File Parser and Logical Link Visualizer",
    author="SCD Parser Team",
    packages=find_packages(),
    install_requires=[
        "lxml>=4.9.0",
        "graphviz>=0.20.0",
        "networkx>=3.0",
        "flask>=2.3.0",
        "werkzeug>=2.3.0",
        "matplotlib>=3.7.0",
        "Pillow>=9.5.0"
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'scd-parser=scd_parser.cli:main',
        ],
    },
)