from pathlib import Path
from pprint import pprint

import ledgertoken as lt


def shorten(s, size, placeholder="..."):
    if len(s) <= size:
        return s
    return s[:size-len(placeholder)] + placeholder

def print_ledger(stream):
    for token in lt.tokenize(stream):
        if token.group == lt.Group.LINE_COMMENT:
            print(f"{token.data['comment_sign']}{token.data['comment']}")
            continue
        if token.group == lt.Group.BLANK:
            print()
            continue
        if token.group == lt.Group.TRANSACTION:
            print(f"{token.data['date'].strftime('%Y/%m/%d')} {token.data['state']} {token.data['payee']} {'; '+token.data['comment'] if token.data['comment'] else ''}")
            continue
        if token.group == lt.Group.POSTING:
            print(f"    {token.data['account']}  {token.data['commodity_front'] if token.data['commodity_front'] else ''} {token.data['amount'] if token.data['amount'] else ''} {token.data['commodity_back'] if token.data['commodity_back'] else ''} {'; '+token.data['comment'] if token.data['comment'] else ''}")
            continue
        if token.group == lt.Group.COMMENT:
            print(f"    {token.data['comment_sign']}{token.data['comment']}")
            continue
        print(token)

if __name__ == "__main__":
    import sys

    def main():
        if len(sys.argv) > 1:
            try:
                for file in sys.argv[1:]:
                    print(file)
                    with open(file) as stream:
                        lines = ((file, i + 1, line) for i, line in enumerate(stream))
                        print_ledger(lines)
            except FileNotFoundError as e:
                print(e)
        else:
            lines = (("stdin", i + 1, line) for i, line in enumerate(sys.stdin))
            print_ledger(lines)

    main()
