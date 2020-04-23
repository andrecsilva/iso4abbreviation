#!/usr/bin/env python3
import sys
import pickle
import os
import re
from functools import reduce

class Trie:
    """A simple implementation of a Trie without compression"""

    def __init__(self, data=None):
        self.data = data
        self.children = dict()


    def insert(self, key, data):
        """Insert a path in the Trie composed of the key (a list) elements in sequence."""
        if not key:
            if self.data is not None:
                pass
                #print("Conflicting entries:")
            self.data = data
        else:
            h, *l = key
            h = h.lower()
            if h not in self.children:
                self.children[h] = Trie()
            self.children[h].insert(l, data)
            
#non-recursive version, not really much faster
#    def insert(self, key, data):
#        """Insert a path in the Trie composed of the key (a list) elements in sequence."""
#        root = self
#        for c in key:
#            cl = c.lower()
#            if cl in root.children:
#                root = root.children[cl]
#            else:
#                root.children[cl] = Trie()
#                root = root.children[cl]
#        root.data = data

    def search(self, key, depth=0):
        """Search if there's a path in key composed of the key's sequence of elements."""
        if not key:
            if '*' in self.children:
                return self.children['*'].data, depth
            return self.data, depth

        h, *l = key
        h = h.lower()
        if '*' in self.children:
            return self.children['*'].data, depth
        if h in self.children:
            return self.children[h].search(l, depth)
        return None, None

    def searchDeepest(self, key, depth=0, deepest=0, ddata=None):
        """Search the deepest data matching a prefix of key"""
        if self.data is not None:
            ddata = self.data
            deepest = depth

        if not key:
            return depth, ddata

        h, *l = key
        h = h.lower()

        if '*' in self.children:
            return self.children['*'].data, depth

        if h in self.children:
            return self.children[h].searchDeepest(l, depth+1, deepest, ddata)
        return deepest, ddata

def cleanWord(word):
    """Clean a word. Removes explanations (e.g. 'Labor (work) -> Labor')
    and trims the leading/following whitespaces"""
    return word.split('(')[0].strip()

#TODO Doesn't really support compound word without hyphens. Should be fine for english at least.
def abbreviateWord(word, prefixTrie, suffixTrie):
    """Abbreviates a single word according to the prefix/suffix Tries.
    Words not included in LTWA are not abbreviated."""
    cword = cleanWord(word)

    sindex = None

    #TODO does not differentiate between uppercase and lowercase (change?)
    pabbrev = prefixTrie.search(cword)[0]

    #Prefixes take precedence over suffix patterns e.g. afield -> n.a.
    if pabbrev:
        if pabbrev == 'n.a.':
            return word
        return pabbrev

    sindex = sabbrev = None
    for sindex in range(len(cword)):
        sabbrev = suffixTrie.search(cword[sindex:])[0]
        if sabbrev:
            break
    if (sabbrev and sindex > 0):
        return word[:sindex] + sabbrev

    #Deals with composite hyphenated words AFTER it tries to abbreviate the whole word
    if '-' in cword:
        lw = cword.split('-')
        lw = [abbreviateWord(x, prefixTrie, suffixTrie) for x in lw]
        return reduce(lambda x, y: x+'-'+y, lw)

    #No abbreviation -> returns word
    return word

def abbreviate(wordList, prefixTrie, suffixTrie, lastWordTrie):
    """Abbreviates a list of words using the prefix/suffix/lastWord Tries"""

    if wordList == []:
        return []

    *l, w = wordList

    #Check if w is the last word of some word sequence
    ct = lastWordTrie.search(w)[0]
    if ct is not None:
        l.reverse()
        #search for the longest suffix ending with w
        d, abbrv = ct.searchDeepest(l)
        l.reverse()
        if abbrv is not None:
            if abbrv == 'n.a.':
                return abbreviate(l[:-d], prefixTrie, suffixTrie, lastWordTrie) + l[-d:] + [w]
            return abbreviate(l[:-d], prefixTrie, suffixTrie, lastWordTrie) +  [abbrv]

    return abbreviate(l, prefixTrie, suffixTrie, lastWordTrie) +\
           [abbreviateWord(w, prefixTrie, suffixTrie)]

def test_compound():
    pt = Trie()
    st = Trie()
    lwt = Trie()

    pt.insert('Haute-Corse', 'Ht.-Corse')
    pt.insert('airplane', 'airpl.')
    pt.insert('field', 'n.a.')
    st.insert('ship', 'sh.')

    s = ['airplane-airship-field-generator','Haute-Corse']
    r = abbreviate(s, pt, st, lwt)
    assert r == ['airpl.-airsh.-field-generator', 'Ht.-Corse']

def test_abbreviate():
    pt = Trie()
    st = Trie()
    lwt = Trie()
    pt.insert('graph*', 'gr.')
    pt.insert('Ciudad*', 'ciudad.')
    pt.insert('labor', 'n.a.')
    pt.insert('Labor', 'lab.')
    pt.insert('Universit*', 'univ.')
    pt.insert('Fairfield', 'Fairfld.')
    pt.insert('afield', 'n.a.')

    wl = 'Ciudad real'.split()
    *l, w = wl

    ct = Trie()
    l.reverse()
    ct.insert(l, 'Ciudad R.')
    lwt.insert(w, ct)

    wl = 'United States of America'.split()
    *l, w = wl

    ct = Trie()
    l.reverse()
    ct.insert(l, 'U. S. A.')
    lwt.insert(w, ct)

    wl = 'South Africa*'.split()
    *l, w = wl

    ct = Trie()
    l.reverse()
    ct.insert(l, 'S. Afr.')
    lwt.insert(w, ct)

    pt.insert('alcoholi*', 'alcohol.')

    st.insert('plane', 'pl.')
    st.insert('ship', 'sh.')
    st.insert('field', 'f.')

    s = ['alcoholic', 'ship', 'airplane', 'united', 'states', 'of',\
            'america', 'south', 'africanism', 'afield', 'Fairfield']

    assert abbreviate(s, pt, st, lwt) == ['alcohol.', 'ship', 'airpl.',\
            'U. S. A.', 'S. Afr.', 'afield', 'Fairfld.']

