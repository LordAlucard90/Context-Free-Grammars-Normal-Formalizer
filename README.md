# Normal Formalizer For Context-Free-Grammars
Requires python 3.x (3.6 tested)
## Supported Normal Forms
- Base Context-Free-Grammar Definition
- Chomsky Normal Form
- Greibach Normal Form

## Input Text Format
```
V : [ V | V_0 ], ...
SIGMA : [ s | # ], ...
S : s0
P : V1 -> s1 V | #,
    V2 -> s1 | s2 | ...
```

## Run Example
```
$ python3 example.py example.txt 

```
More examples can be found in 'ContextFreeGrammars/tests'
