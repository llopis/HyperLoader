#!/usr/bin/env python

import sys
from pprint import pprint



def main():
	if (len(sys.argv) != 4):
		print "Usage: %s datafile outfile zero_duration" % sys.argv[0]
		return

	zeroBitLength = int(sys.argv[3])
	zeroBitLengthLow = zeroBitLength & 0xFF
	zeroBitLengthHigh = (zeroBitLength >> 8) & 0xFF

	oneBitLength = zeroBitLength*2
	oneBitLengthLow = oneBitLength & 0xFF
	oneBitLengthHigh = (oneBitLength >> 8) & 0xFF


	dataFileName = sys.argv[1]
	with open(dataFileName, mode='rb') as fin:
		fileContent = fin.read()
	fin.close()
	contentLength = len(fileContent)
	contentLengthLow = contentLength & 0xFF
	contentLengthHigh = (contentLength >> 8) & 0xFF

	data = bytearray('ZXTape!')
	data.append(0x1A)
	# Version
	data.extend([0x01, 0x0D])

	# Block group
	data.append(0x21)			# Block ID
	data.append(0x00)			# No name

	# Pure tone 1  
	data.append(0x12)			# Block ID
	data.append(0x22)			# Pulse length (L)
	data.append(0x0B)			# Pulse length (H)
	data.append(0xFF)			# Pulse count (L)
	data.append(0x03)			# Pulse count (H)

	# Pure tone 2
	data.append(0x12)			# Block ID
	data.append(zeroBitLengthLow)			# Pulse length (L)
	data.append(zeroBitLengthHigh)			# Pulse length (H)
	data.append(0x14)			# Pulse count (L)
	data.append(0x00)			# Pulse count (H)


	# Pure data block
	data.append(0x14)			# Block ID
	data.append(zeroBitLengthLow)			# Pulse length (L)
	data.append(zeroBitLengthHigh)			# Pulse length (H)
	data.append(oneBitLengthLow)			# Pulse length (L)
	data.append(oneBitLengthHigh)			# Pulse length (H)
	data.append(0x08)			# Bits used in last byte
	data.append(0x00)			# No pause
	data.append(0x00)			# No pause
	data.append(0x21)			# Data length (L)
	data.append(0x00)			# Data length (M)
	data.append(0x00)			# Data length (H)

	for c in range(32):
		data.append(0xAA)

	data.append(0xAC);			# Synchronization byte

	# Main data block
	data.append(0x14)			# Block ID
	data.append(zeroBitLengthLow)			# Pulse length (L)
	data.append(zeroBitLengthHigh)			# Pulse length (H)
	data.append(oneBitLengthLow)			# Pulse length (L)
	data.append(oneBitLengthHigh)			# Pulse length (H)
	data.append(0x08)			# Bits used in last byte
	data.append(0x00)			# No pause
	data.append(0x00)			# No pause
	data.append(contentLengthLow)			# Data length (L)
	data.append(contentLengthHigh)			# Data length (M)
	data.append(0x00)			# Data length (H)
	
	for i in range(contentLength):
		data.append(fileContent[i])


	# Pause
	data.append(0x20)			# Block ID
	data.append(0x50)			# Pause (L)
	data.append(0x00)			# Pause (H)

	# Group end
	data.append(0x22)


	outFileName = sys.argv[2]
	out = open(outFileName, "wb")
	out.write(data)
	out.close()

	
if __name__ == '__main__':
    main()

