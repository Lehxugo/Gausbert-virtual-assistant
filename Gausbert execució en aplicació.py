#Importació de les llibreries necessàries per al programa general.
import numpy as np
import os
import time
from gensim.models import Word2Vec
from sklearn.neural_network import MLPClassifier
import datetime
import keyboard
import pickle
import speech_recognition as sr
import sys
import winsound
import webbrowser
from chatterbot import ChatBot
import pyowm
import requests
import json
import smtplib, ssl
import email
import pyautogui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#Es carrega la xarxa neuronal un cop a l'inici del programa per haver d'evitar carregar-lo cada vegada que s'ha d'utilitzar.
#S'obre en mode de lectura binària.
Classificador = pickle.load(open("C:/Users/Xavi/Desktop/Gausbert/Classificador_Sklearn", 'rb'))

#Obrim el fitxer de text que serveix per indicar si el chatbot està entrenat o no, en el cas que sigui el primer cop que 
#s'executa el programa en un nou dispositiu, es realitzarà el procediment següent, ja que l'arxiu per predeterminació no
#té contingut, la qual cosa indica que el chatbot no està entrenat.

#Obrim l'arxiu.
with open("C:/Users/Xavi/Desktop/Gausbert/Entrenament Chatbot.txt", "r+") as arxiu:
	#Es llegeix el seu contingut i si no hi ha res escrit, el programa fa el següent: 
	text_arxiu = arxiu.read()
	if text_arxiu == "":
		#Importa les llibreries de chatbot i el mètode d'entrenament.
		from chatterbot.trainers import ListTrainer

		#Estableix un Chatbot nou i l'entrena a partir de les converses guardades a l'arxiu "conversations.corpus.txt".
		Gausbert = ChatBot('Gausbert')
		Gausbert.set_trainer(ListTrainer)
		with open("C:/Users/Xavi/Desktop/Gausbert/català corpus chatbot/conversations.corpus.txt", "r") as converses:
			Gausbert.train(converses) 
		#A l'arxiu s'escriu "Entrenat" per la pròxima vegada que s'executi el programa sencer, així no es repeteix aquest procediment.
		arxiu.write("Entrenat")
		#Es tanca l'arxiu.
		arxiu.close()

#-------------------------------------------------------------------------------------------------------------

#Definim una funció per tractar el contingut del e-mail que es veurà a la pantalla i que quedi tot dintre del requadre on ha d'anar. 
def Tractament_text_Email(Contingut):
	#Establim un comptador que serveix per contar les lletres que hi ha al contingut inicial.
    Comptador = 0
    #I una variable on guardarem el text que sortirà a la pantalla.
    Contingut_final = ""
    #Per a cada lletra en el text:
    for i in range(len(Contingut)):
    	#40 és el màxim de lletres que poden haver-hi en una mateixa línia sense que el text surti fora del requadre.
        if Comptador == 40:  #Quan el comptador arribi a 40, s'afegirà a la variable de text una línia inferior i la lletra en qüestió.
            Contingut_final += "\n" + Contingut[i]  
            Comptador = 0    #Es restableix el comptador.
            Comptador += 1	#S'incrementa el comptador en 1.
        else:
            Contingut_final += Contingut[i] #Només s'afegeix la lletra.
            Comptador += 1   

    return Contingut_final

#Nova classe d'interfície per a la recol·lecció de dades de l'e-mail.
class GUI_email(QDialog):
	def __init__(self):
		super(GUI_email, self).__init__()
		#Finestra situada a la posició (1000, 100) a la pantalla de l'ordinador i de mida 300x200 píxels amb títol "E-mail".
		self.setGeometry(1000,100,300,200)
		self.setWindowTitle("E-mail")
		#Per evitar que l'usuari faci més gran la finestra, s'estableix la mida màxima en 300x200.
		self.setMaximumSize(300, 200)

		#Establim com a fons la imatge "FinestraEmail.jpg".
		Fons = QImage("C:/Users/Xavi/Desktop/Gausbert/GUI/FinestraEmail.jpg")
		palette = QPalette()
		palette.setBrush(10, QBrush(Fons))
		self.setPalette(palette)

		#Creació del botó per enviar les dades al programa principal.
		#Botó sense text, amb la imatge "BotóEnviarEmail.png" i de mida 45x45.
		self.botóEnviarEmail = QPushButton("", self)
		self.botóEnviarEmail.setIcon(QIcon("C:/Users/Xavi/Desktop/Gausbert/GUI/BotóEnviarEmail.png"))
		self.botóEnviarEmail.setIconSize(QSize(45, 45)) 
		#Eliminem les vores del botó, ja que si no quedaria un quadrat negre de fons.
		self.botóEnviarEmail.setStyleSheet('QPushButton{border: 0px solid;}')
		self.botóEnviarEmail.resize(45, 45)
		#Es col·loca el botó en la posició (125, 145).
		self.botóEnviarEmail.move(125, 145)

		#Creació del botó que activarà el reconeixement de veu.
		self.botóMicròfon = QPushButton("", self)
		self.botóMicròfon.resize(50,50)
		self.botóMicròfon.setIcon(QIcon("C:/Users/Xavi/Desktop/Gausbert/GUI/Icona Micròfon 50 x 50.png"))
		self.botóMicròfon.setIconSize(QSize(50, 50)) 
		self.botóMicròfon.setStyleSheet('QPushButton{border: 0px solid;}')
		#Es col·loca en la posició (245, 80).
		self.botóMicròfon.move(245,80)

		#Línia de text de color blanc situada a la posició (130, 10).
		self.Adreça_capçalera = QLabel("Adreça", self)
		self.Adreça_capçalera.setStyleSheet("color: white;")
		self.Adreça_capçalera.move(130, 10)

		#Línia de text de color blanc situada a la posició (138, 60).
		self.Cos_capçalera = QLabel("Cos", self)
		self.Cos_capçalera.setStyleSheet("color: white;")
		self.Cos_capçalera.move(138, 60)

		#Línia de text buida, de mida 210x90 i situat a (24, 60), on s'escriurà el text del reconeixement de veu.
		self.Cos_text = QLabel("                                      " 
                             "\n                                      "
                             "\n                                      "
                             "\n                                      ", self)
		self.Cos_text.resize(210, 90)
		self.Cos_text.move(24, 60)

		#Element que permet l'entrada de text escrit i on s'introduirà l'adreça del destinatari.
		self.InputAdreça = QLineEdit(self)
		#Sense vores negres.
		self.InputAdreça.setFrame(False)
		#El color de la barra que hi ha al fons, per tal que sembli un únic element.
		self.InputAdreça.setStyleSheet("background-color: rgb(236, 230, 206);") 
		self.InputAdreça.move(38, 26)
		self.InputAdreça.resize(223, 30)

		#En clicar "botóMicròfon" s'activa el reconeixement de veu.
		self.botóMicròfon.clicked.connect(self.Obtenir_contingut_email)
		#En clicar "botóEnviarMail" es llegeix el que hi ha escrit a la part de l'adreça i el contingut 
		#reconegut, i "s'envia" a la MainWindow.
		self.botóEnviarEmail.clicked.connect(self.Obtenir_dades_email)

		#Mostra la finestra.
		self.show()


	#Funció del reconeixement de veu.
	def Reconeixement_veu_email(self):
		Contingut_reconegut = ""
		Contingut_reconegut_per_veure_GUI = ""
		Reconeixedor = sr.Recognizer()
		#El device_index indica el micròfon que s'utilitza, el número 0 és el que ve de sèrie amb l'ordinador, per utilitzar
		#un altre micròfon només s'ha de cambiar l'índex a un altre dígit.
		with sr.Microphone(device_index=0) as source:
			Reconeixedor.adjust_for_ambient_noise(source, duration = 1)
			Audio = Reconeixedor.listen(source) #Obtenció d'audio a partir del micrófon

		try:
			#S'utilitza el reconeixedor de google per passar l'àudio a text.
			Contingut_reconegut = Reconeixedor.recognize_google(Audio, language="ca-ES")
            
            #Aquí cridem a la funció definida anteriorment que guardarà a la variable "Contingut_reconegut_per_veure_GUI"
            #el text tractat, de forma que en aquesta variable hi haurà el text correctament col·locat perquè es vegi bé a la interfície. 
			Contingut_reconegut_per_veure_GUI = Tractament_text_Email(Contingut_reconegut)
			#A la línia de text que abans era buida s'hi col·loca el text de la variable "Contingut_reconegut_per_veure_GUI".
			self.Cos_text.setText(Contingut_reconegut_per_veure_GUI)
		except:
			#Si en el procés sorgeix cap error, no es veurà res a la pantalla i no hi haurà contingut a l'e-mail. 
			Contingut_reconegut = ""

		return Contingut_reconegut

	def Obtenir_contingut_email(self):
		#Guarda a la propietat de la classe el que la funció retorna, és a dir, el contingut de l'e-mail.
		MainWindow.Contingut = self.Reconeixement_veu_email()

	def Obtenir_dades_email(self):
		#Guarda a la propietat de la classe l'adreça que hi hagi a "InputAdreça".
		MainWindow.Adreça = self.InputAdreça.text()
		#Tanca la finestra i permet continuar el flux del programa general.
		self.close()


