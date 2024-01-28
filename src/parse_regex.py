import re
from pathlib import Path

PAT_TRANSACTION = re.compile(r"(\d{4,}.+(?:\n[^\S\n\r]{1,}.+)+)")
PAT_TRANSACTION_DATA = re.compile(
    r"(?P<year>\d{4})[/|-](?P<month>\d{1,2})[/|-](?P<day>\d{1,2})((?:=(?P<year_aux>\d{4})[/|-](?P<month_aux>\d{2})[/|-](?P<day_aux>\d{2}))? (?P<state>[\*|!])?[ ]?(\((?P<code>[^\)].+)\) )?(?P<payee>[^;\n\r]+)(;+(?P<comment>.+))?)?"
)
PAT_COMMENT = re.compile(r"\s+(?P<comment_sign>[;#%\|\*]+)(?P<comment>.*)")
# PAT_COMMENT = re.compile(r"[^\S\n\r]{1,};(.+)")
PAT_ACCOUNT = re.compile(
    r"(\s+)(?P<account>\S+(\s\S+)*)(\s+)?(?P<commodity_front>[a-z]\w+)?(\s+)?(?P<amount>[-+]?[\d|,|\.]+)?(\s+)?(?P<commodity_back>[a-z]\w+)?(\s+)?(;\s*(?P<comment>.*))?",
    re.I
    #    r"\s+(?P<account>\S+(\s\S+)*)\s+?(?:(?P<commodity_front>[a-zA-Z]\w+))?\s+?(?P<amount>[-+]?\d+[,|\.]?\d+?)?(?:[^\S\n\r]+?(?P<commodity_back>[^\d\;]+))?(?:[^\S\n\r]+)(;(?P<comment>.*))?", re.DEBUG
)
PAT_ACCOUNT_ONLY = re.compile(r"[^\S\n\r]{1,}(?P<account>[^;].+)")
PAT_BLANK = re.compile(r"^\s*$")
PAT_LINE_COMMENT = re.compile(r"(?P<comment_sign>[;#%\|\*]+)(?P<comment>.*)")
# PAT_LINE_COMMENT = re.compile(r"^[#*;](.*)$")
PAT_INCLUDE = re.compile(r"^include\s+(.*)\s*$")


# PAT_TRANSACTION_DATA = re.compile(
#     r"(?P<year>\d{4})[/|-](?P<month>\d{1,2})[/|-](?P<day>\d{1,2})(?:=(?P<year_aux>\d{4})[/|-](?P<month_aux>\d{2})[/|-](?P<day_aux>\d{2}))? (?P<state>[\*|!])?[ ]?(\((?P<code>[^\)].+)\) )?(?P<payee>[^;\n\r]+)(;+(?P<comment>.+))?"
# )
# PAT_TRANSACTION_DATA = re.compile(
#     r"(?P<year>\d{4})[/|-](?P<month>\d{2})[/|-](?P<day>\d{2})(?:=(?P<year_aux>\d{4})[/|-](?P<month_aux>\d{2})[/|-](?P<day_aux>\d{2}))? (?P<state>[\*|!])?[ ]?(\((?P<code>[^\)].+)\) )?(?P<payee>.+)"
# )
# PAT_ACCOUNT = re.compile(
#     r"[^\S\n\r]{1,}(?P<account>[^;].+)(?:[^\S\n\r]{2,})(:?(?P<commodity_front>[^\d].+)?[^\S\n\r]{1,})?(?P<amount>[-+]?\d+[,|\.]?(?:\d+)?)?(?:[^\S\n\r]{1,}(?P<commodity_back>[^\d].+))?"
# )

# PAT_ACCOUNT = re.compile(
#     r"\s+(?P<account>\S+(\s\S+)*)\s+?(?:(?P<commodity_front>[a-zA-Z]\w+))?\s+?(?P<amount>[-+]?\d+[,|\.]?\d+?)?(?:[^\S\n\r]+?(?P<commodity_back>[^\d\;]+))?(?:[^\S\n\r]+)(;(?P<comment>.*))?", re.DEBUG
# )

if __name__ == "__main__":

    def test_re(original):
        m_account = PAT_ACCOUNT.match(original)
        if m_account:
            t_account = m_account.group("account")
            t_amount = m_account.group("amount")
            t_commodity_front = m_account.group("commodity_front")
            t_commodity_back = m_account.group("commodity_back")
            t_comment = m_account.group("comment")
            #            print(f'"{original}" => "{t_account}", "{t_commodity_front}", "{t_amount}", "{t_commodity_back}", "{t_comment}"')
            #            print(m_account)
            print(
                f'"{original}" => "{t_account}", "{t_commodity_front}", "{t_amount}", "{t_commodity_back}", "{t_comment}"'
            )
        else:
            print("not match")

    test_re("    a:b:c  100.01")
    test_re("    a:b :c  100")
    test_re("    a:b :c  100,10 USD")
    test_re("    a:b :c  NZD 100.99  ;  入金")
    test_re("    資産:現金:財布 特別   100")
    test_re("    資産:現金:財布 特別   100  ; 入金")
    test_re("    資産:現金:財布 特別   100 JPY ; 入金")
