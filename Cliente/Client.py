from math import sin, cos, radians
from struct import unpack
import pygame
import random
import socket   
import sys      


# VARIÁVEIS PARA O SOCKET UDP
host = 'localhost'
port = 8080

MAX_MESSAGE_LENGTH = 1024

# TENTA CRIAR O SOCKET UDP - SEMELHANTE AO DE CPP
try:	
	socket.setdefaulttimeout(1/2)
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

except socket.error:
    print("Failed to create socket")
    sys.exit()


# DEFINIÇÕES PARA AS DIMENSÕES DA TELA
screen_dimensions = [20*40,20*15]
center = [screen_dimensions[0]/2, screen_dimensions[1]]


# CLASSE PARA AS CORES NO ESTILO RGB - opcional 
class Color:
	white =  [255, 255, 255]
	black =  [  0,   0,   0]
	gray  =  [ 75,  75,  75]
	green =  [  0, 200,   0]
	blue  =  [ 50,  50, 200]
	red   =  [200,   0,   0]
	orange = [ 255, 127,  0]
	lightGray = [200,200,200]

cor = Color()

# INICIA OS PEDAÇOS DO SONAR
piece_radial = []
for i in range(180):
	piece_radial.append(0)


# FUNÇÃO QUE DESENHA OS PEDAÇOS DO SONAR 
def drawPiece(raio, angulo=[0,0], _raioMax = 250, _num=5):
	raioMax = _raioMax
	(x,y) = center
	num = _num

	angulo[0] = radians(angulo[0])
	angulo[1] = radians(angulo[1])

	xo,x1 = raio*cos(angulo[1]), raio*cos(angulo[0])
	yo,y1 = raio*sin(angulo[1]), raio*sin(angulo[0])
	xob,x1b = raioMax*cos(angulo[1]), raioMax*cos(angulo[0])
	yob,y1b = raioMax*sin(angulo[1]), raioMax*sin(angulo[0])
	
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


# FUNÇÃO USADA PARA DESENHAR TODOS OS RETANGULOS NO PROGRAMA
def drawRetangulo(fonte, dim = [0,0], texto="", cor = [0,0,0], enquadro=[5,5]):
	text = fonte.render(texto,2,(0,0,0))
	surface = pygame.Surface((dim[0],dim[1]))
	surface.fill(cor)
	surface.blit(text, (enquadro[0],enquadro[1]))
	border = pygame.Surface((dim[0]+2,dim[1]+2), 0)
	border.fill((0,0,0))
	border.blit(surface, (1,1))
	return border
	

# FUNÇÃO QUE DESENHA AS OPÇÕES DE CONTROLE DO PROGRAMA
optionPos = []
def drawProcessOptions(process):
	options = ['DEMO', 'REMOTO', 'AUTOMÁTICO']
	optionPos = []
	for i in range(len(options)):
		txtOption = drawRetangulo(pygame.font.SysFont(systemFont,22), [110,30], options[i], cor.red if process is not i else cor.green)
		screen.blit(txtOption, (screen_dimensions[0]-120, 5 + 40*i))
		optionPos.append([screen_dimensions[0]-120,  5+ 40*i])
	return optionPos

def drawConnection(str):
	font = pygame.font.SysFont(systemFont,22)
	if str == "DISCONNECTED":
		conn = drawRetangulo(font, [150, 30], str, cor.red, [10,10] )
	elif str == "CONNECTED":
		conn = drawRetangulo(font, [150, 30], str, cor.green, [10,10] )
	else: 
		conn = drawRetangulo(font, [150, 30], str, cor.orange, [10,10] )
	screen.blit(conn, [screen_dimensions[0]/2 - 75, 5])


# SEND AND LISTEN - FUNÇÃO UDP 
def sendAndListening(msg):	

    #CODIFICA A MENSAGEM EM ARRAY DE BYTES
    msg = bytearray(msg.encode())

    #ENVIA A SOLICITAÇÃO
    s.sendto(msg, (host, port))

    #AGUARDA A RESPOSTA
    d = s.recvfrom(MAX_MESSAGE_LENGTH)

    #MENSAGEM RECEBIDA
    reply = d[0]

    print ('Servidor retornou: ' + str(reply))
    return reply


# INICIANDO PROCESSO NO PYGAME
pygame.init()

pygame.font.init()
systemFont = pygame.font.get_default_font()

screen = pygame.display.set_mode(screen_dimensions)

pygame.display.set_caption("Teste de sensor de proximidade")
pygame.display.set_icon(pygame.image.load("../.icon.png"))

clock = pygame.time.Clock()

# VARIÁVEIS UTILIZADAS 
x,y = 0,0

angulo = 0 
raio = 0
value = 0 
process = 0

dim = [100,30]
offset = (10,10)

