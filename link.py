# Link layer
# Handles checksum and Time To Live
#
# checksum	TTL	contents
# 16		4

import hashlib
import struct
import logging

from general_utility import *

class Link:

	# The starting TTL for origin messages
	TTL_origin = 50

	def __init__(self, upper_layer):

		# Should be the route layer
		self.upper_layer = upper_layer

	# Uses md5 to return the hash value for the sent string
	def get_hash(self, sent):

		# Make the md5 hasher
		hasher = hashlib.md5()

		# Add the string
		hasher.update(sent)

		# Return the hash
		return hasher.digest()

	# Takes the TTL and the contents. Creates a hash for the packet
	# Decrements TTL and rasies RuntimeError if it goes below 0. Throws packet contents as well
	def pack(self, contents, TTL = None):

		# TTL not set means this message is originating from this node
		if TTL is None:

			TTL = self.TTL_origin

		# Decrement TTL
		else:

			# Get new TTL
			TTL = int(TTL) - 1

		# Raise if less than 0
		if TTL < 0:

			logging.info("DROPPED: Time to live expired.")
			logging.debug("Packet contents: " + contents)

			raise RuntimeError("Time To Live expired", contents)

		# Add TTL
		packet_whole = struct.pack("!L", TTL) + contents

		# Make the checksum and add to the whole
		packet_whole = self.get_hash(packet_whole) + packet_whole

		# Return the packet
		return packet_whole

	# Returns TTL, contents
	# Raises RuntimeError if the checksum shows corrupted data
	def unpack(self, packet):

		# Separate the hash from the rest of the packet
		sent_hash = packet[:hash_size]
		packet_body = packet[hash_size:]

		# Get the hash for the packet_body
		packet_hash = self.get_hash(packet_body)

		# Check for corruption
		if sent_hash != packet_hash:

			logging.info("DROPPED: Packet corrupted")

			raise RuntimeError("Packet corrupted")

		# Get the TTL and the body
		TTL = struct.unpack("!L", packet_body[:field_size])
		packet_body = packet_body[field_size:]

		return TTL, packet_body
