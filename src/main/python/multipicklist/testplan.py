import random
import sys
import getopt
import uuid


sql_template = "insert poc_multi_picklist (tenant_id, oid, cf_data) values ( '{tenant_id}', '{oid}', '{cf_data}');\n"

def generate_insert(option_set, tenant_id):
    option_value_arr = random.sample(option_set, random.randint(1, 10))
    option_value = ";".join(option_value_arr)
    oid = uuid.uuid4().hex
    return sql_template.format(tenant_id=tenant_id, oid=oid, cf_data=option_value)


def usage():
    print """

Usage: python {file_name} [OPTIONS] \n

Options
    -o output -i input -n number -t tenant
    -o, --output=               Output file name, Required.
    -i, --input=option.set      File name of option set
    -t, --tenant=2034           Tenant id of test data
    -n, --number=0              The size of test data

    """.format(file_name=__name__)


def main(argv):
    input_file = "option.set"
    tenant = 2034
    output = ""
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
    o = open(output, "w")

    lines = f.readlines()
    option_set = ';'.join(lines).replace('\n', '').split(';')
    i = 0
    while i < number:
        i += 1
        insertSQL = generate_insert(option_set, tenant)
        o.write(insertSQL)
        if i % 1000 == 0:
            o.flush()

    o.close()


if __name__ == "__main__":
    main(sys.argv[1:])