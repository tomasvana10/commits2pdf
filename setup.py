from setuptools import setup, find_packages

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="commits2pdf",
    version="0.1",
    author="Tomas Vana",
    url="https://github.com/tomasvana/commits2pdf",
    description="View commit history through a PDF",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    license="MIT",
    install_requires=[],
    classifiers=[
        "Topic :: Multimedia"
    ],
    platforms="any",
    entry_points={
        "console_scripts": [
            "commits2pdf = commits2pdf.cli:main"
        ],
        "gui_scripts": [
            "commits2pdf-ctk = commits2pdf.gui:main"
        ]
    }
)