def test_cleanword():
    assert cleanWord('Labor (work)') == 'Labor'


#TODO make it download automaticaly
ltwaurl = ''

def getLtwa():
    """ Opens the latest LTWA file in the same directory """
    p = re.compile(r'ltwa_\d+', re.IGNORECASE)
    ls = os.listdir()
    ltwa_path = sorted(filter(p.match, ls))
    if len(ltwa_path) == 0:
        print("No LTWA file in the directory.")
    return ltwa_path[0]

def getLtwaDate():
    """ Returns the date of the lastest LTWA file in the same directory """
    p = re.compile(r'ltwa_\d+', re.IGNORECASE)
    ls = os.listdir()
    ltwa_path = sorted(filter(p.match, ls))[0]
    return int(ltwa_path.split('_')[1].split('.')[0])


#Cleans problematic entries from the ltwa file
def cleanLtwa():
    pass

#For now, it has only some common english articles, conjunctjions and prepositions
def removeForbidden(wordList):
    """Removes articles, conjunctions and prepositions from a list of words.
    Starting prepositions are not removed"""

    articles = [
        'a',
        'the',
        'an'
    ]

    wordList = [x for x in wordList if not x.lower() in articles]

    conjunctions = [
        'for',
        'and',
        'nor',
        'but',
        'or',
        'yet',
        'so',
        'until',
        'when',
        'whenever',
        'since',
        '&'
    ]

    wordList = [x for x in wordList if not x.lower() in conjunctions]

    prepositions = [
        'from',
        'of',
        'by',
        'on',
        'in',
        'at'
    ]

    #By ISO4, starting prepositions are not removed
    wordList = [wordList[0]] + [x for x in wordList[1:] if not x.lower() in prepositions]

    return wordList

#Fix punctuation
def fixPunctuation():
    pass

def getTries():
    """Deserializes Tries built from LTWA. Build from LTWA if they do not exist."""
    if os.path.isfile('tries.pkl'):
        with open('tries.pkl', 'rb') as tries_pkl:
            l = pickle.load(tries_pkl)
            if l[0] >= getLtwaDate():
                return l[1], l[2], l[3]
    pt, st, lwt = buildTries()
    with open('tries.pkl', 'wb') as tries_pkl:
        pickle.dump([getLtwaDate(), pt, st, lwt], tries_pkl)
    return pt, st, lwt



def buildTries():
    """ Parses the LTWA file and builds three Tries.
        prefixTrie: A Trie built with all the prefixes and words (e.g. Yankee, alchoholic-).
        The data in the nodes are the abbreviation. (e.g. Yank., alchohol.)
        suffixTrie: A Trie built with all the suffixes (e.g. -graph-, -field).
        The data in the nodes are the abbreviations (e.g. gr., fl.)
        lastWordTrie: A Trie built with the last word from all the expressions
        with more than one word (e.g. Africa in South Africa-).
        The data in the nodes are the list of words in the rest of the expression in reverse order
        (e.g. ['of', 'States', 'United'] in United States of America)
    """
    with open(getLtwa(), 'r', encoding='utf-16_le') as ltwa_file:
        #Skip first line with field names
        ltwa_file.readline()
        pt = Trie()
        st = Trie()
        lwt = Trie()

        for line in ltwa_file:
            word, abbrv, lang = line.split('\t')
            word = cleanWord(word)

            words = word.split()
            #check if it is a compound expression
            if len(words) > 1:
                lastword = words.pop()
                if lastword.endswith('-'):
                    lastword = lastword[:-1] + '*'
                ct = lwt.search(lastword)[0]
                words.reverse()
                if ct is None:
                    ct = Trie()
                    ct.insert(words, abbrv)
                    lwt.insert(lastword, ct)
                else:
                    ct.insert(words, abbrv)
                words.reverse()

            else:
                #replaces - at the end of the words with * to not confuse with hyphenated words
                if word.endswith('-'):
                    word = word[:-1] + '*'
                if word.startswith('-'):
                    st.insert(word[1:], abbrv)
                else:
                    pt.insert(word, abbrv)

    return pt, st, lwt


#TODO cut pdf Mathscinet and get abbreviations
#example -> https://github.com/marcinwrochna/tokenzeroBot/blob/master/abbrevIsoBot/databases.py
def msnParser():
    pass

def cleanAndAbbreviate(line,pt,st,lwt):
    s = line.strip().split()
    if len(s) > 1:
        s = abbreviate(s, pt, st, lwt)
        s = removeForbidden(s)
        s = reduce(lambda x, y: x+ ' ' + y, s)
        return s.title()
    if len(s) == 1:
        return s[0]
    return ''

def main():
    pt, st, lwt = getTries()

    for line in sys.stdin:
        s = cleanAndAbbreviate(line,pt,st,lwt)
        if s is not '':
            print(s)

if __name__ == "__main__":
    main()
