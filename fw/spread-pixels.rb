#!/usr/bin/ruby
#
# This script takes each byte of a file and turns it into eight bytes,
# corresponding to its bits:
#
#                             0xad
#   -->                     1010 1101
#   -->             ff 00 ff 00  ff ff 00 ff
#
# This makes it easier to view the file in some raw image viewers.

filename = ARGV[0]

if not filename
	puts "Usage: ./spead-pixels.rb FILENAME"
	exit 1
end

data = File.read filename, :encoding => 'binary'

out = []
data.each_byte do |x|
	8.times do |i|
		if x & 0x80 == 0x80
			out << 0xff
		else
			out << 0
		end

		x <<= 1
	end
end

File.write "#{filename}.out", out.pack('C*')
