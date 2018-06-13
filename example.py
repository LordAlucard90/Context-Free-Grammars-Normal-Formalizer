if __name__ == "__main__":
    from ContextFreeGrammars import *
    from sys import argv
    G=Grammar()
    G.loadFromFile(argv[1])
    print(' - Input')
    print(G)
    print(' - Output')
    if Greibach().isInNF(G):
        print('Context Free Grammar is allready in Greibach Normal Form')
    else:
        print(Greibach().convertToNF(G))
