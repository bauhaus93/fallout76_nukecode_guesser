import os
import logging

import tkinter

import code_generator
import util

CODES_STR = "C6 D8 E3 G9 L3 M8 R3 T3"
CODEWORD_FRAGMENT = "P_RIG_TA_L"
DICTIONARY_DIRECTORY = os.path.join(".", "dicts")

if __name__ == "__main__":
    util.setup_logger()
    logger = logging.getLogger()

    codes = util.parse_codecards(CODES_STR)
    logger.info("Codes used: {}".format(CODES_STR))
    results = code_generator.create_codes_by_fragment(codes, CODEWORD_FRAGMENT, DICTIONARY_DIRECTORY)
    if len(results) == 0:
        logger.info("No valid codes found!")
    else:
        code_generator.print_results(results)
    input("Press RETURN to exit")