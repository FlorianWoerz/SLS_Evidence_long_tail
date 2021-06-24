import random
import os
from functools import lru_cache
import numpy


def modify_instance(orig, resolvents, seed=42, M=5000, outputPath='./modified', p=None, E=0.1, shuffle=False):
    """Repeatedly modifies a CNF with some of its resolvents and writes the file in DIMACS format.

    For each clause in the resolvent-file specified in `resolvents`, the function samples with
    propbability `p`, if the clauses should be chosen for the modified instance.
    The random number generator used for this sampling is initialized with the `seed` given.
    This modified instance comprises of the original clauses as specified via `orig`
    plus the sampled clauses. If `shuffle` is True, all clauses will be shuffled.
    The function creates `M` such modified instances in the folder specified in `outputPath`
    and writes them to files in DIMACS format.

    Parameters
    ----------
    orig : str
        the path to the original cnf-file

    resolvents: str
        the path to the resolvents-file from where the clauses are sampled

    seed : int, optional
        the seed to initalize the random number generator responsible for sampling the resolvents
        (default: 42)

    M : int, optional
        how many new files are generated for the given cnf-file and resolvents-file
        (default: 5000)

    outputPath : str, optional
        the output path to save the generated new cnf-files
        if the folder does not exist, it will be created
        (default: "./modified")

    p : float, optional
        specifies the probability for adding each resolvent
        the sampling occures by a binomial experiment
        (default: m / (n' * E), where m is the number of clauses in the original formula and n' is the total number of resolvents)

    E: float/int, optional
		probability of adding each resolvent w.r.t. number of original resolvents, p = m / (n' * E).
		(default: 10)

    shuffle : bool, optional
        if True, all clauses (original and resolvents picked) will be shuffled before writing to the file
        (default: False)

    Raises
    ------
    TypeError
        see above

    ValueError
        if M <= 0 or p <= 0 or p > 1, E <= 0

    See Also
    --------
        modify_single(orig, resolvents, seed, outputPath, p, E) for modifying a single file outputPath/{orig}_mod_s{seed}_p{p}.cnf 

    """

    check_non_M_and_p_parameters(orig, resolvents, seed, outputPath, shuffle)

    if not isinstance(p,float) and p is not None:
        raise TypeError("p has to be of type float.")

    if E <= 0:
    	raise ValueError("p must be positive.")

    if not isinstance(E, float) and not isinstance(E, int):
    	raise TypeError("E must be float or int.")

    p = calculate_standard_p_value(p, orig, resolvents, E)

    # Next, we check for Values:
    if p <= 0 or p > 1:
        raise ValueError("It must hold 0 < p <= 1.")

    if not isinstance(M, int):
        raise TypeError("M has to be of type int.")

    if M <= 0:
        raise ValueError("M has to be positive.")


    #### Here, the actual code starts. ####

    # Wir verwenden aus einem technischen Grund ein Random-Objekt:
    # Der Seed, der in generator.main() gesetzt wird, würde ansonsten die Zufallszahlen hier beeinflussen.
    # Damit wären, technisch gesehen, die Zufallszahlen nicht unabhängig.
    # Das Problem wird umgangen, wenn ein Random-Objekt initialisiert wird.

    rng = random.Random()
    rng.seed(seed) 

    # Iterate over the M files to be created.
    # Make sure no seeds are used twice.
    used_seeds = []

    for modfile in range(M):
        # Each file should be created with a random, independent seed.
        seed = rng.randint(1, 2**32 - 1)

        while seed in used_seeds: # seed was already used, try another one.
            seed = rng.randint(1, 2**32 - 1)

        used_seeds.append(seed)
        modify_single(orig, resolvents, seed, outputPath, p, E, shuffle)




def modify_single(orig, resolvents, seed=42, outputPath='./modified', p=None, E=0.1, shuffle=False):
    """This function creates a single file with the filename {outputPath}/orig_mod_s{seed}_p{p}.cnf

    WARNING: This function should normally only be called via modify_instance (e.g. with parameter M = 1).

    See Also
    --------
        modify_instance(orig, resolvents, seed, M, outputPath, p, E)

    """

    check_non_M_and_p_parameters(orig, resolvents, seed, outputPath, shuffle)

    if not isinstance(p,float) and p is not None:
        raise TypeError("p has to be of type float.")

    p = calculate_standard_p_value(p, orig, resolvents, E)

    # Next, we check for Values:
    if p <= 0 or p > 1:
        raise ValueError("It must hold 0 < p <= 1.")

    if not os.path.isdir(outputPath):
        os.makedirs(outputPath)

    
    #rng_single = random.Random()
    #rng_single.seed(seed)
    numpy.random.seed(seed)


    # TODO: Doppelt
    # Make sure, the folder to save the output-files exists.
    # If the folder already exists, it will be overwritten.
    os.makedirs(outputPath, exist_ok=True)

    # Get the DIMACS lines of the original file.
    original_clauses = get_clauses(orig)

    # Get the contents of the resolvents-file.
    resolvent_clauses = get_clauses(resolvents)

    # Sample the clauses.
    sampled_clauses = []
    randoms = numpy.random.rand(len(resolvent_clauses))
    zipped_list = filter(lambda x: x[0] < p, zip(randoms.tolist(), resolvent_clauses))
    for _, res in zipped_list:
        sampled_clauses.append(res)

    # Calculate the content of the file
    new_header = generate_new_header_up_to_p_line(orig, resolvents, seed, p)

    file_name = outputPath + "/" + get_file_name_without_path_without_extension(orig) + f"_mod_s{seed}_p{p}.cnf"

    f = open(file_name, "w")

    for line in new_header:
        f.write(line.rstrip()+"\n")

    # Calculate the p-line
    n = get_parameter_line_from_cnf_file(orig).split(" ")[2]
    no_of_orig_clauses = len(get_clauses(orig))

    f.write(f"p cnf {n} {no_of_orig_clauses + len(sampled_clauses)}\n")

    # Combine all clauses, maybe shuffle, and write to file
    all_clauses = original_clauses + sampled_clauses

    if shuffle:
        numpy.random.shuffle(all_clauses)

    for clause in all_clauses:
        f.write(clause.rstrip()+"\n")

    f.close()



