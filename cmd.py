# -*-coding=utf-8 -*-
import argparse
from loguru import logger
from main import run_maintainer
# from main import run_maintainer_ping
from main import run_maintainer_init
import sys

optional_title = 'optional arguments'


def str2bool(v):
    """
    convert string to bool
    :param v:
    :return:
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    return True


class CapitalisedHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super(CapitalisedHelpFormatter, self).__init__(prog,
                                                       indent_increment=2,
                                                       max_help_position=30,
                                                       width=200)
        self._action_max_length = 20

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'Usage: '
        return super(CapitalisedHelpFormatter, self).add_usage(
            usage, actions, groups, prefix)

    class _Section(object):

        def __init__(self, formatter, parent, heading=None):
            self.formatter = formatter
            self.parent = parent
            self.heading = heading
            self.items = []

        def format_help(self):
            # format the indented section
            if self.parent is not None:
                self.formatter._indent()
            join = self.formatter._join_parts
            item_help = join([func(*args) for func, args in self.items])
            if self.parent is not None:
                self.formatter._dedent()

            # return nothing if the section was empty
            if not item_help:  return ''

            # add the heading if the section was non-empty
            if self.heading is not argparse.SUPPRESS and self.heading is not None:
                current_indent = self.formatter._current_indent
                if self.heading == optional_title:
                    heading = '%*s\n%s:\n' % (current_indent, '', self.heading.title())
                else:
                    heading = '%*s%s:' % (current_indent, '', self.heading.title())
            else:
                heading = ''

            return join(['\n', heading, item_help])


parser = argparse.ArgumentParser(description='Demo of argparse',
                                 formatter_class=CapitalisedHelpFormatter, add_help=False)

parser.add_argument('-v', '--version', action='version', version="1.0", help='Get version of ProxyPool')
parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
parser.add_argument('-u', '--url', help='check ip test url', default='http://www.baidu.com')
parser.add_argument('-name', '--name', help='check function', default='web_check')
parser.add_argument('-api', '--api', help='api url', default='https://eproxy.ppio.cloud/proxy_list?num=20')

# subparsers = parser.add_subparsers(dest='command', title='Available commands', metavar='')
subparsers = parser.add_subparsers(dest='args', title='Available commands', metavar='')
# check web_url
parser_serve = subparsers.add_parser('run_maintainer', help='Run maintainer')
parser_serve.add_argument('-l', '--loop', default=True, type=str2bool, nargs='?', help='Run checker for infinite')

# check ping
parser_check = subparsers.add_parser('run_maintainer_ping', help='Run maintainer_ping')
parser_check.add_argument('-l', '--loop', default=True, type=str2bool, nargs='?', help='Run checker for infinite')

# init 初始化获取IP and 检验
parser_check = subparsers.add_parser('run_maintainer_init', help='Run maintainer_init')
parser_check.add_argument('-l', '--loop', default=True, type=str2bool, nargs='?', help='Run checker for infinite')

# show help info when no args
if len(sys.argv[1:]) == 0:
    parser.print_help()
    parser.exit()


def cmd():
    args = parser.parse_args()
    api_url = args.api
    name = args.name
    check_url = args.url
    if name == "ping":
        pass
    elif api_url and name == "init":
        run_maintainer_init(api_url,check_url)
    else:
        url = args.url
        run_maintainer(url)


if __name__ == '__main__':
    cmd()
