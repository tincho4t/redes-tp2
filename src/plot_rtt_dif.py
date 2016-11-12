import numpy as np
import matplotlib.pyplot as plt

directory = "msu.ru/"

rtts = []

first = True
with open(directory + 'rrt_lala_dif') as file_data:
    for line in file_data:
        if first:
            first = False
        else:
            rtts.append(float(line[:-1]))

mean = [np.mean(rtts) for _ in range(len(rtts))]

x = [6, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 20, 21]
print(len(x))
print(len(rtts))

plt.plot(x, rtts, 'ro', color = 'b', label = "Diferencia de rtt")

plt.plot(x, mean, color = 'r', label = "Promedio")

plt.show()