#########################################################################
########################  MINI HELPER FUNCTIONS #########################          
#########################################################################


def check_non_M_and_p_parameters(orig, resolvents, seed, outputPath, shuffle):
    """This function will be called by the functions modify_single and modify_instance to check all non-M-related parameters."""

    if not isinstance(orig, str):
        raise TypeError("orig has to be of type str.")
    if not isinstance(resolvents, str):
        raise TypeError("resolvents has to be of type str.")
    if not isinstance(seed, int):
        raise TypeError("seed has to be of type int.")
    if not isinstance(outputPath, str):
        raise TypeError("outputPath has to be of type str.")
    if not isinstance(shuffle, bool):
        raise TypeError("shuffle has to be a bool.")

    if not os.path.isfile(orig):
        raise FileNotFoundError("The orig file was not found.")
    if not os.path.isfile(resolvents):
        raise FileNotFoundError("The resolvents file was not found.")


@lru_cache(maxsize=100)
def calculate_standard_p_value(p, orig, resolvents, E=0.1):
    """This function checks if p = None.
    If this is the case, p will be calculated according to the `orig`-file and `resolvents`-file, as explained below.
    Otherwise, the passed p will simply be returned (regardless of the given E value).

    Notes
    -----
        If no argument for p was passed, use the standard argument.
        Let X be the random variable that denotes how many resolvents are being added.
        Then X ~ Bin(n', p), where n' is the number of total resolvents.
        Hence, E[X] = n' * p.
        Let m be the number of clauses in the original formula.
        We want our standard argument for p in such a way, that E[X] = m * E holds.
        I.e., we choose p = m / n' * E

    """

    if p is None:       
        no_of_orig_clauses = len(get_clauses(orig))
        no_of_resolvents = len(get_clauses(resolvents))    
        return min(no_of_orig_clauses / no_of_resolvents * E, 1.0)
    else:
        return p 


@lru_cache(maxsize=100)
def get_header(filepath):
    """Returns the header of a specified file as a list of strings.
    The header are all lines starting with 'c' (comment line) or 'p' until a line starts with neither."""

    lines = []
    with open(filepath, 'r') as f:
        line = f.readline()
        while line and (line.startswith("c") or line.startswith("p")):
            lines.append(line)
            line = f.readline()
    return lines



def get_parameter_line_from_cnf_file(filepath):
    return get_header(filepath)[-1]


@lru_cache(maxsize=100)
def get_clauses(filepath):
    with open(filepath, 'r') as f:
            lines = f.readlines()
    clauses = []
    for line in lines:
        if not (line.startswith("c") or line.startswith("p")):
            clauses.append(line)

    return clauses



def get_file_name_without_path_without_extension(path):
    return os.path.splitext(os.path.basename(path))[0]



def generate_new_header_up_to_p_line(origFile, resFile, seed, p):
    # TODO: Problems: What if the extensions are different.
    # TODO: What if a file uses two dots?

    no_of_resolvents = len(get_clauses(resFile))
    original_cnf_file = get_file_name_without_path_without_extension(origFile) + ".cnf"
    resolvent_file = get_file_name_without_path_without_extension(resFile) + ".resolvents"

    new_header = ["c Modified by xyzFancyModifier\n",
    f"c Used with seed {seed} and p {p}\n",
    f"c Sampled from {no_of_resolvents} resolvents\n",
    f"c Original cnf file {original_cnf_file}\n",
    f"c Resolvent file {resolvent_file}\n"]

    for entry in get_header(origFile)[:-1]:
        new_header.append(entry)

    return new_header



#########################################################################
######################  if __name__ == '__main__' #######################          
#########################################################################

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-orig", default=None, help="Specifies the path to the original cnf-file.")
    parser.add_argument("-resolvents", default=None, help="Specifies the path the the resolvents-file from where the clauses are sampled.")
    parser.add_argument("-seed", type=int, default=42, help="Specifies the seed to initalize the random number generator responsible for sampling the resolvents.")
    parser.add_argument("-M", type=int, default=5000, help="Specifies how many new files are generated.")
    parser.add_argument("-outputPath", default="./modified", help="Specifies the output path to save the generated new cnf-files.")
    parser.add_argument("-p", type=float, default=None, help="Specifies the propbability for adding each resolvent.")
    parser.add_argument("-E", type=float, default=0.1, help="Specifies the propbability for adding each resolvent w.r.t. the number of original clauses.")
    parser.add_argument("--shuffle", default=False, action="store_true" , help="Shuffle the clauses before writing to the file.")

    args = parser.parse_args()

    modify_instance(orig=args.orig, resolvents=args.resolvents, seed=args.seed, M=args.M, outputPath=args.outputPath, p=args.p, E=args.E, shuffle=args.shuffle)