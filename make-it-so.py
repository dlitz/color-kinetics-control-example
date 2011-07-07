#!/usr/bin/python
# -*- encoding: utf-8 -*-
#############################################################
# Control a Philips Color Kinetics iColor Tile MX board using Python!
# Actually, we control the PDS-60CA power supply / control board.
#
# The iColor Tile MX is a 12-by-12 array of RGB LEDs.  We send UDP packets with
# the RGB data over a local Ethernet connection.
#
#############################################################
# Originally by Dwayne Litzenberger <dlitz@dlitz.net> and Andrew Plumb <andrew@plumb.org>
#
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#############################################################

import socket
import struct
import time

def update_display(skt, lines):
	# TODO - Rotate 90 degrees clockwise

	# Rearrange the pixels
	values1 = lines[6] + lines[7] + lines[8] + lines[9] + lines[10] + lines[11]
	values2 = lines[5] + lines[4] + lines[3] + lines[2] + lines[1] + lines[0]

	# Convert 24-bit RGB values into strings of bytes
	rgb_data1 = "".join(chr(v >> 16) + chr((v >> 8) & 0xff) + chr(v & 0xff) for v in values1)
	rgb_data2 = "".join(chr(v >> 16) + chr((v >> 8) & 0xff) + chr(v & 0xff) for v in values2)

	# Header values (raw hexadecimal values; copied & pasted from a packet dump)
	header1 = "0401 dc4a 0100 0801 0000 0000 ffff ffff 0198 0000 0002 0000".replace(" ", "").decode('hex') # Port 1
	header2 = "0401 dc4a 0100 0801 0000 0000 ffff ffff 0298 0000 0002 0000".replace(" ", "").decode('hex') # Port 2

	# Make packet data:
	# - header
	# - RGB data padded to 512 bytes
	pkt_data1 = header1 + struct.pack("512s", rgb_data1)
	pkt_data2 = header2 + struct.pack("512s", rgb_data2)

	# Send the packets
	skt.send(pkt_data1)
	skt.send(pkt_data2)

# Network stuff
destination_address = ('10.32.77.5', 6038)
skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	# SOCK_DGRAM means UDP
skt.connect(destination_address)	# Sets the destination address for skt.send()

# This is the image (RGB values)
pixels = [
 [ 0x00ff00, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0x444444 ],
 [ 0xffffff, 0x0000ff, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xffffff ],
 [ 0xffffff, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xffffff ],
 [ 0xffffff, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xffffff ],
 [ 0xffffff, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xffffff ],
 [ 0xffffff, 0x000000, 0x000000, 0x000000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xffffff ],
 [ 0xffffff, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xffffff ],
 [ 0xffffff, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xffffff ],
 [ 0xffffff, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xffffff ],
 [ 0xffffff, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xffffff ],
 [ 0xffffff, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xffffff ],
 [ 0xff00ff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffff00 ],
]

# True for animation; False to just send the pixel data
#animation = True
animation = False

if not animation:
	update_display(skt, pixels)

else:
	# Silly animation - scrolling & fading
	m = 0
	d = 4
	while True:
		pp = list(list(int(v * m / 255) for v in line) for line in pixels)
		update_display(skt, pp)

		time.sleep(0.05)

		for y in range(len(pixels)):
			pixels[y] = [pixels[y][-1]] + pixels[y][0:-1]

		m = m + d
		if m > 255:
			d *= -1
			m = 255
		if m < 0:
			d *= -1
			m = 0
		print repr([m,d])
