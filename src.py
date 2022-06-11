class Automat():
    def __init__(self, fisier):
        f = open(fisier)
        self.stari, self.autom = int(f.readline()), {
            int(x): []for x in f.readline().split()}
        self.alf = []
        for _ in [0]*int(f.readline()):
            i, j, v = f.readline().split()
            self.autom[int(i)].append((int(j), v))
            self.alf.append(v)
        self.q0, self.final = (int(f.readline()), f.readline())[
            0], ([int(i)for i in f.readline().split()], f.readline())[0]
        self.alf = list(dict.fromkeys(self.alf))


class DFA(Automat):
    def __init__(self, fisier): super().__init__(fisier)

    def checkWord(self, cuv):
        nod = self.q0
        for litera in cuv:
            for tup in self.autom[nod]:
                if tup[1] == litera:
                    nod = tup[0]
                    break
            else:
                return 0
        else:
            if nod in self.final:
                return 1
            return 0


class PushDown(Automat):
    def __init__(self, fisier):
        f = open(fisier)
        self.stari, self.autom = int(f.readline()), {
            int(x): []for x in f.readline().split()}
        self.z0 = f.readline()[:-1]
        self.alf = []
        for _ in [0]*int(f.readline()):
            i, j, st, po, pu = f.readline().split()
            self.autom[int(i)].append((int(j), st, po, pu))
            self.alf += [st, po, pu]
        self.q0, self.final = (int(f.readline()), f.readline())[
            0], ([int(i)for i in f.readline().split()], f.readline())[0]
        self.alf = list(dict.fromkeys(self.alf))

    def checkWord(self, cuv):  # cu stare finala
        stack = [self.z0]
        i = 0
        avemTreaba = 1
        nod = self.q0
        while avemTreaba:
            avemTreaba = 0  # ia hai
            for tup in self.autom[nod]:
                if tup[1] == '~' and tup[2] == stack[-1]:
                    stack.pop()
                    if tup[3] != '~':
                        stack += list(tup[3])[::-1]
                    nod = tup[0]
                    avemTreaba = 1
                    break
                if i < len(cuv) and tup[1] == cuv[i] and tup[2] == stack[-1]:
                    stack.pop()
                    if tup[3] != '~':
                        stack += list(tup[3])[::-1]
                    nod = tup[0]
                    avemTreaba = 1
                    i += 1
                    break
        if nod in self.final and i == len(cuv):
            return 1
        return 0


class NFA(Automat):
    def __init__(self, fisier): super().__init__(fisier)

    def checkWord(self, cuv):
        def func(c, i, nod, k):
            if len(c) == i and nod in self.final:
                return 1
            for tup in self.autom[nod]:
                if tup[1] == '~' and k[tup[0]] == 0:
                    k[tup[0]] = 1
                    if func(c, i, tup[0], k):
                        return 1
                if i < len(c) and tup[1] == c[i]:
                    if func(c, i+1, tup[0], dict.fromkeys(k.keys(), 0)):
                        return 1

        if func(cuv, 0, self.q0,  dict.fromkeys(self.autom.keys(), 0)):
            return 1
        return 0

    def transformToDfa(self):
        coad = [[self.q0]]
        new, idd = {(self.q0,): []}, {}
        while len(coad) != 0:
            for lit in self.alf:
                s = set()  # dap trebuia set
                for lis in coad[0]:
                    for tup in self.autom[lis]:
                        if tup[1] == lit:
                            s.add(tup[0])
                copie = list(dict.fromkeys(s))
                initial = tuple(copie)
                if initial not in new:
                    coad.append(copie[:])
                    new[initial] = []
                new[tuple(coad[0])].append(tuple(copie+[lit]))
            coad.pop(0)
        fin = []
        self.stari = len(new)
        for i, j in enumerate(new):
            for k in list(j):
                if k in self.final:
                    fin.append(i)
                    break
        self.final = fin
        k = 1
        for i in new:
            idd[i] = k
            k += 1
        d = {}
        for i in new:
            if i in idd:
                d[idd[i]] = []
            else:
                d[i] = []
            for j in new[i]:
                if tuple(j[:-1]) in idd:
                    d[idd[i]].append((idd[j[:-1]], j[-1]))
                else:
                    d[i].append(j)
        self.autom = d

    def minimizare(self):
        amGasit = 1
        undemerg = []
        Q = [-1212]+list(self.autom)
        m = [[0]*len(Q) for _ in range(len(Q))]
        for i in range(1, len(m)-1):
            for j in range(i+1, len(m)):
                if(Q[i] in self.final and Q[j] not in self.final) or (Q[i] not in self.final and Q[j] in self.final):
                    m[i][j] = 'x'

        while amGasit:  # asta calculeaza care stari sunt echivalente
            amGasit = 0
            for i in range(1, len(m)-1):
                for j in range(i+1, len(m)):
                    if m[i][j] == 0:
                        for lit in self.alf:
                            for tup in self.autom[i]:
                                if tup[1] == lit:
                                    undemerg.append(tup[0])
                                    break
                            for tup in self.autom[j]:
                                if tup[1] == lit:
                                    undemerg.append(tup[0])
                                    break
                            if len(undemerg) == 2 and m[undemerg[0]][undemerg[1]] == 'x':
                                m[i][j] = 'x'
                                amGasit = 1
                            undemerg = []
        d = {}
        # creez un dict ajutator si recalculez final [stare] : [e echivalenta cu...]
        for i in range(1, len(m)-1):
            for j in range(i+1, len(m)):
                if m[i][j] == 0:
                    if i in self.final:
                        self.final.remove(i)
                    if j in d:
                        d[j].append(i)
                    else:
                        d[j] = [i]
        self.final = list(set(self.final+[j]))
        d = dict(sorted(d.items(), key=lambda item: -len(item[1])))
        for i in d:  # asta reface starea initiala
            for j in d[i]:
                if j == self.q0:
                    self.q0 = i
                    break
            else:
                continue
            break
        for boss in d:
            if boss in self.autom:
                for sublocotenentMajor in d[boss]:
                    for caut in self.autom[sublocotenentMajor]:
                        self.autom[boss].append(caut)
                    for i in self.autom:  # aici dam copypaste ca la carte la tranzitii si le redenumim
                        pizza = []
                        for j in self.autom[i]:
                            if j[0] == sublocotenentMajor:
                                pizza.append((boss, j[1]))
                            else:
                                pizza.append(j)
                        self.autom[i] = pizza
                    del self.autom[sublocotenentMajor]
        for damCuMatura in self.autom:  # eliminam dublurile cu aceasta manevra
            self.autom[damCuMatura] = list(set(self.autom[damCuMatura]))
        self.stari = len(self.autom)


if __name__ == "__main__":
    # print(NFA('input.txt').checkWord('cabcbabc'))
    a = NFA('input.txt')
    # print(a.autom)
    # print()
    # a.transformToDfa()
    # print(a.autom)
    # print()
    # a.minimizare()
    # a = PushDown('input.txt')
    # print(a.autom)
    # print()
    # Word('abaa'))
    # print(a.checkWord('aaaabbb'))
    # print(a.checkWord('aaabbb'))
    # print(a.checkWord('aabb'))
