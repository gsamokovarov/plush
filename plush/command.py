import sys

import tornado.options
from tornado.options import define, options


def parse_command_line(args=None):
    '''
    Parses the command line options from `args` or if not given from
    `sys.argv`.

    Returns the parsed options in a `dict`ionary of `(name, value)` pairs.
    '''

    tornado.options.parse_command_line(args or sys.argv)

    return dict([name, opt.value()] for name, opt in options.iteritems())
