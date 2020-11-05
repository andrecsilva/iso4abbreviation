# Iso4Abbreviation

A small script (python3/abbr.py) and vim plugin to abbreviate titles according to ISO 4 format. The plugin is mostly a thin wrapper for the script.

Useful to organize `.bib` files.

## Script - Usage Example

Make sure you either have the [List of Title Abbreviation Words - LTWA](http://www.issn.org/services/online-services/access-to-the-ltwa/) as `LTWA\_\<date\>.txt`, where \<date\> is the build date of the LTWA file, or the tries.pkl file in the same directory. Then:

``` 
./abbr.py < titles.txt
```
Remember to `chmod +x` the script if needed. The script will generate a tries.pkl file containing a serializaton of the abbreviations read from the LTWA file. If some some more recent LTWA file is in the same directory, the tries.pkl file will be rebuilt.

## Plugin

### Requirements

Requires Vim with +python3.

### Instalation

Add the following to your `.vimrc`:

```
Plug andrecsilva/iso4abbreviation
```

Or manually copy the plugin/python3 directories to the your `.vim` directory.

### Mappings

`\<leader\>a{motion}` - abbreviates the words covered by the motion. (e.g. i{ or iw )

`v_\<leader\>a` - abbreviates the visually selected words.

`V_\<leader\>a` - abbreviates the visually selected lines.

## Updating the LTWA

Copy the most recent LTWA file into the directory containing  the script (`abbr.py`). Make sure the filename has the format `LTWA_\<date\>.txt` where \<date\> is the build date of the LTWA file.

## Known Problems and Questions/Issues

### Some compound words are not abbreviated

Currently there's no support for compound words that are not separated by hyphen (e.g. Forschungstechnologie -> Forsch.technol.).

### Single words are not abbreviated

Titles with a single word should not be abbreviated according to ISO4.

### Some titles have the wrong abbreviation

This happens sometimes with math journals as they don't stricly follow the ISO4 standard. For example, Discrete Mathematics is usually abbreviated to Discrete Math. but the ISO4 abbreviation is Disc. Math. You can customize the abbreviations on the LTWA file if needed.
