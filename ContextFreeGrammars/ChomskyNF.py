from ContextFreeGrammars.GenericNF import GenericNF
from ContextFreeGrammars.CFG import CFG
import re


class ChomskyNF(GenericNF):
    """ Chomsky Normal Form Class """

    def isInNF(self, cfg):
        """ X -> a | YZ  """
        if re.escape('#') in cfg._SIGMA:
            return False
        else:
            for v, PS in cfg._P.items():
                for p in PS:
                    if len(p) > 2:
                        return False
                    elif len(p) == 2 and (p[0] not in cfg._V or p[1] not in cfg._V):
                        return False
                    elif len(p) == 1 and p[0] in cfg._V:
                        return False
        return True

    def convertToNF(self, cfg):
        self._loadCFG(cfg)
        self._reduceCFG()
        self._removeNullProductins()
        self._replaceMixedTerminals()
        self._splitNonTerminalSequences()
        self._removeUnitProductins()
        return CFG().create(self._V, self._SIGMA, self._S, self._P)

    def _replaceMixedTerminals(self):
        _P = {}
        _wrongPs = {}
        for v, Ps in self._P.items():
            _P[v] = []
            for p in Ps:
                if len(p) > 1 and len([x for x in p.values() if x in self._SIGMA]) > 0:
                    if v not in _wrongPs.keys():
                        _wrongPs[v] = []
                    _wrongPs[v].append(p)
                else:
                    _P[v].append(p)
        _conv = {}
        for v, Ps in _wrongPs.items():
            for p in Ps:
                for s in list(set([y for y in [x for x in p.values() if x in self._SIGMA] if y not in _conv.keys()])):
                    _v = self._createVariable(v[0])
                    self._V.append(_v)
                    _conv[s] = _v
                    _P[_v] = [{0: s}]
                _p = {}
                for j, s in p.items():
                    if s in self._SIGMA:
                        _p[j] = _conv[s]
                    else:
                        _p[j] = s
                _P[v].append(_p)
        self._P = _P

    def _createVariable(self, S):
        i = 0
        while (S + '\\_' + str(i) in self._V):
            i += 1
        return S + '\\_' + str(i)

    def _splitNonTerminalSequences(self):
        _P = {}
        _wrongPs = {}
        for v, Ps in self._P.items():
            _P[v] = []
            for p in Ps:
                if len(p) > 2 and len([x for x in p.values() if x in self._V]) > 0:
                    if v not in _wrongPs.keys():
                        _wrongPs[v] = []
                    _wrongPs[v].append(p)
                else:
                    _P[v].append(p)
        for v, Ps in _wrongPs.items():
            if v not in _P.keys():
                _P[_v[j]] = []
            for p in Ps:
                n = len(p)
                _v = {0: v}
                for j in range(1, n):
                    if j != n - 1:
                        _v[j] = self._createVariable('X')
                        self._V.append(_v[j])
                    else:
                        _v[j] = p[j]
                    if _v[j] not in _P.keys():
                        _P[_v[j]] = []
                    _P[_v[j - 1]].append({0: p[j - 1], 1: _v[j]})
        self._P = _P


if __name__ == "__main__":
    print("Chomsky Normal Form")
    G = CFG()

    print('\nTest : check normal form (test/ChomskyNF.txt)')
    G.loadFromFile('tests/ChomskyNF.txt')
    result = ChomskyNF().isInNF(G)
    print(G)

    if result:
        print('\ngrammar is in Chomsky normal form')
    else:
        print('\ngrammar is not in Chomsky normal form\n')
        g = ChomskyNF().convertToNF(G)
        print(g)

        if ChomskyNF().isInNF(g):
            print('\ngrammar is now in Chomsky normal form')
        else:
            print('\ngrammar is still not in Chomsky normal form')
