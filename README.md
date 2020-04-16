# Iso4Abbreviation

A small script to abbreviate titles according to ISO 4 format. Reads a list of titles from stdin and outputs the abbreviations.

I use it within Vim to organize my .bib files.

# Usage Example

Make sure you have the [List of Title Abbreviation Words - LTWA](http://www.issn.org/services/online-services/access-to-the-ltwa/) as ltwa.txt in the same directory. Then:

``` ./abbr.py < titles.txt ```


# Known Problems

Currently there's no support for compound words that are not separated by hyphen (e.g. Forschungstechnologie -> Forsch.technol.). 
