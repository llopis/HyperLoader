#!/usr/bin/env python

import sys
from pprint import pprint



def main():
	if (len(sys.argv) != 4 and len(sys.argv) != 5):
		print "Usage: %s datafile outfile zero_duration [loaderfile]" % sys.argv[0]
		return

	zeroBitLength = int(sys.argv[3])
	zeroBitLengthLow = zeroBitLength & 0xFF
	zeroBitLengthHigh = (zeroBitLength >> 8) & 0xFF

	oneBitLength = zeroBitLength*2
	oneBitLengthLow = oneBitLength & 0xFF
	oneBitLengthHigh = (oneBitLength >> 8) & 0xFF

	if len(sys.argv) == 5:
		loaderFileName = sys.argv[4]
		with open(loaderFileName, mode='rb') as fin:
			loaderContent = bytearray(fin.read())
		fin.close()
		loaderLength = len(loaderContent)
		loaderLengthLow = loaderLength & 0xFF
		loaderLengthHigh = (loaderLength >> 8) & 0xFF
		loaderSegments = loaderLength // 256 + 1				# Calculate number of 256 byte segments required
		loaderBlockLength = loaderSegments * 258 +5				# Caclulate block length (data + flags + checksums + trailer)
		for i in range(loaderSegments * 256 - loaderLength):	# Pad loader up to the next 256 byte boundary with zeroes
			loaderContent.append(0x00)
		loaderBlockLengthLow = loaderBlockLength & 0xFF
		loaderBlockLengthHigh = (loaderBlockLength >> 8) & 0xFF	
	
	dataFileName = sys.argv[1]
	with open(dataFileName, mode='rb') as fin:
		fileContent = bytearray(fin.read())
	fin.close()
	contentLength = len(fileContent)
	contentLengthLow = contentLength & 0xFF
	contentLengthHigh = (contentLength >> 8) & 0xFF

	data = bytearray('ZXTape!')
	data.append(0x1A)
	# Version
	data.extend([0x01, 0x14])

	# Standard CPC header block
	# TZX header
	if len(sys.argv) == 5:
		data.append(0x11)			# Block ID
		data.append(0x21)			# Pilot pulse length (L)
		data.append(0x0B)			# Pilot pulse length (H)
		data.append(0xAD)			# Sync1 pulse length (L)
		data.append(0x05)			# Sync1 pulse length (H)
		data.append(0xAD)			# Sync2 pulse length (L)
		data.append(0x05)			# Sync2 pulse length (H)
		data.append(0xA2)			# Zero pulse length (L)
		data.append(0x05)			# Zero pulse length (H)
		data.append(0x05)			# One pulse length (L)
		data.append(0x0B)			# One pulse length (H)
		data.append(0x02)			# Pilot pulse count (L)
		data.append(0x10)			# Pilot pulse count (H)
		data.append(0x08)			# Bits used in last byte
		data.append(0x11)			# Pause after this block (L)
		data.append(0x00)			# Pause after this block (H)
		data.append(0x07)			# Data length (L)
		data.append(0x01)			# Data length (M)
		data.append(0x00)			# Data length (H)
	# CPC header
		data.append(0x2c)			# Flag (0x2c for header, 0x16 for data)
		data.extend([0x48, 0x59, 0x50, 0x45,\
					 0x52, 0x4C, 0x4F, 0x41,\
					 0x44, 0x45, 0x52, 0x00,\
					 0x00, 0x00, 0x00, 0x00])	# Filename ("HYPERLOADER" padded to 16 bytes with zeroes)
		data.append(0x01)			# Block number
		data.append(0xFF)			# Last block indicator (non-zero = last block)
		data.append(0x02)			# File type
									#	Bits 1-3 determine file type:-
									#		0	BASIC
									#		1	Binary
									#		2	Screen Image
									#		3	ASCII
									#		4-7	Unused
		data.append(loaderLengthLow)	# Data length (L)
		data.append(loaderLengthHigh)	# Data length (H)
		data.append(0x00)			# Destination address (L)
		data.append(0x40)			# Destination address (H)
		data.append(0xFF)			# First block indicator (non-zero = first block)
		data.append(loaderLengthLow)	# File length (L)
		data.append(loaderLengthHigh)	# File length (H)
		data.append(0x00)			# Exec address (L)
		data.append(0x40)			# Exec address (H)
		for i in range(228):		
			data.append(0x00)		# Pad up to 256 bytes with zeroes
		data.append(0xD2)			# Checksum (H)
		data.append(0x00)			# Checksum (L)
		data.extend([0xFF, 0xFF, 0xFF, 0xFF])	#	Trailer

	# Standard CPC data block
	# TZX Header
		data.append(0x11)			# Block ID
		data.append(0x21)			# Pilot pulse length (L)
		data.append(0x0B)			# Pilot pulse length (H)
		data.append(0xA6)			# Sync1 pulse length (L)
		data.append(0x05)			# Sync1 pulse length (H)
		data.append(0xA6)			# Sync2 pulse length (L)
		data.append(0x05)			# Sync2 pulse length (H)
		data.append(0x8B)			# Zero pulse length (L)
		data.append(0x05)			# Zero pulse length (H)
		data.append(0x1D)			# One pulse length (L)
		data.append(0x0B)			# One pulse length (H)
		data.append(0x02)			# Pilot pulse count (L)
		data.append(0x10)			# Pilot pulse count (H)
		data.append(0x08)			# Bits used in last byte
		data.append(0x78)			# Pause after this block (L)
		data.append(0x11)			# Pause after this block (H)
		data.append(loaderBlockLengthLow)	# Data length (L)
		data.append(loaderBlockLengthHigh)	# Data length (M)
		data.append(0x00)			# Data length (H)
	# CPC Data
		data.append(0x16)			# Flag
		for i in range(loaderSegments):
			crc = 0xFFFF								# CRC initial seed
			for j in range(256):
				data.append(loaderContent[j])			# Add byte from loader
				k = crc >> 8 ^ loaderContent[j]			# CRC iteration
				k = k ^ k >> 4
				crc = crc << 8 ^ k << 12 ^ k << 5 ^ k
				crc	= crc & 0xFFFF
			crc = crc ^ 0xFFFF							# One's complement for final CRC value
			crcHigh = crc >> 8 & 0xFF
			crcLow = crc & 0xFF
			data.append(crcHigh)	# Checksum (H)
			data.append(crcLow)		# Checksum (L)
		data.extend([0xFF, 0xFF, 0xFF, 0xFF])	#	Trailer

	# Block group
	data.append(0x21)			# Block ID
	data.append(0x00)			# No name

	# Pure tone 1  
	data.append(0x12)			# Block ID
	data.append(0x22)			# Pulse length (L)
	data.append(0x0B)			# Pulse length (H)
	data.append(0x00)			# Pulse count (L)
	data.append(0x04)			# Pulse count (H)

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

