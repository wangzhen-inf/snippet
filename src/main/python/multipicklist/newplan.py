import random
import sys
import getopt
import uuid

sql_prefix = "insert poc_multi_picklist (tenant_id, oid, cf_data) values "

sql_template = " ('{tenant_id}', '{oid}', '{cf_data}') "


def generate_one_row(option_set, tenant_id):
    option_value_arr = random.sample(option_set, random.randint(1, 10))
    option_value = ";".join(option_value_arr)
    oid = uuid.uuid4().hex
    return sql_template.format(tenant_id=tenant_id, oid=oid, cf_data=option_value)


def do_insertion(queue):
    import MySQLdb

    # Open database connection
    db = MySQLdb.connect(host="localhost", port=63306, user="zuora", passwd="123456", db="test")

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    while True:
        # Prepare SQL query to INSERT a record into the database.
        sql_segment = queue.get()
        if sql_segment == 'Poison':
            break
        try:
            # Execute the SQL command
            sql = sql_prefix + sql_segment + ";"
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
        except:
            # Rollback in case there is any error
            db.rollback()

    # disconnect from server
    db.close()


def usage():
    print """

Usage: python {file_name} [OPTIONS] \n

Options
    -o output -i input -n number -t tenant
    -o, --output=               Output file name, Required.
    -i, --input=option.set      File name of option set
    -t, --tenant=2034           Tenant id of test data
    -n, --number=0              The size of test data

    """.format(file_name=sys.argv[0])


def main(argv):
    input_file = "option.set"
    tenant = 2034
    number = 1000
    try:
        opts, args = getopt.getopt(argv, "hn:o:i:t:", ["help", "number=", "output=", "input=", "tenant="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-o", "--output"):
            output = arg
        elif opt in ("-n", "--number"):
            number = arg
        elif opt in ("-o", "--input"):
            input_file = arg
        elif opt in ("-t", "--tenant"):
            tenant = arg
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
    db_thread = Thread(target=do_insertion, args=(sql_queue,))
    db_thread.start()

    i = 0
    sql_segment_buffer = ''
    while i < number:
        i += 1
        one_row = generate_one_row(option_set, tenant)
        sql_segment_buffer += one_row
        if i % 1000 == 0:
            sql_queue.put_nowait(sql_segment_buffer)
            sql_segment_buffer = ''


if __name__ == "__main__":
    main(sys.argv[1:])