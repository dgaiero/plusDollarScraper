import argparse
from scraper import *
from config import *
parser = argparse.ArgumentParser(
    description="To run and configure the CP plus dollar scraper application.")
parser.add_argument('-c', action='store_true', default=False,
                    dest='config',
                    help='configure application')
parser.add_argument('-t', action='store_true', default=False,
                    dest='task',
                    help='create windows task')

parser.add_argument('--version', action='version', version='%(prog)s 1.0')
args = parser.parse_args()
print(args.config)
print(args.task)

# if args.config:
#
