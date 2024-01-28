from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from pprint import pprint

from transitions import Machine

import ledgertoken as lt


class LedgerAmountError(Exception):
    pass


@dataclass
class LedgerPosts:
    account: str
    file: str
    line: int
    original: str
    account_list: list[str] = field(default_factory=list)
    amount: Decimal = field(default_factory=Decimal)
    amount_in: Decimal = field(default_factory=Decimal)
    comments: list[str] = field(default_factory=list)

    def __repr__(self):
        filename = Path(self.file).name
        return f"<{self.account} {self.amount_in} {self.amount} {filename} {self.line} {self.comments}>"


@dataclass
class LedgerTransaction:
    date: date
    date_aux: date
    state: str | None
    code: str | None
    payee: str
    file: str
    line: int
    original: str
    comments: list[str] = field(default_factory=list)
    posts: list[LedgerPosts] = field(default_factory=list)

    def __repr__(self):
        filename = Path(self.file).name
        return f"<{self.date} {self.state} {self.payee} {filename} {self.line} {self.comments} {self.posts}>"


@dataclass
class LedgerParser:
    trans: list[LedgerTransaction] = field(default_factory=list)
    c_trans: LedgerTransaction | None = None
    c_post: LedgerPosts | None = None

    def _real_amount(self):
        nones = len(
            [post.amount_in for post in self.c_trans.posts if post.amount_in == None]
        )
        s = sum(post.amount_in if post.amount_in else 0 for post in self.c_trans.posts)
        if (nones > 1) or (nones == 0 and s != 0):
            pprint(self.c_trans)
            raise LedgerAmountError
        for post in self.c_trans.posts:
            if post.amount_in == None:
                post.amount = -s
            else:
                post.amount = post.amount_in

    def on_end_posts(self):
        if self.c_post:
            self.c_trans.posts.append(self.c_post)
            self.c_post = None

    def on_end_trans(self):
        if self.c_trans:
            self.on_end_posts()
            self._real_amount()
            self.trans.append(self.c_trans)
            self.c_trans = None

    def on_skip1(self, token: lt.Token):
        pass

    def on_trans(self, token: lt.Token):
        self.on_end_trans()
        self.c_trans = LedgerTransaction(
            date=token.data["date"],
            date_aux=token.data["date_aux"],
            state=token.data["state"],
            code=token.data["code"],
            payee=token.data["payee"],
            file=token.context.file,
            line=token.context.line,
            original=token.context.original,
        )
        if token.data["comment"]:
            self.c_trans.comments.append(token.data["comment"])

    def on_post(self, token: lt.Token):
        if self.c_post:
            self.c_trans.posts.append(self.c_post)
        self.c_post = LedgerPosts(
            account=token.data["account"],
            account_list=token.data["account_list"],
            amount_in=token.data["amount"],
            file=token.context.file,
            line=token.context.line,
            original=token.context.original,
        )
        if token.data["comment"]:
            self.c_post.comments.append(token.data["comment"])

    def on_comm1(self, token: lt.Token):
        if self.c_trans:
            self.c_trans.comments.append(token.data["comment"])

    def on_comm2(self, token: lt.Token):
        if self.c_post:
            self.c_post.comments.append(token.data["comment"])

    def on_end(self):
        self.on_end_trans()


def run(model: LedgerParser, machine: Machine, stream: Sequence) -> None:
    for token in lt.tokenize(stream):
        if token.group == lt.Group.TRANSACTION:
            model.OnTrans(token)

        if token.group == lt.Group.COMMENT:
            import re

            trigger = next(
                s
                for s in machine.get_triggers(model.state)
                if re.search(r"OnComm[1-9]", s)
            )
            model.trigger(trigger, token)

        if token.group == lt.Group.POSTING:
            model.OnPost(token)

    model.OnEnd()
    pprint(model)


def parse_ledger(stream):
    states = ["I", "T", "P", "END", "E"]

    transitions = [
        dict(trigger="OnTrans", source=["I", "T", "P"], dest="T", before="on_trans"),
        dict(trigger="OnPost", source=["T", "P"], dest="P", before="on_post"),
        dict(trigger="OnComm1", source="T", dest="T", before="on_comm1"),
        dict(trigger="OnComm2", source="P", dest="P", before="on_comm2"),
        dict(trigger="OnSkip1", source="I", dest="I", before="on_skip1"),
        dict(trigger="OnSkip2", source="T", dest="T", before="on_skip2"),
        dict(trigger="OnSkip3", source="P", dest="P", before="on_skip3"),
        dict(trigger="OnEnd", source="*", dest="END", before="on_end"),
    ]

    model = LedgerParser()
    machine = Machine(
        model=model, states=states, transitions=transitions, initial=states[0]
    )
    run(model, machine, stream)


if __name__ == "__main__":
    import sys

    def main():
        if len(sys.argv) > 1:
            try:
                for file in sys.argv[1:]:
                    print(file)
                    with open(file) as stream:
                        lines = ((file, i + 1, line) for i, line in enumerate(stream))
                        parse_ledger(lines)
            except FileNotFoundError as e:
                print(e)
        else:
            lines = (("stdin", i + 1, line) for i, line in enumerate(sys.stdin))
            parse_ledger(lines)

    main()