#-----------------------------------------------------------------------------------------------------------
#ALARMES_RECORDATORIS_TEMPORITZADORS
#Classe de QThread que fa sonar el to d'alarma.
class Sonar_Alarma(QThread):
	def __init__(self):
		#S'inicia l'element en segon pla.
		QThread.__init__(self)

	def run(self):
		#Es reprodueix l'arxiu d'àudio en format wav.
		winsound.PlaySound(r"C:/Users/Xavi/Desktop/Gausbert/matrix_clock.wav", winsound.SND_ASYNC)

#-------------------------------------------------------------------------------------------------------------
#Classe amb el QThread amb la funció de parar l'alarma quan l'usuari la desactiva mitjançant la tecla 'enter'.
class Parar_Alarma_Recordatori_Temporitzador(QThread):
	def __init__(self):
		#S'inicia l'element en segon pla.
		QThread.__init__(self)

	def run(self):
		#Es crea un element de la classe "Sonar_Alarma" i s'inicia el procés en segon pla que reproduirà l'arxiu amb el to d'alarma.
		self.Sonar_alarma = Sonar_Alarma()
		self.Sonar_alarma.start()
		#En un bucle infinit:
		while True:
			#Quan la tecla 'enter' sigui premuda:
			if keyboard.is_pressed("enter"):
				#Para de reproduir-se l'àudio,
				winsound.PlaySound(None, winsound.SND_ASYNC)
				#Es canvia el text de la Caixa_de_text_3 per espais en blanc, 
				MainWindow.Caixa_de_text_3.setText("                                                             ")
				#I s'amaga la imatge de la campana que acompanya les alertes. 
				MainWindow.Campana.hide()
				#Es trenca el bucle.
				break

#-------------------------------------------------------------------------------------------------------------
#Classe que, en segon pla, fa la funció d'esperar i comprovar els temps de les alarmes, els recordatoris i els temporitzadors.
class Alarma_Recordatori_temporitzador_procés_en_segon_pla(QThread):
	def __init__(self, Dígit, Hora, Recordatori, Temporitzador):
		try:
			QThread.__init__(self)
			#Segons el dígit, es portarà a terme un procés o un altre. 0 és per alarmes, 1 és per recordatoris i 2 és per temporitzadors.
			self.Dígit = Dígit
			#Hora de l'alarma o el recordatori.
			self.Hora = Hora
			#El que ha de recordar.
			self.Recordatori = Recordatori
			#El temps del temporitzador
			self.Temporitzador = Temporitzador
			
		except:
			pass

	def run(self):
		try:
			#Alarma.
			if self.Dígit == 0:
				while True:
					#Mira l'hora actual i crea una llista amb els dos números separats.
					Hora_actual = str(datetime.datetime.now().time()).split(":")
					#Llista amb el números de l'hora en que ha de sonar l'alarma separats.
					Hora_alarma = self.Hora.split(":")

					#Si l'hora actual i la de l'alarma són la mateixa:
					if int(Hora_alarma[0]) - int(Hora_actual[0]) == 0 and int(Hora_alarma[1]) - int(Hora_actual[1]) == 0:
						#El text de "Caixa_de_text_3" passa a ser l'hora i com es desactiva l'alarma
						MainWindow.Caixa_de_text_3.setText(self.Hora + " ( 'Enter' per desactivar ).")
						#Es mostra la imatge de la campana que acompanya les alertes.
						MainWindow.Campana.show()
						
						#Es trenca el bucle.
						break #
				#S'inicia el procés per parar l'alarma en segon pla. 
				self.Parar_Alarma_Recordatori_Temporitzador = Parar_Alarma_Recordatori_Temporitzador()
				self.Parar_Alarma_Recordatori_Temporitzador.start()		

			#Recordatori.
			#És el mateix codi que el de les alarmes, l'única cosa diferent és que a la pantalla també surt el que l'usuari ha
			#de recordar.
			elif self.Dígit == 1:
				while True:
					Hora_actual = str(datetime.datetime.now().time()).split(":")
					Hora_recordatori = self.Hora.split(":")


					if int(Hora_recordatori[0]) - int(Hora_actual[0]) == 0 and int(Hora_recordatori[1]) - int(Hora_actual[1]) == 0:
						MainWindow.Caixa_de_text_3.setText(self.Hora + " --> " + self.Recordatori + 
															"\n( 'Enter' per desactivar ).")
						print(self.Recordatori)
						MainWindow.Campana.show()
						
						break
				self.Parar_Alarma_Recordatori_Temporitzador = Parar_Alarma_Recordatori_Temporitzador()
				self.Parar_Alarma_Recordatori_Temporitzador.start()

			#Temporitzador.
			elif self.Dígit == 2:
				#Es fa al programa esperar els segons indicats per l'usuari.
				time.sleep(self.Temporitzador)
				#En acabar l'espera, a la pantall surt l'avís de finalització del temporitzador.
				MainWindow.Caixa_de_text_3.setText("Compte enrere finalitzat" + " ( 'Enter' per desactivar ).")
				#Es mostra la imatge de la campana que acompanya les alertes.
				MainWindow.Campana.show()
				#S'inicia el procés per parar l'avís en segon pla.
				self.Parar_Alarma_Recordatori_Temporitzador = Parar_Alarma_Recordatori_Temporitzador()
				self.Parar_Alarma_Recordatori_Temporitzador.start()

		except :
			pass


