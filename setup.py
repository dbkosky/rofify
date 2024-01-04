from setuptools import setup, find_packages

with open("README.md", 'r') as fh:
    long_description = fh.read()

setup(

    name="rofify",
    version="0.0.41",
    description="Rofi menu script that controls spotify playback.",
    url="https://github.com/dbkosky/rofify.git",
    author="Daniel Kosky",
    author_email="dbkosky@gmail.com",

    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=find_packages(),
    keywords=['spotify', 'rofi'],

    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],

    install_requires=[
        "spotipy>=2.7.0",
        "spotipy<=2.18.0",
        "rofi_menu>=0.5.1",
        "rofi_menu<=0.6",
    ],
)
