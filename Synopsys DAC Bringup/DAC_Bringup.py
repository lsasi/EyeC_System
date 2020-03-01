#!/usr/bin/env python3

import time
import copy
import eyec_gen1_py as eyec
import csv
from matplotlib import pyplot as plt
import numpy as np
from lecroy_scope import lecroy_scope


def negtohex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return val


def padhexa(s, pad):
    return '0x' + s[2:].zfill(pad)


def clearBit(int_type, offset):
    mask = ~(1 << offset)
    return (int_type & mask)


# g = 7
#
#
# data = []
# ind = 0
# for i in range(2048):
#     data.append(padhexa(hex(ind), 4) + hex(ind+1)[2:].zfill(4))
#     ind += 2
#
# clb = 0
# data_mask = []
# ind = 0
# for i in range(2048):
#     data_mask.append(padhexa(hex(clearBit(ind, clb)), 4) + hex(clearBit(ind+1, clb))[2:].zfill(4))
#     ind += 2
#
#
# f = []
# for d in data_mask:
#     f.append(int(d, 16))


# ############## LOAD SECTION ################
# plt.close()
# client.tx_stop()
# clb =0
# data_mask = []
# ind = 0
# for i in range(512):
#     for j in range(14):
#         data_mask.append(padhexa(hex(clearBit(ind, clb)),4) + hex(clearBit(ind+1, clb))[2:].zfill(4))
#     ind += 32
# f = []
# for d in data_mask:
#     f.append(int(d, 16))
# client.tx_set_chirp(f, 0)
# plt.plot(f)


def write_chirp_from_file(filename):
    ############### LOAD CHIRP FROM CSV ########################################
    rr = []
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            rr.append(row)

    fi = []
    for w in range(rr.__len__()):
        fi.append(int(rr[w][0], 16))
    return fi


def split_data_to_bits(rr, two_words=False):
    ##################### SPLIT DATA TO BITS ###############################
    t = []
    for j in range(12):
        tt = []
        for i in range(rr.__len__()):
            tt.append(int((int(rr[i][0][1:4], 16) & 2 ** j) / 2 ** j))
            if two_words:
                tt.append(int((int(rr[i][0][5:8], 16) & 2 ** j) / 2 ** j))
        t.append(tt)
    return t


def remove_glitch(t):
    rt = copy.deepcopy(t)
    z = []
    for w in rt:
        for i in range(w.__len__() - 2):
            if w[i] < w[i + 1] > w[i + 2]:
                w[i + 1] = 0
            if w[i] > w[i + 1] < w[i + 2]:
                w[i + 1] = 1
        z.append(w)

    dd = []
    for e in range(z[0].__len__()):
        da = ''
        for i in range(z.__len__()):
            da += str(z[11 - i][e])
        dd.append(da)

    gh = []
    for i in range(dd.__len__()):
        gh.append(int(dd[i], 2))

    in_fil = []
    ind = 0
    for i in range(int(gh.__len__() / 2)):
        in_fil.append(int(str(padhexa(negtohex(gh[ind], 12), 4)) + str(padhexa(negtohex(gh[ind + 1], 12), 4)[2:]), 16))
        ind += 2


def shifted_data(data, bit, shift):
    shifted_da = []
    for i in range(data.__len__()):
        if i != bit:
            shifted_da.append(data[i])
        else:
            shifted_da.append(rotate(data[i], shift))
    return s(shifted_da), shifted_da


def rotate(l, n):
     return l[n:] + l[:n]


######## GENERATE SINEWAVE ################
def generate_sinewave(frequency=20e3, Fs=160e6, periods=1, shift=np.pi/2, max_amp=2047, sample_first=False):
    sample = 2 * periods * Fs / frequency
    x = np.divide(np.arange(sample), 2)
    y = (max_amp * np.sin(shift + 2 * np.pi * frequency * x / Fs)).astype(int)

    g = []
    for i in range(len(y)):
        g.append(padhexa(negtohex(y[i], 12), 4))

    z = []
    z_hex = []
    ind = 0
    for i in range(int(g.__len__() / 2)):
        z_hex.append(g[ind + 1][3:] + g[ind][3:])
        if sample_first:
            z.append(int(g[ind + 1][2:] + g[ind][2:], 16))
        else:
            z.append(int(g[ind][2:] + g[ind + 1][2:], 16))
        ind += 2
    f = extract_bit(z)
    return z, z_hex, f


def extract_bit(z):
    t_0_11 = []
    for j in range(12):
        tt = []
        for i in range(z.__len__()):
            tt.append(int((z[i] & 2 ** j) >> j))
        t_0_11.append(tt)
    t_12_27 = []
    for j in range(12):
        ff = []
        for i in range(z.__len__()):
            ff.append(int((z[i] & 2 ** (16 + j)) / 2 ** (16 + j)))
        t_12_27.append(ff)

    lst = [0] * t_12_27[0].__len__()
    f = []
    for i in t_0_11:
        f.append(i)
    for i in range(4):
        f.append(lst)
    for i in t_12_27:
        f.append(i)
    for i in range(4):
        f.append(lst)
    return f