#--------------------------------------------------------------------------------------------------------------------------------
#La classe principal, conté la major part del programa.
class MainWindow(QWidget):
	def __init__(self):
		#Variable booleana per evitar que el programa realitzi tot el procès si ha ocorregut un error amb el reconeixement de veu.
		self.Reconeixement_sense_error = False

		#Finestra de mida 300x160 i títol "Gausbert" que apareix a la posició (1000, 100) de la pantalla .
		GUI = QWidget.__init__(self)
		self.setGeometry(1000,100,300,160)
		self.setWindowTitle("Gausbert")
		self.setMaximumSize(300, 160)

		#S'estableix com a fons la imatge "Fons.jpg".
		Fons = QImage("C:/Users/Xavi/Desktop/Gausbert/GUI/Fons.jpg")
		palette = QPalette()
		palette.setBrush(10, QBrush(Fons))                     # 10 = Windowrole
		self.setPalette(palette)

		#Únic botó de la finestra, serveix per activar el reconeixement de veu principal,
		#sense text i amb la imatge "Icona Micròfon 50 x 50.png".
		self.botóMicròfon = QPushButton("", self)
		self.botóMicròfon.resize(50,50)
		self.botóMicròfon.setIcon(QIcon("C:/Users/Xavi/Desktop/Gausbert/GUI/Icona Micròfon 50 x 50.png"))
		self.botóMicròfon.setIconSize(QSize(50, 50)) 
		self.botóMicròfon.setStyleSheet('QPushButton{border: 0px solid;}')
		#Es col·loca a la posició (230, 10).
		self.botóMicròfon.move(230,10)

		#Primer element de text, el seu contingut serà l'ordre de l'usuari i el mostrarà a pantalla.
		#Inicialment el text és "Clica i digues alguna cosa -->" per indicar a l'usuari què ha de fer 
		#per utilitzar l'aplicació i té un color gris per no ressaltar massa.
		self.Caixa_de_text_1 = QLabel("            Clica i digues alguna cosa -->", self)
		self.Caixa_de_text_1.setStyleSheet("color: grey;")
		self.Caixa_de_text_1.move(26, 28.5)

		#Segon element de text, el seu contingut és la resposta de l'assistent, que variarà en cada cas.
		#Inicialment conté el text "Hola, en què et puc ajudar?". 
		self.Caixa_de_text_2 = QLabel("    Hola, en què et puc ajudar?                              ", self)
		self.Caixa_de_text_2.move(99, 87.5)

		#Tercer element de text, aquest mostrarà les alertes quan acabi una alarma, un recordatori o un temporitzador.
		#Inicialment no conté text.  
		self.Caixa_de_text_3 = QLabel("                                                                    ", self)
		#Text de color blanc per ressaltar sobre fons gris.
		self.Caixa_de_text_3.setStyleSheet("color: white;")
		self.Caixa_de_text_3.move(65, 126)

		#L'element campana és un element de text sense informació escrita, només té una imatge d'una campana que 
		#es mostrarà, juntament amb el text de "Caixa_de_text_3" en finalitzar una alarma, un recordatori 
		#o un temporitzador. Inicialment és invisible.
		self.Campana = QLabel(self)
		pixmap = QPixmap('C:/Users/Xavi/Desktop/Gausbert/GUI/Campana.png')
		self.Campana.setPixmap(pixmap)
		self.Campana.resize(35, 35)
		self.Campana.move(25, 118)
		self.Campana.hide()

		#Les dues variables que s'utilitzaran en la funció d'email.
		self.Contingut = ""
		self.Adreça = ""

		#En ser clicat el botó botóMicròfon, es porta a terme la funció escoltar.
		self.botóMicròfon.clicked.connect(self.Escoltar)




	#Funció que representa el 80% del projecte, té tots els processos per a cada tipus d'ordre.
	#El seu únic argument és l'ordre de l'usuari.
	def Predicció(self, Ordre):
		#La variable Resposta_assistent és global perquè així des de totes parts del programa es pot modificar el seu valor.
		global Resposta_assistent 
		#Si no hi ha hagut cap error amb el reconeixement de veu:
		if self.Reconeixement_sense_error:
			try:
				Resposta_assistent = ""
				#Se separen les paraules de l'ordre i es guarden en una llista.
				Ordre_llista = Ordre.split()
				#Si la primera paraula és "Gausbert" o "gausbert", l'elimina de la llista.
				if Ordre_llista[0] == "Gausbert" or Ordre_llista[0] == "gausbert":
					Ordre_llista.remove(Ordre_llista[0])
				#Es carrega el Word2Vec (Paraula a vector).
				vectors_ca = "C:/Users/Xavi/Desktop/Gausbert/ca/ca.bin"
				model = Word2Vec.load(vectors_ca)
				#Llista buida per contenir els vectors.
				Ordre_llista_embeddings = []
				#Per a cada paraula a la llista:
				for paraula in Ordre_llista:
					try:
						#Es busca la llista de vectors que correspon.
						Embedding = model.wv[paraula]
						#Les prediccions de la xarxa neuronal només funcionen amb vectors fila, per tant,
						#a la llista Ordre_llista_embeddings afegim només el primer vector de la paraula.
						Ordre_llista_embeddings.append(Embedding[0])
					#En cas que no hi hagués vector per a la paraula, s'intenta fer el mateix, 
					#però amb la mateixa paraula en minúscules.
					except:
						try:
							Embedding = model.wv[paraula.lower()]
							Ordre_llista_embeddings.append(Embedding[0])
						except:
							#I si no hi hagués vectors per a la paraula en minúscules,
							#s'afegeix a la llista un 0.
							Ordre_llista_embeddings.append(0)
	 	
	 			#S'omple la llista de zeros fins que contingui 15 elements en total.
				Límit_de_paraules = 15
				Ordre_llista_embeddings_zeros = [0]*Límit_de_paraules
				índex_de_parada = min(len(Ordre_llista_embeddings), Límit_de_paraules)
				Ordre_llista_embeddings_zeros[:índex_de_parada] = Ordre_llista_embeddings[:índex_de_parada]
				Ordre_llista_embeddings = Ordre_llista_embeddings_zeros  

				#Amb la xarxa neuronal es fa la predicció de la llista d'embeddings, però en forma de vector
				#fila de 15 columnes, és a dir, en lloc de ser [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
				#és [0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 ].
				Skpredicció = Classificador.predict([np.array(Ordre_llista_embeddings)])
	 		
				#Com que la predicció serà una llista amb un vector fila ([[0  0  0  0  0  0]]), agafem el primer
				#i únic element, què és el que indica realment la predicció i, ho convertim en una llista
				#per poder tractar millor el seu contingut.
				Skpredicció = Skpredicció[0]
				Skpredicció = Skpredicció.tolist()

				Jipiti = ["obre", "Obre", "Obra", "obra", "Obrir", "obrir"]
				if Ordre_llista[0] in Jipiti:
					Skpredicció = [0, 0, 0, 0, 0, 1]
				print(Skpredicció)

	  			#Si el primer element és un 1, això ens indica que l'ordre pertany a la
	  			#categoria d'alarmes, recordatoris i temporitzadors.
	  			#Skpredicció = [1, 0, 0, 0, 0, 0].
				if Skpredicció[0] == 1:
						
					Frase = Ordre
					#Llista amb les paraules de l'ordre.
					Paraules_frase = Frase.split()
					#Primera paraula en minúscules
					Paraules_frase[0] = Paraules_frase[0].lower()


					#La llibreria Speech Recognition normalment posa l'hora en format hores:minuts,
					#en formar-se la llista, és tractada com un únic element de text per exemple, si l'ordre és 
					#"Alarma 3:00" la llista de paraules serà ["Alarma", "3:00"].

					#Ja que la llibreria ja reconeix l'hora, la majoria del codi de les següents funcions
					#no s'utilitza, però es manté per algunes excepcions.

					#Per això s'han de separar els dígits,el següent bucle mira si a cada element de la
					#llista hi ha ":" i separa els números,introduïnt-los a la llista a la posició
					#on eren abans, quedant la llista de la següent manera: ["Alarma", "3", "00"].
					
					for i in range(len(Paraules_frase)):
						if ":" in Paraules_frase[i]:
							Dígits_separats = Paraules_frase[i].split(":")
							Posició = Paraules_frase.index(Paraules_frase[i])		
							Paraules_frase.pop(i)
							for i in range(len(Dígits_separats)):
								Paraules_frase.insert(i + Posició, Dígits_separats[i])

					#Llista de paraules clau per a la següent part del codi.
					Paraules_clau = ["alarma", "recorda", "recordatori", "recorda'm", "enrere", "temporitzador"]
					#Llista on s'emmagatzemaràn les paraules filtrades i llestes per utilitzar a les funcions següents.
					Paraules_frase_2 = []
					p = 0

					#Aquest bucle filtra les paraules de l'ordre, el que fa és analitzar cada paraula, si no es 
					#troba a la llista Paraules_clau, no l'afegeix a la llista Paraules_frase_2, en el moment
					#que detecti una que s'hi trobi a les dues llistes, l'afegeix a Paraules_frase_2 i a partir
					#d'aquí, afegeix les restants. D'aquesta manera ens assegurem que la primera paraula 
					#és una de Paraules_clau i així després, mirant la primera paraula de la sèrie, el programa pot 
					#saber quin mètode aplicar.
					#Exemple: 
					#["estableix", "una", "alarma", "per", "a", "les", "6", "00"] --->
					#["alarma", "per", "a", "les", "6", "00"]
					for paraula in Paraules_frase:
						if p == 0:
							if paraula in Paraules_clau:
								Paraules_frase_2.append(paraula)
								p = 1
							else:
								pass
						else:
							Paraules_frase_2.append(paraula)



					#Funció per a les alarmes.
					def Alarma(Paraules_frase_2):
						global Resposta_assistent

						#Llista on s'aniran afegint els nombres de l'alarma.
						Hora = []	
						#Eliminem la primera paraula de la llista, que és "alarma".
						Paraules_frase_2.remove(Paraules_frase_2[0])	


						#En aquesta part només s'itenta buscar l'hora que l'usuari vol, per tant altres elements 
						#que es trobin a la frase no es tindran en compte.

						#Una avantatge que hi ha a la llibreria Speech Recognition és que pot reconèixer hores, 
						#tot i això, a vegades falla i reconeix els números com a paraules,
						#per tant, aquesta funció soluciona aquest problema, ja que és capaç de tractar dígits i paraules. 


						for i in range(len(Paraules_frase_2)):


							#Això és un mètode per evitar confusions amb l'hora per part de la màquina i per assegurar que només hi hagi hores i minuts.

							#Si la llista Hora no conté més de 2 elements:
							if len(Hora) < 2:	


								

								#Ja que no només ens podem referir a l'hora amb dígits, la següent part del codi 
								#tracta amb les paraules claus que normalment s'utilitza:

								#Si l'element en aquesta posició és "quart":
								if Paraules_frase_2[i] == "quart":
									#S'afegeix a la llista Hora el 15.													
									Hora.append("15")
								
								#Si l'element en aquesta posició és "mitja":
								elif Paraules_frase_2[i] == "mitja":	
									#S'afegeix a la llista Hora el 30.
									Hora.append("30")	

								elif Paraules_frase_2[i] == "menys":

									#Com que també es pot utilitzar el "quart" davant del menys:

									#Si l'element que hi ha en la següent posició és "quart":
									if Paraules_frase_2[i + 1] == "quart":	
										Hora.append("45")	

									#Si no ho és:
									else:	
										#S'afegeix a la llista Hora el número resultant de restar el 
										#número de la següent posició a 60.
										Hora.append(str(60-int(Paraules_frase_2[i + 1]))) 

									#Com que es tracta de "menys", el que es fa a continuació és restar 
									#una unitat a l'hora registrada, així que si l'hora és 3 menys 20, 
									#aquesta part canvia el 3 pel 2:

									#Canviem el número que hi hagi a la primera posició de la llista pel mateix número menys 1.
									Hora[0] = str(int(Hora[0]) - 1)	

								if Paraules_frase_2[i].isdigit():	#Si l'element en aquesta posició és un número...
									Hora.append(Paraules_frase_2[i])	#S'afegeix a la llista Hora l'element


						#Aquí obtenim l'hora que hi hagi en aquest moment i separem els elements que hi hagi entre dos 
						#punts, per exemple, si l'hora en aquest moment fos 15:51:53:, obtindríem la llista ["15", "51", "53"],
						#d'aquesta manera serà molt més fàcil d'utilitzar per fer comparacions amb l'hora de l'alarma.
						#Hora[0] i Hora_actual[0] contenen les hores.
						#Hora[1] i Hora_actual[1] contenen els minuts.
						#El segons no són necessaris per a les següents tasques.  

						#Es crea una llista amb els números de la hora actual
						Hora_actual = str(datetime.datetime.now().time()).split(":")	


						#Com que també pot ser que l'usuari no indiqui una hora específica, en aquesta part tenim una excepció 
						#d'errors, ja que si no s'ha captat cap hora, ni Hora[0] ni Hora[1] existeixen i això causaria un
						#error, la qual cosa no permetria al codi seguir funcionant.


						try:


						#També es mira si tant les hores com els minuts superen les 24 i les 60 unitats, si és el cas, 
						#el codi fa saltar un error que faria passar directament a l'except de sota. 


							if int(Hora[0]) > 24 or int(Hora[1]) > 60:	
								Hora = []	
								raise Hora_error


						#La següent part és un mètode per afegir 12 unitats a les hores de l'alarma en cas que sigui una 
						#hora inferior a l'actual, per exemple, si l'usuari demana una alarma a les 3:15, però l'hora 
						#actual és 14:34, en lloc d'establir-la a les 3:15, serà una alarma per a les 15:15, en canvi,
						#si l'hora actual és 23:46, l'alarma serà a les 3:15.


							else:
								if int(Hora[0]) < int(Hora_actual[0]) and int(Hora[0]) <= 12 and (int(Hora[0]) + 12) >= int(Hora_actual[0]):	
									Hora[0] = str(int(Hora[0]) + 12)	
									if int(Hora[0]) == int(Hora_actual[0]) and int(Hora[1]) <= int(Hora_actual[1]): 
										Hora[0] = str(int(Hora[0]) - 12)

						except:	


							#Com que abans s'ha presentat la possibilitat que l'usuari no hagués dit una hora en concret 
							#o no hi hagués minuts, la següent part cobreix ambdós problemes. Si l'error és degut
							#a la falta de minuts, se soluciona afegint "00" a la llista i després utilitzant el mateix codi
							#que unes línies més amunt per afegir o no 12 unitats, però si el problema és perquè no hi ha 
							#ni hores ni minuts, s'agafa l'hora actual i se suma una hora.


							if len(Hora) == 1:	
								Hora.append("00")	
								if int(Hora[0]) < int(Hora_actual[0]) and int(Hora[0]) <= 12 and (int(Hora[0]) + 12) >= int(Hora_actual[0]):
									Hora[0] = str(int(Hora[0]) + 12)
									if int(Hora[0]) == int(Hora_actual[0]) and int(Hora[1]) <= int(Hora_actual[1]):
										Hora[0] = str(int(Hora[0]) - 12)

							else:
								#S'afegeixen a la llista Hora les hores actuals més 1 unitat.
								Hora.append(str(int(Hora_actual[0]) + 1))	
								#S'afegeixen a la llista Hora els minuts actuals.
								Hora.append(Hora_actual[1])		


						#Un altre problema que pot sorgir és una confusió amb els minuts, per exemple, si l'hora establerta 
						#per l'usuari és tres i 2, això seria traduït pel codi com 3:2, però podria ser entès com a 3:20, 
						#per tant, les línies a continuació canvien el 3:2 per 3:02.


						if len(Hora[1]) == 1:	#Si la quantitat de minuts és menor que una desena...
							Hora[1] = "0" + Hora[1]	   #Es coloca un zero davant


						#Per evitar altres errors, per exemple que l'alarma no arribi a sonar mai, les hores que siguin 24 
						#es canvien a 00 i els minuts que són iguals a 60 també es canvien per 00.


						if int(Hora[0]) == 24:
							Hora[0] = "00"

						elif int(Hora[1]) == 60:
							Hora[1] = "00"


						#Obtenim una cadena de text amb l'hora de l'alarma.


						Hora_alarma = Hora[0] + ":" + Hora[1]	

						#La resposta de l'assistent que es mostrarà a la pantalla.
						Resposta_assistent = "Alarma establerta per a les " + str(Hora_alarma) + "."

					
						#S'inicien els processos en segon pla, per esperar fins a l'hora i posar 
						#l'avís en pantalla. 
						self.Procés = Alarma_Recordatori_temporitzador_procés_en_segon_pla(0, Hora_alarma, "", 0)
						self.Procés.start()
				


					#Funció per als recordatoris.
					def Recordatori(Paraules_frase_2):
						global Resposta_assistent

						#Recordatori és quasi igual a Alarma, però en aquesta funció la resta de paraules 
						#que intervenen en l'obtenció de l'hora són guardades en una llista que serà
						#filtrada després per obtenir el que s'ha de recordar.
			
						Guardant_hora = False
						Llista_recordatori = []
						Hora = []
						Hora_recordatori = ""
						Recordatori = ""
						Hora_paraules_clau = ["quart", "mitja", "menys"]
						#Paraules clau per a saber si els números en la llista són destinats a l'hora o 
						#números qualsevol.
						Recordatori_paraules_clau = ["a", "les", "que", "i", "per", "la"]
						Paraules_frase_2.remove(Paraules_frase_2[0])

						for i in range(len(Paraules_frase_2)):


							if len(Hora) < 2:

								#Si l'element en aquesta posició és un dígit i les paraules anteriors són 
								#una combinació de paraules:
								if Paraules_frase_2[i].isdigit() and (Paraules_frase_2[i - 2] == "a" or Paraules_frase_2[i - 2] == "per") and (Paraules_frase_2[i - 1] == "les" or Paraules_frase_2[i -1] == "la"):
									#S'afegeix a la llista.
									Hora.append(Paraules_frase_2[i])
									#L'estat Guardant_hora passa a ser True.
									Guardant_hora = True #
					
								#Per evitar que les paraules "quart", "mitja" i "menys" que no estan destinades a
								#ser part de l'hora siguin tractades com a tal, l'estat Guardant_hora només 
								#és True quan l'element anterior és un dígit que compleix els requeriments per
								#ser part de l'hora de l'alarma, i passa a ser False després d'haver afegit 
								#els minuts corresponents.
								elif Guardant_hora: 

									if Paraules_frase_2[i] == "quart":
										Hora.append("15")
										Guardant_hora = False 

									elif Paraules_frase_2[i] == "mitja":
										Hora.append("30")
										Guardant_hora = False 

									elif Paraules_frase_2[i] == "menys":

										if Paraules_frase_2[i + 1] == "quart":
											Hora.append("45")
											Guardant_hora = False 

										else:
											Hora.append(str(60-int(Paraules_frase_2[i + 1])))
											Guardant_hora = False 

										Hora[0] = str(int(Hora[0]) - 1)


									elif Paraules_frase_2[i].isdigit():
										Hora.append(Paraules_frase_2[i])
										Guardant_hora = True 

						#Quan una paraula no compleix cap dels requisits anteriors, s'afegeix a la llista de recordatori
									else: 
										Llista_recordatori.append(Paraules_frase_2[i]) #

								else: 
									Llista_recordatori.append(Paraules_frase_2[i]) #

							else: 
								Llista_recordatori.append(Paraules_frase_2[i]) #

						Hora_actual = str(datetime.datetime.now().time()).split(":")

						try:
							if int(Hora[0]) > 24 or int(Hora[1]) > 60:
								Hora = []
								raise Hora_error

							else:
								if int(Hora[0]) < int(Hora_actual[0]) and int(Hora[0]) <= 12 and (int(Hora[0]) + 12) >= int(Hora_actual[0]):
									Hora[0] = str(int(Hora[0]) + 12)
									if int(Hora[0]) == int(Hora_actual[0]) and int(Hora[1]) <= int(Hora_actual[1]):
										Hora[0] = str(int(Hora[0]) - 12)

						except:
							if len(Hora) == 1:
								Hora.append("00")
								if int(Hora[0]) < int(Hora_actual[0]) and int(Hora[0]) <= 12 and (int(Hora[0]) + 12) >= int(Hora_actual[0]):
									Hora[0] = str(int(Hora[0]) + 12)
									if int(Hora[0]) == int(Hora_actual[0]) and int(Hora[1]) <= int(Hora_actual[1]):
										Hora[0] = str(int(Hora[0]) - 12)

							else:
								Resposta_assistent ="Hi ha hagut un problema, s'ha programat l'alarma per d'aquí una hora"
								Hora.append(str(int(Hora_actual[0]) + 1))
								Hora.append(Hora_actual[1])

						if len(Hora[1]) == 1:
							Hora[1] = "0" + Hora[1]

						if int(Hora[0]) == 24:
							Hora[0] = "00"

						elif int(Hora[1]) == 60:
							Hora[1] = "00"

						Hora_recordatori = Hora[0] + ":" + Hora[1]

						#Es filtra els elements del recordatori que apareixen també a la llista Recordatori_paraules_clau.

						for i in range(2):
							try:
								for i in range(len(Recordatori_paraules_clau)): #
									if Llista_recordatori[-1] in Recordatori_paraules_clau: #
										Llista_recordatori.pop(-1) #

									elif Llista_recordatori[0] in Recordatori_paraules_clau: #
										Llista_recordatori.pop(0) #
								break
							except:
 
								Recordatori = [""]

						#Obtenim la cadena de text amb el recordatori.
						for paraula in Llista_recordatori: 
							Recordatori += paraula + " " 

						#Resposta de l'assistent que sortirà en pantalla.
						Resposta_assistent = "Et recordaré " + Recordatori + "."


						self.Procés = Alarma_Recordatori_temporitzador_procés_en_segon_pla(1, Hora_recordatori, Recordatori, 0)
						self.Procés.start()
						



					#Funció del compte enrere.
					def Compte_enrere(Paraules_frase_2):
						#Llista on aniran tots els segons, utilitzem segons perquè la llibreria time, que
						#serveix per fer esperar el programa l'estona desitjada, utilitza segons en lloc de mil·lisegons.
						Segons = []
						Temps = 0
						#Afegim un espai a la llista perquè en el següent bucle es mira també l'element que hi ha
						#a la posició següent i sense l'element adddicional, a l'última iteració causaria un error perquè
						#no hi hauria un element a la següent posició
						Paraules_frase_2.append(" ")
						for i in range(len(Paraules_frase_2) - 1):
							#Si l'element és un dígit:
							if Paraules_frase_2[i].isdigit():
								#Si el següent element és "hores", s'afegeix a la llista Segons les hores en segons.
								if Paraules_frase_2[i + 1] == "hores" or Paraules_frase_2[i + 1] == "hora":
									Segons.append(int(Paraules_frase_2[i]) * 3600)

								#Si és "minuts", s'afegeixen els minuts en segons.
								elif Paraules_frase_2[i + 1] == "minuts":
									Segons.append(int(Paraules_frase_2[i]) * 60)

								#Si és "segons", s'afegeixen sense cap modificació
								elif Paraules_frase_2[i + 1] == "segons":
									Segons.append(int(Paraules_frase_2[i]))

								#Si no hi ha cap element en la següent posició, s'afegeix el dígit com si fossin segons
								else:
									Segons.append(int(Paraules_frase_2[i]))

						#Se sumen tots els segons de la llista.
						for i in range(len(Segons)):
							Temps += int(Segons[i])


						#S'inicien els processos en segon pla, on el programa esperarà els segons que hi hagi a Temps
						self.Procés = Alarma_Recordatori_temporitzador_procés_en_segon_pla(2, 0, "", Temps)
						self.Procés.start()
						

					#Aquí és on la filtració de les línies de la 451 a la 459 ens faciliten el procés.
					#Segons la primera paraula de la llista Paraules_frase_2, es farà servir una funció o una altra.

					if Paraules_frase_2[0] == "alarma":
						Alarma(Paraules_frase_2)


					elif Paraules_frase_2[0] == "recordatori" or Paraules_frase_2[0] == "recorda'm" or Paraules_frase_2[0] == "recorda":
						Recordatori(Paraules_frase_2) 


					elif Paraules_frase_2[0] == "enrere" or Paraules_frase_2[0] == "temporitzador":
						Resposta_assistent = "Compte enrere establert."
						Compte_enrere(Paraules_frase_2)
				



				#Si a Skpredicció, l'1 es troba a la posició 1, l'ordre és de la categoria "Cerca a Internet".
				#Skpredicció = [0, 1, 0, 0, 0, 0].
				elif Skpredicció[1] == 1:
					#Categoria = "Cerca a Internet"

					def Cerca_a_Internet(Frase):
						#Paraules a eliminar de la llista, normalment és la primera paraula de Frase.
						Paraules_a_eliminar = ["Cerca", "Busca", "cerca", "busca","Cercar", "Buscar", "cercar", "buscar"]
						#Llista amb les paraules de Frase.
						Paraules_element_a_cercar_no_filtrades = Frase.split()
						Paraules_element_a_cercar_filtrades = []
						Element_a_cercar_filtrat = ""
						#Si la paraula no és a Paraules_a_eliminar, s'afegeix a les paraules filtrades.
						for paraula in Paraules_element_a_cercar_no_filtrades:
							if paraula in Paraules_a_eliminar:
								pass
							else:
								Paraules_element_a_cercar_filtrades.append(paraula)
						#Obtenim la cadena de text amb l'element a cercar.
						for paraula in Paraules_element_a_cercar_filtrades:
							Element_a_cercar_filtrat += (paraula + " ")
						#Busquem a google l'element.
						webbrowser.open("https://google.com/search?q=%s" % Element_a_cercar_filtrat)

					Cerca_a_Internet(Ordre)
					Resposta_assistent = "Cercant..."

				#Si es troba a la tercera posició, la categoria és "Chatbot".
				#Skpredicció = [0, 0, 1, 0, 0, 0]. 
				elif Skpredicció[2] == 1:

					def Chatbot(Frase):
						global Resposta_assistent
						#Carreguem el chatbot.
						Gausbert = ChatBot('Gausbert')

						Resposta_assistent = str(Gausbert.get_response(Frase))

					Chatbot(Ordre)


				#A la quarta posició indica que pertany a la categoria "Clima".
				#Skpredicció = [0, 0, 0, 1, 0, 0]
				elif Skpredicció[3] == 1:

					def Climatologia(Frase):
						global Resposta_assistent
						Paraules_a_filtrar = ["quin", "quina", "és", "la", "el", "fa", "a", "busca", "cerca", "de", "relativa","hi", "ha", "que"]
						Ciutat_a_cercar_migfiltrada = ""
						Ciutat_a_cercar_filtrada = ""
						Caracteristica_desitjada = ""
						Paraules_Ciutat_a_cercar = Frase.split()
						Paraules_Ciutat_a_cercar[0] = Paraules_Ciutat_a_cercar[0].lower()
						#Si la paraula no és a Paraules_a_filtrar, s'afegeix a Ciutat_a_cercar_migfiltrada.
						for paraula in Paraules_Ciutat_a_cercar:
							if paraula in Paraules_a_filtrar:
								pass
							else:
								Ciutat_a_cercar_migfiltrada += paraula + " "

						Ciutat_a_cercar_migfiltrada = Ciutat_a_cercar_migfiltrada.split()
						#Es busca la característica desitjada per l'usuari.
						for i in range(len(Ciutat_a_cercar_migfiltrada)):
							if Ciutat_a_cercar_migfiltrada[i] == "temperatura":
								Caracteristica_desitjada = "temperatura"
							elif Ciutat_a_cercar_migfiltrada[i] == "temps":
								Caracteristica_desitjada = "temps"
							elif Ciutat_a_cercar_migfiltrada[i] == "humitat":
								Caracteristica_desitjada = "humitat"
							elif Ciutat_a_cercar_migfiltrada[i] == "pressió":
								Caracteristica_desitjada = "pressió"
								#Si ja hi ha una ciutat no es fa res.
							elif len(Ciutat_a_cercar_filtrada) > 1:
								pass
							else:
								#Si la paraula en aquesta iteració no és cap característica, és perquè és la ciutat 
								#de la qual es vol saber. 
								Ciutat_a_cercar_filtrada += Ciutat_a_cercar_migfiltrada[i]

						#Clau del compte de la web de l'API.
						key = "530ed146e3e8c6add062d4878c81112a"
						#Inici de l'enllaç.
						base_url = "http://api.openweathermap.org/data/2.5/weather?"
						#Afegim tots els components i variables per crear l'enllaç i cerquem.
						url_completa = base_url + "appid=" + key + "&q=" + Ciutat_a_cercar_filtrada + "&units=metrics" #Metrics para que la temperatura salga en Celsius
						resposta = requests.get(url_completa)
						#Obtenim la resposta en format .json.
						x = resposta.json()
						#Si no hi ha hagut error 404:
						if x["cod"] != "404": 

							#A y es guarden totes les dades.
							y = x["main"]

							Temperatura_actual = y["temp"]

							Pressió_actual = y["pressure"]

							Humitat_actual = y["humidity"]

							z = x["weather"]

							Descripció = z[0]["description"]

							if Caracteristica_desitjada == "temperatura":
								Resposta_assistent = str(round(Temperatura_actual - 273)) + " ºC"
							elif Caracteristica_desitjada == "temps":
								Resposta_assistent =  str(round(Temperatura_actual - 273)) + " ºC, " + str(Descripció)
							elif Caracteristica_desitjada == "humitat":
								Resposta_assistent = str(Humitat_actual) + " %"
							elif Caracteristica_desitjada == "pressió":
								Resposta_assistent =  str(Pressió_actual) + " hPa"

							else: 
								Resposta_assistent = " No s'ha trobat la ciutat "

						else:
							Resposta_assistent = " No s'ha trobat la ciutat "

					Climatologia(Ordre)


				#A la posició 5, l'ordre és de tipus "E-mail".
				#Skpredicció = [0, 0, 0, 0, 1, 0].
				elif Skpredicció[4] == 1:


					def Email(Frase):
						global Resposta_assistent
						#Llista amb les paraules de l'ordre, la primera en minúscules.
						Paraules_frase = Frase.split()
						Paraules_frase[0] = Paraules_frase[0].lower()

						Paraules_clau = ["correu", "missatge", "email", "mail"]
						Paraules_frase_2 = []
						p = 0

						#S'aplica el mateix procediment que amb les alarmes per tal que la primera paraula
						#de la llista sigui una de les que hi ha a Paraules_clau.
						for paraula in Paraules_frase:
							if p == 0:
								if paraula in Paraules_clau:
									Paraules_frase_2.append(paraula)
									p = 1
								else:
									pass
							else:
								Paraules_frase_2.append(paraula)

						Assumpte_llista = []
						Assumpte = ""
						Guardant_assumpte = False
						Cos = ""
						Elements_a_filtrar_cos = ["Escriu", "que", "Posa", "Com", "a", "cos", "De"]

						for i in range(len(Paraules_frase_2)):
							#Si hi ha la següent combinació de paraules:
							if Paraules_frase_2[i - 1] == "amb" or Paraules_frase_2[i - 1] == "a" and Paraules_frase_2[i] == "assumpte":
								#S'agafa l'índex on es troba la paraula "assumpte".
								índex = i
								#S'elimina de la llista.
								Paraules_frase_2.remove(Paraules_frase_2[i])
								Guardant_assumpte = True

							else:
								pass

							try:
								if Paraules_frase_2[i + 1] == "posa" or Paraules_frase_2[i + 1] == "escriu":
									Paraules_frase_2.remove(Paraules_frase_2[i + 1])
							except:
								pass


						if Guardant_assumpte:
							#S'itera la llista des de l'índex guardat a la variable anteriorment.
							for paraula in Paraules_frase_2[índex:]:
								#Es guarden les paraules en una llista.
								Assumpte_llista.append(paraula)
						else:
							Assumpte = ""
						try:
							#S'aconsegueix la cadena de text amb l'assumpte.
							for i in range(len(Assumpte_llista)):
								Assumpte += Assumpte_llista[i] + " "
						except:
							pass

						try:
							#Inici de la finestra d'e-mail. 
							MainWindow_email = GUI_email()
							#Aquesta línia no permet el flux del programa fins que la finestra no es tanca. 
							MainWindow_email.exec_()
							#Obtenim el cos, guardat en una variable de la classe MainWindow, i el convertim en una llista.
							Cos_llista = MainWindow.Contingut
							Cos_llista = Cos_llista.split()
							#Obtenim també l'adreça.
							Adreça = MainWindow.Adreça
						except:
							pass

						#Filtració dels elements de Cos_llista.
						for i in range(len(Elements_a_filtrar_cos)):
							if Cos_llista[0] in Elements_a_filtrar_cos:
								Cos_llista.remove(Cos[0])

						#Primera lletra de la paraula inicial en majúscula.
						Cos_llista[0] = Cos_llista[0].capitalize()
				
						#Cadena de text amb el cos.
						for paraula in Cos_llista:
							Cos += paraula + " "

						try:
							#Establim connexió amb el servidor i la pàgina.
							with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
								smtp.ehlo()
								smtp.starttls()
								smtp.ehlo()

								#Inici de sessió (correu electrònic, contrasenya).
								smtp.login("gausbertassistentvirtual@gmail.com", "Contrasenya")

								#Unió dels continguts de les variables per formar l'e-mail sencer.
								Email = f'Subject: {Assumpte}\n\n{Cos}'.encode('utf-8')

								#Envia el correu (remitent, destinatari, missatge).
								smtp.sendmail("gausbertassistentvirtual@gmail.com", Adreça, Email)

							Resposta_assistent = "Correu enviat."
						except:
							#Si hi ha cap error.
							Resposta_assistent = "Error a l'enviar."

					Email(Ordre)

				#Última categoria: Interacció amb programes.
				#Skpredicció = [0, 0, 0, 0, 0, 1]
				elif Skpredicció[5] == 1:

					def Interacció_amb_programes(Frase):
						global Resposta_assistent
						Paraules_a_eliminar = ["Obre", "obre", "Obra", "obra", "Obrir", "obrir", "el", "la", "Entra", "entra", "a"]
						#Llista de paraules.
						Paraules_element_a_obrir_no_filtrades = Frase.split()
						Paraules_element_a_obrir_filtrades = []
						Element_a_obrir_filtrat = ""
						#S'eliminen les paraules de la llista Paraules_element_a_obrir_no_filtrades que es trobin
						#a Paraules_a_eliminar.
						for i in range(len(Paraules_element_a_obrir_no_filtrades)):
							if Paraules_element_a_obrir_no_filtrades[i] in Paraules_a_eliminar:
								if  Paraules_element_a_obrir_no_filtrades[i+1] in Paraules_a_eliminar:
									pass
								else:
									pass
							else:
								Paraules_element_a_obrir_filtrades.append(Paraules_element_a_obrir_no_filtrades[i])
						#Única cadena de text.
						for paraula in Paraules_element_a_obrir_filtrades:
							Element_a_obrir_filtrat += (paraula + " ")

						Resposta_assistent = "Obrint " + Element_a_obrir_filtrat
						#La funció size() ens dóna la resolució de la pantalla,guardem la quantitat de píxels de cada eix a les dues variables
						Píxels_eix_X, Píxels_eix_Y = pyautogui.size()
						#Es mou el cursor fins als 65 píxels a l'eix x i fins als píxels que hi hagi a l'eix Y menys 20 
						#en un temps de 0.05 segons (en aquesta posició hi és la barra o la icona de Cortana).
						pyautogui.moveTo(Píxels_eix_X - (Píxels_eix_X - 65), Píxels_eix_Y - 20, duration = 0.05) 
						#S'obté la posició del cursor i es guarden les seves coordenades X i Y.
						Posició_cursor_X, Posició_cursor_Y = pyautogui.position() 
						#Es fa un clic.
						pyautogui.click(Posició_cursor_X, Posició_cursor_Y) 
						#Espera d'1 segon.
						time.sleep(1) 
						#S'escriu l'element que es vol obrir.
						pyautogui.typewrite(Element_a_obrir_filtrat) 
						#El cursor es mou 30 píxels a la dreta i 530 píxels cap a dalt.
						pyautogui.moveRel(30, -530, duration = 0.05) 
						time.sleep(1)
						 #Es torna a obtenir la posició del cursor i es guarden les seves coordenades X i Y.
						Posició_cursor_X, Posició_cursor_Y = pyautogui.position()
						#Es fa un clic.
						pyautogui.click(Posició_cursor_X, Posició_cursor_Y) 


					Interacció_amb_programes(Ordre)

				#Si a la llista no hi ha cap 1, s'utilitza la funció de chatbot.
				#Skpredicció = [0, 0, 0, 0, 0, 0]
				else:
					Categoria = "Chatbot"

					def Chatbot(Frase):
						global Resposta_assistent
						Gausbert = ChatBot('Gausbert')
						Resposta_assistent = str(Gausbert.get_response(Frase))

					Chatbot(Ordre)
			

			except:
				Resposta_assistent = "S'ha produit un error"
	


	def Ordre_Veu(self):
		global Resposta_assistent
		Ordre_reconeguda = ""
		Reconeixedor = sr.Recognizer()
		with sr.Microphone(device_index=1) as source:
			Reconeixedor.adjust_for_ambient_noise(source, duration = 1)
			#Obtenció d'àudio a partir del micrófon
			Audio = Reconeixedor.listen(source) 

		try:
			#Reconeixedor de català de Google.
			Ordre_reconeguda = Reconeixedor.recognize_google(Audio, language="ca-ES")
			#Lletra de color negre.
			self.Caixa_de_text_1.setStyleSheet("color: black;")
			#Es mostra a pantalla l'ordre reconeguda.
			self.Caixa_de_text_1.setText(Ordre_reconeguda)
			self.Reconeixement_sense_error = True
		#Error, Recognizer no reconeix el que s'ha dit.
		except sr.UnknownValueError:
			self.Reconeixement_sense_error = False
			Resposta_assistent = "Ho sento, no ho he entés."
		#No s'han pogut obtenir les dades del servei de Google
		except sr.RequestError:
			self.Reconeixement_sense_error = False
			Resposta_assistent = "No hi ha connexió."


		return Ordre_reconeguda



	def Escoltar(self):
		try:
			global Resposta_assistent
			#Reconeixement de veu.
			Ordre = self.Ordre_Veu()
			time.sleep(0.1)
			#Predicció i funcions.
			self.Predicció(Ordre)
			time.sleep(0.1)
			#Es mostra la resposta de l'assistent.
			self.Caixa_de_text_2.setText(Resposta_assistent)
		except:
			self.Caixa_de_text_2.setText("Error")

#-----------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
	#Execució del programa i l'aplicació.
	app = QApplication(sys.argv)
	MainWindow = MainWindow()
	MainWindow.show()
	#El programa no acaba fins que no es tanqui l'aplicació.
	sys.exit(app.exec_())
