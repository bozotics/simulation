import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np

xvals = np.arange(0,910, 0.01) # Grid of 0.01 spacing from 0 to 910 representing ball distance
yvals = np.minimum(0.002*(np.power(np.e,6.7*(1-xvals/850))),1)  #blue, y = min(ae^[b(1-cx)],1)
yvals2 = np.minimum(0.02*(np.power(np.e,6.7*(1-xvals/850))),1)  #orange, increasing a, compresses the graph, scale parallel to y-axis
yvals3 = np.minimum(0.002*(np.power(np.e,10*(1-xvals/850))),1)  #green, increasing b, increases the degree of curvature, 
yvals4 = np.minimum(0.002*(np.power(np.e,6.7*(1-xvals/2000))),1)    #red, increasing c, stretches the graph, scale parallel to x-axis

plt.figure(1)
plt.plot(xvals, yvals)
plt.plot(xvals, yvals2)
plt.plot(xvals, yvals3)
plt.plot(xvals, yvals4) 
plt.title('Graph of offset multiplier against ball distance')
plt.xlabel('Ball Distance')
plt.ylabel('Multiplier')

plt.figure(2)
xvals2 = np.arange(-180,179.99, 0.01) # Grid of 0.01 spacing from 0 to 359.99 representing ball angle
offset = np.maximum(np.minimum(xvals2*1.0,90),-90) #y = max(min(x,90),90), its just a graph of y=x capped at 90 and -90
plt.plot(xvals2, offset) # Create line plot with yvals against xvals
plt.title('Graph of offset against ball angle')
plt.xlabel('Ball Angle (Relative)')
plt.ylabel('Offset')

plt.figure(3)
x = np.arange(0,910, 30) # Grid of 30 spacing from 0 to 910 representing ball distance
y = np.arange(-180,179, 3) # Grid of 3 spacing from 0 to 359 representing ball angle
X, Y = np.meshgrid(x, y)
Z = np.minimum(0.002*(np.power(np.e,6.7*(1-X/850))),1)*np.maximum(np.minimum(Y*1.0,90),-90) #multiplier*offset for each ball distance & angle
ax = plt.axes(projection='3d')
ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                cmap='coolwarm', edgecolor='none')
ax.set_title('Offset Angle Surface')
ax.set_xlabel('Ball Distance')
ax.set_ylabel('Ball Angle')
ax.set_zlabel('Offset Angle')

plt.figure(4)
Z = Y+Z #add final offset angle to each ball angle
ax2 = plt.axes(projection='3d')
ax2.plot_surface(X, Y, Z, rstride=1, cstride=1,
                cmap='coolwarm', edgecolor='none')
ax2.set_title('Robot Angle Surface')
ax2.set_xlabel('Ball Distance')
ax2.set_ylabel('Ball Angle')
ax2.set_zlabel('Robot Angle')

plt.show() # Show the figure
