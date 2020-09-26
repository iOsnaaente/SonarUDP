from math import sin, cos, radians
from struct import pack, unpack
from SerialMod.Serial import * 
import pygame
import random
import socket
import math
import time

# USE UDP_IP = '' TO CATH ALL IPS
# USE UDP_PORT = ARBITRARY NUMBER 
UDP_IP = '127.0.0.1'
UDP_PORT = 8080

NUM_MAX_CLIENTS = 10 

# DEFINE THE BUFFER SIZE
BUFFER_SIZE = 1024
flagReceive = 0
sock = 0

# FLAG TO SET THE UDP CONNECTION
flagReceive = False

try:
	socket.setdefaulttimeout(1/10)
	# CRIAÇÃO DO SOCKET - SOCK_DGRAM = UDP 
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# INICIALIZAÇÃO DO SERVIDOR SOCKET
	sock.bind((UDP_IP, UDP_PORT))

	# FLAG PARA CONTROLE DE TRANSMISSÕES
	flagReceive = False

except:
	print("Erro na criação do socket, sugiro que reinicie o processo!!!")


# SERIAL DEFINIÇÕES 
comportList = showSerialAvailable()
comport = serial.Serial()

BAUDRATE = 9600

flagComport = False

surfaceListPorts = []


class Color:
	white =  [255, 255, 255]
	black =  [  0,   0,   0]
	gray  =  [ 75,  75,  75]
	green =  [  0, 200,   0]
	blue  =  [ 50,  50, 200]
	red   =  [200,   0,   0]
	lightGray = [200,200,200]
cor = Color()

piece_radial = []
for i in range(180):
	piece_radial.append(0)

def piecesZeros():
	for i in range(180):
		piece_radial[i] = 0


def drawPiece(raio, angulo=[0,0], _raioMax = 250, _num=5):

	raioMax = _raioMax
	(x,y) = center
	num = _num

	angulo[0] = radians(angulo[0])
	angulo[1] = radians(angulo[1])

	xo,x1 = raio*math.cos(angulo[1]), raio*math.cos(angulo[0])
	yo,y1 = raio*math.sin(angulo[1]), raio*math.sin(angulo[0])
	xob,x1b = raioMax*math.cos(angulo[1]), raioMax*math.cos(angulo[0])
	yob,y1b = raioMax*math.sin(angulo[1]), raioMax*math.sin(angulo[0])
	
	pygame.draw.polygon(screen, cor.red, [[x,y], [x+xob,y-yob],[x+x1b,y-y1b]],0)
	pygame.draw.polygon(screen, cor.green   , [[x,y], [x+xo,y-yo],[x+x1,y-y1]],4)	
	pygame.draw.line   (screen, cor.black   , [x+xob,y-yob], [x+x1b,y-y1b],5) 
	pygame.draw.line   (screen, cor.black   , [x+xo,y-yo], [x+x1,y-y1],5) 

	prop = raioMax/num
	for i in range(1,num):
		pygame.draw.arc(screen, cor.black, [x-(i*prop),y-(i*prop), 2*(i*prop),2*(i*prop)], 0, radians(190), 1)
		x1 = raioMax*cos(radians((180/num)*i))
		y1 = raioMax*sin(radians((180/num)*i))
		pygame.draw.line(screen, cor.black, [x,y], [x+x1,y-y1], 1)


def drawRetangulo(fonte, dim = [0,0], texto="", cor = [0,0,0], enquadro=[5,5]):
	text = fonte.render(texto,2,(0,0,0))
	surface = pygame.Surface((dim[0],dim[1]))
	surface.fill(cor)
	surface.blit(text, (enquadro[0],enquadro[1]))
	border = pygame.Surface((dim[0]+2,dim[1]+2), 0)
	border.fill((0,0,0))
	border.blit(surface, (1,1))
	return border

def drawText():
	textFonte  = pygame.font.SysFont(systemFont,30)
	textFonte15  = pygame.font.SysFont(systemFont,15)

	txtPortas = drawRetangulo(textFonte, [275,30], "Lista de portas disponíveis", cor.gray)
	screen.blit(txtPortas, (5,5))

	if flagComport is True:		
		txtConexao = drawRetangulo(textFonte15, [110,30], "DESCONECTAR", cor.green, [15,10])
		screen.blit(txtConexao, (screen_dimensions[0]-120, screen_dimensions[1]-40))
		txtConexao = drawRetangulo(textFonte, [210,30], str(comport.name), cor.green)

	else:
		txtConexao = drawRetangulo(textFonte15, [110,30], "DESCONECTADO", cor.red, [10,10])
		screen.blit(txtConexao, (screen_dimensions[0]-120, screen_dimensions[1]-40))
		txtConexao = drawRetangulo(textFonte, [210,30], "Porta não conectada", cor.red)
	
	screen.blit(txtConexao, (screen_dimensions[0]*2/5, 5 ))

	for num,port in enumerate(comportList):
		txtPorta = drawRetangulo(textFonte, [200,30], str(port), cor.blue)
		screen.blit(txtPorta, (5, (num+1)*30 +10))

		if [0,(num+1)*33, port] not in surfaceListPorts:
			surfaceListPorts.append([5, (num+1)*30 +10, port])
	
def Clients(num, mode):

	fonte25 = pygame.font.SysFont(systemFont,25)
	fonte   = pygame.font.SysFont(systemFont,30)
	
	clientBox = drawRetangulo(fonte, [150,30], "Clientes", cor.green, [40,5])
	screen.blit(clientBox, [screen_dimensions[0]-160, 5])
	
	numClients = drawRetangulo(fonte, [150,30], str(num), cor.white, [70,5])
	screen.blit(numClients, [screen_dimensions[0]-160, 40])	
	
	modos = drawRetangulo(fonte, [150,30], "Modo", cor.green, [55,5])
	screen.blit(modos, [screen_dimensions[0]-160, 75])

	modo = drawRetangulo(fonte25, [150,30], modosOperacao[mode], cor.white)
	screen.blit(modo, [screen_dimensions[0]-160, 110])


