# FolderCompare

![GitHub release (latest by date)](https://img.shields.io/github/v/release/skarfie123/FolderCompare)
![GitHub all releases](https://img.shields.io/github/downloads/skarfie123/FolderCompare/total)
![GitHub issues](https://img.shields.io/github/issues/skarfie123/FolderCompare)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

## Installation

`pipx install compare-folders`

## Usage

`compare-folders path\to\source path\to\destination`

This will write a markdown file with:

- missing files from the source not in the destination
- extra files in the destination not in the source
- files in both locations with different modification dates

It will also print a table of stats.

Use `-o`/`--output` to override the output filename. If the output file already exists, the resulsts will be appended to the file, unless you specify `--no-append`, in which case the file will be overwritten.
