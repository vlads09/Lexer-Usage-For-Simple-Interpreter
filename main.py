
from sys import argv
from .Parser import print_result

def main():
	if len(argv) != 2:
		return

	filename = argv[1]
	print_result(filename)

if __name__ == '__main__':
	main()
