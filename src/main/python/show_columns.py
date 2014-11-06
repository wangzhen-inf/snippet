__author__ = 'zhenwang'

import MySQLdb
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger_main = logging.getLogger('Main')

if len(sys.argv) <= 0:
    sys.exit( "Need an argument: pattern")

column_pattern = sys.argv[1]
db = MySQLdb.connect(host="192.168.59.103", user="zuora", passwd="wz123")
cur = db.cursor()
cur4table = db.cursor()

databases = ("main", "main_global")


def hasColumn(table):
    cur4table.execute("desc " + table + ";")
    fields = map(lambda x: x[0], cur4table.fetchall())
    auditInfo = filter( predicate, fields)
    return (table, len(auditInfo), auditInfo)

def predicate(column):
    return column.find(column_pattern) >= 0

def ignore_cf(table):
    return table.endswith("_cf")

def ignore_known(table):
    return table in ["zg_fx_cursor", "zg_fx_currency_rate", "zg_fx_failed_job"]

def ignore(table):
    # rules = [ignore_cf, ignore_known]
    rules = []
    def applyRule(r):
        return r(table)
    return any(map(applyRule, rules))

def checkDB(database):
    cur.execute("use " + database)
    cur.execute("show tables")
    tables = map(lambda x: x[0], cur.fetchall())
    auditStatistic = filter( notContain , map(hasColumn, filter(lambda t: not ignore(t), tables)))
    map(output, auditStatistic)
    return auditStatistic

def notContain(stat):
    if stat[1] == 0:
        return False
    return True
def output(info):
    print ",".join(map(str, info)) + '\r\n'

map(checkDB, databases)
