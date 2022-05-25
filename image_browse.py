import argparse
import os
import glob
import sys
import typing

import matplotlib as mpl
import matplotlib.pyplot as plt
import pydicom
import random

def greeting(name: str) -> str:
    return 'Hello ' + name

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


import itertools
# From Alex Chan https://alexwlchan.net/2018/12/iterating-in-fixed-size-chunks/
def chunked_iterable(iterable, size):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk

def img_browse():
    """
    Image browsing utility.
    """
    parser = argparse.ArgumentParser(description='Browse images')
    parser.add_argument('--file_path', required=True, help='File or directory to process')
    parser.add_argument('--list_dicom', default=False, action='store_true', help='Print full content of DICOM files')
    parser.add_argument('--view_image', default=True, action='store_true', help='Display images')
    parser.add_argument('--glob_str', default=False, help='Unix-style wildcard file pattern')
    parser.add_argument('--grid', default='1,1', help='Image display grid (rows, cols) default="1,1"')
#    parser.add_argument('--batchsize', default=1, help='How many images to display on a page?')
    parser.add_argument('--random', default=False, action='store_true', help='Random shuffle images?')

    opt = parser.parse_args()
    print(f"Arguments = {opt}")

    grid_tuple = tuple(map(int, opt.grid.split(',')))
    print(f'grid_tuple = {grid_tuple}')
    print(f'type(grid_tuple) = {type(grid_tuple)}')

    file_path = opt.file_path
    if not os.path.exists(file_path):
        print(f"ERROR: couldn't open file_path: {file_path}")
        sys.exit()

    if os.path.isfile(file_path):
        basename = os.path.basename(file_path)
        dicom_ds = pydicom.read_file(file_path, force=True)
        if opt.list_dicom:
            print(dicom_ds)
        if opt.view_image:
            fig, ax = plt.subplots()
            pixel_array = dicom_ds.pixel_array
            ishape = pixel_array.shape
            ax.set_title(basename)
            ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)
            ax.set_xlabel(ishape[1])
            ax.set_ylabel(ishape[0])
            ax.imshow(pixel_array, cmap=plt.cm.bone)
            plt.show()
    else:
        plt.ion()
        assert(os.path.isdir(file_path))
        batch_size = grid_tuple[0] * grid_tuple[1]
        print(f'batch_size = {batch_size}')
        batch_num = 1

        full_list = get_file_list(file_path, opt.glob_str)
        fsize = (grid_tuple[1] * 6, grid_tuple[0] * 4)
        print(f'len(full_list) = {len(full_list)}')
        print(f'fsize = {fsize}')
        fig, axs = plt.subplots(grid_tuple[0], grid_tuple[1], figsize=fsize)
        start = batch_size * (batch_num - 1)
        end = batch_size * batch_num
        if len(full_list) % batch_size != 0:
            batches = int(len(full_list)/batch_size) + 1
        cmd = 'n'
        while cmd != 'q':
            for ax, file in zip(axs.ravel(), full_list[start:end]):
                print(batch_num, start, end)
                basename = os.path.basename(file)
                dicom_ds = pydicom.read_file(file, force=True)
                if opt.list_dicom:
                    print(dicom_ds)
                pixel_array = dicom_ds.pixel_array
                ishape = pixel_array.shape
                #print(ishape[0])
                ax.set_title(basename)
                ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)
                ax.set_xlabel(ishape[1])
                ax.set_ylabel(ishape[0])
                ax.imshow(pixel_array, cmap=plt.cm.bone)

            fig.suptitle(f"Batch {batch_num} of {batches}")
            fig.canvas.draw()
            fig.canvas.flush_events()
            cmd = input('"n" for next batch; "q" to quit->')
            print(f'cmd: {cmd}')
            if not cmd.startswith('q') and not cmd.startswith('Q'):
                if cmd.startswith('n') or cmd.startswith('N'):
                    batch_num += 1
                elif cmd.startswith('b') or cmd.startswith('B'):
                    batch_num -= 1

                start = batch_size * (batch_num - 1)
                end = batch_size * batch_num
                if end > len(full_list):
                    end = len(full_list)


if __name__ == '__main__':
    print(f'Backend: {mpl.get_backend()}')
    img_browse()