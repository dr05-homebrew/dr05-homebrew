import os

# http://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-a-python-script
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

data = [l.strip().split("|") for l in open(os.path.join(__location__, "mmr.txt")).readlines()]

for e in data:
	MakeName(int(e[0], 16), e[1])
