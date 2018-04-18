"""
Script to check proper nesting and matching of html tags.
Right now, this only cheecks tags that stand alone on a line.
More checks will be added later.
"""

import sys
import urllib.request as req
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
import re
import argparse

try:
    from typing import List, Set
except ImportError:
    print("WARNING: Cannot find any module named 'Typing'! Kindly install the latest version of python!")

ARG_ERROR = 1 # type: int
PARSE_ERROR = 2 # type: int
MAX_LINE = 80 # type: int

# for some reason, the following header seems to work best:
#  meaning fewer false URL erros
HEADER_TXT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/50.0.2661.102 Safari/537.36' # type :str

tag_stack = [] # type: List[str]
line_no = 0 # type: int
saw_error = False # type: bool
url_error = False # type: bool

void_tags = {"area", "base", "br", "col", "hr", "img", "input", "link",
             "meta", "param"} # type :Set[str]


def line_msg():# type: () -> str
    return " at line number " + str(line_no)

class OurHTMLParser(HTMLParser):
    def __init__(self):# type: () -> None
        self.is_in_script_tag = False
        self.links = [] # type: List[str]
        super(OurHTMLParser, self).__init__(convert_charrefs=False)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attr = dict(attrs)
            if 'href' in attr:
                self.links.append(attr['href'])
        if tag == "img":
            attr = dict(attrs)
            if 'src' in attr:
                self.links.append(attr['src'])

    def is_accessible(self, link):# type: (str) -> bool
        '''
        Here we check if the web page is accessible.
        '''
        mock_header = {'User-Agent': HEADER_TXT}
        for i in range(3):
            try:
                request = req.Request(link, headers = mock_header)
                response = req.urlopen(request)
                return True
            except:
                pass
        return False

    def check_urls_accessibility(self, links, relative_link_header):# type: (List[str], str) -> None
        print("Checking accessibility of urls...")
        for link in parser.links:
            '''
            If it is a relative link, we will add a header 
            link to verify its accessbility again
            '''
            if not self.is_accessible(link):  
                if link.startswith('http') or link.startswith('https'):
                    self.print_warning_msg(link, line_msg())
                else:
                    link = urljoin(relative_link_header, link)
                    if not self.is_accessible(link):
                        self.print_warning_msg(link, line_msg())
    
    def print_warning_msg(self, link, line):
        if url_error:
            print("ERROR: url not accessible") + line
            saw_error = True # type:bool
        else:
            print("WARNING: url not accessible" + line
                    + "; " + link)

if __name__ == '__main__':
    # if you want invalid url to throw errors invoke program with -e flag
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("html_filename")
    arg_parser.add_argument("-e", action = "store_true")
    arg_parser.add_argument('relative_link_header')
    args = arg_parser.parse_args()
    url_error = args.e
    relative_link_header = args.relative_link_header

    parser = OurHTMLParser()
    file_nm = args.html_filename

    file = open(file_nm, "r")
    for line in file:
        line_no += 1
        parser.feed(line)

    parser.check_urls_accessibility(parser.links, relative_link_header)

    if saw_error:
        exit(PARSE_ERROR)
    else:
        exit(0)
