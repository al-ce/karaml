# Regex that parses chars in parens from those that are not
# 'parse_chars_in_parens'. For separating modiifers that are mandatory
# e.g. not in parens, from those that are optional, e.g. in parens
# <s(m)o> : s and o are mandatory, o is optional

import re

slist = [
    "(S)c",
    "m(os)c",
    "mc",
    "o(Mc)",
    "(so)c",
    "m(c)",
]


def parse(string):
    # use regex to extract text within parentheses
    in_parens = re.findall(r"\((.*?)\)", string)

# use regex to extract text not within parentheses
    not_in_parens = re.findall(r"[\w+]+(?![^()]*\))", string)
    # not_in_parens = re.findall(r"[^()]+(?![^()]*\))", s)

    print(string)
    print("Text within parentheses: ", in_parens)
    print("Text not within parentheses: ", not_in_parens)


for s in slist:
    parse(s)
