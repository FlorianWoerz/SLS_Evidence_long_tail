import math
import random
import os.path

import generator as g
#from . import generator as g

def create_instances(ns, r, N=10, k=3, s=42, o='./', ps=None, q=None):
    """
    Diese Funktion erstellt eine Reihe von k-SAT Instanzen mit hidden solution.
    :param ns: Sollte eine Liste sein. Jedes Element sollte ein int sein und entspricht der
                Anzahl der Variablen.
    :param r: Die Clause-to-Variable ratio. Die Anzahl der Klauseln werden aus r und den jeweiligen n Werten berechnet.
    :param N: Die Anzahl der Instanzen pro Instanzgröße. Standard: 10
    :param k: Die Anzahl der Literale pro Klausel. Standard: 3.
    :param s: Der Startseed. Dieser wird verwendet, um weitere Seeds für die Instanzerstellung zu generieren. Standard: 42.
    :param o: Der Pfad in den die Instanzen generiert werden.
    :param ps: Die p-Werte mit der die planted Solution versteckt wird. Die Anzahl der p-Werte muss gleich k sein.
                Außerdem muss entweder p oder q None sein. Standard None.
    :param q: Aus dem q-Wert können die p-Werte bestimmt werden. Entweder q oder p müssen None sein.
            Standard: None. ABER: Falls auch ps None entspricht, wird q auf (sqrt(5)-1)/2 gesetzt.
    """
    # Wir überprüfen zunächst die Bedingungen.
    if not hasattr(ns, '__iter__'):
        raise TypeError("ns has to be iterable.")

    if not all(isinstance(x, int) for x in ns):
        raise TypeError('ns has to be a list of integers.')

    if not all(x > 0 for x in ns):
        raise ValueError('All ns have to be greater than zero.')

    if not isinstance(r, float):
        raise TypeError('r should be a float.')

    if not all(isinstance(x, int) for x in [N, k, s]):
        raise TypeError("N, k and s should be integers.")
    if any(x<1 for x in [N, k]):
        raise ValueError('k and N should be at least 1.')

    if not isinstance(o, str):
        raise TypeError("o should be a string.")

    if (ps is not None) and (q is not None):
        raise ValueError("Eiter ps oder q has to be None.")

    if ps is not None:
        if not all(isinstance(x, float) for x in ps):
            raise TypeError("The p-values have to be floats.")
        if len(ps) != k:
            raise ValueError("The number of p-values has to match k.")

    else:
        # In diesem Fall ist also ps == None.
        if q is None:
            # In diesem Fall sind also q und ps None.
            # Als Standardfall setzen wir q auf den goldenen Schnitt.
            q = (math.sqrt(5)-1)/2.0
        if not isinstance(q, float):
            raise TypeError("The q-value has to be a float.")

        # Zu diesem Zeitpunkt ist q definiert. Entweder per Übergabe oder es ist auf den goldenen Schnitt gesetzt worden
        # Wir berechnen nun die p-Werte aus der Formel:
        # p_i = q^i/((1+q)^k - 1)
        # Wobei i hier von 1 bis k geht.
        denom = (pow(1+q, k) - 1)
        ps = []
        for i in range(1, k+1):
            # k+1 ist nicht inklusive.
            ps.append(pow(q,i)/denom)

    # Wir kontrollieren noch ob jedes p im Intervall [0,1] liegt.
    if not all(x <= 1.0 and x >= 0.0 for x in ps):
        raise ValueError("The p-values have to be between 0 and 1.")

    #### Hier startet der eigentliche Code. ####
    rng = random.Random()
    # Wir verwenden aus einem technischen Grund ein Random-Objekt:
    # Der Seed, der in generator.main() gesetzt wird, würde ansonsten die Zufallszahlen hier beeinflussen.
    # Damit wären, technisch gesehen, die Zufallszahlen nicht unabhängig.
    # Das Problem wird umgangen, wenn ein Random-Objekt initialisiert wird.
    rng.seed(s)
    for n in ns:
        # Für jedes n werden die Anzahl der Klauseln berechnet und und der Ausgabepfad bestimmt.
        output_path_n = os.path.join(o, f"n{n}")
        m = round(n*r)
        # Track the seed that were used.
        used_seeds = []
        for i in range(N):
            # Jede Datei soll mit einem neuen, unabhängigen Seed erstellt werden.
            seed = rng.randint(1, 2**32 - 1)
            while seed in used_seeds: # seed was already used, try another one.
            	seed = rng.randint(1, 2**32 - 1)
            used_seeds.append(seed)
            g.main(n, m, k=k, p=ps, s=seed, o=output_path_n)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-ns", nargs='+', type=int, default=None, help="Specifies the number of variables in the formulas.")
    parser.add_argument("-r", type=float, default=None, help="Specifies the clause-to-variable ratio in the formulas.")
    parser.add_argument("-N", type=int, default=10, help="Specifies how many formulas of each size are generated.")
    parser.add_argument("-k", type=int, default=3, help="Specifies the k-value of the formula.")
    parser.add_argument("-s", type=int, default=42, help="The seed to initialize the random number generator.")
    parser.add_argument("-o", type=str, default='./tmp', help="The output-path to save the generated cnf-file.")
    parser.add_argument("-ps", type=float, default=None, nargs='+',
                        help="Specify the p-values as described in the paper.....")
    parser.add_argument("-q", type=float, default=None, help="Specifies the q-value. The p-values can be determined from q.")
    args = parser.parse_args()

    create_instances(args.ns, args.r, N=args.N, k=args.k, s=args.s, o=args.o, ps=args.ps, q=args.q)

