import argparse
import sys
from .nop_conn import NopConn
from .nopper import Nopper

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", '--api_key', help='GPT-3 API key to load.')
    parser.add_argument('-l', '--log', action='store_false', help='disable logging, Default = true.')
    parser.add_argument('-m', '--master', action='store_true', help='Should you start as the master.')
    parser.add_argument('-s', '--server', action='store_true', help='Should initialize the server.')
    args = parser.parse_args()

    api_key = ''
    with open("api_keys/" + args.api_key, "r") as f:
        api_key = f.read()

    nop_conn = NopConn(args.server)
    nopper = Nopper(nop_conn, api_key, args.log, args.master)
    nopper.run()

if __name__ == '__main__':
    sys.exit(main())