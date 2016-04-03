#!/usr/bin/env python3
import subprocess
import re
from os import pardir
from os.path import dirname, realpath, join


def get_git_authors():
    command = ['git', '--no-pager', 'shortlog', '-nse', 'HEAD']
    authors = subprocess.check_output(command)
    return authors.decode('utf-8').split('\n')


def parse_git_author(line):
    format_regex = r'^\s*(?P<commit_count>\d+)\s*(?P<name>.*\w)\s*<(' \
                   r'?P<email>[^\s]+)>$'
    result = re.search(format_regex, line)
    if result:
        return {
            'commits': result.group('commit_count'),
            'name': result.group('name'),
            'email': result.group('email')
        }
    else:
        raise ValueError('Could not extract authors from line %s' % line)


def to_markdown(author):
    return '* [%s](mailto:%s)' % (author['name'], author['email'])


def get_authors_file():
    directory = dirname(realpath(__file__))
    directory = join(directory, pardir)
    return join(directory, 'AUTHORS.rst')


def main():
    authors = get_git_authors()
    authors = filter(lambda name: name.strip() != '', authors)
    authors = map(parse_git_author, authors)
    authors = map(to_markdown, authors)
    authors = ['# Authors', ''] + list(authors)
    markdown = '\n'.join(authors)
    with open(get_authors_file(), 'w') as f:
        f.write(markdown)


if __name__ == '__main__':
    main()
