#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

def cimbala_outliers(samples):
  outliers = []
  deltas = []
  umbral = 0

  if (len(samples) > 0):
    still_outliers = True
    print samples

    #calcular la media
    mean = np.mean(samples)

    #calcular el desvio standard
    std_deviation = np.std(samples)

    #calcula el chirimbolo "r"
    thompson_gamma = calculate_thompson_gamma(samples)

    #busca outliers
    umbral = thompson_gamma * std_deviation
    for sample in samples:
      delta = np.absolute(sample - mean)
      deltas.append(delta)
      if (delta > thompson_gamma * std_deviation):
        outliers.append(sample)

    return outliers, deltas, umbral

#Usa los nombres de variables como los que estan en las formulas del paper
def calculate_thompson_gamma(rtts):
  n = len(rtts)

#Studnt, n=999, p<0.05, 2-tail
#equivalent to Excel TINV(0.05,999)
  t_a_2	= stats.t.ppf(1-0.025, n - 2)
  n_root = np.sqrt(n)

  numerator	 = t_a_2 * (n - 1)
  denominator = n_root * np.sqrt( n - 2 + np.power(t_a_2, 2) )

  return numerator / denominator

directory = "msu.ru/"

rtts = []

first = True
with open(directory + 'rrt_lala_dif') as file_data:
    for line in file_data:
        if first:
            first = False
        else:
            rtts.append(float(line[:-1]))

outliers, deltas, umbral = cimbala_outliers(rtts)

umbral = [umbral for _ in range(len(rtts))]

x = [6, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 20, 21]
print(len(x))
print(len(deltas))
print deltas

plt.plot(x, deltas, 'ro', color = 'b', label = "Valor obtenido por cimbala")

plt.plot(x, umbral, color = 'r', label = u"Umbral de detección de outliers")

plt.show()
