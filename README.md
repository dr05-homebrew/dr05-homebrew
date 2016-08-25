# Tascam DR-05 homebrew firmware development

The [Tascam DR-05] is a handheld audio recorder. This repository contains
tools to understand and modify its firmware.

The omniscient etherpad: https://public.etherpad-mozilla.org/p/dr05reveng

[Tascam DR-05]: http://tascam.com/product/dr-05/


## External tools

* [Binutils and GCC][gcc] have been ported to blackfin (including objdump)
* crackwitz's [spi-flash-reassembler][reasm] can reassemble flash memory
  images from logic analyzer traces.
* [binmap]: A visualization tool for binaries, vaguely similar to
  [..cantor.dust..][cantor]
* [QEMU] has been [ported to blackfin][qemu-bfin]
* If you happen to have the [IDA Pro] SDK, you can use Andreas Schuler's
  [blackfin plugin][ida-bfin]

[gcc]: https://gcc.gnu.org/
[reasm]: https://github.com/dr05-homebrew/spi-flash-reassembler
[binmap]: https://github.com/dr05-homebrew/binmap
[cantor]: https://sites.google.com/site/xxcantorxdustxx/
[QEMU]: http://wiki.qemu.org/Main_Page
[qemu-bfin]: https://github.com/vapier/qemu
[IDA Pro]: https://www.hex-rays.com/products/ida/index.shtml
[ida-bfin]: https://github.com/krater/Blackfin-IDA-Pro-Plugin
