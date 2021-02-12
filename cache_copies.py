#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import filecmp
import os
import pathlib
import re
import subprocess
import sys
from drf_generator import generate


def main(extended_drf):
    operational_devices = []
    cache_devices = []
    origin_path = pathlib.Path('origin_devices.dbl')
    new_path = pathlib.Path('new_cache_devices.dbl')

    # Generate DABBEL file to list details of existing devices.
    with open(origin_path, 'w+') as origin_file:
        for device in generate(extended_drf):
            operational_devices.append(device)
            origin_file.write(f'LIST {device}\n')

    for device in operational_devices:
        cache_devices.append(re.sub(r'^\w:(.*)$', r'Z:\1', device))

    # Run dabbel to get details of existing devices
    existing_dabbel = subprocess.check_output(
        f'dabbel {origin_path.absolute()} list --stdout',
        shell=True,
        encoding='utf-8'
    )

    # Replace all MOD with ADD and change device prefix
    adds = re.sub(r'\nMOD \w:([\w\d_]+)', r'\nADD Z:\1', existing_dabbel)
    # Replace full name
    f_name = re.sub(r'(\nFNAME .* )\w:([\w\d_]+\))', r'\1Z:\2', adds)
    # Replace front-end with CACHE
    new_fe = re.sub(r'(\nADD .*\(.*,) [\w\d_]{2,6}(,.*\n)', r'\1 CACHE\2', f_name)

    # Write modifications to file
    with open(new_path, 'w+') as new_file:
        for line in new_fe:
            new_file.write(line)

    # Run dabbel against new file to create new devices
    os.system(f'dabbel {new_path} modify')


if __name__ == '__main__':
    main(sys.argv[1])
