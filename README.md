# re0_translations

Repository for translations of content from [Re:Zero](https://en.wikipedia.org/wiki/Re:Zero), like side stories

Project files use the [OmegaT](https://omegat.org/) CAT for translation and translation memory

It's recommended to use [my fork of OmegaT](https://github.com/liraymond04/omegat), as it includes fixes for storing and using multiple reference language TMX files in a central translation memory folder

The dictionary used is the [CC-CEDICT](https://www.mdbg.net/chinese/dictionary?page=cedict) Chinese-English dictionary, and a conversion to the [Stardict format](https://simonwiles.net/projects/cc-cedict/) for use in OmegaT

## Converting docx to markdown

The `scripts` directory contains a [Python](https://www.python.org/) script that searches for OmegaT projects that contain translated documents in their `target` directories

OmegaT projects contain an `omegat.project` file in its directory, and translated documents are converted using [Pandoc](https://pandoc.org/), and its relative path in the project root is mirrored and outputted to a specified output directory

### Requirements

Install [pandoc](https://github.com/jgm/pandoc) and Python via your system's respective package manager

```bash
# Arch Linux
$: sudo pacman -S --needed pandoc python
```

### Usage

An example usage of the conversion script to search the current project for document files to convert to markdown and save to the `posts` directory

```bash
python scripts/convert.py ./ posts/ --lua-filter filters/docx-to-md.lua
```
