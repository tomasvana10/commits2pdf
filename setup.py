from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="commits2pdf",
    version="1.1.17",
    author="Tomas Vana",
    url="https://github.com/tomasvana10/commits2pdf",
    description="Convert Git commits to a PDF",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    license="MIT",
    platforms="any",
    install_requires=[
        "GitPython",
        "fpdf",
        "tqdm",
        "pathvalidate"
    ],
    entry_points={
        "console_scripts": [
            "c2p = commits2pdf.cli:main"
        ]
    },
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
    ]
)
