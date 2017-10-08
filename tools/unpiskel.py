#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import os.path
import re
import json
from base64 import b64decode

if len(sys.argv) != 2:
    print('usage: %s input.piskel' % sys.argv[0], file=sys.stderr)
    sys.exit(1)

data_uri_pattern = re.compile('^data:([^;]*);base64,(.*)$')

def decode_image(data_uri):
    m = data_uri_pattern.match(data_uri)
    
    mimetype = m.group(1)
    data = b64decode(m.group(2))

    extension = ''
    if mimetype == 'image/png':
        extension = '.png'
    elif mimetype == 'image/jpeg':
        extension = '.jpg'

    return (extension, data)

if __name__ == '__main__':
    input_path = sys.argv[1]
    j = None
    with open(input_path, 'r') as f:
        j = json.load(f)

    layers = j['piskel']['layers']
    for layer_num, layer_str in enumerate(layers):
        layer = json.loads(layer_str)

        for chunk_num, chunk in enumerate(layer['chunks']):
            ext, data = decode_image(chunk['base64PNG'])
            output_path = os.path.join(*input_path.rsplit('.', 1)[0:-1])
            output_path += '_%02d_%02d' % (layer_num, chunk_num)
            output_path += ext
            with open(output_path, 'wb') as f:
                f.write(data)
