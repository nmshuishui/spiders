#! coding: utf8
import hashlib
import re


def get_md5(url):
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

def extract_num(text):
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums

# if __name__ == '__main__':
    # print get_md5('http://jobbole.com')