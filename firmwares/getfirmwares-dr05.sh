#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" #http://stackoverflow.com/questions/59895/can-a-bash-script-tell-which-directory-it-is-stored-in
wget -c 'http://tascam.com/content/downloads/products/558/dr05-29.zip'
wget -c 'http://tascam.com/content/downloads/products/558/dr-05_fw_v111.zip'
wget -c 'http://tascam.com/content/downloads/products/558/dr-05_fw_v112.zip'
wget -c 'http://tascam.com/content/downloads/products/558/dr-05_fw_v200.zip'
wget -c 'http://tascam.com/content/downloads/products/558/dr-05_fw_v210.zip'
wget -c 'http://tascam.com/content/downloads/products/558/dr-05_2.11.zip'

sha256sum --check --ignore-missing SHA256SUMS
