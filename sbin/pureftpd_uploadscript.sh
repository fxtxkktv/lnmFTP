#!/bin/bash

dstdir=$(dirname $1)
convmv -f gbk -t utf-8 --nosmart --notest $dstdir >/dev/null 2>&1
