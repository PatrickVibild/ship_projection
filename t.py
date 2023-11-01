import matplotlib.pyplot as plt
import numpy as np

xpoints = np.array([-1150.7577671442102, -1193.392592042944, -484.3127808633345, -1141.7541395252306])
ypoints = np.array([-674.5649542359331, -409.8094681998868, -386.7920865924868, -638.648943320662])

plt.plot(xpoints, ypoints, 'o')
plt.xlim([-1200, 0])
plt.ylim([-700, 0])

plt.show()