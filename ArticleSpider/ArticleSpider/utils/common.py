#! coding: utf8
import hashlib

def get_md5(url):
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


# if __name__ == '__main__':
    # print get_md5('http://jobbole.com')