import formula as form
import clause as clause

def parse_line(line):
    if line.startswith('c') or line.startswith('p'):
        return None

    line = line.strip()
    variables = line.split(' ')
    if '0' not in variables:
        return None

    variables = list(map(lambda x: int(x), variables))
    variables.remove(0)
    if variables == []:
        return None
    return variables

def parse_length(lines):
    for line in lines:
        if line.startswith('p'):
            return (int(line.split()[2]), int(line.split()[3])) # return n_vars and m_clauses
    print("Error: No problem definition.")
    quit()

def parse_lines(lines):
    formula = form.Formula()
    (n_vars, m_clauses) = parse_length(lines)
    formula.set_n_vars(n_vars)
    for line in lines:
        variables = parse_line(line)
        if variables != None:
            c = clause.Clause()
            c.set_variables(variables)
            formula.add_clause(c)
    return (formula, n_vars, m_clauses)


def parse_formula(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        return parse_lines(lines)


        