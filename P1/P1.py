#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       P1.py
#

from time import time
from math import floor, ceil, sqrt
from fractions import gcd
import random

import sys


lista_primos = [
	46199,
	629243,
	7715177,
	82376809,
	756065159,
	4093082899,
	735773424149,
	5746175430239
	#,25569934528771
	#,740745508071383 # CUIDADO. Uso de entre 4GB y 6GB de RAM.
	]


def main():
	# Comprobación de versión de Python
	if sys.version_info[0] < 3:
		print("\nERROR: Este programa debe ejecutarse con una versión de Python igual o superior a la 3.0.\n")
		sys.exit()
	menu_P1()

def menu_P1():
	last = 9
	print('')
	print(' '+'*'*64)
	print(' *' + 'Criptografía - 2012 - TrollScience'.center(62) + '*')
	print(' '+'*'*64)
	print(' *  ' + 'Parte Obligatoria'.ljust(60) + '*')
	print(' *    ' + '1) Módulo - a ^ b (mod p)'.ljust(58) + '*')
	print(' *    ' + '2) Logaritmo Discreto - log_a b (mod p)'.ljust(58) + '*')
	print(' *    ' + '3) Tabla comparativa'.ljust(58) + '*')
	print(' *    ' + '4) Test probabilístico de primalidad'.ljust(58) + '*')
	print(' *    ' + ''.ljust(58) + '*')
	print(' *  ' + 'Parte Voluntaria'.ljust(60) + '*')
	print(' *    ' + '5) Factorización: Fuerza bruta'.ljust(58) + '*')
	print(' *    ' + '6) Factorización: Rho de Pollard'.ljust(58) + '*')
	print(' *    ' + '7) Factorización: Método de Fermat'.ljust(58) + '*')
	print(' *    ' + '8) Factorización: Algoritmo de Strassen'.ljust(58) + '*')
	print(' *    ' + ''.ljust(58) + '*')
	print(' *  ' + 'Herramientas'.ljust(60) + '*')
	print(' *    ' + '9) Generar impar de n dígitos'.ljust(58) + '*')
	print(' *    ' + ''.ljust(58) + '*')
	print(' *    ' + 'Q) Salir'.ljust(58) + '*')
	print(' '+'*'*64)

	i = 1

	entrada = None
	while (entrada == None):
		entrada = input('Seleccione una opción: ').upper()

		if (entrada == 'Q' or i == 5):
			exit()
		elif (entrada.isdigit() and int(entrada) > 0 and int(entrada) <= last):
			entrada = int(entrada)
		else:
			entrada = None
			i += 1

	if entrada == 1:
		r = potencia_modulo()
		print ("El resultado es {0}.".format(r))
	elif entrada == 2:
		r = logaritmo_discreto(mas_soluciones=True)
		print ("El resultado es {0}.".format(r))
	elif entrada == 3:
		comparativa()
	elif entrada == 4:
		r = primalidad_probabilistica()
		if r: print ("es probable primo")
		else: print ("no es primo")
	elif entrada == 5:
		r = factorizacion_bruta()
		print ("El resultado es {0}.".format(r))
	elif entrada == 6 or entrada == 7:
		n = entrada_segura('Introduzca el valor de n (natural a factorizar):', type_numer = True)

		ti = time()
		if entrada == 6:
			r = factorizacion_pollard(n)
		if entrada == 7:
			r = factorizacion_fermat(n)
		t1 = (time() - ti)

		if(n!=1 and r.count(1) > 0):
			r.remove(1)

		print ("El resultado es {0}.".format(r))
		print ("Tiempo empleado: ",t1,".")

	elif entrada == 8:
		n = entrada_segura('Introduzca el valor de n (natural a factorizar):', type_numer = True)
		ti = time()
		r = factorizacion_strassen(n)
		print ("El resultado es {0}.".format(r))
		t1 = (time() - ti)
		print ("Tiempo empleado: ",t1,".")
	elif entrada == 9:
		r = genera_impar_enorme();
		print(r)

	sys.exit()

def potencia_modulo(a = None, b = None, p = None):

	if not a: a = entrada_segura('Introduzca el valor de a (base):', type_numer = True)
	if not b: b = entrada_segura('Introduzca el valor de b (exponente):', type_numer = True)
	if not p: p = entrada_segura('Introduzca el valor de p (módulo):', type_numer = True)

	r = 1

	while b != 0:
		if b % 2 == 1:
			r = (r*a)%p
			b = (b-1)//2
		else:
			b = b// 2
		a = (a*a)%p

	return r


