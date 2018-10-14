"""
CLI Tool to check word spelling in an file.

Uses multiple sources of truth for spelling, checked in the following order:
  1. ./data/Dictionary.json, unioned with ./data/English.txt
  2. the oxford dictionary api

If a user decides that a word, not found in either source, ought not to count as a misspelling,
  they have the opportunity to add said word to the dictionary located in ./data/English.txt.

The tool was written to anticipate the following situations, and produce appropriate outcomes:
  * Hyphenated compound words, of the grammar "{word}-{hyphenated-compound-word}"
    --> Detection: hyphens exist in the string
    --> Solution: string split on hyphens, each segment is spellchecked separately
  * Possessives, of the grammar "{word}'s" 
    --> Detection: last two characters of string are "'s"
    --> Solution: string split on hyphen, word prior is checked.
  * Single-character words
    --> Detection: length is one.
    --> Solution: everything passes.
"""

import json
import os
import subprocess
import requests
from html.parser import HTMLParser
import string
import re
import argparse

try:
    from typing import List, Set
except ImportError:
    print(
        "WARNING: Typing module is not found! Kindly install the latest "
        "version of python!")

ARG_ERROR = 1  # type: int
SPELL_ERROR = 2  # type: int

# Application keys for Oxford dictionary API
app_id = '4dcc2c67'
# Should we be storing API keys in a public repo?
# We might want to investigate https://www.vaultproject.io/
app_key = 'c7d48867f7506e51e70507d85bc9cbe6'
language = 'en'


class FileChangedException(Exception):
    pass


def is_word(s, search=re.compile(r'[^a-zA-Z-\']').search):
    return not bool(search(s))


def check_files_exist(*files):
    for file_name in files:
        if not os.path.isfile(file_name):
            print(file_name + " is not a file")
            exit(ARG_ERROR)


def spellCheckFile(spell_checker, file_name):
    """
    Description:
        Parses the file with name file, using the passed-in spell_checker.
    Returns:
        None if the file was spell-checked without any hiccups
    Raises:
        If an irrecoverable error was encountered
    """
    code_tag_on = False  # type:bool
    line_num = 0
    try:
        spell_checker.reset()
        with open(file_name, "r", ) as f:
            for line in f:
                if "<code>" in line:
                    code_tag_on = True
                if "</code>" in line:
                    code_tag_on = False
                    continue

                if not code_tag_on:
                    spell_checker.feed(line)
                line_num += 1
    except FileChangedException:
        return spellCheckFile(spell_checker, file_name)


class HTMLSpellChecker(HTMLParser):
    def __init__(self):  # type: () -> None
        self.is_in_script_tag = False
        super(HTMLSpellChecker, self).__init__(convert_charrefs=False)

    def handle_bad_word(self, word):
        """
        Description:
            A REPL loop allowing the user to handle their misspelt word.
        Returns:
            Nothing normally
        Raises:
            FileChangedException if the edit option was chosen
        """
        validResponse = False  # type: bool
        while not validResponse:
            response = input(
                "How would you like to handle the bad word {}?\n".format(word) +
                "1. Add as valid word to dictionary (1/a/add)\n" +
                "2. Skip error, because words is a unique string (2/s/skip)\n" +
                "3. Edit file, to fix the word (3/e/edit)\n" +
                "4. Close the spell-checker for this file (4/c/close)\n" +
                ">>")
            if response.lower() == 'add' or response.lower() == 'a' or response == '1':
                added_words.add(word)
                word_set.add(word)
                return None
            elif response.lower() == 'skip' or response.lower() == 's' or response == '2':
                return None
            elif response.lower() == 'edit' or response.lower() == 'e' or response == '3':
                # This opens up vim, at the first instance of the troublesome word, with all instances highlighted.
                subprocess.call(
                    ['vimdiff', '+{}'.format(line_num), '-c', '/ {}'.format(word), file_name])
                raise FileChangedException
            elif response.lower() == 'close' or response.lower() == 'c' or response == '4':
                exit(0)
            else:
                print("Invalid response, Please try again!")

    def isWordInOxfordDictionary(self, lower_word):
        url = ('https://od-api.oxforddictionaries.com/api/v1/inflections/'
               + language + '/' + lower_word)
        r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
        return r.status_code == 200

    def isPossessive(self, word):
        return '\'s' == word[len(word)-2:]

    def checkWord(self, word):
        if word is "":
            return
        if len(word) == 1:
            return
        if self.isPossessive(word):
            return self.checkWord(word[:len(word)-2])
        if not is_word(word):
            return
        if not strict_mode and word[0].isupper():
            return

        lower_word = word.lower()  # type: (str)

        if lower_word not in word_set and not self.isWordInOxfordDictionary(lower_word):
            self.handle_bad_word(lower_word)  # raises if edit is chosen

    def handle_data(self, data):  # type: (str) -> None
        """
        Description:
            This is the core function of the parser, called on a line-by-line basis in parser.feed().
            We check if any of the words in the line are not in the oxford dictionary, or our local dictionary.
        Exceptions:
            Raises a FileChangedException if the file is edited in handle_bad_word, 
              so that the main execution thread can restart the file parsing process.
        """
        web_page_words = data.split()  # type: List[str]

        if web_page_words and web_page_words[0] == "{%" and web_page_words[len(web_page_words)-1] == "%}":
            return

        for web_page_word in web_page_words:
            # strip other punctuations
            word = web_page_word.strip(string.punctuation).strip()
            if "-" in web_page_word:
                for word in web_page_word.split("-"):
                    self.checkWord(word)
            else:
                self.checkWord(word)


exit_error = False  # type: bool
strict_mode = False  # type: bool
file_name = None
main_dict = None
custom_dict = None

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file_name", help="html file to be parsed")
    arg_parser.add_argument("main_dict", help="main dictionary file")
    arg_parser.add_argument("custom_dict", help="custom dictionary file")
    arg_parser.add_argument(
        "-e", help="enable exit error", action="store_true")
    arg_parser.add_argument("-s", help="strict mode checks capitalized words",
                            action="store_true")
    args = arg_parser.parse_args()
    exit_error = args.e
    strict_mode = args.s
    file_name = args.file_name
    main_dict = args.main_dict
    custom_dict = args.custom_dict

added_words = set()  # type: Set[str]

# Make sure all the files exist, before doing anything heavy
check_files_exist(file_name, main_dict, custom_dict)

# Load words from Dictionary files
word_set = set()  # type: Set[str]
with open(main_dict, 'r') as f:
    word_set = set(json.load(f).keys())
with open(custom_dict, 'r') as f:
    for line in f:
        word_set.add(line.split()[0].lower())

# Execute the spellchecker
parser = HTMLSpellChecker()
line_num = 0
spellCheckFile(parser, file_name)

with open(custom_dict, 'a+') as f:
    f.writelines(i + '\n' for i in added_words)
    added_words.clear()

if exit_error:
    exit(SPELL_ERROR)
else:
    exit(0)
