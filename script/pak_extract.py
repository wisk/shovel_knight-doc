#!/usr/bin/python

import os, errno
import sys
import struct

def read_string(data, off):
    res = ''
    while True:
        char = data[off]
        if char == '\x00':
            return res
        off += 1
        res += char

def pak_extract(path):
    pak_data = open(path, 'rb').read()

    is_conv, entries_no, data_off, unk0, name_off, unk =\
        struct.unpack('IIIIII', pak_data[0:4 * 6])
    print 'name: %s, entries_no: %08x, data_off: %08x, name_off: %08x' %\
        (path, entries_no, data_off, name_off)

    pak_entries = []

    for i in range(entries_no):
        data_curr_off = struct.unpack('I', pak_data[data_off + i * 8:data_off + i * 8 + 4])[0]
        name_curr_off = struct.unpack('I', pak_data[name_off + i * 8:name_off + i * 8 + 4])[0]

        if i != entries_no - 1:
            data_next_off = struct.unpack('I', pak_data[data_off + (i + 1) * 8:data_off + (i + 1) * 8 + 4])[0]
            #name_next_off = struct.unpack('I', pak_data[name_off + (i + 1) * 8:name_off + (i + 1) * 8 + 4])[0]
        else:
            data_next_off = name_off
            #name_next_off = -1

        entry_size = struct.unpack('I', pak_data[data_curr_off:data_curr_off + 4])[0]
        entry_data = pak_data[data_curr_off + 0x20:data_next_off]
        entry_name = read_string(pak_data, name_curr_off)

        pak_entries.append((entry_name, entry_data))

    return pak_entries


if len(sys.argv) < 4 or sys.argv[1] != '--out':
    print '%s --out <folder> <file.pak>+' % sys.argv[0]
    exit(-1)

#http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


for arg in sys.argv[3:]:


    paks_entries = pak_extract(arg)

    for entry_name, entry_data in paks_entries:
        print 'data entry: %s, len: %08x' % (entry_name, len(entry_data))

        off = entry_name.rfind('/')
        filename = entry_name[off + 1:]
        filepath = '%s/%s/%s' % (sys.argv[2], arg.replace('.', '_'), entry_name[:off])

        mkdir_p(filepath)
        open('%s/%s' % (filepath, filename), 'wb').write(entry_data)
