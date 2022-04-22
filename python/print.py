#! /usr/bin/env python3
# print
# Receive products from Monto and print them.

import montolib


def sink_print(product):
    print(product)
    return True

montolib.sink(sink_print)