def logaritmo_discreto(a = None, c = None, p = None, mas_soluciones = False):

	if not a: a = entrada_segura('Introduzca el valor de a (base):', type_numer = True)
	if not c: c = entrada_segura('Introduzca el valor de c (número):', type_numer = True)
	if not p: p = entrada_segura('Introduzca el valor de p (módulo):', type_numer = True)

	s = int(ceil((p-1)**0.5))
	#a_pot_s = (a**s)%p
	a_pot_s = potencia_modulo(a, s, p)

	dic_i = {a_pot_s: 1}

	last = a_pot_s
	for i in range(s-1):
		last = (last * a_pot_s)%p
		dic_i[last] = i+2


	base = c
	encontrado = False
	for j in range(s):
		if base in dic_i.keys():
			j_final = j
			i_final = dic_i[base]
			encontrado = True
			if mas_soluciones:
				print ("Encontrada solución: {0}".format(s * i_final - j_final))
				asdf = input("¿Seguir buscando? [N/s]")
				if asdf != 's': break
				else: base = (base * a) %p
			else:
				break
		else:
			base = (base * a) %p


	if encontrado: resultado = s * i_final - j_final
	else: resultado = None

	return resultado


def comparativa():
	random.seed()

	for primo in lista_primos:

		a = random.randint(primo//10, primo)
		b = random.randint(primo//10, primo-2)

		repeticiones_modulo = 100
		repeticiones_logaritmo = 1


		print ("Ejecución para primo {0} - Valores aleatorios: {1}, {2}:".format(primo, a, b))

		print ("	Aritmética Modular")
		t1 = 0.0
		while t1 == 0.0:
			ti = time()
			for i in range(repeticiones_modulo):
				c = potencia_modulo(a, b, primo)
			t1 = (time() - ti)/repeticiones_modulo
			repeticiones_modulo *= 10
		print ("		Resultado: {0} - Tiempo: {1}".format(c, t1))

		print ("	Logaritmo Discreto")
		t2 = 0.0
		while t2 == 0.0:
			ti = time()
			for i in range(repeticiones_logaritmo):
				d = logaritmo_discreto(a, c, primo)
			t2 = (time() - ti)/repeticiones_logaritmo
			repeticiones_logaritmo *= 10
		print ("		Resultado: {0} - Tiempo: {1}".format(d, t2))

		print()

def primalidad_probabilistica(N = None, rondas = None, evitar_salida = False):
	if not N: N = entrada_segura('Introduzca el valor de N :', type_numer = True)
	if not rondas:
		rondas = input('Introduzca cantidad máxima de rondas O porcentaje de probabilidad (con %):')

		if rondas[-1] == '%':
			probabilidad = float(rondas[:-1])
			rondas = 0
			while (1 - (1/4)**rondas)*100.0 < probabilidad:
				rondas += 1

		elif rondas.isdigit():
			rondas = int(rondas)
		else:
			if not evitar_salida: print("Error en entrada.")
			return False

	probabilidad = 	1 - (1/4)**rondas

	# Mecanismo básico
	if N % 10 not in [1,3,7,9]: return False
	if N < 10:
		if N in [3,5,7]: return True
		else: return False

	# Comprobación de demasiadas rondas
	if rondas >= int(N * 0.4):
		if not evitar_salida: print ("Demasiadas rondas para un número pequeño")
		return False

	usados = []
	for _ in range(rondas):
		a_escogido = False
		while not a_escogido:
			a = random.randint(3, N-1) # No sirve que sea 1, ni que sea igual a N-1
			# Comprobaciones de selección de a
			if (a not in usados) and (a % 10 in [1,3,7,9]):
				usados.append(a)
				a_escogido = True

		# Descomposición de N-1
		s = 0
		r = N-1
		while (r % 2 == 0):
			s += 1
			r = r // 2

		b = potencia_modulo(a, r, N)
		if b in [N-1, 1]: continue

		siguiente_ronda = False
		for i in range(1, s):
			#b = modulo(a, r**(2*i), N)
			b = (b ** 2)%N
			if b == N-1:
				siguiente_ronda = True
				break
			elif b == 1:
				break


		if not siguiente_ronda: return False

	# No tengo motivos para creer que no sea primo
	if not evitar_salida: print("Probabilidad: {0}%".format(probabilidad*100.0))
	return True

def genera_impar_enorme(cifras = None):
	if not cifras: cifras = entrada_segura('Introduzca el número de cifras:', type_numer = True)
	n = random.randint(0, 10)

	for i in range(cifras-1):
		n *= 10
		n += random.randint(0, 10)

	if n % 2 == 0: n+=1

	return n


def factorizacion_bruta(n = None):

	if not n: n = entrada_segura('Introduzca el valor de n (natural a factorizar):', type_numer = True)

	if primalidad_probabilistica(n,10,True):
		return [int(n)]

	ti = time()

	resultado = []
	top = int(floor(n/2))

	while n % 2 == 0:
		resultado.append(2)
		n = n//2

	i = 3
	while (i <= top):
		if (n % i == 0):
			resultado.append(i)
			n = n/i
			i = i-2
		i = i+2

	t1 = (time() - ti)
	print ("Tiempo empleado: ",t1,".")

	return resultado


def factorizacion_pollard(n = None):

	if not n: return None #n = entrada_segura('Introduzca el valor de n (natural a factorizar):', type_numer = True)

	if primalidad_probabilistica(n,10,True):
		return [int(n)]

	resultado = []

	while (n%2 == 0):
		resultado.append(2)
		n = n/2

	if n==1:
		resultado.append(1)
		return resultado

	x = int(random.random())
	y = int(random.random())
	d = 1

	while(d==1):
		x = (x*x+1)%n
		y = ((y*y+1)*(y*y+1)+1)%n
		d = gcd(abs(x-y),n)

	if d==n:
		resultado.append(int(n))
		return resultado

	resultado.extend(factorizacion_pollard(d))
	resultado.extend(factorizacion_pollard(n//d))

	return resultado


def factorizacion_fermat(n = None):

	if not n: return None #n = entrada_segura('Introduzca el valor de n (natural a factorizar):', type_numer = True)

	if primalidad_probabilistica(n,10,True):
		return [int(n)]

	resultado = []

	while (n%2 == 0):
		resultado.append(2)
		n = n//2

	if n==1:
		resultado.append(1)
		return resultado

	x = isqrt(n)+1
	y = x*x-n

	while(not is_square(y)):
		x = x+1
		y = x*x-n

	y = isqrt(y)

	if(x+y == n or x-y == n):
		resultado.append(int(n))
		return resultado

	resultado.extend(factorizacion_fermat(x+y))
	resultado.extend(factorizacion_fermat(x-y))

	return resultado

def factorizacion_strassen(n = None):

	if not n: return None

	if primalidad_probabilistica(n,10,True):
		return [int(n)]

	resultado = []

	while (n%2 == 0):
		resultado.append(2)
		n = n//2

	if n==1:
		return resultado

	b = isqrt(n)
	c = isqrt(b)
	if(not is_square(b)):
		c+=1

	limit = ceil(b/c)

	for a in range(c):
		g = 1
		x = a*c
		for i in range(1,limit+1):
			g = (g*(x+i))%n
		d = mcd(g,n)
		if(d != 1):
			break

	if(d == 1):
		resultado.append(int(n))
		return resultado

	resultado.extend(factorizacion_strassen(d))
	resultado.extend(factorizacion_strassen(n//d))

	return resultado

def isqrt(x):
	if x < 0:
		raise ValueError('ERROR. Raíz cuadrada de un número negativo.')

	n = int(x)
	if n == 0: return 0

	a, b = divmod(n.bit_length(), 2)
	x = 2**(a+b)

	while True:
		y = (x + n//x)//2
		if y >= x: return x
		x = y

def is_square(n):
	referencia = isqrt(n)
	if referencia ** 2 == n: return True
	return False


def entrada_segura(mensaje, paciencia = None, type_numer = False, type_list = False):
	a = None
	veces = 0

	if not (type_numer or type_list): return None

	while (a == None):
		if paciencia and veces > paciencia: exit
		a = input(mensaje + ' ')
		if type_numer and a.isdigit():
			a = int(a)
		elif type_list and a in type_list:
			pass
		else:
			print ('Valor inválido.')
			a = None

	return a

def mcd(a,b):
	while (a != 0):
		a,b = b%a,a
	return b


if __name__ == '__main__':
	main()
