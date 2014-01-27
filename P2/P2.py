#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       P2.py
#

import sys
import os.path
from collections import deque
import array

from ProgressBar import ProgressBar

if sys.version_info[0] == 3:
	raw_input = input

def main():
	if len(sys.argv) >= 4 and sys.argv[1] == '-c':
		archivo = sys.argv[2]
		archivo_llave = sys.argv[3]
		semillas = procesar_archivo_semillas_a5(archivo_llave)
		if semillas and '-ff' not in sys.argv:
			cifrador_a5_1(archivo, semillas = semillas)
		else:
			cifrador_archivo(archivo, archivo_llave)
	else:
		menu_P2()

def menu_P2():
	archivo = None
	if len(sys.argv) > 1:
		archivo = sys.argv[1]

	if archivo and not os.path.exists(archivo):
		print ("ERROR: El archivo de entrada no existe.")
		print ("Uso: python P2.py [<archivo_de_entrada>]")
		sys.exit()

	last = 7
	print('')
	print(' '+'*'*64)
	print(' *' + 'Criptografía - 2012 - TrollScience'.center(62) + '*')
	print(' *' + '- Práctica 2 -'.center(62) + '*')
	print(' '+'*'*64)
	print(' *  ' + 'Estudio de secuencias pseudoaleatorias'.ljust(60) + '*')
	print(' *    ' + '1) Extractor de Periodo'.ljust(58) + '*')
	print(' *    ' + '2) Análisis de Periodo (Postulados de Golomb)'.ljust(58) + '*')
	print(' *    ' + ''.ljust(58) + '*')
	print(' *  ' + 'Generadores de secuencias'.ljust(60) + '*')
	print(' *    ' + '3) NLFSR'.ljust(58) + '*')
	print(' *    ' + '4) LFSR'.ljust(58) + '*')
	print(' *    ' + '5) A5/1'.ljust(58) + '*')
	print(' *    ' + ''.ljust(58) + '*')
	print(' *  ' + 'Cifrador'.ljust(60) + '*')
	print(' *    ' + '6) A5/1'.ljust(58) + '*')
	print(' *    ' + '7) Archivo'.ljust(58) + '*')
	print(' *    ' + 'Q) Salir'.ljust(58) + '*')
	print(' '+'*'*64)

	i = 1

	entrada = None
	while (entrada == None):
		entrada = raw_input('Seleccione una opción: ').upper()

		if (entrada == 'Q' or i == 5):
			exit()
		elif (entrada.isdigit() and int(entrada) > 0 and int(entrada) <= last):
			entrada = int(entrada)
		else:
			entrada = None
			i += 1

	if entrada in [1,2,3]:
		if not archivo:
			archivo = raw_input("Introduzca nombre de archivo de entrada: ")
			if not os.path.exists(archivo):
				print ("ERROR: El archivo de entrada no existe.")
				sys.exit()
		with open(archivo) as f:
			leido = f.readline().rstrip()

	if entrada in [6,7]: # Cifrador
		if not archivo:
			archivo = raw_input("Introduzca nombre de archivo a cifrar/descifrar: ")
			if not os.path.exists(archivo):
				print ("ERROR: El archivo no existe.")
				sys.exit()

		archivo_llave = raw_input("Introduzca nombre de archivo de semilla/llave: ")
		if not os.path.exists(archivo_llave):
			print ("ERROR: El archivo no existe.")
			sys.exit()



	if entrada == 1:
		extraer_periodo(leido, salida_archivo = "periodo.txt", salida_pantalla = True, posibilidad_analisis = True)
	elif entrada == 2:
		postulados_golomb(leido)
	elif entrada == 3:
		nlfsr(archivo_minterms = archivo)
	elif entrada == 4:
		lfsr()
	elif entrada == 5:
		if not archivo:
			archivo = raw_input("Introduzca nombre de archivo de semillas: ")
			if not os.path.exists(archivo):
				print ("ERROR: El archivo de semillas no existe.")
				sys.exit()
		a5_1(archivo_semillas = archivo, salida_archivo = "secuencia_a5.txt", salida_pantalla = True)
	elif entrada == 6:
		cifrador_a5_1(archivo, archivo_llave)
	elif entrada == 7:
		cifrador_archivo(archivo, archivo_llave)

	sys.exit()

