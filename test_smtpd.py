#!/usr/bin/env python
import argparse
import asyncore
import smtpd
import time
import os


SMTPD_MAIN_CLASSES = [
    smtpd.DebuggingServer.__name__,
    smtpd.PureProxy.__name__,
    smtpd.MailmanProxy.__name__,
]


def storeproxy_factory(base_class, store_path):
    class StoreProxy(base_class):

        def process_message(self, peer, mailfrom, rcpttos, data):
            filename = '%d_%s.eml' % (int(time.time()), '_'.join(rcpttos))
            with open(os.path.join(store_path, filename), 'w') as f:
                f.write(data)

    return StoreProxy

def get_argparser():
    parser = argparse.ArgumentParser(description='Development SMTPd')
    parser.add_argument(
        '-c',
        '--class',
        choices=SMTPD_MAIN_CLASSES,
        default=SMTPD_MAIN_CLASSES[0],
        type=str,
        dest='klass'
    )
    parser.add_argument(
        '-l',
        '--localaddr',
        nargs=1,
        default='127.0.0.1:1025',
        type=str
    )
    parser.add_argument(
        '-r',
        '--remoteaddr',
        nargs=1,
        default='127.0.0.1:2525',
        type=str
    )
    parser.add_argument(
        '-s',
        '--store',
        nargs=1,
        type=str
    )

    return parser

def normalize_addr(addr):
    if isinstance(addr, list):
        addr = addr[0]
    if ':' in addr:
        host, port = addr.split(':')
        return (host, int(port))
    return None

def main():
    args = get_argparser().parse_args()

    server_class = getattr(smtpd, args.klass)
    if args.store:
        server_class = storeproxy_factory(server_class, args.store[0])

    server = server_class(
        normalize_addr(args.localaddr),
        normalize_addr(args.remoteaddr)
    )

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        server.close()

if __name__ == '__main__':
    main()
