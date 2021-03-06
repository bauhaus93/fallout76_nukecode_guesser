import os
import string
import logging

logger = logging.getLogger()

def setup_logger():
    FORMAT = r"[%(asctime)-15s] %(levelname)s - %(message)s"
    DATE_FORMAT = r"%Y-%m-%d %H:%M:%S"
    logging.basicConfig(level = logging.INFO, format = FORMAT, datefmt = DATE_FORMAT)

def load_dictionary(directory):
    wordlist = set()
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, "r", encoding="ISO 8859-1") as file:
                words = [line.strip().upper() for line in file.read().split()]
                words = set([word for word in words if all(char in string.ascii_uppercase for char in word)])
                wordlist = wordlist.union(words)
    return sorted(list(wordlist))

def create_dictionary(name, wordlist):
    with open(name, "w") as f:
        for w in sorted(wordlist):
            f.write(w + "\n")

def parse_codecards(code_str):
    codes_parsed = []
    for code in code_str.split(" "):
        if len(code) != 2:
            logger.error("Codecard has incorrect length, must be 2, but got {}".format(len(code)))
            return None
        char = code[0].upper()
        try:
            num = int(code[1])
        except ValueError:
            logger.info("Could not parse '{}' to integer, second part of codecard must be a number".format(code[1]))
            return None
        codes_parsed.append((char, num))
    if len(codes_parsed) != 8:
        logger.error("Need 8 codecards, but got {}".format(len(codes_parsed)))
        return None
    return codes_parsed

def parse_codeword_fragment(codeword_fragment):
    valid_chars = string.ascii_uppercase + "_"
    frag_parsed = ""
    for char in codeword_fragment.upper():
        if not char in valid_chars:
            logger.error("Char '{}' is not a valid codeword character, must be A-Z, a-z or _".format(char))
            return None
        else:
            frag_parsed += char
    return frag_parsed
