import sys
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pprint import pprint

import parse_regex as pat


class LedgerInvalidLineError(Exception):
    pass


class Group(Enum):
    BLANK = 1
    LINE_COMMENT = 2
    COMMENT = 3
    INCLUDE = 4
    TRANSACTION = 5
    POSTING = 6


@dataclass
class Context:
    original: str
    file: str
    line: int


@dataclass
class Token:
    group: Group
    data: dict
    context: Context


def maybe(value, func, default=None):
    return func(value) if value else default


def tokenize(lines):
    state = "None"

    total_lines = 0
    read_lines = 0

    for file, line, original in lines:
        context = Context(original, file, line)
        total_lines += 1

        m_trans = pat.PAT_TRANSACTION_DATA.match(original)
        m_account = pat.PAT_ACCOUNT.match(original)
        m_account_only = pat.PAT_ACCOUNT_ONLY.match(original)
        m_comment = pat.PAT_COMMENT.match(original)
        m_blank = pat.PAT_BLANK.match(original)
        m_line_comment = pat.PAT_LINE_COMMENT.match(original)
        m_include = pat.PAT_INCLUDE.match(original)

        if m_blank:
            read_lines += 1
            yield Token(group=Group.BLANK, context=context, data=dict())
            continue

        if m_line_comment:
            tmp_comment_sign = m_line_comment.group("comment_sign")
            tmp_comment = m_line_comment.group("comment")
            read_lines += 1
            yield Token(
                group=Group.LINE_COMMENT,
                context=context,
                data=dict(comment_sign=tmp_comment_sign, comment=tmp_comment),
            )
            continue

        if m_comment:
            tmp_comment_sign = m_comment.group("comment_sign")
            tmp_comment = m_comment.group("comment")
            read_lines += 1
            yield Token(
                group=Group.COMMENT,
                context=context,
                data=dict(comment_sign=tmp_comment_sign, comment=tmp_comment),
            )
            continue

        if m_include:
            tmp_include = m_include.group(1)
            read_lines += 1
            yield Token(
                group=Group.INCLUDE, context=context, data=dict(include=tmp_include)
            )
            continue

        if m_trans:
            tmp_date = date(
                int(m_trans.group("year")),
                int(m_trans.group("month")),
                int(m_trans.group("day")),
            )

            if (
                m_trans.group("year_aux") != None
                and m_trans.group("month_aux") != None
                and m_trans.group("day_aux") != None
            ):
                tmp_date_aux = datetime(
                    int(m_trans.group("year_aux")),
                    int(m_trans.group("month_aux")),
                    int(m_trans.group("month_day")),
                )
            else:
                tmp_date_aux = tmp_date
            tmp_state = m_trans.group("state") if m_trans.group("state") else ""
            tmp_code = m_trans.group("code") if m_trans.group("code") else ""
            tmp_payee = m_trans.group("payee")
            tmp_comment = m_trans.group("comment") if m_trans.group("comment") else ""

            read_lines += 1
            yield Token(
                group=Group.TRANSACTION,
                context=context,
                data=dict(
                    date=tmp_date,
                    date_aux=tmp_date_aux,
                    state=tmp_state,
                    code=tmp_code,
                    payee=tmp_payee,
                    comment=tmp_comment,
                ),
            )
            continue

        if m_account:
            tmp_account = m_account.group("account")
            tmp_account_list = tmp_account.split(":")
            tmp_commodity_front = m_account.group("commodity_front")
            tmp_amount = m_account.group("amount")
            tmp_amount = Decimal(tmp_amount.replace(",", "")) if tmp_amount else None
            tmp_commodity_back = m_account.group("commodity_back")
            tmp_comment = m_account.group("comment")
            if tmp_commodity_front:
                tmp_commodity = tmp_commodity_front
            elif tmp_commodity_back:
                tmp_commodity = tmp_commodity_back
            else:
                tmp_commodity = "JPY"

            read_lines += 1
            yield Token(
                group=Group.POSTING,
                context=context,
                data=dict(
                    account=tmp_account,
                    account_list=tmp_account_list,
                    amount=tmp_amount,
                    commodity=tmp_commodity,
                    commodity_front=tmp_commodity_front,
                    commodity_back=tmp_commodity_back,
                    comment=tmp_comment,
                ),
            )
            continue

        raise LedgerInvalidLineError
