import random
import sys
import getopt
import uuid
import logging

"""
Generate test data for the approach one of the POC of custom field.
The script will generate test data for ACS-111	POC: Add Custom Field of type "Multi-select picklist"

-- Table structure for table `poc_multi_picklist`
--

create table poc_multi_picklist_two (id bigint(20) primary key not null auto_increment, tenant_id varchar(32), oid varchar(32), cf_data varchar(32) );

"""
sql_prefix = "insert poc_multi_picklist_two (tenant_id, oid,  cf_data) values "

sql_template = " ('{tenant_id}', '{oid}', '{cf_data}') "

POISON = "POISON-" + uuid.uuid4().hex

logging.basicConfig(filename=sys.argv[0].replace("py", 'log'), level=logging.DEBUG)
logger_main = logging.getLogger('Main')


def generate_sqls_for_one_object(option_set, tenant_id):
    option_value_arr = random.sample(option_set, random.randint(1, 10))
    option_value_arr.sort()
    oid = uuid.uuid4().hex
    return [sql_template.format(tenant_id=tenant_id, oid=oid, cf_data=option_value) for option_value in option_value_arr]


def dry_run(queue):
    logger_dry = logging.getLogger('DRY RUN')
    while True:
        sql_segment = queue.get()
        if sql_segment == POISON:
            break
        sql = sql_prefix + sql_segment
        logger_dry.debug(sql)


def do_insertion(queue):
    import MySQLdb
    import config
    # Open database connection
    db = MySQLdb.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER, passwd=config.DB_PASS, db=config.DB_DATABASE)

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    logger_db = logging.getLogger('DB')
    while True:
        # Prepare SQL query to INSERT a record into the database.
        sql_segment = queue.get()
        if sql_segment == POISON:
            break
        try:
            # Execute the SQL command
            sql = sql_prefix + sql_segment
            logger_db.debug(sql)
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
        except Exception as e:
            logger_db.error(e)
            # Rollback in case there is any error
            db.rollback()

    # disconnect from server
    db.close()

input_file = "option.set"
tenant = 2034
number = 1000


def usage():
    print """

Usage: python {file_name} [OPTIONS] \n
Default: python {file_name} -i {input_file} -t {tenant} -n {number}
Options
    -i input -n number -t tenant
    -i, --input=option.set      File name of option set
    -t, --tenant=2034           Tenant id of test data
    -n, --number=0              The size of test data

    """.format(file_name=sys.argv[0], input_file=input_file, tenant=tenant, number=number)


def main(argv):
    global input_file
    global tenant
    global number
    dryrun = False
    try:
        opts, args = getopt.getopt(argv, "hn:i:t:d", ["help", "number=", "input=", "tenant=", "dryrun"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if len(opts) == 0:
        logger_main.info("Will use default parameter: python {file_name} -i {input_file} -t {tenant} -n {number}".format(
            file_name=sys.argv[0], input_file=input_file, tenant=tenant, number=number))
    for opt, arg in opts:
        if opt in ("-n", "--number"):
            number = int(arg)
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-t", "--tenant"):
            tenant = arg
        elif opt in ("-d", "--dryrun"):
            dryrun = True
        elif opt in ("-h", "--help"):
            usage()
            exit()
        else:
            usage()
            exit(1)

    f = open(input_file)

    lines = f.readlines()
    option_set = ';'.join(lines).replace('\n', '').split(';')

    from threading import Thread
    from Queue import Queue

    #initialize a queue
    sql_queue = Queue()

    #initialize a thread to process DB insertion
    if dryrun == True:
        dryrun_thread = Thread(target=dry_run, args=(sql_queue,))
        dryrun_thread.start()
    else:
        db_thread = Thread(target=do_insertion, args=(sql_queue,))
        db_thread.start()

    i = 0
    sql_segment_buffer = ''
    while i < number:
        i += 1
        sqls = generate_sqls_for_one_object(option_set, tenant)
        one_row = ",".join(sqls)
        if i % 1000 == 0:
            sql_segment_buffer += one_row + ';'
            sql_queue.put_nowait(sql_segment_buffer)
            sql_segment_buffer = ''
            logger_main.info("Generate the {index}th insert SQL".format(index=i))
        else:
            sql_segment_buffer += one_row + ','

    logger_main.info("Finish SQL generation")
    sql_queue.put_nowait(POISON)
    if dryrun == True:
        dryrun_thread.join()
    else:
        db_thread.join()

if __name__ == "__main__":
    main(sys.argv[1:])
