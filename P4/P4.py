#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       P4.py
#

import sys
import os.path
from getpass import getpass
from ProgressBar import ProgressBar

try:
	from base import sbox, isbox, gfp2, gfp3, gfp9, gfp11, gfp13, gfp14, Rcon
except:
	import base_gen
	base_gen.generate()

	try:
		from base import sbox, isbox, gfp2, gfp3, gfp9, gfp11, gfp13, gfp14, Rcon
	except:
		print ("No se ha podido importar el módulo de base.")
		sys.exit()

if sys.version_info[0] == 3:
	raw_input = input


def RotWord(word):
	return word[1:] + word[0:1]

def SubWord(word):
	return [sbox[byte] for byte in word]


def SubBytes(state):
	return [[sbox[byte] for byte in word] for word in state]

def InvSubBytes(state):
	return [[isbox[byte] for byte in word] for word in state]


def ShiftRows(state):
	n = [word[:] for word in state]

	n[0][1], n[1][1], n[2][1], n[3][1] = n[1][1], n[2][1], n[3][1], n[0][1]
	n[0][2], n[1][2], n[2][2], n[3][2] = n[2][2], n[3][2], n[0][2], n[1][2]
	n[0][3], n[1][3], n[2][3], n[3][3] = n[3][3], n[0][3], n[1][3], n[2][3]

	return n

def InvShiftRows(state):
	n = [word[:] for word in state]

	n[0][1], n[1][1], n[2][1], n[3][1] = n[3][1], n[0][1], n[1][1], n[2][1]
	n[0][2], n[1][2], n[2][2], n[3][2] = n[2][2], n[3][2], n[0][2], n[1][2]
	n[0][3], n[1][3], n[2][3], n[3][3] = n[1][3], n[2][3], n[3][3], n[0][3]

	return n


def MixColumns(state):
	n = [word[:] for word in state]

	for i in range(len(state)):
		n[i][0] = gfp2[state[i][0]] ^ gfp3[state[i][1]] ^ state[i][2] ^ state[i][3]
		n[i][1] = state[i][0] ^ gfp2[state[i][1]] ^ gfp3[state[i][2]] ^ state[i][3]
		n[i][2] = state[i][0] ^ state[i][1] ^ gfp2[state[i][2]] ^ gfp3[state[i][3]]
		n[i][3] = gfp3[state[i][0]] ^ state[i][1] ^ state[i][2] ^ gfp2[state[i][3]]

	return n

def InvMixColumns(state):
	n = [word[:] for word in state]

	for i in range(len(state)):
		n[i][0] = gfp14[state[i][0]] ^ gfp11[state[i][1]] ^ gfp13[state[i][2]] ^ gfp9[state[i][3]]
		n[i][1] = gfp9[state[i][0]] ^ gfp14[state[i][1]] ^ gfp11[state[i][2]] ^ gfp13[state[i][3]]
		n[i][2] = gfp13[state[i][0]] ^ gfp9[state[i][1]] ^ gfp14[state[i][2]] ^ gfp11[state[i][3]]
		n[i][3] = gfp11[state[i][0]] ^ gfp13[state[i][1]] ^ gfp9[state[i][2]] ^ gfp14[state[i][3]]

	return n



def AddRoundKey(state, key):
	new_state = [[None for j in range(4)] for i in range(4)]
	for i, word in enumerate(state):
		for j, byte in enumerate(word):
			new_state[i][j] = byte ^ key[i][j]

	return new_state


def Cipher(block, w, Nb = 4, Nk = 4, Nr = 10):
	''' Este procedimiento de cifrado está preparado para algoritmos
	AES de 128, 192 y 256 bits, ajustando los parámetros Nr, Nk y Nb.

	'''

	state = AddRoundKey(block, w[:Nb])

	for r in range(1, Nr):
		state = SubBytes(state)
		state = ShiftRows(state)
		state = MixColumns(state)
		state = AddRoundKey(state, w[r*Nb:(r+1)*Nb])

	state = SubBytes(state)
	state = ShiftRows(state)
	state = AddRoundKey(state, w[Nr*Nb:(Nr+1)*Nb])

	return state

def InvCipher(block, w, Nb = 4, Nk = 4, Nr = 10):
	''' Este procedimiento de cifrado inverso está preparado para
	algoritmos AES de 128, 192 y 256 bits, ajustando los parámetros
	Nr, Nk y Nb.

	'''

	state = AddRoundKey(block, w[Nr*Nb:(Nr+1)*Nb])

	for r in range(Nr-1, 0, -1):
		state = InvShiftRows(state)
		state = InvSubBytes(state)
		state = AddRoundKey(state, w[r*Nb:(r+1)*Nb])
		state = InvMixColumns(state)

	state = InvShiftRows(state)
	state = InvSubBytes(state)
	state = AddRoundKey(state, w[:Nb])

	return state


