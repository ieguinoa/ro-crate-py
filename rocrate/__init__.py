#!/usr/bin/env python

## Copyright 2019 The University of Manchester, UK
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

"""
Create/parse RO-Crate metadata.

This module intends to help create or parse
RO-Crate metadata, see rocrate_ 


.. _rocrate: https://w3id.org/ro/crate/
"""

__author__      = "Stian Soiland-Reyes <http://orcid.org/0000-0001-9842-9718>"
__copyright__   = "Copyright 2019 The University of Manchester"
__license__     = "Apache License, version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>"

import os
from urllib.parse import urlsplit

# Convenience export of public functions/types
from .metadata import Metadata



def inspect_path(path):
    abs_path = os.path.abspath(path)
    exists = os.path.exists(abs_path)
    is_uri = is_file = is_dir = False
    if not exists:
        upr = urlsplit(path)
        drive, tail = os.path.splitdrive(path)
        if upr.scheme and upr.scheme.lower() != drive.rstrip(":").lower():
            is_uri = True
    if not is_uri:
        is_file = os.path.isfile(abs_path)
        is_dir = os.path.isdir(abs_path)

    return is_file, is_dir, is_uri

