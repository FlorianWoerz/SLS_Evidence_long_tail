original_clauses = []

fobj = open("PHP32.txt", "r")

for line in fobj:
    clause = []
    line = line.strip() # remove "\n"
    line = line.strip(" 0")
    line = line.split(" ")
    for lit in line:
        clause.append(int(lit))
    original_clauses.append(clause)

fobj.close()

print(original_clauses)

clauses_to_resolve = original_clauses
level = 1

condition = True


while condition:
    found_clauses_in_level = False
    resolvents_of_level = []
    for i in range(len(clauses_to_resolve)):
        for j in range(len(clauses_to_resolve)):
            for lit in clauses_to_resolve[i]:
                if -lit in clauses_to_resolve[j]:
                    res = clauses_to_resolve[i] + clauses_to_resolve[j]
                    res.remove(lit)
                    res.remove(-lit)
                    if len(res) == len(set(res)):
                        #found_clauses_in_level = True
                        resolvents_of_level.append(res)
            for lit in clauses_to_resolve[j]:
                if -lit in clauses_to_resolve[i]:
                    res = clauses_to_resolve[i] + clauses_to_resolve[j]
                    res.remove(lit)
                    res.remove(-lit)
                    if len(res) == len(set(res)):
                        #found_clauses_in_level = True
                        resolvents_of_level.append(res)

    for res in resolvents_of_level:
        if res not in clauses_to_resolve:
            found_clauses_in_level = True
            clauses_to_resolve.append(res)
    if found_clauses_in_level == False:
        print("Done!")
        condition = False
        break

print(clauses_to_resolve)




