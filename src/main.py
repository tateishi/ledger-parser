import parser
import sys


def main():
    if len(sys.argv) > 1:
        try:
            for file in sys.argv[1:]:
                print(file)
                with open(file) as stream:
                    lines = ((file, i + 1, line) for i, line in enumerate(stream))
                    parser.parse_ledger(lines)
        except FileNotFoundError as e:
            print(e)
    else:
        lines = (("stdin", i + 1, line) for i, line in enumerate(sys.stdin))
        parser.parse_ledger(lines)


if __name__ == "__main__":
    main()
