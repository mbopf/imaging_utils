#!/usr/bin/env python

import os
import glob
import typing
import matplotlib.pyplot as plt
import pydicom
import random

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


random.seed(11)
image_dir = '/slurm_storage/mbopf/data/PedTB/renamed'
full_list = get_file_list(image_dir, "*[AP|PA]*.dcm")
random.shuffle(full_list)
batch_size = 8
batch_num = 1
print(full_list[:8])

fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(18,8))
start = batch_size * (batch_num - 1)
end = batch_size * batch_num
print(batch_num, start, end)
for ax, file in zip(axs.ravel(), full_list[start:end]):
    print(file)
    basename = os.path.basename(file)
    dicom_ds = pydicom.read_file(file, force=True)
    print(dicom_ds)
    pixel_array = dicom_ds.pixel_array
    ishape = pixel_array.shape
    #print(ishape[0])
    ax.set_title(basename)
    ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)
    ax.set_xlabel(ishape[1])
    ax.set_ylabel(ishape[0])
    ax.imshow(pixel_array, cmap=plt.cm.bone) 
    
plt.show()
batch_num += 1

