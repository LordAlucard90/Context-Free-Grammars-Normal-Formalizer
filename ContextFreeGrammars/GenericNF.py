from itertools import product
from ContextFreeGrammars.CFG import CFG
import re


class GenericNF(object):
    """ Generic Normal Form Class """

    def isInNF(self, CFG):
        pass

    def convertToNF(self, CFG):
        pass

    def _loadCFG(self, cfg):
        self._V = [x for x in cfg._V]
        self._SIGMA = [x for x in cfg._SIGMA]
        self._S = cfg._S
        self._P = {}
        for v, p in cfg._P.items():
            self._P[v] = []
            for el in p:
                _p = {}
                for i, s in el.items():
                    _p[i] = s
                self._P[v].append(_p)

    def simplifyCFG(self, cfg):
        """ Base Normal Form : epsilon-free Grammar """
        self._loadCFG(cfg)
        self._reduceCFG()
        self._removeUnitProductins()
        self._removeNullProductins()
        return CFG().create(self._V, self._SIGMA, self._S, self._P)

    def _removeNullProductins(self):
        if re.escape('#') not in self._SIGMA:
            return
        self._SIGMA = [x for x in self._SIGMA if x is not re.escape('#')]
        _P = {}
        for v in self._V:
            if v not in _P.keys():
                _P[v] = []
            for p in self._P[v]:
                if len(p) == 1 and p[0] == re.escape('#'):
                    newPs = self._createProductions(v)
                    for _v, _p in newPs.items():
                        if _v not in _P.keys():
                            _P[_v] = []
                        _P[_v] = [x for x in _p if x not in _P[_v]] + _P[_v]
                else:
                    _P[v] = [x for x in [p] if x not in _P[v]] + _P[v]
        self._P = _P

    def _createProductions(self, s):
        _P = {}
        for v in self._V:
            for p in self._P[v]:
                if s in p.values():
                    if len(p.values()) > 1:
                        # generate all possible combination
                        i = list(p.values()).count(s)
                        cases = [[x for x in l] for l in list(product([True, False], repeat=i))]
                        # [Treu]*i means that all ss do not change eg. s=B, V->aBa remain aBa
                        cases = [x for x in cases if x != [True] * i]
                        for case in cases:
                            k = 0  # production length
                            _i = 0  # number of s appeared
                            c = {}
                            for key, val in p.items():
                                if val != s:
                                    c[k] = val
                                    k += 1
                                elif case[_i]:
                                    c[k] = val
                                    k += 1
                                    _i += 1
                                else:
                                    _i += 1
                            if v not in _P.keys():
                                _P[v] = []
                            _P[v] = [x for x in [c] if x not in _P[v] and x != {}] + _P[v]
                    else:
                        # this mean that v -> p is equl to v -> #
                        newPs = self._createProductions(v)
                        for _v, _p in newPs.items():
                            if _v not in _P.keys():
                                _P[_v] = []
                            _P[_v] = [x for x in _p if x not in _P[_v]] + _P[_v]
        return _P

    def _removeUnitProductins(self):
        P = {}
        for v in self._V:
            P[v] = []
            for p in self._P[v]:
                if len(p) == 1 and p[0] in self._V:
                    newPs = self._findTerminals(v, p[0])
                    P[v] = [x for x in newPs if x not in P[v]] + P[v]
                else:
                    P[v] = [x for x in [p] if x not in P[v]] + P[v]
        self._P = P
        self._reduceCFG()

    def _findTerminals(self, parent, son):
        T = []
        for p in self._P[son]:
            if len(p) > 1 or p[0] in self._SIGMA:
                T = [x for x in [p] if x not in T] + T
            elif p[0] != parent:
                T = [x for x in self._findTerminals(parent, p[0]) if x not in T] + T
        return T

    def _reduceCFG(self):
        W = {}
        W[0] = self._updateW(self._SIGMA)
        i = 1
        W[i] = self._updateW(W[i - 1], W[i - 1])
        while (W[i] != W[i - 1]):
            i += 1
            W[i] = self._updateW(W[i - 1], W[i - 1])
        V = W[i]
        _P = {}
        for v in V:
            _P[v] = []
            for _p in self._P[v]:
                if [True for x in range(len(_p))] == [x in V + self._SIGMA for n, x in _p.items()]:
                    _P[v].append(_p)
        self._P = _P
        Y = {}
        Y[0] = [self._S]
        j = 1
        Y[1] = self._propagateProduction(Y[0])
        while (Y[j] != Y[j - 1]):
            j += 1
            Y[j] = self._propagateProduction(Y[j - 1], Y[j - 2])
        self._V = [x for x in V if x in Y[j]]
        self._SIGMA = [x for x in self._SIGMA if x in Y[j]]

    def _propagateProduction(self, Y, _prev=None):
        _y = [x for x in Y]
        y = [x for x in Y if x not in self._SIGMA]
        if _prev is not None:
            y = [x for x in y if x not in _prev]
        for v in y:
            for p in self._P[v]:
                for n, s in p.items():
                    if s not in Y:
                        _y.append(s)
        return _y

    def _updateW(self, SET, _prev=None):
        if _prev is not None:
            W = [x for x in _prev]
        else:
            W = []
        for v in self._P:
            for p in self._P[v]:
                for n, _v in p.items():
                    if _v in SET and v not in W:
                        W.append(v)
        return W


if __name__ == "__main__":
    G = CFG()

    print('\nTest : reduce CFG (test/GenericNF_reduce.txt.txt)')
    G.loadFromFile('tests/GenericNF_reduce.txt')
    g = GenericNF().simplifyCFG(G.__copy__())
    print(G, '\n', g)

    print('\nTest : remove unit productins (tests/GenericNF_unit.txt)')
    G.loadFromFile('tests/GenericNF_unit.txt')
    g = GenericNF().simplifyCFG(G.__copy__())
    print(G, '\n', g)

    print('\nTest : remove null productins (tests/GenericNF_null.txt)')
    G.loadFromFile('tests/GenericNF_null.txt')
    g = GenericNF().simplifyCFG(G.__copy__())
    print(G, '\n', g)