def prepare_block(block):
	c = []
	for word in block:
		for byte in word:
			c.append(byte)

	s = None
	for byte in c:
		if sys.version_info[0] == 3:
			if not s:
				s = bytes([byte])
			else:
				s += bytes([byte])
		elif sys.version_info[0] == 2:
			if not s:
				s = chr(byte)
			else:
				s += chr(byte)

	return s


def get_block(inf, Nb = 4):
	return process_block(inf[:Nb*4]), inf[Nb*4:]


def padding(inf, Nb = 4):
	l = len(inf) # Bytes
	hl = [int((hex(l*8)[2:]).rjust(16,'0')[i:i+2],16)
		for i in range(0,16,2)]

	l0 = (8 - l)%16
	if not l0:
		l0 = 16

	if isinstance(inf, str):
		inf += chr(0b10000000)
		inf += chr(0)*(l0-1)
		for a in hl: inf += chr(a)
	elif isinstance(inf, bytes):
		inf += bytes([0b10000000])
		inf += bytes(l0-1)
		inf += bytes(hl)

	return inf


def unpadding(inf, Nb = 4):

	if sys.version_info[0] == 3:
		hl = inf[-8:]
	else:
		hl = [ord(a) for a in inf[-8:]]

	l = ''
	for b in hl:
		if b < 0x10: l += '0'
		l += hex(b)[2:]
	l = int(l, 16)

	return inf[:l]


def process_block(block, Nb = 4, Nk = 4):
	if sys.version_info[0] == 3:
		if type(block) == type(""): block = bytes(block, 'utf8')
		pass
	elif sys.version_info[0] == 2:
		block = map(ord, block)

	return [[block[i*4+j] for j in range(4)] for i in range(4)] # Lista de columnas


def process_key(key, Nk = 4):
	try:
		key = key.replace(" ","")
		return [[int(key[i*8+j*2:i*8+j*2+2], 16) for j in range(4)] for i in range(Nk)] # Lista de columnas
	except:
		print ("La contraseña no tiene un formato correcto. Debe estar formada por dígitos hexadecimales.")
		sys.exit()


