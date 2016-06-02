from os.path import dirname, realpath, join


def get_version() -> str:
    directory = dirname(realpath(__file__))
    version_file = join(directory, 'version.txt')
    with open(version_file, 'r') as infile:
        return ''.join(infile.read().split())
