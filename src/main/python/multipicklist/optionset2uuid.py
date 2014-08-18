import sys
import getopt
import uuid
import logging

logging.basicConfig(filename='option2uuid.log',level=logging.INFO)
logger_main = logging.getLogger('Main')

def usage():
    print """

Usage: python {file_name} [OPTIONS] \n

Options
    -o output -i input -o output
    -o, --output=               Output file name, Required.
    -i, --input=option.set      File name of option set

    """.format(file_name=__name__)


def main(argv):
    input_file = "option.set"
    output_file = "option.uuid.set"
    try:
        opts, args = getopt.getopt(argv, "ho:i:", ["help",  "output=", "input="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if len(opts) == 0:
        logger_main.info("Will use default parameter: python {file_name} -i {input_file} -o {output_file}".format(
            file_name=sys.argv[0], input_file=input_file, output_file=output_file))

    for opt, arg in opts:
        if opt in ("-o", "--output"):
            output_file = arg
        elif opt in ("-o", "--input"):
            input_file = arg
        elif opt in ("-h", "--help"):
            usage()
            exit()
        else:
            usage()
            exit(1)

    f = open(input_file)
    o = open(output_file, "w")

    for line in f:
        lineuuid = uuid.uuid3(uuid.NAMESPACE_DNS, line).hex
        o.write(lineuuid + "\n")
    o.flush()
    o.close()


if __name__ == "__main__":
    main(sys.argv[1:])