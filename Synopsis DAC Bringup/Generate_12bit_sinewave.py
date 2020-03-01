import csv
import numpy as np
from matplotlib import pyplot as plt
import os
import sys


def get_array_from_file(filename):
    fre = []
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            fre.append(float(row[0]))

    freq = np.array(fre)
    return freq


def get_file_names(folder):
    dir_names = os.listdir(r'/home/administrator/Documents/MATLAB/Lior/TSW1400 Tones/')
    dir_ = []
    for di in dir_names:
        dir_.append(os.path.join(folder, di))
    full_path = []
    onlyfiles = []
    for i in dir_:
        onlyfiles.append([f for f in os.listdir(i) if os.path.isfile(os.path.join(i, f))])
        for g in onlyfiles[onlyfiles.__len__() - 1]:
            full_path.append(os.path.join(i, g))
    return dir_names, onlyfiles, full_path


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


def negtohex(val, nbits):
  return hex((val + (1 << nbits)) % (1 << nbits))


def padhexa(s, pad):
    return s[2:].zfill(pad)


def main():
    main_dir = r'/home/administrator/Documents/MATLAB/Lior/TSW1400 Tones'
    # main_dir = sys.argv[1]
    # g = 0
    dir_names, onlyfiles, full_path = get_file_names(main_dir)

    try:
        for i in dir_names:
            i += r"_12bit"
            os.mkdir(os.path.join(main_dir, i))
    except:
        print("folder already exist")

    gi = []
    for i in full_path:
        filename, file_extension = os.path.splitext(os.path.basename(i))
        tmp = []
        tmp.append(i)
        tmp.append(os.path.dirname(i) + r'_12bit/' + filename + r'_12bit' + file_extension)
        tmp.append((get_array_from_file(i) // 2 ** 4).astype(int))
        # tmp.append((get_array_from_file(i) * 0.5 // (2 ** 16)).astype(float))
        gi.append(tmp)

    for w in gi:
        with open(w[1], mode='w', newline='') as employee_file:
            employee_writer = csv.writer(employee_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in range(int(w[2].__len__() / 2)):
            # for i in range(int(w[2].__len__())):
                odd = str(padhexa(negtohex(w[2][i], 12), 4))
                even = str(padhexa(negtohex(w[2][i + 1], 12), 4))
                employee_writer.writerow([even + odd])

if __name__ == "__main__":
   main()