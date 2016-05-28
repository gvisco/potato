# -*- coding: utf-8 -*-
import argparse
import os.path
import pickle
import re


class MarkovChain(object):
    def __init__(self, order):
        verbose("New Markov Chain. Order %i" % order)
        self.order = order
        # the state is a tuple made of 'order' element
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
            output('[%s][%s] %s' % (tag, str(likelihood), line.rstrip()))

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


def check_args(args):
    if not os.path.isfile(args.input):
        raise ValueError('Invalid input. Not a file. Value: ' + args.input)
    if not args.learn:
        raise ValueError("Nothing can be processed without previous knowledge. Let's learn something first")
    if args.regex is None:
        raise ValueError('A regular expression must be specified to get some new knowledge')
    if args.order < 1:
        raise ValueError('Markov Chain order must be positive. Value: ' + args.order)


if __name__ == '__main__':
    global verb
    parser = argparse.ArgumentParser(description="Artificial Ignorance applied to LOG files")
    parser.add_argument('input', help='Input file')
    parser.add_argument('-k', '--knowledge', help='File used to load/save knowledge.\n'
                                                  'Default: potato.kb', default='potato.kb')
    parser.add_argument('-l', '--learn', help='Learn from input. '
                                              'Mandatory if the knowledge file does not exist.', action='store_true')
    parser.add_argument('-re', '--regex', help='Regular expression to extract data from the input file. '
                                               'Mandatory if the knowledge file does not exist, ignored otherwise.')
    parser.add_argument('-o', '--order', help='Markov Chain order. '
                                              'Mandatory if the knowledge file does not exist, ignored otherwise.\n'
                                              'Default: 1',
                        type=int, default=1)
    parser.add_argument('-v', '--verbose', help='Print debug output', action='store_true')

    args = parser.parse_args()
    verb = args.verbose

    # instantiate
    if os.path.isfile(args.knowledge):
        verbose("Loading knowledge file: %s" % args.knowledge)
        potato = pickle.load(open(args.knowledge, 'r'))
    else:
        check_args(args)
        potato = WisePotato(args.regex, args.order)

    # process
    if args.learn:
        potato.learn_from_file(args.input)
    else:
        potato.process_file(args.input)

    # save
    if args.learn:
        verbose("Saving knowledge file: %s" % args.knowledge)
        pickle.dump(potato, open(args.knowledge, 'w'))
