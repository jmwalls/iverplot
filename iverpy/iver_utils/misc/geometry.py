import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# point and line
x = np.arange (-10.,10.,1.)
y = (1./2)*x + 3.

x0 = np.array ([[x[7]],[y[7]]])
x1 = np.array ([[x[-7]],[y[-7]]])

r0, r1 = 3., 5.

# solve

# point on line between two centers
dx = x1-x0
D = np.linalg.norm (dx)
t = (r0**2 - r1**2 + D**2)/(2*D**2)
xl = x0 + t*dx

# intersection points
tangent = dx/D
normal = np.dot (np.array ([[0.,-1.],[1.,0.]]), tangent)

l0 = np.linalg.norm (xl-x0)
h = (r0**2 - l0**2)**(1./2)

xp0 = xl + h*normal
xp1 = xl - h*normal

print np.linalg.norm (xp0-x0) - r0
print np.linalg.norm (xp1-x0) - r0

print np.linalg.norm (xp0-x1) - r1
print np.linalg.norm (xp1-x1) - r1


# plot everything
fig = plt.figure ()
ax = fig.add_subplot (111)

# draw lines
ax.plot (x, y, 'b-', lw=2)
ax.plot (x0[0], x0[1], '*', mfc='g', mec='g', ms=10)
ax.plot (x1[0], x1[1], '*', mfc='r', mec='r', ms=10)

# draw circles
ax.add_patch (Circle (x0, r0, color='g', fill=False, lw=2))
ax.add_patch (Circle (x1, r1, color='r', fill=False, lw=2))

ax.plot (xl[0], xl[1], '.', mfc='w', mec='k', ms=10, mew=3)
ax.plot (xp0[0], xp0[1], 'kx', ms=5, mew=3)
ax.plot ([xp0[0],xl[0]], [xp0[1],xl[1]], 'k')
ax.plot (xp1[0], xp1[1], 'kx', ms=5, mew=3)
ax.plot ([xp1[0],xl[0]], [xp1[1],xl[1]], 'k')

ax.axis ('equal')
ax.grid ()

plt.show ()
