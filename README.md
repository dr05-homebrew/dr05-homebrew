# Tascam DR-05 homebrew firmware development

The [Tascam DR-05] is a handheld audio recorder. This repository contains
tools to understand and modify its firmware.

The omniscient etherpad: https://public.etherpad-mozilla.org/p/dr05reveng

[Tascam DR-05]: http://tascam.com/product/dr-05/


## Hardware overview

* BF514, an [Analog Devices][adi] [blackfin] digital signal processor
* 2 MiB of flash memory
* 16 MiB of external RAM
* a micro-SD slot
* a [Cirrus Logic][cirrus] audio CODEC
* a 128x64 pixel monochrome display with orange backlight

[adi]: http://www.analog.com/en/index.html
[blackfin]: http://www.analog.com/en/products/processors-dsp/blackfin.html
[cirrus]: https://www.cirrus.com/


## External tools

The following tools are not maintained in this repository, but may be useful
when dealing with DR-05 firmware:

* [Binutils and GCC][gcc] have been ported to blackfin (including objdump)
* crackwitz's [spi-flash-reassembler][reasm] can reassemble flash memory
  images from logic analyzer traces.
* [binmap]: A visualization tool for binaries, vaguely similar to
  [..cantor.dust..][cantor]
* [QEMU] has been [ported to blackfin][qemu-bfin]
* If you happen to have the [IDA Pro] SDK, you can use Andreas Schuler's
  [blackfin plugin][ida-bfin]
* [LdrViewer][ldrv] is a Windows program to view LDR bootstreams, the format
  that blackfin processors understand

[gcc]: https://gcc.gnu.org/
[reasm]: https://github.com/dr05-homebrew/spi-flash-reassembler
[binmap]: https://github.com/dr05-homebrew/binmap
[cantor]: https://sites.google.com/site/xxcantorxdustxx/
[QEMU]: http://wiki.qemu.org/Main_Page
[qemu-bfin]: https://github.com/vapier/qemu
[IDA Pro]: https://www.hex-rays.com/products/ida/index.shtml
[ida-bfin]: https://github.com/krater/Blackfin-IDA-Pro-Plugin
[ldrv]: http://dolomitics.com/downloads/ldrviewer.html
