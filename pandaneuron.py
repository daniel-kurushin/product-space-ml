import numpy as np
import pandas as pd

boats = pd.ExcelFile("boats.xlsx")
boat_prices = boats.parse('Лист1')

D = np.hstack((boat_prices.values[:,1:5], 
               boat_prices.values[:,6:7]) ).astype(np.double)
Y = boat_prices.values[:,5:6].astype(np.int32).flatten()

for i in range(len(D[0])):
    a, b = np.polyfit(
        np.sort(D[:,i]),
        np.linspace(0,1,len(D[:,i])),1
    )
    D[:,i] = D[:,i] * a + b

w = np.zeros((len(D[0]))).astype(np.double)

α =  0.2 
β = -0.4 
σ = lambda x: x

def f(x):
    s = β + np.sum(x @ w)
    return σ(s)

def train():
    global w
    _w = w.copy()
    for x, y in zip(D, Y):
        w += α * (y - f(x)) * x
    return (w != _w).any()
            
while train():
    print(w)

for x, y in zip(D, Y):
    print(x, y, round(f(x)))
