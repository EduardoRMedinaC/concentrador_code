# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from socketIO_client import SocketIO, LoggingNamespace
import serial
import time
import json

def send():
	try:
		rasbpy = serial.Serial(		#
			port = '/dev/ttyAMA0',	#
			baudrate = 9600,		#
			bytesize = 7,			#
			parity = 'E',			# Inicialización del puerto serial.		
			stopbits = 1,			#
			timeout = 1.5			#
		)							#
		rasbpy.open()
			envia = dataread(rasbpy)
			raspby.close()
			return envia
	except:
		print "Error al leer el dato"
		if(rasbpy.isOpen()):
			rasbpy.close()
		return ""			

def dataread(port):
	lista_de_direcciones = ['1234','2345','7654']
	lista_check = ['pendiente','pendiente','pendiente']
	avisos = [
	"No identification message\r\n",
	"Identification Message too short\r\n",
	"El resultado no es el correcto, pruebe nuevamente\r\n",
	"No se ha encontrado el STX\r\n",
	"La comunicacion fue un exito!"]
	vuelta = 1 

	while vuelta <= 3:
		for estado in lista_check:
			flag1 = False
			flag2 = False
			if estado == "pendiente":
				indice = lista_check.index(estado)		
				direccion = lista_de_direcciones[indice]
				port.write(direccion)
				tiempoinicio = time.time() # tiempo en segundos
				tiempoespera = 5 # tiempo en segundos

				while True:
					delta = time.time() - tiempoinicio 
					
					if delta >= tiempoespera: #verifica que no pase mas de 5 segundos
						if flag1 == False:
							break	
					
					while port.inWaiting()>0:	# se mantiene escuchando el puerto serial del raspberry
						try:
							data_json = port.readline()
							for mensaje in avisos:
								if data_json == mensaje: 
									resultado = direccion + "-" + avisos.index(mensaje)
									with SocketIO('ipdelserver', 8000, LoggingNamespace) as socketIO:
										socketIO.emit('read', resultado)  # envío del mensaje de error.
										socketIO.wait(seconds=1)
										flag2 = True
										break
							if flag2:
								break

							data_object = json.loads(data_json) # decodifica datos tipo json a objeto.
							with SocketIO('ipdelserver', 8000, LoggingNamespace) as socketIO:
								socketIO.emit('read', data_object) #envio de los resultados de la lectura.
								socketIO.wait(seconds=1) 
							flag1 = True
							break

						except:
							print "Error, no json data"

					if flag2:
						break

					if flag1:
						lista_check[indice] = "listo" # confirmación al enviar las mediciones correctamente.
						break
		vuelta += 1					

# bloque encargado de notificar al concentrador de aquellos nodos que no se comunican con el mismo. 
	for estado in lista_check:
		if estado == "pendiente":
				indice = lista_check.index(estado)		
				direccion = lista_de_direcciones[indice]
				print "Atención, el dispositvo final con direccion " + direccion + ", No responde"		



print "Inicio de la lectura"
send()
print "fin del proceso"



