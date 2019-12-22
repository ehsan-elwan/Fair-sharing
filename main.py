from sys import argv
from CarPooling import *

data = "data.json"
if len(argv) > 1:
    data = argv[1]

r = Pool(json_input=data)
print("* Stand-alone cost per passenger:")
for p in r.Passengers:
    print("\t-", p, "=", r.stand_alone_cost(p))

print()
print("* Proportional allocation per passenger:")
total_cost = r.total_cost()

for p in r.Passengers:
    print("\t-", p, "=", r.pro_allocation[p])
satisfies_stand_alone = r.prop_alloc_satisfies_stand_alone()
print("\t- Allocation satisfies stand alone test:", satisfies_stand_alone)
print()
print("* Total cost:", total_cost)
print()
print("* Costs per different combination:")
for i in range(2, len(r.Passengers)):
    costs = r.cost_per(i)
    print("\t-", "Costs per", i, "are:")
    for x in costs:
        print("\t" * 2, x[0], "=", x[1])
    print()
print("* Proportional allocation in the core:", r.pro_core["in"])
for reason in r.pro_core["res"]:
    print("\t-", reason)
print()
print("* Allocation by separation:")
for p in r.Passengers:
    print("\t-", p, "=", r.sep_allocation[p])
print()
print("* separation allocation in the core:", r.sep_core["in"])
for reason in r.sep_core["res"]:
    print("\t-", reason)
print()
print("* The Shapley solution:")
for p in r.Passengers:
    print("\t-", p, "=", r.sh_values[p])
print()
print("* Would you like to propose an allocation? (y/n) ")
test = input()
if test.lower().startswith('y'):
    tmp = r.get_user_input()
