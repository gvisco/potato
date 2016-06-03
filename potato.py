# -*- coding: utf-8 -*-
import argparse
import os.path
import pickle
import re


class MarkovChain(object):
    def __init__(self, order):
        verbose("New Markov Chain. Order %i" % order)
        self.order = order
        # the state is a tuple made of 'order' different elements
        self.current_state = (None,) * order
        # the chain is a dictionary of adjacent states
        # keep a counter for each reachable state
        # use the hash key to keep the total
        self.chain = {self.current_state: {'#': 0.0}}

    def add_transition(self, element):
        next_state = self.current_state[1:] + (element,)
        verbose('New transition: (%s) -> (%s)' % (str(self.current_state), str(next_state)))

        reachable_states = self.chain[self.current_state]
        if next_state not in reachable_states:
            reachable_states[next_state] = 1
        else:
            reachable_states[next_state] += 1
        reachable_states['#'] += 1

        self.current_state = next_state
        if self.current_state not in self.chain:
            self.chain[self.current_state] = {'#': 0.0}

    def move_to(self, element):
        likelihood = 0.0

        next_state = self.current_state[1:] + (element,)
        verbose('Transition: (%s) -> (%s)' % (str(self.current_state), str(next_state)))
        if self.current_state in self.chain:
            reachable_states = self.chain[self.current_state]
            if next_state in reachable_states:
                likelihood = reachable_states[next_state] / reachable_states['#']

        self.current_state = next_state

        verbose('Likelihood: %f' % likelihood)
        return likelihood


class WisePotato(object):
    def __init__(self, regex, order):
        verbose('New Potato. Regex: %s' % regex)
        self.regex = re.compile(regex)
        self.chain = MarkovChain(order)

    def learn_from_file(self, path):
        verbose("Learn from file: %s" % path)
        for line in open(path, 'r'):
            tokens = self._extract_tokens(line)
            verbose('Tokens: %s - Input: %s' % (str(tokens), line.rstrip()))
            if tokens:
                self.chain.add_transition(tokens)

    def process_file(self, path):
        verbose("Process file: %s" % path)
        for line in open(path, 'r'):
            tokens = self._extract_tokens(line)
            verbose('Tokens: %s - Input: %s' % (str(tokens), line.rstrip()))
            tag = 'SKIP'
            likelihood = None
            if tokens:
                likelihood = self.chain.move_to(tokens)
                tag = WisePotato._tag_likelihood(likelihood)
            output('%s [%s][%s]' % (line.rstrip(), tag, str(likelihood)))

    def _extract_tokens(self, line):
        m = self.regex.match(line)
        return m.groups() if m else None

    @staticmethod
    def _tag_likelihood(likelihood):
        if likelihood <= 0.05:
            tag = 'POTATO!'
        elif likelihood <= 0.25:
            tag = 'WARNING'
        elif likelihood <= 0.5:
            tag = 'UNUSUAL'
        elif likelihood <= 0.75:
            tag = 'COMMON'
        else:
            tag = 'EXPECTED'
        return tag


def verbose(txt):
    global verb
    if verb:
        print "[DEBUG] %s" % txt


def output(txt):
    print txt


def check_positive(value):
    ival = int(value)
    if ival <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ival


def check_file(value):
    if not os.path.isfile(value):
        raise argparse.ArgumentTypeError("%s is not a file" % value)
    return value


def check_regex(value):
    try:
        re.compile(value)
    except re.error:
        raise argparse.ArgumentTypeError("%s is not a valid regex" % value)
    return value


if __name__ == '__main__':
    global verb
    parser = argparse.ArgumentParser(description="Log tagging through Artificial Ignorance")
    parser.add_argument('-v', '--verbose', help='Print debug output', action='store_true')

    subparsers = parser.add_subparsers(help='Potato command')

    init_parser = subparsers.add_parser('init')
    init_parser.set_defaults(which='init')
    init_parser.add_argument('regex', help='Regular expression to extract data from the input file.', type=check_regex)
    init_parser.add_argument('-k', '--knowledge', help='File used to store knowledge.\n'
                                                       'Default: potato.kb', default='potato.kb')
    init_parser.add_argument('-o', '--order', help='Markov Chain order.\n'
                                                   'Default: 1', type=check_positive, default=1)

    learn_parser = subparsers.add_parser('learn')
    learn_parser.set_defaults(which='learn')
    learn_parser.add_argument('input', help='Training data')
    learn_parser.add_argument('-k', '--knowledge', help='File used to store knowledge.\n'
                                                        'Default: potato.kb', default='potato.kb', type=check_file)

    tag_parser = subparsers.add_parser('tag')
    tag_parser.set_defaults(which='tag')
    tag_parser.add_argument('input', help='File to tag')
    tag_parser.add_argument('-k', '--knowledge', help='File used to store knowledge.\n'
                                                      'Default: potato.kb', default='potato.kb', type=check_file)

    args = parser.parse_args()
    verb = args.verbose

    if args.which is 'init':
        potato = WisePotato(args.regex, args.order)
        verbose("Init knowledge file: %s" % args.knowledge)
        pickle.dump(potato, open(args.knowledge, 'w'))
    elif args.which is 'learn':
        verbose("Loading knowledge file: %s" % args.knowledge)
        potato = pickle.load(open(args.knowledge, 'r'))
        potato.learn_from_file(args.input)
        verbose("Saving knowledge file: %s" % args.knowledge)
        pickle.dump(potato, open(args.knowledge, 'w'))
    elif args.which is 'tag':
        verbose("Loading knowledge file: %s" % args.knowledge)
        potato = pickle.load(open(args.knowledge, 'r'))
        potato.process_file(args.input)
    else:
        raise ValueError('Unrecognized command line args')

