# Registers and associated values
_NOOP = const(0x0)	# Used when cascading Max7219
_DIGIT0 = const(0x1)
_DIGIT1 = const(0x2)
_DIGIT2 = const(0x3)
_DIGIT3 = const(0x4)
_DIGIT4 = const(0x5)
_DIGIT5 = const(0x6)
_DIGIT6 = const(0x7)
_DIGIT7 = const(0x8)
_DECODEMODE = const(0x9)	# (0 = no decode/raw segment values, 1 = decode only digit 0, 0xFF = decode on all digits)
_INTENSITY = const(0xA)		# (0 = lowest intensity, 0xF = max intensity)
_SCANLIMIT = const(0xB)		# (0 = display digit 0 only, 7 = display all 7 digits)
_SHUTDOWN = const(0xC)		# (0 = shutdown, 1 = normal operation)
_DISPLAYTEST = const(0xF)	# (0 = normal mode, 1 = test mode)

_HEX_TO_SEG = { 0x0: 0b1111110, 0x1: 0b0110000, 0x2: 0b1101101, 0x3: 0b1111001, 0x4: 0b0110011, 0x5: 0b1011011, 0x6: 0b1011111, 0x7: 0b1110000, 0x8: 0b1111111, 0x9: 0b1111011, 0xA: 0b1110111, 0xB: 0b0011111, 0xC: 0b1001110, 0xD: 0b0111101, 0xE: 0b1001111, 0xF: 0b1000111,}

class Max7219:
	def __init__(self, spi, cs):
		self.spi = spi
		self.cs = cs
		self.cs.init(cs.OUT, True)
		self.init()

	def register(self, command, data):
		self.cs.low()
		self.spi.write(bytearray([command, data]))
		self.cs.high()

	def init(self):
		for command, data in (
			(_SHUTDOWN, 0),	# Turn display off
			(_SCANLIMIT, 7),	# Display all 7 digits
			(_DECODEMODE, 0xFF),# Decode all digits 
			(_INTENSITY, 0x3),	# Set brightness to 3
			(_SHUTDOWN, 1),	# Turn display on
		):
			self.register(command, data)
            
	def brightness(self, value):
		if 0 <= value <= 15:
			self.register(_INTENSITY, value)
		else:
			raise ValueError("Brightness out of range")
		
	def clear(self):
		self.register(_DECODEMODE, 0xFF)
		for i in range(8):
			self.register(_DIGIT0 + i, 0x0)
		    
	def write_num(self, value):
		self.register(_DECODEMODE, 0xFF)
		if (0 <= value <= 99999999):
			for i in range(8):
				self.register(_DIGIT0 + i, value % 10)
				value = value // 10
		elif (0 > value >= -9999999):
			value = -value
			self.register(_DIGIT7, 0xA)
			for i in range(7):
				self.register(_DIGIT0 + i, value % 10)
				value = value // 10
		else:
			raise ValueError("Value out of range")
		
	def write_hex(self, value):
		self.register(_DECODEMODE, 0x0)
		if (0 <= value <= 99999999):
			for i in range(8):
				self.register(_DIGIT0 + i, _HEX_TO_SEG[value % 16])
				value = value // 16
		else:
			raise ValueError("Value out of range")
