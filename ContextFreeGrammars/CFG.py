################################################################################
# 
#  Author  : Khaufra Maggini
#  Date    : May 2016
#  Version : 1.0
#  Python  : 2.7.11+
# 
################################################################################
import re
import sys


class CFG:
    """ Context Free Gramamr Class """
    # Variables - Non Terminal Symbols
    _V = []
    # Alphabet - Terminal Symbols
    _SIGMA = []
    # Start Symbol
    _S = None
    # Productions
    _P = []
    # Accepted Variables - Non Terminal Symbols - RegExp
    _V_set = '[A-Z](_[0-9]*)?(,[A-Z](_[0-9]*)?)*'
    # Accepted Alphabet - Terminal Symbols - RegExp
    _SIGMA_set = '.*(,.*)*'
    # Accepted Start Symbol - RegExp
    _S_set = '[A-Z](_[0-9]*)?'
    # Accepted Productions - RegExp
    _P_set = '([A-Z](_[0-9]*)?->.*(|.*)*(,[A-Z](_[0-9]*)?->.*(|.*)*)*)'

    def loadFromFile(self, txtFile):
        """ Costructor From File """
        with open(txtFile) as f:
            lines = f.readlines()
        g = ''.join([re.sub(" |\n|\t", "", x) for x in lines])
        if not re.search('V:' + self._V_set + 'SIGMA:' + self._SIGMA_set + 'S:' + self._S_set + 'P:' + self._P_set, g):
            raise ImportError('Error : grammar bad definition, define your grammar as :'
                              '\nV:[V|V_0],...\nSIGMA:[s|#],...\nS:s0\nP:V1->s1V|#,V2->s1|s2|...')
        v = re.search('V:(.*)SIGMA:', g).group(1)
        sigma = re.search('SIGMA:(.*)S:', g).group(1)
        s = re.search('S:(.*)P:', g).group(1)
        p = re.search('P:(.*)', g).group(1)
        self.load(v, sigma, s, p)

    def load(self, v, sigma, s, p):
        """ Costructor From Strings """
        self._V = [re.escape(x) for x in re.split(',', v.replace(" ", ""))]
        self._SIGMA = [re.escape(x) for x in re.split(',', sigma.replace(" ", ""))]
        if [x for x in self._V if x in self._SIGMA]:
            sys.exit('Error : V intersection SIGMA is not empty')
        s = re.escape(s.replace(" ", ""))
        if s in self._V:
            self._S = s
        else:
            sys.exit('Error : start symbol is not in V')
        p = p.replace(" ", "")
        self._P = self._parsProductions(p)

    def _parsProductions(self, p):
        """ Productions Builder """
        P = {}
        v = []
        self.symbols = self._V + self._SIGMA
        rows = re.split(',', p)
        for row in rows:
            item = re.split('->', row)
            left = re.escape(item[0])
            if (left in self._V):
                v.append(left)
                P[left] = []
                rules = re.split('\|', item[1])
                for rule in rules:
                    P[left].append(self._computeRule(rule))
            else:
                raise ImportError('Rigth simbol in production ' + row + ' is not in V')
        if [True] * len(self._V) == [x in self._V for x in v]:
            return P
        else:
            raise ImportError('Error : not all vocabulary has been used : ' + ''.join([x for x in self._V if x not in v]))

    def _computeRule(self, rule):
        """ Single Rule Builder"""
        _rule = rule
        rules = {}
        i = 0
        while len(_rule) > 0:
            r = re.search('|'.join(self.symbols), rule)
            if r.start() == 0:
                rules[i] = re.escape(_rule[0:r.end()])
                _rule = _rule[r.end():]
                i += 1
            else:
                raise ImportError('Error : undefined symbol find in production : ' + _rule)
        return rules

    def __copy__(self):
        """ Copy Costructor """
        return CFG().create(self._V, self._SIGMA, self._S, self._P)

    def create(self, v, sigma, s, p):
        """ Static Costructor """
        newCFG = CFG()
        newCFG._V = v
        newCFG._SIGMA = sigma
        newCFG._S = s
        newCFG._P = p
        return newCFG

    def __str__(self, order=False):
        _str = 'V: ' + ', '.join(self._V) + '\n'
        _str += 'SIGMA: ' + ', '.join(self._SIGMA) + '\n'
        _str += 'S: ' + self._S + '\n'
        _str += 'P:'
        if order:
            V = [x for x in order if x in self._V] + [x for x in self._V if x not in order]
        else:
            V = self._V
        for v in V:
            _str += '\n\t' + v + ' ->'
            _PS = []
            for p in self._P[v]:
                _p = ''
                for i, s in p.items():
                    _p += ' ' + s
                _PS.append(_p)
            _str += ' |'.join(_PS)
        return _str.replace('\\', '')


if __name__ == "__main__":
    print('Context Free Grammar')
    G = CFG()

    print('Test : load from file (tests/Grammar.txt)')
    G.loadFromFile('tests/Grammar.txt')

    print('Grammar Loaded Correctly')
    print(G)
