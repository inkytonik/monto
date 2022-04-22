#! /usr/bin/env python3
# reverse
# Receive Monto version and report their reverse.

import montolib


def version_reverse(version):
    reverse_product = {
        'source': version['source'],
        'product': 'reverse',
        'language': 'text',
        'contents': version['contents'][::-1]
    }
    return ([reverse_product], True)

montolib.server(version_reverse)
