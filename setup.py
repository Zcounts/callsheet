# setup.py
from setuptools import setup, find_packages

setup(
    name="CallSheetGenerator",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "reportlab",
        "pillow",
    ],
    entry_points={
        'console_scripts': [
            'callsheet=main:main',
        ],
    },
)
