from utilites import load
import numpy as np

X = load('data/BD2009-2019.json')
s = {}

for year in [ str(x) for x in range(2009,2020) ]:
    for region in X[year].keys():
        for industry in X[year][region].keys():
            if 'компьютерн' in industry or 'программн' in industry:
                try:
                    s[year] += X[year][region][industry]
                except KeyError:
                    s.update({year:X[year][region][industry]})
print(s)
X = list(range(2009,2020))
Y = [ s[str(k)] for k in range(2009,2020) ]

a, b, c = np.polyfit(X,Y,2)

print(2019, a*2019**2 + b*2019 + c)
print(2020, a*2020**2 + b*2020 + c)
print(2021, a*2021**2 + b*2021 + c)
print(2022, a*2022**2 + b*2022 + c)

X += [2020, 2021, 2022]
Y += [a*2020**2 + b*2020 + c, a*2021**2 + b*2021 + c, a*2022**2 + b*2022 + c]