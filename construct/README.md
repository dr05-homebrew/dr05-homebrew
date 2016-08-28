Parsing the firmware update files with the Construct (developed on 2.5.2) library on Python 2.7.
Requires the "Texttable" package for output.
Requires the "Click" package for commandline parsing.

Disassembly dumping requires an objdump executable with blackfin support.

Uses the LUTs from fwupdate.


Example:
python2 process.py ../../dr05rev/tmp/cccac.yay dump block --headerinfo --disas --to-files test --fname-format "{dxe}-{blockid}.txt"
