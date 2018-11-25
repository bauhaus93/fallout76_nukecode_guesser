import string
import logging
import multiprocessing as mp
import queue
import time
import collections
import os

import util
import guess_word

Result = collections.namedtuple('Result', ['codeword', 'candidates'])
Candidate = collections.namedtuple('Candidate', ['word', 'code'])

logger = logging.getLogger()

def create_codes_by_fragment(codes, codeword_fragment, wordlist_directory):
    logger.info("Creating codes by codeword fragment {}".format(codeword_fragment))
    logger.debug("Loading wordlist...")
    wordlist = util.load_dictionary(wordlist_directory)
    wordlist_sorted = [''.join(sorted(s)) for s in wordlist]
    logger.info("Wordlist size: {} words".format(len(wordlist)))

    codewords = guess_word.guess_word_super(codeword_fragment, wordlist)
    if len(codewords) == 0:
        return []
    elif len(codewords) > 10:
        logger.info("Possible codewords count: {}".format(len(codewords)))
    else:
        logger.info("Possible codewords: {}".format(", ".join(codewords)))

    logger.info("Creating codes based on codewords...")
    process_count = min(len(codewords), os.cpu_count())
    input_queue = mp.Queue()
    output_queue = mp.Queue()
    worker_args = (codes, wordlist, wordlist_sorted, input_queue, output_queue)
    logger.info("Using {} worker processes".format(process_count))
    processes = [mp.Process(target=worker, args = worker_args) for _ in range(process_count)]

    [input_queue.put(cw) for cw in codewords]
    [p.start() for p in processes]
    total_results = []
    
    start_time = time.time()
    last_print = start_time
    start_words = len(codewords)
    while input_queue.qsize() > 0 or output_queue.qsize() > 0:
        try:
            result = output_queue.get(timeout = 3)
            total_results.append(result)
        except queue.Empty:
            pass

        if time.time() - last_print > 3:
            last_print = time.time()
            words_left = input_queue.qsize()
            done_count = start_words - words_left
            uptime = max(1.0, time.time() - start_time)
            words_per_second = max(1.0, done_count / uptime)
            eta = round(words_left / words_per_second)
            if eta >= 60:
                time_left = "{:02}m {:02}s".format(round(eta / 60), eta % 60)
            else:
                time_left = "{:02}s".format(eta)
            logger.info("Codewords left: {:6} | Rate: {:4} Words/s | ETA: {:}".format(words_left, round(words_per_second), time_left))
    logger.info("Waiting for subprocesses to stop...")
    [p.join() for p in processes]
    logger.debug("All subprocesses stopped")
    return total_results

#Created using https://www.reddit.com/r/fo76/comments/9ygyy9/stepbystep_guide_to_decrypting_launch_codes/
def create_code(codes, codeword_original, wordlist, wordlist_sorted):
    alphabet_code = create_alphabet(codeword_original)
    alphabet = string.ascii_uppercase

    codeword = ""
    for (c, _n) in codes:
        pos = alphabet_code.find(c)
        if pos < 0 or pos >= 26:
            print("'" + codeword_original + "'")
            return []
        codeword += alphabet[pos]
    
    codeword_sorted = "".join(sorted(codeword))
    candidate_indices = [i for (i, word) in enumerate(wordlist_sorted) if word == codeword_sorted]

    results = []
    for index in candidate_indices:
        word = wordlist[index]
        word_conv = ""
        for c in word:
            word_conv += alphabet_code[alphabet.find(c)]

        final_code = ""
        for _w, wc in zip(word, word_conv):
            code = [c for (wf, c) in codes if wf == wc]
            final_code += str(code[0])
        results.append(Candidate(word = word, code = final_code))
    return Result(codeword = codeword_original, candidates = results)

def create_alphabet(codeword):
    rest = string.ascii_uppercase
    for c in codeword:
        rest = rest.replace(c, '')
    return codeword + rest

def worker(codes, wordlist, wordlist_sorted, input_queue, output_queue):
    while not input_queue.empty():
        codeword = input_queue.get()
        result = create_code(codes, codeword, wordlist, wordlist_sorted)
        if len(result) > 0:
            output_queue.put(result)

def create_summary_string(results):
    total_codes = 0
    empty_codewords = 0

    for result in results:
        total_codes += len(result.candidates)
        if len(result.candidates) == 0:
            empty_codewords = 0
    res_str = ""
    res_str += "Codes found: {}\n".format(total_codes)
    res_str += "Empty codewords: {}".format(empty_codewords)
    if total_codes > 0:
        res_str += "\n{:15} | {:8} | {:8}\n".format("Codeword", "Word", "Code")
        res_str += "-" * 37
        for result in results:
            for candidate in result.candidates:
                res_str += "\n{:15} | {:8} | {:8}".format(result.codeword, candidate.word, candidate.code)
    return res_str

def print_results(results):
    for line in create_summary_string(results).split("\n"):
        if len(line) > 0:
            logger.info(line)

def write_results(results, filepath):
    with open(filepath, "w") as f:
        f.write(create_summary_string(results))



    


