#https://youtu.be/ekaWB70qJ8I
from itertools import combinations

def all_combinations(lst):
    for r in range(len(lst) + 1):
        for comb in combinations(lst, r):
            yield comb

lst = [1,2, 3,4,5]
for comb in all_combinations(lst):
    print(comb)
