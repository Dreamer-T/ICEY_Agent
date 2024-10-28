import matplotlib.pyplot as plt
import numpy as np
x = np.linspace(1, 80, 80)
s = ""
with open("fig.txt", "r") as f:
    s = f.readlines()
m = []
m1 = [0]
a = []
a1 = [0]
for i in range(len(s)):
    t = s[i].split(":")[1]
    m.append(float(t.split("|")[0]))
    m1.append(m[i]+m1[i])
    a.append(int(t.split("|")[1][0:-1]))
    a1.append(a[i]+a1[i])
y1 = m1
y2 = a1
plt.figure()
plt.subplot(2, 1, 1)
plt.subplot(2, 1, 1)
plt.plot(x, y1[1:])
plt.xlabel("step")
plt.ylabel("reward")
plt.title("move")
plt.subplot(2, 1, 2)
plt.plot(x, y2[1:])
plt.xlabel("step")
plt.ylabel("reward")
plt.title("action")
plt.show()
