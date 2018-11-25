import re

def find_codewords(codeword_fragment, wordlist):
    match_list = wordlist.copy()
    match_list = [word for word in match_list if len(word) >= len(codeword_fragment) and len(set(word)) == len(word)]
    codeword_regex = codeword_fragment.replace("_", ".")
    pattern = re.compile(codeword_regex)
    match_list = [word for word in match_list if pattern.search(word) != None]
    return match_list



