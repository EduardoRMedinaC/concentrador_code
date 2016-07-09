# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from socketIO_client import SocketIO, LoggingNamespace
import serial
import time

def active():
	try:
		rasbpy = serial.Serial(		#
			port = '/dev/ttyAMA0',	#
			baudrate = 9600,		#
			bytesize = 7,			#	inicialización del puerto serial.
			parity = 'E',			#
			stopbits = 1,			#
			timeout = 1.5			#
		)
		rasbpy.open()
			envia = check(rasbpy)
			raspby.close()
			return envia
	except:
		print "Error al leer el dato"
		if(rasbpy.isOpen()):
			rasbpy.close()
		return ""	

def check(port):
	lista_de_direcciones = ["123","234","456"]

	flag = False

	for direccion in lista_de_direcciones:
		port.write(direccion)
		tiempoinicio = time.time() # tiempo en segundos
		tiempoespera = 5 # tiempo en segundos
		
		while True:
			delta = time.time() - tiempoinicio
			
			if delta >= tiempoespera: # verifica que no supere los 5 segundos
				if flag == False:
					resultado = direccion + "-" + "6"
					with SocketIO('ipdelserver', 8000, LoggingNamespace) as socketIO:
						socketIO.emit('check', resultado) #envia la alerta al centro de supervision.
						socketIO.wait(seconds=1)
					break	
			
			while port.inWaiting()>0:	# escuchando el puerto serial del raspberry
				respuesta = port.readline()
				
				if respuesta == "Active": 
					resultado = direccion + "-" + "5"
					with SocketIO('ipdelserver', 8000, LoggingNamespace) as socketIO:
						socketIO.emit('check', resultado) # envia la confirmación de actividad.
						socketIO.wait(seconds=1)
					flag = True
					break

			if flag:
				flag = False
				break 

print "Inicio de analisis de funcionamiento de cada nodo"
active()
print "Final del analisis"