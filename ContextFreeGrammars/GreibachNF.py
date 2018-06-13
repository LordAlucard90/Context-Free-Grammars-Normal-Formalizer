from ContextFreeGrammars.ChomskyNF import ChomskyNF
from ContextFreeGrammars.CFG import CFG
import re


class GreibachNF(ChomskyNF):
    """ Greibach Normal Form Class """

    # Variables Conversion Dictionary
    _conv = {}

    def isInNF(self, cfg):
        """ A -> a | a A_1 ... A_n"""
        if re.escape('#') in cfg._SIGMA:
            return False
        else:
            for v, PS in cfg._P.items():
                for p in PS:
                    if p[0] in cfg._V:
                        return False
                    elif len(p) > 1:
                        for i in range(1, len(p)):
                            if p[i] not in cfg._V:
                                print(p, i, cfg._V)
                                return False
        return True

    def convertToNF(self, cfg):
        ChomskyNF.convertToNF(self, cfg)
        self._renameCFG()
        self._orderProductions()
        self._terminateFirstSymbol()
        self._renameBackCFG()
        return CFG().create(self._V, self._SIGMA, self._S, self._P)

    def _terminateFirstSymbol(self):
        _P = {}
        for v in sorted(self._V, key=lambda n: int(n[3:]), reverse=True):
            _P[v] = []
            for p in self._P[v]:
                if p[0] in self._V:
                    newPs = self._terminateProduction(p)
                    _P[v] = [x for x in newPs if x not in _P[v]] + _P[v]
                else:
                    _P[v].append(p)
        self._P = _P

    def _terminateProduction(self, p):
        _Ps = []
        for _p in self._P[p[0]]:
            if _p[0] in self._V:
                T = self._terminateProduction(_p)
            else:
                T = [_p]
            for t in T:
                new = {}
                for i in range(len(t)):
                    new[i] = t[i]
                i = len(new) - 1
                for j in range(1, len(p)):
                    new[i + j] = p[j]
                _Ps.append(new)
        return _Ps

    def _renameCFG(self):
        self._conv[self._S] = 'A\\_0'
        _P = {'A\\_0': []}
        _S = 'A\\_0'
        _P[_S] = self._renameCFGProductions(self._S)
        for v in [x for x in self._V if x != self._S]:
            if v not in self._conv.keys():
                self._conv[v] = self._createConvVariable()
            _P[self._conv[v]] = self._renameCFGProductions(v)
        self._V = list(_P.keys())
        self._S = _S
        self._P = _P

    def _createConvVariable(self):
        i = 0
        while ('A\\_' + str(i) in self._conv.values()):
            i += 1
        return 'A\\_' + str(i)

    def _renameCFGProductions(self, v):
        _Ps = []
        for el in self._P[v]:
            _p = {}
            for i, s in el.items():
                if s in self._SIGMA:
                    _p[i] = s
                elif s in self._conv.keys():
                    _p[i] = self._conv[s]
                else:
                    _v = self._createConvVariable()
                    self._conv[s] = _v
                    _p[i] = _v
            _Ps.append(_p)
        return _Ps

    def _renameBackCFG(self):
        _cB = {}
        for old, new in self._conv.items():
            _cB[new] = old
        self._S = _cB[self._S]
        self._V = list(_cB.values()) + [x for x in self._V if x not in list(_cB.keys())]
        _P = {}
        for v, Ps in self._P.items():
            if v in _cB.keys():
                _v = _cB[v]
            else:
                _v = v
            _P[_v] = []
            for p in Ps:
                _p = {}
                for i, s in p.items():
                    if s in _cB.keys():
                        _p[i] = _cB[s]
                    else:
                        _p[i] = s
                _P[_v].append(_p)
        self._P = _P

    def _orderProductions(self):
        _Ps = {}
        for v in self._V:
            if v not in _Ps.keys():
                _Ps[v] = []
            for p in self._P[v]:
                if p[0] == v:
                    _newPs = self._removeLeftRecursion(v, p)
                    for _v, s in _newPs.items():
                        if _v not in _Ps.keys():
                            _Ps[_v] = []
                            self._V = [x for x in [_v] if x not in self._V] + self._V
                        _Ps[_v] = [x for x in s if x not in _Ps[_v]] + _Ps[_v]
                else:
                    _Ps[v].append(p)
        _P = {}
        for v in sorted(self._V, key=lambda n: int(n[3:])):
            if v not in _P.keys():
                _P[v] = []
            for p in _Ps[v]:
                if p[0] in self._V:
                    if int(p[0][3:]) < int(v[3:]):
                        _newPs = self._replaceProduction(v, p, _Ps)
                        _P[v] = [x for x in _newPs if x not in _P[v]] + _P[v]
                    else:
                        _P[v] = [x for x in [p] if x not in _P[v]] + _P[v]
                else:
                    _P[v] = [x for x in [p] if x not in _P[v]] + _P[v]
        self._P = _P

    def _replaceProduction(self, v, p, Ps):
        _Ps = []
        for _ps in Ps[p[0]]:
            _p = {}
            for k, el in _ps.items():
                _p[k] = el
            i = len(_p) - 1
            for j in range(1, len(p)):
                _p[i + j] = p[j]
            if _p[0] in self._V:
                if int(_p[0][3:]) < int(v[3:]):
                    _newPs = self._replaceProduction(v, _p, Ps)
                    _Ps = [x for x in _newPs if x not in _Ps] + _Ps
                else:
                    _Ps = [x for x in [_p] if x not in _Ps] + _Ps
            else:
                _Ps = [x for x in [_p] if x not in _Ps] + _Ps
        return _Ps

    def _removeLeftRecursion(self, v, p):
        _T = []
        _v = self._createVariable('A')
        for s in self._P[v]:
            if s[0] != v:
                _T.append(s)
        _Ps = {v: [], _v: []}
        for t in _T:
            p0 = {}
            for i, el in t.items():
                p0[i] = el
            p0[len(p0)] = _v
            _Ps[v] = [x for x in [p0] if x not in _Ps[v]] + _Ps[v]
        p1 = {}
        p2 = {}
        for i, s in p.items():
            if i != 0:
                p1[i - 1] = s
                p2[i - 1] = s
        p2[len(p2)] = _v
        _Ps[_v] = [x for x in [p1, p2] if x not in _Ps[_v]] + _Ps[_v]
        return _Ps


if __name__ == "__main__":
    print("Greibach Normal Form")
    G = CFG()

    print('\nTest : check normal form (tests/GreibachNF.txt)')
    G.loadFromFile('tests/GreibachNF.txt')
    result = GreibachNF().isInNF(G)
    print(G)

    if result:
        print('\ngrammar is in Greibach normal form')
    else:
        print('\ngrammar is not in Greibach normal form\n')
        g = GreibachNF().convertToNF(G)
        print(g.__str__(['S', 'A', 'B', 'X\\_1', 'A\\_9', 'A\\_8', 'X\\_0', 'S\\_0', 'B\\_0', 'B\\_1']))

        if GreibachNF().isInNF(g):
            print('\ngrammar is now in Greibach normal form')
        else:
            print('\ngrammar is still not in Greibach normal form')
