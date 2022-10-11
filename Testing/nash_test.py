# list1 = [(30, [3, 2, 1, 4]), (40, [3, 4, 1, 2]), (35, [4, 4, 1, 2]), (40, [1, 3, 4, 4]), (35, [3, 4, 2, 1])]
#
# list1.sort(reverse=True, key=lambda x: (x[0], sum(x[1])) )
#
# list1 = list(dict(reversed(list1)).items())[0]
#
# print(list1)
a = [30, 40]

print(a.index(max(a)))
