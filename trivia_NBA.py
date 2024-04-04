import firebase_admin
from firebase_admin import credentials, db
import random
import pygame
import time
import json
import sys

# Inicializar firebase de nustra base de datos
cred = credentials.Certificate("acces-python-firebase-adminsdk-l60g2-5a382732ba.json") # nombre del .json de nuestro proyecto
firebase_admin.initialize_app(cred, {"databaseURL": "link de tu base de datos de firebase"}) #link base de datos

# # Obtener las preguntas des de Firebase
# ref = db.reference('/')

# Lista de preguntas con respuestas correctas y opciones
with open("preguntas.json", "r", encoding="utf-8") as file:
    preguntas_juego = json.load(file)
    
# Estructura de datos para almacenar las preguntas y respuestas
trivial_data = preguntas_juego

# Inicializar Pygame
pygame.init()

# Definir colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)

# Definir dimensiones de la pantalla
ANCHO = 1200
ALTO = 600


# Icono de la ventana
pygame_icon = pygame.image.load("img/logo.png")
pygame.display.set_icon(pygame_icon)


# Poner imagen de fondo a la pantalla de inicio
try:
    fondo_inicio = pygame.image.load("img/fondo.jpg")
except pygame.error as e:
    print("Error al cargar la imagen:", e)

# Poner imagen de fondo a la pantalla de juego  
try:
    fondo_juego = pygame.image.load("img/descarga.jpg")
except pygame.error as e:
    print("Error al cargar la imagen:", e)


# Inicializar pantalla 
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("NBA Trivia")


# Funcion para renderizar el texto en una superficie   
def draw_text(text, font, color, surface, x, y, max_width=None):
    words = text.split(' ')
    space = font.size(' ')[0]  # Obtener el ancho de un espacio en la fuente
    line_spacing = font.get_linesize()  # Obtener el espaciado entre líneas

    x_pos = x
    y_pos = y
    for word in words:
        word_surface = font.render(word, True, color)
        word_width, word_height = word_surface.get_size()
        if max_width and x_pos + word_width >= x + max_width:
            x_pos = x  # Regresar al inicio de la línea
            y_pos += word_height  # Mover a la siguiente línea
        surface.blit(word_surface, (x_pos, y_pos))
        x_pos += word_width + space
    return y_pos + word_height  # Devolver la posición Y final


# Función para mostrar preguntas y opciones
def mostrar_pregunta(pregunta, opciones):
    pantalla.fill(BLANCO)
    fuente = pygame.font.Font(None, 36)
    
    texto_pregunta = fuente.render(pregunta, True, NEGRO)
    pantalla.blit(texto_pregunta, (50, 50))
    y = 150
    
    for opcion in opciones:
        texto_opcion = fuente.render(opcion, True, AZUL)
        pantalla.blit(texto_opcion, (50, y))
        y += 50
        
    pygame.display.flip()