posRel = [(dim[0]+offset[0])/2, dim[1]+offset[1]]

sliderPos = [posRel[0]/2 + 2, posRel[1]+1]
flagSlider = False 

auto_pos = 1
desconnect = 0

dots = ''

while True:
	# COLORIR O PLANO DE FUNDO COM A COR CINZA
	screen.fill(cor.lightGray)

	# BUSCA EVENTOS DENTRO DO PYGAME 
	for event in pygame.event.get():
		# SE O BOTÃO DE FECHAR FOR PRESSIONADO
		if event.type == pygame.QUIT:
			pygame.quit()
		
		# SE UMA TECLA FOR PRESSIONADO 
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				pygame.quit()

			if event.key == pygame.K_a:
				#ATUALIZA AS PORTAS PRESSIONANDO 'a'
				# NÃO UTILIZADO NA VERSÃO 1
				pass

		# VERIFICA O MODO DO PROCESSO ATIVO
		if pygame.mouse.get_pressed()[0]:
			coords = pygame.mouse.get_pos()
			for surface in optionPos:
				if coords[0] >= surface[0] and coords[0] <= surface[0]+110:
					if coords[1] >= surface[1] and coords[1] <= surface[1]+30:
						process = optionPos.index(surface)
			
			# CONTROLE DO SLIDER
			if process == 1:
				if coords[0] >= sliderPos[0] and coords[0] <= sliderPos[0]+dim[0]:
					if coords[1] >= posRel[1] and coords[1] <= posRel[1]+180:
						sliderPos[1] = coords[1]
						if sliderPos[1] > posRel[1]+180:
							sliderPos[1] =  posRel[1]+180
						if sliderPos[1] < posRel[1]:
							sliderPos[1] = posRel[1] +1

	#DEMO
	if process == 0:
		try:
			angulo = angulo +1 if angulo < 180 else 1 
			piece_radial[angulo] = abs(angulo*cos(radians(angulo))) + random.randint(-20,75) if piece_radial[angulo] < 250 else 250
			print(piece_radial[angulo])
		except:
			pass
	
	# REMOTO
	elif process == 1:

		fonte = pygame.font.SysFont(systemFont,30)

		# DESENHA A LINHA ONDE ESTARÁ O SLIDER
		pygame.draw.line(screen, cor.gray, posRel, [posRel[0], posRel[1]+180], 6) 
		
		txtOption = drawRetangulo(fonte, dim, "Angulo", cor.blue)
		screen.blit(txtOption, offset)
		angulo = sliderPos[1] - posRel[1]
		slider = drawRetangulo(fonte, [50, 23], str(angulo), cor.green)
		screen.blit(slider, sliderPos)

	# AUTOMÁTICO
	elif process == 2:

		auto_pos = auto_pos+1 if auto_pos+1 < 180 else 0 
		angulo = auto_pos
		# SEND THE VALUE ANGLE 

		fonte = pygame.font.SysFont(systemFont,30)

		txtOption = drawRetangulo(fonte, dim, "Angulo", cor.blue)
		screen.blit(txtOption, offset)
		
		ang = drawRetangulo(fonte, [50, 23], str(angulo), cor.green)
		screen.blit(ang, [sliderPos[0], posRel[1]+10])

	# USA A CONEXÃO UDP SE FOR AUTO OU REMOTO 
	if process != 0:
		drawConnection("CONNECTED")
		try:
			# RECEBE OS VALORES DO SERVIDO - EXEMPLO [ ' 12 120 34 45']
			reply = sendAndListening(str(angulo)).decode().split(' ')
			#reply = int(reply[0])
			desconnect = 0
			'''
			# TRANSFORMA OS VALORES EM ARRAY DE BYTES 
			reply = bytes([ int(x) for x in reply ])

			# CONVERTE PARA FLOAT 
			ans = unpack('f', reply)
			'''
			# SALVA O VALOR DO ANGULO - CONVERTE FLOAT PARA INT 
			piece_radial[angulo] = int(reply[1])

			print("O valor de %i é %i \n" %(angulo, piece_radial[angulo]))


		except:
			desconnect = desconnect + 1
			if desconnect%5 >0:
				dots = dots + "."
			else: 
				dots = "" 
			drawConnection("CONNECTING"+dots)
			print("Tentativa de conexão número %s" %desconnect)
	else: 
		drawConnection("DISCONNECTED")
		
	if desconnect == 20:
		desconnect = 0
		process = 0 

	# DESENHA NA TELA AS OPÇÕES - DEMO REMOTO AUTO 
	optionPos = drawProcessOptions(process)
	

	# DESENHA OS PEDAÇOS DO SONAR 
	for i in range(0,180,1):
		drawPiece(piece_radial[i], [i,i+1])

	pygame.display.update()
	clock.tick(60)
