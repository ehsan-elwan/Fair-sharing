from itertools import chain, combinations, permutations
from math import factorial
import json


class Pool:
    def __init__(self, json_input):
        with open(json_input) as json_file:
            data = json.load(json_file)
            route = data['route']
            self.costPerKm = data['costPerKm']
            self.Passengers = data['Passengers']
            self.depCity = route['depCity']
            self.arrCity = route['arrCity']
            self.stops = route['stops']
            self.__route = [self.depCity] + self.stops + [self.arrCity]
            self.distance = route['distance']
            tmp = self.__build_distance_dict()
            self.distance = tmp
            self.pro_allocation = dict()
            self.sep_allocation = dict()
            self.__proportional_allocation()
            self.__allocation_by_separation()
            self.pro_core = {"in": True, "res": []}
            self.sep_core = {"in": True, "res": []}
            self.sh_values = dict()
            self.__sh_values()

    def __build_distance_dict(self):

        new_dict = dict()
        for c in self.__route:
            new_dict[c] = {}
            for k in self.__route:
                new_dict[c][k] = 0

        tmp = []
        for a in self.distance:
            for b in self.distance[a]:
                new_dict[a][b] = self.distance[a][b]
                new_dict[b][a] = self.distance[a][b]
            tmp.append(list(new_dict[a].values()))
        tmp.append(list(new_dict[self.arrCity].values()))

        rg = round(len(tmp) / 2)

        for a in range(rg + 1):
            index_a = 0
            index_b = rg + a
            for k in range(rg + 1 - a):
                tmp[index_a][index_b] = tmp[index_a + 1 + a][index_b] + tmp[index_a][index_b - 1]
                tmp[index_b][index_a] = tmp[index_a + 1 + a][index_b] + tmp[index_a][index_b - 1]
                index_a += 1
                index_b += 1

        keys = new_dict.keys()
        for index, city in enumerate(new_dict, start=0):
            new_dict[city].update(dict(zip(keys, tmp[index])))

        return new_dict

    def total_cost(self):
        return self.distance[self.depCity][self.arrCity] * self.costPerKm

    def stand_alone_cost(self, p):
        return self.distance[self.depCity][self.Passengers[p]] * self.costPerKm

    def __proportional_allocation(self):
        stand_alone_sum = 0
        for ps in self.Passengers:
            stand_alone_sum += self.stand_alone_cost(ps)
        for p in self.Passengers:
            self.pro_allocation[p] = self.total_cost() * self.stand_alone_cost(p) / stand_alone_sum

    def prop_alloc_satisfies_stand_alone(self):
        for p in self.Passengers:
            if self.pro_allocation[p] > self.stand_alone_cost(p):
                return False
        return True

    def __all_subsets_per(self, subset):
        return map(list, chain(
            *map(lambda x: combinations(self.Passengers.keys(), x), range(subset, subset + 1))))

    def cost_per(self, nb_passengers):
        res = []
        tmp = self.__all_subsets_per(nb_passengers)
        for group in tmp:
            mx = self.distance[self.depCity][self.Passengers[group[0]]] * self.costPerKm
            sum_prop = 0
            sum_sep = 0
            for p in group:
                sum_prop += self.pro_allocation[p]
                sum_sep += self.sep_allocation[p]
                test = self.distance[self.depCity][self.Passengers[p]] * self.costPerKm
                if mx < test:
                    mx = test
            if sum_prop > mx:
                self.pro_core.update({"in": False})
                st = ",".join(group)
                st += " spent together " + str(
                    sum_prop) + " according to the proportional allocation while they would pay only " + str(
                    mx) + " if sharing another car on their own."
                self.pro_core["res"].append(st)
            res.append([group, mx])
            if sum_sep > mx:
                self.sep_core.update({"in": False})
                st = ",".join(group)
                st += " spent together " + str(
                    sum_sep) + " according to the separation allocation while they would pay only " + str(
                    mx) + " if sharing another car on their own."
                self.sep_core["res"].append(st)
        return res

    def __allocation_by_separation(self):
        passes = len(self.Passengers)
        sub = 0
        carry = 0
        for index, p in enumerate(self.Passengers, start=0):
            dist_to_share = abs(self.distance[self.depCity][self.Passengers[p]] - sub)
            tmp = dist_to_share / (passes - index)
            res = carry + tmp
            carry = res
            sub = self.distance[self.depCity][self.Passengers[p]]
            self.sep_allocation[p] = res * self.costPerKm

    def __order_agents(self):
        tmp = dict()
        for p in self.Passengers:
            tmp[self.stand_alone_cost(p)] = p
        t = sorted(tmp.keys(), reverse=True)
        for order, value in enumerate(t, start=1):
            key = tmp[value]
            tmp[value] = order
            tmp[key] = tmp.pop(value)
        return tmp

    def __sh_values(self):
        t = list(permutations(self.Passengers.keys()))
        n = len(self.Passengers)
        res = dict()
        order = self.__order_agents()
        # Building Shapley table with default values of 0
        for group in t:
            c = "".join(group)
            res[c] = {}
            for p in self.Passengers.keys():
                res[c][p] = 0
        # Filling Shapley table
        for group in res.keys():
            current_value = 0
            current_order = n
            for p in group:
                if current_value == self.total_cost():
                    break
                else:
                    if order[p] <= current_order:
                        tmp = self.distance[self.depCity][self.Passengers[p]] * self.costPerKm
                        res[group][p] = abs(tmp - current_value)
                        current_value += res[group][p]
                        current_order = order[p]
        # Display Shapley table:
        # for index, x in enumerate(res, start=0):
        #     print(index, x, res[x])
        #     print()

        # Computing Shapley value for each passenger
        fact_n = factorial(n)
        for p in self.Passengers:
            tmp_sum = 0
            for group in res.keys():
                tmp_sum += res[group][p]
            self.sh_values[p] = tmp_sum / fact_n

    def __test_user_allocation(self, input_allocation):
        stand_alone_test = True
        for p in input_allocation:
            if input_allocation[p] > self.stand_alone_cost(p):
                stand_alone_test = False
                print("Passenger", p,
                      "would prefer to travel alone, it'll cost him more to travel with the group than by him self")
                print("Stand-alone cost for passenger", p, ":", self.stand_alone_cost(p), "<", input_allocation[p])
                print("-" * 10)
        print("*" * 18)
        if stand_alone_test:
            print("This allocation satisfy the stand alone test")
        proportional_test = True
        for p in input_allocation:
            if input_allocation[p] > self.pro_allocation[p]:
                proportional_test = False
                print("Passenger", p,
                      "won't approve the proportional allocation", end=" ")
                print("it'll cost him more to travel with the group than by him self")
                print("Stand-alone cost for passenger", p, ":", self.stand_alone_cost(p), "<", input_allocation[p])
                print("-" * 10)
        print("*" * 18)
        if proportional_test:
            print("This allocation satisfy the proportional allocation test")

    def get_user_input(self):
        user_input = dict()
        for p in self.Passengers:
            user_input[p] = float(input("Enter value for passgenger " + p + ": "))
        return self.__test_user_allocation(user_input)


if __name__ == "__main__":
    pass