# Funcion para mostrar puntuacion
def mostrar_puntuacion(puntuacion, surface, fuente, color):
    # Creamos un rectangulo de color blanco para ir borrando el txto en cada segundo
    surface.fill(BLANCO, (40, surface.get_height() - 60, surface.get_width(), 50))
    
    puntuacion_texto = fuente.render("Puntuación: " + str(puntuacion), True, color)
    text_rect = puntuacion_texto.get_rect()
    text_rect.midbottom = (surface.get_width() // 2, surface.get_height() - 40)
    surface.blit(puntuacion_texto, text_rect)

# Funcion para mostrar timpo restante
def mostrar_tiempo_restante(tiempo_restante, surface, fuente, color):
    # Creamos un rectangulo de color blanco para ir borrando el txto en cada segundo
    surface.fill(BLANCO, (40, surface.get_height() - 110, surface.get_width(), 50))
  
    tiempo_texto = fuente.render("Tiempo restante: " + str(tiempo_restante) + " segundos", True, color)
    text_rect = tiempo_texto.get_rect()
    text_rect.midbottom = (surface.get_width() // 2, surface.get_height() - 85)
    surface.blit(tiempo_texto, text_rect)

    
# Función para mostrar pantalla de inicio de juego
def pantalla_inicio():
    while True:
        pantalla.blit(fondo_inicio, (0, 0))
        
        norma1 = ("Utiliza los números 1, 2 y 3 respectivamente para seleccionar la opción de respuesta que consideres correcta")
        norma2 = ("Una vez que hayas seleccionado una respuesta, no podrás cambiarla. Avanza a la siguiente pregunta sin posibilidad de retractarte.")
        
        fuente = pygame.font.Font(None, 36)
        
        draw_text('Bienvenido al Trivia de NBA', fuente, BLANCO, pantalla, 80, 50, 1000)
        draw_text('Normas del Juego:', fuente, BLANCO, pantalla, 80, 125, 1000)
        
        draw_text('- Selección de respuestas:', fuente, BLANCO, pantalla, 80, 200, 1000)
        draw_text(norma1, fuente, BLANCO, pantalla, 80, 235, 1000)
        
        draw_text(' - Respuestas irrevocables:', fuente, BLANCO, pantalla, 80, 335, 1000)
        draw_text(norma2, fuente, BLANCO, pantalla, 80, 370, 1000)
        
        draw_text('¡Diviértete!', fuente, BLANCO, pantalla, 80, 470, 1000)
        
        draw_text('Presiona cualquier tecla para comenzar', fuente, BLANCO, pantalla, 80, 540, 1000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

        pygame.display.update()

# Funcion para mostrar la pantalla de juego
def pantalla_juego():
    
    # Crear un contador para responder a las preguntas
    tiempo_respuesta = 10  # tiempo en segundos para responder a cada pregunta

    random.shuffle(preguntas_juego)

    fuente = pygame.font.Font(None, 36)
    puntuacion = 0
    
    for pregunta_data in preguntas_juego:
        pregunta = pregunta_data["pregunta"]
        opciones = pregunta_data["opciones"]
        respuesta_correcta = pregunta_data["respuesta_correcta"]     
        
        mostrar_pregunta(pregunta, opciones)

        tiempo_inicial_pregunta = pygame.time.get_ticks()  # Tiempo en milisegundos cuando se inicia la pregunta
        
        while True:
            
            tiempo_actual = pygame.time.get_ticks()
            tiempo_transcurrido_pregunta = (tiempo_actual - tiempo_inicial_pregunta) // 1000
            tiempo_restante = max(tiempo_respuesta - tiempo_transcurrido_pregunta, 0)

            mostrar_tiempo_restante(tiempo_restante, pantalla, fuente, NEGRO)
            mostrar_puntuacion(puntuacion, pantalla, fuente, NEGRO)
            
            pygame.display.flip()  # Actualiza la pantalla para mostar el tiempo y la puntuación

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        respuesta_usuario = opciones[0]
                        break
                    elif event.key == pygame.K_2:
                        respuesta_usuario = opciones[1]
                        break
                    elif event.key == pygame.K_3:
                        respuesta_usuario = opciones[2]
                        break
            else:
                continue
            break

        if respuesta_usuario == respuesta_correcta:
            puntuacion += 1

    pygame.display.flip()  # Actualiza la pantalla al finalizar el juego
    
    pantalla_fin(puntuacion)

# Función para mostrar pantalla de fin de juego
def pantalla_fin(puntuacion):
    
    pantalla.blit(fondo_inicio, (0, 0))
    fuente = pygame.font.Font(None, 75)
    fuente2 = pygame.font.Font(None, 50)
    fuente3 = pygame.font.Font(None, 35)
    
    
    # Mensaje de fin de juego
    texto_fin = fuente.render("FIN DEL JUEGO", True, BLANCO)
    
    # Obtengo la informacion del texto
    ancho_texto = texto_fin.get_width()

    # Calculo las coordenada para centrar el texto mediante la informacion de la poscion del texto
    posicion_texto = ((ANCHO - ancho_texto) // 2, (ALTO - 250) // 2)

    # Dibujo el texto centrado en la pantalla
    pantalla.blit(texto_fin, posicion_texto)
    
    
    
    # Mostrar Puntuacion encima del mensaje de fin de juego
    # Paso la puntuacion a texto
    parseo = str(puntuacion)
    
    texto_puntuacion = fuente2.render("PUNTUACION: " + parseo, True, BLANCO)
    
    # Obtengo la informacion del texto
    ancho_texto = texto_puntuacion.get_width()

    # Calculo las coordenada para centrar el texto mediante la informacion de la poscion del texto
    posicion_texto = ((ANCHO - ancho_texto) // 2, (ALTO - 450) // 2)

    # Dibujo el texto centrado en la pantalla
    pantalla.blit(texto_puntuacion, posicion_texto)
    

    
    # Creo la variable donde guardare el mensaje que saldra dependiendo de la puntuacion del usuario
    mensaje = ""
    
    if puntuacion == 0:
        mensaje = "Al banquillo novato, ¡toca mejorar!"
        fondo_img = pygame.image.load("img/banquillo.jpg")
        
    elif 0 < puntuacion <= 2:
        mensaje = "¡Nada mal, ¡Sigue así!"
        fondo_img = pygame.image.load("img/esfuerzo.jpeg")
        
    elif 2 < puntuacion <= 4:   
        mensaje = "¡Partidazo! ¡Sigue adelante!"
        fondo_img = pygame.image.load("img/partidazo.jpg")
        
    elif puntuacion == 5:
        mensaje = "¡MVP! ¡MVP! ¡MVP!"
        fondo_img = pygame.image.load("img/jumbo.jpg")
    
    # Mensaje dependiendo de tu puntuacion
    # Repito el procedimiento anterior pero le cambio la altura
    texto_mensaje = fuente3.render(mensaje, True, BLANCO)
    
    # Obtengo la informacion del texto
    ancho_texto = texto_mensaje.get_width()

    # Calculo las coordenada para centrar el texto mediante la informacion de la poscion del texto
    posicion_texto = ((ANCHO - ancho_texto) // 2, (ALTO - 100) // 2)

    # Dibujo el texto centrado en la pantalla
    pantalla.blit(texto_mensaje, posicion_texto)
    
    
    
    # Obtener las dimensiones de la imagen de fondo
    ancho_img = fondo_img.get_width()
    
    # Imagen de fondo dependiendo de la puntuacion
    # Calculo las coordenada para centrar una imagen
    posicion_img = ((ANCHO - ancho_img) // 2, 300)
      
    pantalla.blit(fondo_img, posicion_img)
    
    pygame.display.flip()
    pygame.time.wait(5000)

def volver_a_jugar():
    # Tamaño de la pantalla para la ventana emergente
    ANCHO_VENTANA_EMERGENTE = 400
    ALTO_VENTANA_EMERGENTE = 200
    
    # Tamaño de la pantalla para el juego
    ANCHO_JUEGO = 1200
    ALTO_JUEGO = 600
    
    pantalla_confirmacion = pygame.display.set_mode((ANCHO_VENTANA_EMERGENTE, ALTO_VENTANA_EMERGENTE))
    pygame.display.set_caption("¿Quieres jugar de nuevo?")
    fuente = pygame.font.Font(None, 30)
    texto_pregunta = fuente.render("¿Quieres jugar de nuevo?", True, (0, 0, 0))
    texto_si = fuente.render("Sí (s)", True, (0, 0, 0))
    texto_no = fuente.render("No (n)", True, (0, 0, 0))
    
    while True:
        pantalla_confirmacion.fill((255, 255, 255))
        pantalla_confirmacion.blit(texto_pregunta, (50, 50))
        pantalla_confirmacion.blit(texto_si, (100, 100))
        pantalla_confirmacion.blit(texto_no, (250, 100))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    pygame.display.set_mode((ANCHO_JUEGO, ALTO_JUEGO))  # Cambiar tamaño de la pantalla
                    pygame.display.set_caption("NBA Trivia")
                    jugar()
                elif event.key == pygame.K_n:
                    pygame.quit()
                    sys.exit() 

# Función principal del juego
def jugar():
    pantalla_inicio()
    
    pantalla_juego()
    
    volver_a_jugar()
     
# Llamar a la función principal del juego
jugar()