# PYGAME DEFINIÇÕES
screen_dimensions = [20*40,20*20]
center = [screen_dimensions[0]/2, screen_dimensions[1]]

pygame.init()

pygame.font.init()
systemFont = pygame.font.get_default_font()

screen = pygame.display.set_mode(screen_dimensions)

pygame.display.set_caption("Teste de sensor de proximidade")
pygame.display.set_icon(pygame.image.load("../.icon.png"))

clock = pygame.time.Clock()

x,y = 0,0

# PROCESSO DEFINIÇÕES
surfaceClose = [screen_dimensions[0]-110, screen_dimensions[1]-30]
modosOperacao = ['DEMO', 'REMOTO', 'AUTOMÁTICO', 'MANUAL']

process = modosOperacao.index('DEMO')

angPos = 0 
angulo = 0

disconnected = 0 

addrList = []

msg_Padrao = ''


# CÓDIGO RODANDO 
while True:
	screen.fill(cor.lightGray)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				pygame.quit()
			if event.key == pygame.K_a:
				surfaceListPorts = []
				comportList = showSerialAvailable()

		if pygame.mouse.get_pressed()[0]:
			coords = pygame.mouse.get_pos()
			
			if flagComport is True:
				if coords[0] >= surfaceClose[0] and coords[0] <= surfaceClose[0]+100:
					if coords[1] >= surfaceClose[1] and coords[1] <= surfaceClose[1]+30:
						closeSerialConnection(comport)
			try:
				for surface in surfaceListPorts:
					if coords[0] >= surface[0] and coords[0] <= surface[0]+200:
						if coords[1] >= surface[1] and coords[1] <= surface[1]+30:
							print("Comport found!!")
							comport = initSerialListening(surface[-1], BAUDRATE, 1)
			except:
				comport = serial.Serial()

	drawText()
	
	# CONTROLE DE CLIENTES
	numClientesConn = int(len(addrList))
	modoOperacao = process 
	Clients(numClientesConn, modoOperacao)
	
	routine = 0
	addrList = []

	temp1 = time.time()

	while True: 
		temp2 = time.time()
		if (temp2 - temp1 > 0.1): break

		try:
			dataSock, addr = sock.recvfrom(BUFFER_SIZE)
			process = modosOperacao.index("REMOTO")

			disconnected = 0			
		
			if dataSock != b'0' :

				funcao  = b'3'
				valor   = int(dataSock)
				fim     = b'\n'	
				addrList.append([0, addr, funcao, valor, fim])

			else:
				addrList.append([1, addr, 0,0,0])

		except:
			disconnected = disconnected + 1
			if disconnected > 20:
				disconnected = 0 
				process = modosOperacao.index("DEMO") 
				break
		
	addrList.sort()
	print(addrList)

	if process == modosOperacao.index("DEMO"):
		angPos = angPos+1 if angPos+1 < 180 else 0 
		funcao  = b'3'
		valor   = angPos
		fim     = b'\n'
		piece_radial[angPos] = random.randint(100,150)

	# SE E SOMENTE SE A COMPORT SERIAL ESTIVER DISNPONÍVEL
	if comport.is_open is True:
		
		flagComport = True
		for client in addrList:

			if client[0] is 0:
				try:
					# CRIA O PACOTE COM AS INFORMAÇÕES PARA A SERIAL
					send = pack('cic', client[2], client[3], client[4])

					# ENVIA O PACOTE PELA SERIAL
					comport.write(send)

					# LÊ A RESPOSTA DA SERIAL
					data = comport.readline()

					# FORMATA A RESPOSTA PARA OS DADOS EM PYTHON
					data = str(data).split(',')
					data[0] = data[0].replace("b'", '')
					data[-1] = data[-1].replace("\\r\\n'",'')
					
					# DEFINIÇÃO FORMAL DA LEITURA
					angulo    = client[3]
					distancia = data[-1]

					# TRANSFORMA OS VALORES EM ARRAY DE BYTES 
					distancia = distancia.split(" ")
					distancia.remove('')
					distancia = [ int(x) for x in distancia]

					# ARRAY DE BYTES
					distancia = bytes(distancia)
					print(distancia)

					# CONVERTE PARA FLOAT 
					distancia = unpack('f', distancia)
					distancia = int(distancia[0])

					# CONFIRMAÇÃO DE RECEBIMENTO EM BYTES -> PRINT
					#print("Recebido de %s : %s -> Angulo= %s : Distancia Ard= %s : Distancia Mon= %s" %(addr, dataSock, angulo, distancia, addr[1] % 250 ))

					distancia =  client[1][1] % 250 
					piece_radial[angulo] = distancia

					str_send = (str(angulo)+str(' ')+str(distancia)).encode()
					sock.sendto(str_send, client[1])

					msg_Padrao = str_send
			
				except:
					print("SERIAL INVÁLIDA!")

			else:
				try:
					sock.sendto(msg_Padrao, client[1])
				except:
					sock.sendto(str("0 0").encode(), client[1])
					print("Sem entidade de controle")
			print(msg_Padrao)

	else:
		flagComport = False
		process = modosOperacao.index('DEMO')


	for i in range(0,180,1):
		drawPiece(piece_radial[i], [i,i+1])
	
	pygame.display.update()
	clock.tick(120)