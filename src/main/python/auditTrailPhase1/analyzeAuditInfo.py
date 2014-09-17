__author__ = 'zhenwang'

import MySQLdb
import logging

logging.basicConfig(level=logging.INFO)
logger_main = logging.getLogger('Main')

db = MySQLdb.connect(host="localhost", user="zuora", passwd="wz123")
cur = db.cursor()
cur4table = db.cursor()

resultFile = open("audit.csv", "w")
databases = ("main", "main_global")

def hasAudit(table):
    cur4table.execute("desc " + table)
    fields = map(lambda x: x[0], cur4table.fetchall())
    auditInfo = filter(lambda x: x in ("created_on", "created_by", "updated_on", "updated_by"), fields)
    return (table, len(auditInfo), auditInfo)


def output(info):
    resultFile.write(str(info) + '\r\n')


def ignore_cf(table):
    return table.endswith("_cf")

def ignore_known(table):
    return table in ["zg_fx_cursor", "zg_fx_currency_rate", "zg_fx_failed_job"]

def ignore(table):
    rules = [ignore_cf, ignore_known]
    def applyRule(r):
        return r(table)
    return any(map(applyRule, rules))

def checkDB(database):
    cur.execute("use " + database)
    cur.execute("show tables")
    tables = map(lambda x: x[0], cur.fetchall())
    auditStatistic = map(hasAudit, filter(lambda t: not ignore(t), tables))
    map(output, auditStatistic)
    return auditStatistic


map(checkDB, databases)