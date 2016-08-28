Parsing the firmware update files with the Construct (developed on 2.5.2) library on Python 2.7.
Requires the "Texttable" package for output.
Requires the "Click" package for commandline parsing.

Disassembly dumping requires an objdump executable with blackfin support.

Uses the LUTs from fwupdate.


Example:
python2 process.py ../../dr05rev/tmp/cccac.yay dump block --headerinfo --disas --to-files test --fname-format "{dxe}-{blockid}.txt"
python2 process.py ../../dr05rev/tmp/cccac.yay dump block --raw --to-files test
python2 process.py ../../dr05rev/tmp/cccac.yay dump block --pbm --to-files test --fname-format "{blockid}.pbm"

./run.sh ../firmwares/DR-05_2.11/DR-05_44.211 dump block --pbm --blockidx 455 --pbm-format 64:0 --iter-widths 8:128 --to-files test5 --fname-format "{blockid}-{width}.pbm"
