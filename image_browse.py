import argparse
import os
import sys
import glob
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import pydicom
from PIL import Image
from matplotlib.widgets import Button


PIL_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tif', '.tiff']
ALL_EXTENSIONS = PIL_EXTENSIONS + ['.dcm']

# Given a filename, use the extension to determine if it is an image
def is_img_ext(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in ALL_EXTENSIONS


# Give a path and optional glob string, return the list of files in
# the directory. Also, optionally filter by image extension.
def get_file_list(path: str, glob_str: str = None, filter_images=True) -> list:
    if os.path.isfile(path):
        if glob_str:
            print('Warning: glob string ignored for single file input')
        return [path]

#    if not glob_str:
#        glob_str = "*.*"

    if not path.endswith('/'):
        path += '/'
    filelist = glob.glob(path + glob_str)

    if filter_images:
        filelist = [file for file in filelist if is_img_ext(file)]

    return filelist


def quitit(event):
    exit(0)

def get_image(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.dcm':
        dicom_data = pydicom.read_file(filename)
        im = dicom_data.pixel_array
        im_shape = im.shape
    elif ext in PIL_EXTENSIONS:
        im = Image.open(filename)
        im_shape = im.size
    else:
        print(f"file not in {PIL_EXTENSIONS}")

    return im, im_shape


class Chunk:

    def __init__(self, filelist, chunk_size, fig, axs):
        self.chunk_idx = 1
        self.filelist = filelist
        self.chunk_size = chunk_size
        self.fig = fig
        self.axs = axs
        self.num_chunks = math.ceil(len(filelist)/chunk_size)

    def get_chunk(self):
        start = self.chunk_size * (self.chunk_idx - 1)
        end = self.chunk_size * self.chunk_idx
        print(f'start: {start}; end: {end}; self.filelist: {self.filelist}')
        if end > len(self.filelist):
            end = len(self.filelist)

        return self.filelist[start:end]

    def display_chunk(self):
        curr_chunk = self.get_chunk()
        print("In display_chunk():")
        print(f"axs: {self.axs}; curr_chunk: {curr_chunk}")
        for ax, file in zip(self.axs, curr_chunk):
            basename = os.path.basename(file)
            img, im_shape = get_image(file)
            ax.set_title(basename)
            ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)
            ax.set_xlabel(im_shape[1])
            ax.set_ylabel(im_shape[0])
            ax.imshow(img, cmap=plt.cm.bone)

        if len(curr_chunk) < self.chunk_size:
            for ax in self.axs[len(curr_chunk):self.chunk_size]:
                ax.clear()

        self.fig.suptitle(f"Batch {self.chunk_idx} of {self.num_chunks}")
#        self.fig.canvas.draw()
#        self.fig.canvas.flush_events()

    def next(self, event):
        if self.chunk_idx < self.num_chunks:
            self.chunk_idx += 1
            self.display_chunk()
        #else: print message?

    def prev(self, event):
        if self.chunk_idx > 1:
            self.chunk_idx -= 1
            self.display_chunk()
        #else: print message?


def img_browse():
    """
    Image browsing utility.
    """
    parser = argparse.ArgumentParser(description='Browse images')
    parser.add_argument('--file_path', required=True, help='File or directory to process')
    parser.add_argument('--list_dicom', default=False, action='store_true', help='Print full content of DICOM files')
    parser.add_argument('--view_image', default=True, action='store_true', help='Display images')
    parser.add_argument('--glob_str', default="*.*", help='Unix-style wildcard file pattern')
    parser.add_argument('--grid', default='1,1', help='Image display grid (rows, cols) default="1,1"')
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

    plt.ion()
    batch_size = grid_tuple[0] * grid_tuple[1]
    print(f'batch_size = {batch_size}')

    full_list = get_file_list(file_path, opt.glob_str)
    fsize = (grid_tuple[1] * 6, grid_tuple[0] * 4)
    print(f'len(full_list) = {len(full_list)}')
    print(f'fsize = {fsize}')
    fig, axs = plt.subplots(grid_tuple[0], grid_tuple[1], figsize=fsize)
    if grid_tuple[0] == 1 and grid_tuple[1] == 1:
        axes = [axs]
    else:
        axes = list(axs.ravel())

    plt.subplots_adjust(bottom=0.2)

    callback = Chunk(full_list, batch_size, fig, axes)
    axprev = plt.axes([0.59, 0.05, 0.1, 0.075])
    axnext = plt.axes([0.7, 0.05, 0.1, 0.075])
    axquit = plt.axes([0.81, 0.05, 0.1, 0.075])
    bprev = Button(axprev, 'Previous')
    bprev.on_clicked(callback.prev)
    bnext = Button(axnext, 'Next')
    bnext.on_clicked(callback.next)
    bquit = Button(axquit, 'Quit')
    bquit.on_clicked(quitit)
    print("before call to 'display_chunk'")
    callback.display_chunk()
#    fig.canvas.draw()
#    fig.canvas.flush_events()
    plt.ioff()
    plt.show()


if __name__ == '__main__':
    print(f'Backend: {mpl.get_backend()}')
    img_browse()