def set_chirp(data):
    client.tx_stop()
    time.sleep(0.5)
    client.tx_set_chirp(data, 0)
    client.write_uint32(eyec.address_space_t.lw, 0x30038, data.__len__()-1)


def s(data):
    dd = []
    for i in range(data[0].__len__()):
        da = ''
        for e in range(data.__len__()):
            da += str(data[data.__len__() - e - 1][i])
        dd.append(da)
    gh = []
    for i in range(dd.__len__()):
        gh.append(int(dd[i], 2))
    return gh


def plot_rx_data(data_len=4096*20):
    client.rx_capture(int(data_len * 2), int(data_len * 2), 0)
    time.sleep(2)
    fg = client.read_block(eyec.address_space_t.reserved, 0, int(data_len / 2))
    w = []
    for i in fg:
        w.append(twos_comp(i & 0xfff, 12))
        w.append(twos_comp((i & 0xfff0000) >> 16, 12))
    return w


def split_raw_samples(fg):
    w = []
    for i in fg:
        w.append(twos_comp(i & 0xfff, 12))
    return w


def get_rx_samples(data_len=4096*100):
    client.rx_capture(int(data_len * 2), int(data_len * 2), 0)
    time.sleep(2)
    rx_raw = split_raw_samples(client.read_block(eyec.address_space_t.reserved, 0, int(data_len / 2)))
    rx_ref = split_raw_samples(client.read_block(eyec.address_space_t.reserved, data_len * 2, int(data_len / 2)))
    rx_events = split_raw_samples(client.read_block(eyec.address_space_t.reserved, 2 * data_len * 2, int(1024 * 640)))
    return [rx_raw, rx_ref, rx_events]


def get_from_file(sample_first=True):
    rr = []
    with open('/home/administrator/Documents/MATLAB/Lior/g.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            rr.append(float(row[0]))
    y = np.asarray(np.multiply(rr, 2 ** 11), int)

    g = []
    for i in range(len(y)):
        g.append(padhexa(negtohex(y[i], 12), 4))
    z = []
    z_hex = []
    for i in range(int(g.__len__() / 2)):
        z_hex.append(g[i + 1][3:] + g[i][3:])
        if sample_first:
            z.append(int(g[i + 1][2:] + g[i][2:], 16))
        else:
            z.append(int(g[i][2:] + g[i + 1][2:], 16))

    return z, z_hex, y


def write_csv(name, data):
    arr = []
    for i in range(data[0].__len__()):
        arr1 = []
        for j in range(data.__len__()):
            arr1.append(data[j][i])
        arr.append(arr1)

    with open('{0}.csv'.format(name), 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(['time', 'channel 3', 'channel 4', 'math'])
        for i in arr:
            writer.writerow(i)


tim = []
c3 = []
c4 = []
f1 = []
# with open('/home/administrator/PycharmProjects/TEMP/500KHz_Short.csv', newline='') as csvfile:
#     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
#     for row in spamreader:
#         try:
#             tim.append(float(row[0][1:-1]))
#             c3.append(float(row[1][1:-1]))
#             c4.append(float(row[2][1:-1]))
#             f1.append(float(row[3][1:-1]))
#         except:
#             pass

#
client = eyec.client_t()
client.connect('143.185.124.58')
data = generate_sinewave(frequency=20e3, periods=1, shift=0, sample_first=False)
frequency = [100e3, 500e3, 1e6, 2e6, 5e6, 10e6, 20e6]
scope = lecroy_scope()
for f in frequency:
    data = generate_sinewave(frequency=f, periods=1, shift=0, sample_first=False)
    scope.set_trigger_mode('normal')
    set_chirp(data[0])
    time.sleep(2)
    scope.set_trigger_mode('stopped')
    time.sleep(1)
    c3_x, c3_y = scope.get_channel("c3")
    c4_x, c4_y = scope.get_channel("c4")
    f1_x, f1_y = scope.get_channel("f1")
    write_csv(str(int(f/1000)) + 'KHz_Short', [c3_x, c3_y, c4_y, f1_y])


# f = []
# f.append(int('0fff0000', 16))
# for i in range(8):
#     f.append(int('0fff0fff', 16))
# f.append(int('00000fff', 16))
# for i in range(10):
#     f.append(int('00000000', 16))
#
# shifted_data(data[2], 11, 1)

hex(client.read_uint32(eyec.address_space_t.lw, 0x30004))


####
###

