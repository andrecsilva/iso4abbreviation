import sys
import pytest

class Trie:
    """A simple implementation of a Trie without compression"""

    def __init__(self,data=None):
        self.data= data
        self.children = dict()


    def insert(self,key,data):
        """Insert a path in the Trie composed of the key (a list) elements in sequence."""
        if(not key):
            if(self.data is not None):
                print("Conflicting entries:")
                print(self.data + ' ' + data)
            self.data = data
        else:
            h,*l = key
            h = h.lower()
            if (h not in self.children):
                self.children[h] = Trie()
            self.children[h].insert(l,data)

    def search(self,key,depth=0):
        """Search if there's a path in key composed of the key's sequence of elements."""
        if (not key):
            return self.data, depth

        h,*l = key
        h = h.lower()
        if ('*' in self.children):
            return self.children['*'].data,depth
        if (h in self.children):
            return self.children[h].search(l,depth+1)
        else:
            return None, None

    def searchDeepest(self,key,depth=0,deepest=0,ddata=None):
        """Search the deepest data matching a prefix of key"""
        if(self.data is not None):
            ddata=self.data
            deepest=depth

        if (not key):
            return depth, ddata

        h,*l = key
        h = h.lower()

        if ('*' in self.children):
            return self.children['*'].data,depth

        if (h in self.children):
            return self.children[h].searchDeepest(l,depth+1,deepest,ddata)
        else:
            return deepest, ddata

def cleanWord(word):
    """Clean a word. Removes explanations (e.g. 'Labor (work) -> Labor') and trims the leading/following whitespaces"""
    return word.split('(')[0].strip()


#What if a word matches a suffix and prefix? e.g. Fairfield -> Fairfld. but -field -> -f. 
def abbreviateWord(word,prefixTrie,suffixTrie):
    """Abbreviates a single word according to the prefix/suffix Tries. Words not included in LTWA are not abbreviated."""
    cword = cleanWord(word)
    pindex = sindex = None
    abbrev = None

    #TODO does not differentiate between uppercase and lowercase (change?)
    pabbrev = prefixTrie.search(cword)[0]
    
    #Prefixes take precedence over suffix patterns e.g. afield -> n.a.
    if (pabbrev):
        if pabbrev == 'n.a.':
            return word
        else:
            return pabbrev

    sindex = sabbrev = None
    for sindex in range(len(cword)):
        sabbrev = suffixTrie.search(cword[sindex:])[0]
        if(sabbrev):
            break
    if (sabbrev and sindex>0):
        return word[:sindex] + sabbrev

    #No abbreviation -> returns word
    return word

def abbreviate(wordList,prefixTrie,suffixTrie,lastWordTrie):
    """Abbreviates a list of words using the prefix/suffix/lastWord Tries"""
   
    if (wordList == []):
        return []

    *l,w = wordList

    #Check if w is the last word of some word sequence
    ct = lastWordTrie.search(w)[0]
    if (ct is not None):
        #search for the longest suffix ending with w
        l.reverse()
        d, abbrv = ct.searchDeepest(l)
        l.reverse()
        return abbreviate(l[:-d],prefixTrie,suffixTrie,lastWordTrie) +  [abbrv]
    else:
        return abbreviate(l,prefixTrie,suffixTrie,lastWordTrie) +  [abbreviateWord(w,prefixTrie,suffixTrie)]
    
def test_abbreviate():
    pt = Trie()
    st = Trie()
    lwt = Trie()
    pt.insert('graph*','gr.')
    pt.insert('Ciudad*','ciudad.')
    pt.insert('labor','n.a.')
    pt.insert('Labor','lab.')
    pt.insert('laboratoir$','lab.')
    pt.insert('Universit*','univ.')
    pt.insert('Fairfield','Fairfld.')
    pt.insert('afield','n.a.')

    wl = 'Ciudad real'.split()
    *l , w = wl

    ct = Trie()
    l.reverse()
    ct.insert(l,'Ciudad R.')
    lwt.insert(w,ct)

    wl = 'United States of America'.split()
    *l,w = wl

    ct = Trie()
    l.reverse()
    ct.insert(l,'U. S. A.')
    lwt.insert(w,ct)

    wl = 'South Africa*'.split()
    *l,w = wl

    ct = Trie()
    l.reverse()
    ct.insert(l,'S. Afr.')
    lwt.insert(w,ct)

    pt.insert('alcoholi*','alcohol.')

    st.insert('plane','pl.')
    st.insert('ship','sh.')
    st.insert('field','f.')

    s = ['alcoholic','ship','airplane','united','states','of','america','south','africanism','afield','Fairfield']

    assert abbreviate(s,pt,st,lwt) == ['alcohol.','ship','airpl.','U. S. A.','S. Afr.','afield','Fairfld.']

def test_cleanword():
    assert cleanWord('Labor (work)') == 'Labor'

ltwaurl = ''

#Open the ltwa file, downloads if either is does not exists or needs update
def getLtwa():
    return open('ltwa.txt','r')

#Cleans problematic entries from the ltwa file
def cleanLtwa():
    pass

#Remove forbidden words in ISO4 abbreviation (e.g. of)
def removeForbidden():
    pass

def getTries():
    """ Parses the LTWA file and builds three Tries.
        prefixTrie: A Trie built with all the prefixes and words (e.g. Yankee, alchoholic-). The data in the nodes are the abbreviation. (e.g. Yank., alchohol.)
        suffixTrie: A Trie built with all the suffixes (e.g. -graph-, -field). The data in the nodes are the abbreviations (e.g. gr., fl.)
        lastWordTrie: A Trie built with the last word from all the expressions with more than one word (e.g. Africa in South Africa-). The data in the nodes are the list of words in the rest of the expression in reverse order (e.g. ['of', 'States', 'United'] in United States of America)
    """
    file = getLtwa()
    #Skip first line with field names
    file.readline()
    pt = Trie()
    st = Trie()
    lwt = Trie()

    for line in file:
        word,abbrv,lang = line.split('\t')
        word = cleanWord(word)

        words = word.split()
        #check if it is a compound expression
        if len(words) >1:
            lastword = words.pop()
            if lastword.endswith('-'):
                lastword = lastword[:-1] + '*'
            ct = Trie()
            ct.insert(words.reverse(),abbrv)
            lwt.insert(lastword,lwt)
        else:
            #replaces - at the end of the words with * to not confuse with hyphenated words
            if word.endswith('-'):
                word = word[:-1] + '*'
            if word.startswith('-'):
                st.insert(word[1:],abbrv)
            else:
                pt.insert(word,abbrv)

    return pt,st,lwt


#TODO cut pdf Mathscinet and get abbreviations
#example -> https://github.com/marcinwrochna/tokenzeroBot/blob/master/abbrevIsoBot/databases.py
def msnParser():
    pass
