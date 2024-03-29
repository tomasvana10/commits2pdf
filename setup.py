from setuptools import setup, find_packages

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="commits2pdf",
    version="1.0.3",
    author="Tomas Vana",
    url="https://github.com/tomasvana10/commits2pdf",
    description="View commit history through a PDF",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "GitPython",
        "pycairo"
    ],
    classifiers=[
        "Topic :: Multimedia",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Education",
        "Topic :: Office/Business",
    ],
    platforms="any",
    entry_points={
        "console_scripts": [
            "commits2pdf = commits2pdf.cli:main"
        ],
    }
)