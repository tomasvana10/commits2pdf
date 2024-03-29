from setuptools import setup, find_packages

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="commits2pdf",
    version="0.0.2",
    author="Tomas Vana",
    url="https://github.com/tomasvana10/commits2pdf",
    description="View commit history through a PDF",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "GitPython"
    ],
    classifiers=[
        "Topic :: Multimedia"
    ],
    platforms="any",
    entry_points={
        "console_scripts": [
            "commits2pdf = commits2pdf.cli:main"
        ],
    }
)