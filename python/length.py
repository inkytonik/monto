#! /usr/bin/env python3
# length
# Receive Monto versions and report their length.

import montolib


def version_length(version):
    length_product = {
        'source': version['source'],
        'product': 'length',
        'language': 'number',
        'contents': str(len(version['contents']))
    }
    return ([length_product], True)

montolib.server(version_length)