def expand_key(key, Nb = 4, Nk = 4, Nr = 10):
	''' Este algoritmo de expansión de clave está preparado para
	algoritmos AES de 128, 192 y 256 bits, ajustando los parámetros
	Nr, Nk y Nb.

	'''

	w = []
	for word in key:
		w.append(word[:])

	i = Nk

	while i < Nb * (Nr + 1):
		temp = w[i-1][:]
		if i % Nk == 0:
			temp = SubWord(RotWord(temp))
			temp[0] ^= Rcon[(i//Nk)]
		elif Nk > 6 and i % Nk == 4:
			temp = SubWord(temp)

		for j in range(len(temp)):
			temp[j] ^= w[i-Nk][j]

		w.append(temp[:])

		i += 1

	return w


def print_block(block):

	s = ''

	# Por columnas
	for i in range(len(block[0])):
		for j in range(len(block)):
			h = hex(block[j][i])[2:]
			if len(h) == 1: h = '0'+h
			s += h + ' '
		s += '\n'
	print (s)


def str_block_line(block):
	s = ''

	# Por columnas
	for i in range(len(block)):
		for j in range(len(block[0])):
			h = hex(block[i][j])[2:]
			if len(h) == 1: h = '0'+h
			s += h
	return (s)


def uso():
	print ("Uso:")
	print("python P4.py -demo")
	print("python P4.py [-e | -d] <archivo> [-192|256]")
	sys.exit()


def main():

	# Comprobación de errores de entrada #
	if len(sys.argv) < 3:
		uso()

	mode = sys.argv[1]
	ifile = sys.argv[2]

	if mode not in ['-e', '-d'] or not os.path.exists(ifile):
		uso()

	try:
		with open(ifile, 'rb') as f:
			inf = f.read()
	except:
		print ("Error leyendo el archivo de entrada.")
		sys.exit()

	Nb = 4
	Nk = 4
	Nr = 10
	if len(sys.argv) > 3 and sys.argv[3] == '-192':
		Nk = 6
		Nr = 12
	elif len(sys.argv) > 3 and sys.argv[3] == '-256':
		Nk = 8
		Nr = 14
	######################################

	#key = getpass("Introduzca una contraseña de cifrado de {0} cifras hexadecimales: ".format(Nb * Nk * 2))
	key = raw_input("Introduzca una contraseña de cifrado de {0} cifras hexadecimales: ".format(Nb * Nk * 2))

	if len(key) < Nb * Nk * 2:
		print ("Contraseña demasiado corta. Rellenando con \'0\' hasta alcanzar una longitud de {0} cifras.".format(Nb * Nk * 2))
		key += "0"* (Nb * Nk * 2 - len(key))
	elif len(key) > Nb * Nk * 2:
		print ("Contraseña demasiado larga. Conservando únicamente las primeras {0} cifras.".format(Nb * Nk * 2))
		key = key[:Nb * Nk * 2]

	key = process_key(key, Nk)

	expanded_key = expand_key(key, Nb, Nk, Nr)

	if mode == '-e':
		ofile = ifile + '.aes'
	elif mode == '-d' and ifile.endswith('.aes'):
		ofile = ifile[:-4]
		if os.path.exists(ofile):
			spam = raw_input('El archivo "{0}" ya existe. ¿Sobreescribir? [s/N]'.format(ofile))
			if spam.upper() != 'S':
				ofile = raw_input('Introduzca nuevo nombre de archivo: ')
	else:
		ofile = ifile

	pb = ProgressBar(len(inf), 0)


	output = None

	if mode == '-e': # Encript
		inf = padding(inf, Nb)

	while inf:
		block, inf = get_block(inf, Nb)

		c = pb.update(len(inf))
		if c: pb.show()

		if mode == '-e': # Encript
			block = Cipher(block, expanded_key, Nb, Nk, Nr)
		elif mode == '-d': # Decript
			block = InvCipher(block, expanded_key, Nb, Nk, Nr)

		block = prepare_block(block)
		if output: output += block
		else: output = block

	if mode == '-d': # Decript
		output = unpadding(output, Nb)


	with open(ofile, 'wb') as f:
		#for block in output: f.write(block)
		f.write(output)

	print('')
	sys.exit()

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == '-demo':
		plaintext = "00112233445566778899aabbccddeeff"
		Nb = 4

		# AES-128
		print("\n")
		print("*"*40)
		print("*" + "AES-128 (Nk=4, Nr=10)".center(38) + "*")
		print("*"*40)
		Nk = 4
		Nr = 10

		key = "000102030405060708090a0b0c0d0e0f"
		print("KEY:\t\t{0}".format(key))
		key = process_key(key, Nk)
		expanded_key = expand_key(key, Nb, Nk, Nr)

		print("PLAINTEXT:\t{0}".format(plaintext))

		block = process_key(plaintext)
		block = Cipher(block, expanded_key, Nb, Nk, Nr)
		print("ENCRYPT:\t{0}".format(str_block_line(block)))

		block = InvCipher(block, expanded_key, Nb, Nk, Nr)
		print("DECRYPT:\t{0}".format(str_block_line(block)))
		print("\n")

		# AES-192
		print("*"*40)
		print("*" + "AES-192 (Nk=6, Nr=12)".center(38) + "*")
		print("*"*40)
		Nk = 6
		Nr = 12

		key = "000102030405060708090a0b0c0d0e0f1011121314151617"
		print("KEY:\t\t{0}".format(key))
		key = process_key(key, Nk)
		expanded_key = expand_key(key, Nb, Nk, Nr)

		print("PLAINTEXT:\t{0}".format(plaintext))

		block = process_key(plaintext)
		block = Cipher(block, expanded_key, Nb, Nk, Nr)
		print("ENCRYPT:\t{0}".format(str_block_line(block)))

		block = InvCipher(block, expanded_key, Nb, Nk, Nr)
		print("DECRYPT:\t{0}".format(str_block_line(block)))
		print("\n")

		# AES-256
		print("*"*40)
		print("*" + "AES-256 (Nk=8, Nr=14)".center(38) + "*")
		print("*"*40)
		Nk = 8
		Nr = 14

		key = "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
		print("KEY:\t\t{0}".format(key))
		key = process_key(key, Nk)
		expanded_key = expand_key(key, Nb, Nk, Nr)

		print("PLAINTEXT:\t{0}".format(plaintext))

		block = process_key(plaintext)
		block = Cipher(block, expanded_key, Nb, Nk, Nr)
		print("ENCRYPT:\t{0}".format(str_block_line(block)))

		block = InvCipher(block, expanded_key, Nb, Nk, Nr)
		print("DECRYPT:\t{0}".format(str_block_line(block)))
		print("\n")

	else:
		main()