def extraer_periodo(secuencia, salida_archivo = None, salida_pantalla = False, posibilidad_analisis = False):
	l = len(secuencia)

	periodo = None # Para archivos vacíos

	for i in range(1, l//2+1):
		init = 0
		periodo = secuencia[0:i]

		for j in range(l // i):
			if secuencia[init:init+i] != periodo:
				periodo = None
				continue
			else:
				init += i

		if periodo and periodo.find(secuencia[init:]) == 0:
			break

	if periodo and salida_archivo:
		with open(salida_archivo, 'w') as f:
			f.write(periodo)

	if salida_pantalla:
		if periodo:
			print("El periodo tiene longitud {0}:\n{1}".format(len(periodo), periodo))
		else:
			print("Secuencia no periódica.")

	if periodo and posibilidad_analisis:
		a = raw_input("\n¿Aplicar análisis de periodo? [S/N] ").upper()
		if a == "S":
			postulados_golomb(periodo)

	return periodo


def postulados_golomb(periodo):
	print("")

	print ("Primer postulado de Golomb: ")#, end='')
	if primer_postulado_golomb(periodo): print("Verdadero.")
	else: print("Falso.")

	print ("Segundo postulado de Golomb: ")#, end='')
	if segundo_postulado_golomb(periodo): print("Verdadero.")
	else: print("Falso.")

	print ("Tercer postulado de Golomb: ")#, end='')
	if tercer_postulado_golomb(periodo): print("Verdadero.")
	else: print("Falso.")


def primer_postulado_golomb(periodo):
	numero_de_unos = periodo.count("1")
	numero_de_ceros = periodo.count("0")

	return (abs(numero_de_ceros - numero_de_unos) <= 1)

def segundo_postulado_golomb(periodo):
	periodo_modificado = periodo[:]
	if periodo_modificado[0] == periodo_modificado[-1]:
		c = -1
		for i, a in enumerate(periodo_modificado[1:]):
			if a != periodo_modificado[i-1]:
				c = i+1
				break

		if c == -1:
			return False
		else:
			periodo_modificado = periodo_modificado[c:]+periodo_modificado[:c]

	rachas = dict()
	actual = periodo_modificado[0]
	tamano_racha_actual = 1


	for i in periodo_modificado[1:]:
		if i == actual:
			tamano_racha_actual += 1
		else:
			if tamano_racha_actual in rachas.keys(): rachas[tamano_racha_actual] += 1
			else: rachas[tamano_racha_actual] = 1
			actual = i
			tamano_racha_actual = 1
	if tamano_racha_actual in rachas.keys(): rachas[tamano_racha_actual] += 1
	else: rachas[tamano_racha_actual] = 1

	mayor = max(list(rachas.keys()))

	if 1 not in rachas.keys(): return False
	actual = rachas[1]


	for i in range(2, mayor+1):
		actual //= 2
		if actual == 0 and i == mayor: actual = 1
		if i not in rachas.keys(): return False
		if rachas[i] != actual and actual != 1: return False


	return True

def tercer_postulado_golomb(periodo):
	distancias = None
	periodo = list(periodo)
	for i in range(1, len(periodo)-1):
		d = distancia_hamming(periodo, periodo[i:]+periodo[:i])
		if distancias == None: distancias = d
		elif d != distancias: return False

	return True


def distancia_hamming(v1, v2):
	if len(v1) != len(v2): return -1
	d = 0
	for i, a in enumerate(v1):
		if a != v2[i]: d += 1
	return d


def nlfsr(n_celdas = None, archivo_minterms = None, semilla = None, n_bits = None):

	if not archivo_minterms:
		archivo_minterms = raw_input("Introduzca nombre de archivo de minterms: ")
		if not os.path.exists(archivo_minterms):
			print ("ERROR: El archivo de minterms no existe.")
			sys.exit()
	if not semilla: semilla = raw_input('Introduzca la semilla: ')
	if not n_bits: n_bits = entrada_segura('Introduzca el número de bits de la secuencia a generar: ', type_numer = True)


	minterms_str = open(archivo_minterms).readline().strip().split(',')
	minterms = [int(x) for x in minterms_str]
	n_celdas = len(str(semilla))
	secuencia = str(semilla)

	for i in minterms:
		if i >= 2 ** n_celdas:
			print ("ERROR: Los minterms superan en tamaño de la semilla")
			sys.exit()

	semilla = deque(semilla)

	for _ in range(n_bits):
		s = 0
		for a in semilla:
			s = (s << 1) + int(a)

		if s in minterms:
			semilla.append('1')
		else:
			semilla.append('0')

		secuencia += semilla.popleft()


	a = raw_input("Número de bits a descartar [0]: ")
	if a.isdigit():
		a = int(a)
		secuencia = secuencia[a:]

	print(secuencia)
	with open("secuencia_nlfsr.txt", 'w') as f:
		f.write(secuencia)

	a = raw_input("\n¿Aplicar análisis de secuencia? [S/N] ").upper()
	if a == "S":
		periodo = extraer_periodo(secuencia, salida_pantalla=True)
		if periodo:
			postulados_golomb(periodo)


def lfsr_antiguo(n_celdas = None, polinomio_conexion = None, semilla = None, n_bits = None):

	if not n_celdas: n_celdas = entrada_segura('Introduzca el número de celdas: ', type_numer = True)
	if not polinomio_conexion: polinomio_conexion = raw_input('Introduzca el polinomio de conexión: ')
	if not semilla: semilla = raw_input('Introduzca la semilla: ')
	if not n_bits: n_bits = entrada_segura('Introduzca el número de bits de la secuencia a generar: ', type_numer = True)

	secuencia = semilla
	semilla = deque(semilla)

	i=n_celdas
	while(i<n_bits):

		suma=0
		for j in range(n_celdas):
			if(polinomio_conexion[j] == '1'):
				suma = suma+int(semilla[j])

		if (suma%2 == 1):
			semilla.append(1)
			secuencia=secuencia+'1'
		else:
			semilla.append(0)
			secuencia=secuencia+'0'
		semilla.popleft()

		i = i+1

	with open("secuencia_lfsr.txt", 'w') as f:
			f.write(secuencia)


def lfsr(semilla = None, archivo_semilla = None, polinomio_conexion = None, n_bits = None):
	if not polinomio_conexion: polinomio_conexion = str(raw_input('Introduzca el polinomio de conexión: '))
	if not semilla:
		if archivo_semilla:
			if not os.path.exists(archivo_semilla):
				print ("ERROR: El archivo de semilla no existe.")
				sys.exit()
		else:
			semilla = str(raw_input('Introduzca la semilla: '))
	if not n_bits: n_bits = entrada_segura('Introduzca el número de bits de la secuencia a generar: ', type_numer = True)

	generador = generador_lfsr(semilla, polinomio_conexion)

	secuencia = ''
	for i in range(n_bits):
		secuencia += str(next(generador))

	print (secuencia)

	with open("secuencia_lfsr.txt", 'w') as f:
		f.write(secuencia)

	a = raw_input("\n¿Aplicar análisis de secuencia? [S/N] ").upper()
	if a == "S":
		periodo = extraer_periodo(secuencia, salida_pantalla=True)
		if periodo:
			postulados_golomb(periodo)



def generador_lfsr(semilla, polinomio_conexion, bit_control = None):
	n_celdas = len(str(semilla))
	semilla = deque(semilla)
	if bit_control != None:
		control = n_celdas - bit_control - 1

	while(True):

		suma=0
		for i in range(n_celdas):
			if(polinomio_conexion[i] == '1'):
				suma ^= int(semilla[i])

		semilla.append(suma) # Entra por la derecha
		salida = int(semilla.popleft()) # Sale el de la izquierda

		if bit_control == None:
			yield salida
		else:
			yield salida, int(semilla[control])


def a5_1(semillas = None, archivo_semillas = None, n_bits = None, salida_pantalla = False, salida_archivo = False):

	if not semillas:
		if not archivo_semillas:
			archivo_semillas = raw_input("Introduzca nombre de archivo de semillas: ")
			if not os.path.exists(archivo_semillas):
				print ("ERROR: El archivo de semillas no existe.")
				sys.exit()
		semillas = procesar_archivo_semillas_a5(archivo_semillas)

	if not semillas:
		print ("ERROR: El archivo de semillas es incorrecto.")
		sys.exit()

	if not n_bits: n_bits = entrada_segura('Introduzca el número de bits de la secuencia a generar: ', type_numer = True)

	g0 = generador_a5_1(semillas)
	secuencia = []

	for i in range(n_bits):
		secuencia.append (str(next(g0)))

	secuencia = ''.join(secuencia)


	if salida_pantalla:
		print (secuencia)
		a = raw_input("\n¿Aplicar análisis de secuencia? [S/N] ").upper()
		if a == "S":
			periodo = extraer_periodo(secuencia, salida_pantalla=True)
			if periodo:
				postulados_golomb(periodo)

	if salida_archivo:
		with open(str(salida_archivo), 'w') as f:
			f.write(secuencia)


def generador_a5_1(semillas):
	# Polinomios de conexión
	D1 = "11100100000000000001"
	D2 = "11000000000000000000001"
	D3 = "111000000000000100000001"

	# Bits de control
	b1 = 9
	b2 = 11
	b3 = 11

	# Generadores
	g1 = generador_lfsr(semillas[0], D1, b1)
	g2 = generador_lfsr(semillas[1], D2, b2)
	g3 = generador_lfsr(semillas[2], D3, b3)

	r = [True, True, True] # Rotaciones
	s = [0, 0, 0] # Bits de salida
	c = [0, 0, 0] # Bits de control

	while True:
		if r[0]: s[0], c[0] = next(g1)
		if r[1]: s[1], c[1] = next(g2)
		if r[2]: s[2], c[2] = next(g3)

		suma = s[0] ^ s[1] ^ s[2]
		yield (suma)
		#secuencia.append (str(suma))

		if (c[0] == c[1]):
			mayoria = c[0]
		else:
			mayoria = c[2]

		for i, control in enumerate(c):
			if control == mayoria:	# Si es igual que la mayoría, rota
				r[i] = True
			else:					# Si es distinto, no rota
				r[i] = False


def procesar_archivo_semillas_a5(archivo):
	semillas = []
	try:
		with open(archivo) as f:
			l = f.readlines()
			if len(l) == 1: # Una única línea
				l = l[0].rstrip()
				semillas.append(l[:19])
				semillas.append(l[19:41])
				semillas.append(l[41:])
			elif len(l) == 3: # Tres líneas
				for a in l:
					semillas.append(a.rstrip())

				if len(semillas[0]) != 19 or len(semillas[1]) != 22 or len(semillas[2]) != 23:
					#for i in semillas: print(i, len(i))
					return None
			else:
				return None

		return semillas
	except:
		return None


def cifrador_a5_1(archivo, archivo_semilla = "semillaA5-1.txt", semillas = None):

	#archivo = "asdf.mp3.cif"

	with open(archivo,"rb") as f:
		contenido = f.read()

	#print ("Archivo leído")

	if not semillas:
		if archivo_semilla:
			semillas = procesar_archivo_semillas_a5(archivo_semilla)
		else:
			print("ERROR: Archivo de semilla no especificado.")
			sys.exit()

	g = generador_a5_1(semillas)

	if(archivo.endswith(".cif")):
		archivo = archivo[:-4]
	else:
		archivo += '.cif'


	last = len(contenido)
	pb = ProgressBar(0, last)
	with open (archivo, 'wb') as f:
		print ("")
		for i in range(last):
			c = pb.update(i)
			if c:
				sys.stdout.write(str(pb))
				sys.stdout.flush()

			# Buffering
			t_buffer = 256 #Buffer de 256 bits (32 bytes)
			if i%t_buffer == 0:
				l = [next(g) for _ in range(t_buffer)]


			byte = 0
			for j in range(8):
				#byte = (byte << 1) + next(g) # Sin buffering
				byte = (byte << 1) + l[i%t_buffer] # Con buffering


			if sys.version_info[0] == 3:
				byte ^= contenido[i]
				f.write(bytes([byte]))
			else:
				byte ^= ord(contenido[i])
				f.write(chr(byte))

		print ("")


def cifrador_archivo(archivo, archivo_llave):

	with open(archivo,"rb") as f:
		contenido = f.read()

	with open(archivo_llave, "rb") as f:
		llave = f.read(len(contenido))


	if(archivo.endswith(".cif")):
		archivo = archivo[:-4]
	else:
		archivo += '.cif'

	with open(archivo, "wb") as f:
		print ("")
		pb = ProgressBar(0, len(contenido))
		for i, byte in enumerate(contenido):
			c = pb.update(i)
			if c:
				sys.stdout.write(str(pb))
				sys.stdout.flush()

			if sys.version_info[0] == 3:
				o = byte ^ llave[i%(len(llave))]
				f.write(bytes([o]))
			else:
				o = ord(byte) ^ ord(llave[i%(len(llave))])
				f.write(chr(o))
		print ("")



def entrada_segura(mensaje, paciencia = None, type_numer = False, type_list = False):
	a = None
	veces = 0

	if not (type_numer or type_list): return None

	while (a == None):
		if paciencia and veces > paciencia: exit
		a = raw_input(mensaje + ' ')
		if type_numer and a.isdigit():
			a = int(a)
		elif type_list and a in type_list:
			pass
		else:
			print ('Valor inválido.')
			a = None

	return a


if __name__ == '__main__':
	main()
