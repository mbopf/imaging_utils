"""
=======
Buttons
=======

Constructing a simple button GUI to modify a sine wave.

The ``next`` and ``previous`` button widget helps visualize the wave with
new frequencies.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import os
import glob
import pydicom

def get_file_list(path: str, wild: str = None) -> list:
    ret_list = []
    if not path.endswith('/'):
        path = path + '/'

    if wild:
        for filename in glob.glob(path + wild):
            ret_list.append(filename)
    else:
        for filename in os.listdir(path):
            ret_list.append(filename)

    return ret_list

files = get_file_list("./", "*.dcm")
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
dicom_ds = pydicom.read_file(files[0], force=True)
pixel_array = dicom_ds.pixel_array
a = ax.imshow(pixel_array, cmap=plt.cm.bone)

def quit(event):
    exit(0)

class Index:
    ind = 0

    def next(self, event):
        self.ind += 1
        ds = pydicom.read_file(files[self.ind], force=True)
        p_array = ds.pixel_array
        ax.imshow(p_array, cmap=plt.cm.bone)
        plt.draw()

    def prev(self, event):
        self.ind -= 1
        ds = pydicom.read_file(files[self.ind], force=True)
        p_array = ds.pixel_array
        ax.imshow(p_array, cmap=plt.cm.bone)
        plt.draw()

"""
freqs = np.arange(2, 20, 3)
print(freqs)

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
t = np.arange(0.0, 1.0, 0.001)
s = np.sin(2*np.pi*freqs[0]*t)
l, = plt.plot(t, s, lw=2)


def quit(event):
    exit(0)

class Index:
    ind = 0

    def next(self, event):
        self.ind += 1
        i = self.ind % len(freqs)
        ydata = np.sin(2*np.pi*freqs[i]*t)
        l.set_ydata(ydata)
        plt.draw()

    def prev(self, event):
        self.ind -= 1
        i = self.ind % len(freqs)
        ydata = np.sin(2*np.pi*freqs[i]*t)
        l.set_ydata(ydata)
        plt.draw()
"""

callback = Index()
axprev = plt.axes([0.59, 0.05, 0.1, 0.075])
axnext = plt.axes([0.7, 0.05, 0.1, 0.075])
axquit = plt.axes([0.81, 0.05, 0.1, 0.075])
bprev = Button(axprev, 'Previous')
bprev.on_clicked(callback.prev)
bnext = Button(axnext, 'Next')
bnext.on_clicked(callback.next)
bquit = Button(axquit, 'Quit')
bquit.on_clicked(quit)

plt.show()

#############################################################################
#    - `matplotlib.widgets.Button`
