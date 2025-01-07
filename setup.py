from setuptools import setup, find_packages

setup(
    name="amutils",
    version="0.0.1",
    py_modules=["main", "bridge", "file_reader"],
    packages=find_packages(),
    install_requires=[
        "appscript",
        "mutagen",
    ],
    entry_points={
        "console_scripts": [
            "amutils=main:main",
        ],
    },
    author="realtvop",
    description="Apple Music Utilties",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/realtvop/amutils",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
) 