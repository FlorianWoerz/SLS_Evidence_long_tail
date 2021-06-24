import pyximport; pyximport.install(setup_args={})

import formula
import more_resolution_formula
import clause
import parse_formula

import argparse
from os.path import isdir, join, basename



def write_resolvents_file(formula, output_path, converge, more, max_length, times, output_list):
    """
    Writes the resolvents of `formula`.cnf as specified in `output_list` to 
    the file `formula`.resolvents in the folder `output_path`.
    The header of this file will contain the information specified via
    `max_length`, `converge`, and `more`/`times`.
    """
    if isdir(output_path):
        suffix = basename(formula).replace(".cnf", "") + ".resolvents"
        output_path = join(output_path, suffix)

    with open(output_path, 'w') as f:
        f.write(f"c Max length {max_length}\n")
        if converge:
            f.write("c To convergence\n")
        elif more:
            f.write(f"c To level {times}\n")
        else:
            f.write("c To level 1\n")

        for clause in output_list:
            f.write(clause)



def resolve_and_write(formula, output_path=None, converge=False, more=None, max_length=4, times=2):
    cnf, n_vars, _ = parse_formula.parse_formula(formula)
    output_list = []

    if converge:
        cnf = more_resolution_formula.MoreResolutionFormula(form=cnf)
        old_n_clauses = cnf.n_clauses
        result_dict = cnf.resolve_to_convergence(max_length=max_length)

        for i in result_dict:
            output_list.extend([str(x) for x in result_dict[i]])

    else:
        if more:
            cnf = more_resolution_formula.MoreResolutionFormula(form=cnf)
            result_dict = cnf.resolve_multiple_times(times=times+1, max_length=max_length)
        else:
            result_dict = {1: cnf.resolve_all(max_length=max_length)}

        for i in result_dict:
            output_list.extend([str(x) for x in result_dict[i]])

    
    if output_path is not None:
        write_resolvents_file(formula, output_path, converge, more, max_length, times, output_list)
    else:
        print(output_list)

    return output_list



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--formula', default='orig.cnf')
    parser.add_argument('-o', '--output_path', default=None, type=str, help="If specified, the resolvents are written in this file.")
    parser.add_argument("--more", default=False, action="store_true" , help="More resolution rounds?")
    parser.add_argument("--converge", default=False, action="store_true" , help="Perform resolution until no new clauses are added?")
    parser.add_argument('-t', '--times', default=2, type=int, help="The number of resolution rounds. Only used if --more is used.")
    parser.add_argument('-l', '--max_length', default=4, type=int, help="The maximal length.")    
    args = parser.parse_args()

    resolve_and_write(args.formula, args.output_path, args.converge, args.more, args.max_length, args.times)
