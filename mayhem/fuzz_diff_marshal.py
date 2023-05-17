#!/usr/bin/python3
import atheris
import sys
from json.decoder import JSONDecodeError

with atheris.instrument_imports():
    from jsondiff import diff

def RandomString(fdp, min_len, max_len):
    str_len = fdp.ConsumeIntInRange(min_len, max_len)
    return fdp.ConsumeUnicodeNoSurrogates(str_len)

def RandomDict(fdp, key_count, allowed_depth):
    entry_count = fdp.ConsumeIntInRange(0, key_count)

    gen_dict = {}

    for i in range(entry_count):
        key = RandomString(fdp, 1, 128)
        entry_type = fdp.ConsumeIntInRange(0, 4)

        value = None

        if entry_type == 0 and allowed_depth > 0:
            value = RandomDict(fdp, key_count, allowed_depth - 1)
        elif entry_type == 0:
            value = fdp.ConsumeBool()
        elif entry_type == 1:
            value = fdp.ConsumeInt(8)
        elif entry_type == 2:
             value = fdp.ConsumeRegularFloat()
        elif entry_type == 3:
            value = RandomString(fdp, 0, 128)
        elif entry_type == 4:
            value = None
           
        gen_dict[key] = value

    return gen_dict

def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)

    key_count = fdp.ConsumeIntInRange(0, 100)
    allowed_depth = fdp.ConsumeIntInRange(0, 15)
    
    dict_1 = RandomDict(fdp, key_count, allowed_depth)
    dict_2 = RandomDict(fdp, key_count, allowed_depth)

    try:
        diff(dict_1, dict_2, marshal=True)
    except TypeError:
        pass

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()