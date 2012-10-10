#!/usr/bin/env python
import sys
import subprocess
import argparse

TAB = 4


class IPTablesObject(object):

    def __init__(self, name=None):
        self.name = name


class Rule(object):

    def __init__(self, opts, to_chain, args):
        self.opts = opts
        self.to_chain = to_chain
        self.args = args

    def format(self, level):
        ret_value = ' ' * TAB * level
        if self.opts:
            ret_value += '%s' % self.opts
        if self.to_chain is not None:
            ret_value += '-> %s' % self.to_chain.format(level + 1, self.args)
        return ret_value


class Chain(IPTablesObject):

    def __init__(self, name, policy=None):
        super(Chain, self).__init__(name)
        self.rules = list()
        self.policy = policy

    def parse(self, dump, chains):
        opts, _, to_chain = dump.partition('-j ')
        to_chain, _, args = to_chain.partition(' ')
        to_chain = chains[to_chain.strip()] if to_chain else None
        self.rules.append(Rule(opts, to_chain, args))

    def format(self, level, args=''):
        args = args.strip('\n')
        rules = [rule.format(level + 1) for rule in self.rules]
        if self.policy:
            ret_value = '%s %s\n' % (self.name, self.policy)
        elif args:
            ret_value = '%s (%s)\n' % (self.name, args)
        else:
            ret_value = '%s\n' % self.name

        ret_value += ''.join(rules)
        return ret_value


class Table(IPTablesObject):

    build_in_chains = ['DROP', 'ACCEPT', 'LOG', 'RETURN', 'DNAT', 'SNAT',
                       'MASQUERADE', 'REJECT', 'CHECKSUM']

    def __init__(self, name):
        super(Table, self).__init__(name)
        self.root = []
        self.chains = dict([(name, Chain(name))
                            for name in self.build_in_chains])

    def parse(self, dump):
        '''
        @type dump: string
        '''
        for line in dump.split('\n'):
            try:
                if line.startswith('-P'):
                    _, name, policy = line.split()
                    chain = Chain(name, policy)
                    self.root.append((name, chain))
                    self.chains[name] = chain
                elif line.startswith('-N'):
                    name = line.split()[1].strip()
                    self.chains[name] = Chain(name)
                elif line.startswith('-A'):
                    _, chain, dump = line.split(None, 2)
                    self.chains[chain.strip()].parse(dump, self.chains)
            except:
                print 'Error on line:', line
                raise

    def format(self):
        separator = '---------------\n'
        ret = [chain[1].format(0) for chain in self.root]
        return separator + separator.join(ret)


if __name__ == '__main__':
    tables = ('nat', 'filter', 'mangle', 'raw', 'security')
    descr = ('Prints iptables in nice and cozy way.\nSupported tables: {%s}' %
             '|'.join(tables))
    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument("-t", "--table", dest="table", default="filter",
                        help="table to show")
    options = parser.parse_args()

    table = options.table

    proc = subprocess.Popen(['sudo', 'iptables', '-t', table, '-S'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
    out, err = proc.communicate()
    rc = proc.returncode

    if rc:
        print err
        sys.exit(1)
    t = Table(table)
    t.parse(out)
    print t.format()
