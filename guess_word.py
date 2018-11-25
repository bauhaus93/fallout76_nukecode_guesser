import string
import multiprocessing as mp
import logging
import time
import os
import re

logger = logging.getLogger()

def guess_word_exact(codeword, wordlist):
    logger.info("Guessing exact codewords")
    possible_codewords = set(enum_possibilities(codeword))
    logger.debug("Generated possible codewords: {}".format(len(possible_codewords)))

    logger.debug("Intersecting possible codewords with wordlist...")
    intersection = possible_codewords.intersection(wordlist)
    return list(intersection)

def cull_list(codeword_fragment, wordlist):
    size_before = len(wordlist)
    wordlist = [word for word in wordlist if len(word) >= len(codeword_fragment) and len(set(word)) == len(word)]
    ex = ""
    for char in codeword_fragment:
        if char == "_":
            ex += "."
        else:
            ex += char
    pattern = re.compile(ex)
    wordlist = [word for word in wordlist if pattern.search(word) != None]
    logger.info("Culled wordlist from {} to {} applicable words".format(size_before, len(wordlist)))

    return wordlist

def guess_word_super(codeword_fragment, wordlist, pool_size = os.cpu_count(), task_size = 100):
    logger.info("Guessing super codewords")
    wordlist = wordlist.copy()
    possible_codewords = enum_possibilities(codeword_fragment)
    logger.info("Generated codewords from fragment: {}".format(len(possible_codewords)))

    wordlist = cull_list(codeword_fragment, wordlist)

    words_found = set()
    pool = mp.Pool(processes = pool_size)
    last_print = time.time()
    total_possible_codewords = len(possible_codewords)
    while len(possible_codewords) > 0:
        word_batch = possible_codewords[:task_size * pool_size]
        possible_codewords = possible_codewords[task_size * pool_size:]
        results = [pool.apply_async(get_super_words, (word_batch[i:i + task_size], wordlist)) for i in range(0, len(word_batch), task_size)]
        for r in results:
            words_found = words_found.union(r.get())
        
        if time.time() - last_print > 3:
            last_print = time.time()
            progress = 100 * (total_possible_codewords - len(possible_codewords)) / total_possible_codewords
            logger.info("Progress: {:5.2f}%, found codewords: {}".format(progress, len(words_found)))
    return list(words_found)

def enum_possibilities(word):
    blank_index = word.find("_")
    if blank_index == -1:
        return [word]
    else:
        words = []
        for a in string.ascii_uppercase:
            new_word = word [:blank_index] + a + word[blank_index + 1:]
            words.extend(enum_possibilities(new_word))
        return words

def get_super_words(words, wordlist):
    result = []
    for word in words:
        result.extend([super_word for super_word in wordlist if word in super_word])
    return result





