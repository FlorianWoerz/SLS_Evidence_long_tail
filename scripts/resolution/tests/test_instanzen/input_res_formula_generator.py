
n=14
clause_list = []
last_clause = ""
for i in range(1,n+1):
    last_clause += str(i) + " "
    clause_list.append(f"-{i} 0\n")

clause_list.append(last_clause + "0\n")
with open(f"input_res_{n}.cnf", 'w') as f:
    f.write(f"p cnf {n} {n+1}\n")
    for clause in clause_list:
        f.write(clause)