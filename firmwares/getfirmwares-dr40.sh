#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
wget -c 'http://tascam.com/content/downloads/products/706/dr40_056.zip'
wget -c 'http://tascam.com/content/downloads/products/706/dr40_062.102'
wget -c 'http://tascam.com/content/downloads/products/706/dr40_066.110.zip'
wget -c 'http://tascam.com/content/downloads/products/706/dr40_v120.zip'
wget -c 'http://tascam.com/content/downloads/products/706/dr-40_v130.zip'
wget -c 'http://tascam.com/content/downloads/products/706/dr-40_fw_v200.zip'
wget -c 'http://tascam.com/content/downloads/products/706/dr-40_fw_v210.zip'
wget -c 'http://tascam.com/content/downloads/products/706/dr-40_fw_v211.zip'
wget -c 'http://tascam.com/content/downloads/products/706/dr-40_fw_v212.zip'

sha256sum --check SHA256SUMS
