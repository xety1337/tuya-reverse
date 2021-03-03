import sys
import string

def make_data_arr(aspace, start, end, sz):
    addr = start
    while addr < end:
        aspace.set_flags(addr, sz, aspace.DATA, aspace.DATA_CONT)
        addr += sz
        
def make_string_arr(aspace, start, end):
    #aspace.set_flags(start, 11, aspace.STR, aspace.DATA_CONT)
    action_make_ascii(aspace, start)
    #aspace.set_flags(0xfe0b8, 4, aspace.DATA_CONT, aspace.DATA_CONT)
#J 0xc6

def check_ascii(aspace, start, end):
    addr = start
    temp=addr
    sz = 0
    while addr < end:
        #fl = aspace.get_flags(addr)
        #if not self.expect_flags(fl, (aspace.DATA, aspace.UNK)):
        #    return

        b = aspace.get_byte(addr)
        if b == 0xc6:
            aspace.set_flags(addr, 1, aspace.CODE, aspace.CODE_CONT)
        if b == 0x00:
            if sz > 2:
                action_make_ascii(aspace, temp)
            addr += 1
            temp=addr
            sz = 0
            continue
        if not (0x20 <= b <= 0x7e or b in (0x0a, 0x0d)):
            addr += 1
            sz = 0
            continue
        if (0x20 <= b <= 0x7e or b in (0x0a, 0x0d)):
            addr += 1
            sz += 1
        

def action_make_ascii(aspace, start):
    addr = start
    #fl = aspace.get_flags(addr)
    #if not self.expect_flags(fl, (aspace.DATA, aspace.UNK)):
    #    return
    sz = 0
    label = "s_"
    while True:
        b = aspace.get_byte(addr)
        #fl = aspace.get_flags(addr)
        if not (0x20 <= b <= 0x7e or b in (0x0a, 0x0d)):
            if b == 0:
    	        sz += 1
            break
        #if fl not in (aspace.UNK, aspace.DATA, aspace.DATA_CONT):
         #   break
        c = chr(b)
        if c < '0' or c in string.punctuation:
            c = '_'
        label += c
        addr += 1
        sz += 1
    if sz > 0:
        aspace.set_flags(start, sz, aspace.STR, aspace.DATA_CONT)
        aspace.make_unique_label(start, label)
        #self.update_model()

FUNCS_BLACKLIST = {
    # Parse issues
    #"__addsf3",
    #"__subdf3",
    #"__divsi3",
    #"__udivsi3",
    #"__floatunsisf",
    #"__floatsidf",
    # multiple entries issues
    #"conv_str_decimal",
    #"ets_vprintf",
    #"UartDwnLdProc",
    #"rom_set_channel_freq",
    #"rom_chip_50_set_channel",
    # too complex, trips propagator
    #"MD5Transform",
    #"SHA1Transform",
}


def dump_funcs(APP):
    import sys
    import os
    from scratchabit import actions
    try:
        os.makedirs("funcs")
    except OSError:
        pass
    for addr, func in APP.aspace.iter_funcs():
        funcname = APP.aspace.get_label(addr)
        print("%08x %s" % (addr, funcname))
        # Dump only BootROM funcs so far
        if 0x00000000 <= addr < 0x000fffff and funcname not in FUNCS_BLACKLIST:
            with open("funcs/%08x-%s.lst" % (addr, funcname), "w") as fobj:
                actions.write_func_stream(APP, func, fobj, comments=False)


def dump_areas(APP):
    for start, end, props, bytes, flags in APP.aspace.get_areas():
        suffix = ""
        if "access" in props:
            suffix = "-" + props["access"].lower()
        else:
            # No access - null area
            continue
        fname = "funcs/%08x-%08x%s.bin" % (start, end + 1, suffix)
        with open(fname, "wb") as f:
            f.write(bytes)
            print(fname, props)


def dump_symtab(APP):
    with open("funcs/symtab.txt", "w") as f:
        items = [[x[0], x[1]] for x in APP.aspace.labels_rev.items()]

        for i in items:
            if isinstance(i[0], int):
                i[0] = APP.aspace.get_default_label(i[0])

        for label, addr in sorted(items, key=lambda x: x[1]):
            if isinstance(label, int):
                label = APP.aspace.get_default_label(addr)
            f.write("%08x %s\n" % (addr, label))


def main(APP):
    #APP.aspace.memcpy(0x3fffc000, 0x4000e388, 0x857)
    #APP.aspace.memcpy(0x3fffc860, 0x4000ebe8, 0x3fffdaac - 0x3fffc860)
    #APP.aspace.memcpy(0x3fffdaac, 0x4000fe34, 4)

    #make_data_arr(APP.aspace, 0x3fffccf0, 0x3fffccf0 + 0x400, 4)
    #make_data_arr(APP.aspace, 0x3fffd100, 0x3fffd100 + 0x400, 4)
    #make_data_arr(APP.aspace, 0x3fffd500, 0x3fffd500 + 0x100, 1)
    #make_data_arr(APP.aspace, 0x3fffd600, 0x3fffd600 + 0x40, 1)
    #make_data_arr(APP.aspace, 0x4000e388, 0x4000fe38, 1)
    #make_string_arr(APP.aspace, 0xfe0b4, 0xfe0be)
    check_ascii(APP.aspace, 0x0, 0xfffff)
    # Uncomment to dump funcs on startup and exit
    #dump_funcs(APP)
    #dump_areas(APP)
    #dump_symtab(APP)
    print(1)
    #sys.exit(0)
