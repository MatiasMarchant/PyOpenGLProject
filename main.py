import pygame
from pygame.locals import *

# import os
# ejemplo_dir = './'

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np
import math
from PIL import Image
from shapely.geometry import Polygon # pip install shapely

# Tecla | Acción
# Click izquierdo: Toma el vértica más cercano y lo arrastra hacia donde está el mouse
# a: Aparece círculo
# Click derecho: Arrastra círculo mencionado antes
# Flechas izq, der, abajo, arriba: Mueve círculo mencionado antes
# c: Círculo texturiza cara de cuadrado más cercana
# t: Texturizar todos los cuadrados
# p: Activar música más cercana (Importante: considerar que juego inicia con volumen 0.03 => usar m para subir volumen)
# s: Detener música
# m: Subir volumen
# n: Bajar volumen

class Vertice:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Cuadrilatero:
    # bl = bottom left
    # br = bottom right
    # tl = top left
    # tr = top right
    def __init__(self, verticebl, verticebr, verticetl, verticetr, color, metexturizo):
        self.verticebl = verticebl
        self.verticebr = verticebr
        self.verticetl = verticetl
        self.verticetr = verticetr
        self.color = color
        self.metexturizo = metexturizo

        self.surfaces = (
            (0, 1, 3, 2)
        )

    def draw(self):
        vertices = (
            (self.verticebl.x, self.verticebl.y, 0),
            (self.verticebr.x, self.verticebr.y, 0),
            (self.verticetl.x, self.verticetl.y, 0),
            (self.verticetr.x, self.verticetr.y, 0)
        )

        # Para texturas 
        # (CREO que esta es la tupla que define el orden en que escoge los vértices para texturizar, por eso la imagen chromatica.jpg está rotada, porque preferí arreglarlo de esa forma que meterme con este arreglo de puro pajero xd)
        # Por ej si cambias de orden el (0, 0) con el (1, 0) en la tupla se renderea súper raro
        vertices_entre_0_y_1 = ( 
            (0, 0),
            (1, 0),
            (0, 1),
            (1, 1)
        )
        
        edges = (
            (0, 1), #bl br
            (0, 2), #bl tl
            (1, 3), #br tr
            (2, 3)  #tl tr
        )

        surfaces = (
            (0, 1, 3, 2)
        )

        colors = (
            # Red
            (1, 0, 0),
            # Orange
            (1, 165/255, 0),
            # Yellow
            (1, 1, 0),
            # Green
            (0, 1, 0),
            # Blue
            (0, 0, 1),
            # Indigo
            (75/255, 0, 130/255)
        )

        if(self.metexturizo):

            # Para texturear cuadriláteros 
            #img = Image.open('wood.jpg')
            #img = Image.open('images.png').convert('RGB')
            #img = Image.open('wall.jpg')
            img = Image.open('chromatica.jpg')
            img_array = np.array(img)

            # Código para texturizar, en su momento lo encontré en internet, fue la parte más difícil del proyecto xd
            FBO = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, FBO)
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT) GL_REPEAT repite, se cambia por clamp to edge para que se estire
            #glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_array.shape[0], img_array.shape[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_array)
            glGenerateMipmap(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)

            glEnable(GL_TEXTURE_2D)

            # Esto hace lineas en las aristas definidas por edges
            # glBegin(GL_LINES)
            # for edge in edges:
            #    for vertex in edge:
            #        glVertex3fv(vertices[vertex])
            # glEnd()

            

            glBindTexture(GL_TEXTURE_2D, FBO)
            glBegin(GL_QUADS)
            for vertice_index in surfaces:
                glTexCoord2f(vertices_entre_0_y_1[vertice_index][0], vertices_entre_0_y_1[vertice_index][1])
                glVertex3f(vertices[vertice_index][0], vertices[vertice_index][1], vertices[vertice_index][2])
            glEnd()
            glBindTexture(GL_TEXTURE_2D, 0)

            glDisable(GL_TEXTURE_2D)
        else:
            # Color
            glBegin(GL_QUADS)
            glColor3fv(colors[self.color])
            for vertex in surfaces:
                glVertex3fv(vertices[vertex])
            glEnd()
    
    def getPuntos(self):
        puntos = [self.verticebl, self.verticebr, self.verticetl, self.verticetr]
        return puntos
    
    def getCentroid(self): # https://stackoverflow.com/questions/53502002/how-to-calculate-the-center-of-gravity-with-shapely-in-python
        lista_poligono = []
        for vertice_index in self.surfaces:
            lista_poligono.append( [ self.getPuntos()[vertice_index].x, self.getPuntos()[vertice_index].y ] )
        centroid = list(Polygon(lista_poligono).centroid.coords) # [(0.5, 0.5)]
        return centroid

class Circulo:
    def __init__(self, Centro, radio, aparezco):
        self.Centro = Centro
        self.radio = radio
        self.aparezco = aparezco
    def draw(self):
        if(self.aparezco):
            glColor3f(1,192/255,203/255)
            glBegin(GL_POLYGON)
            for i in range(0, 360):
                theta = i*3.142/180
                glVertex2f(self.radio*math.cos(theta) + self.Centro.x, self.radio*math.sin(theta) + self.Centro.y)
            glEnd()
            

def Punto_mas_cercano(puntos, x_world, y_world):
    distancia_menor = 99999999
    punto_mas_cercano = Vertice(9999, 9999)
    for punto in puntos:
        distancia = ( (x_world - punto.x)**2 + (y_world - punto.y)**2 )**(1/2)
        if(distancia < distancia_menor):
            distancia_menor = distancia
            punto_mas_cercano = punto
    return punto_mas_cercano


def obtener_viewPos(z, aspect, fov_y):
    # https://stackoverflow.com/questions/46801701/how-to-find-pygame-window-coordinates-of-an-opengl-vertice
    mpos = pygame.mouse.get_pos()
    width, height = aspect
    ndc = [ 2.0 * mpos[0]/width - 1.0, 1.0 - 2.0 * mpos[1]/height ]
    tanFov = math.tan( fov_y * 0.5 * math.pi / 180 )
    aspect = width / height 
    viewPos = [z * ndc[0] * aspect * tanFov, z * ndc[1] * tanFov ] # Posicion mouse con respecto a mundo
    return viewPos

def main():
    pygame.init()
    button_down = False
    button_down_right = False
    metexturizo = False
    circulo_aparezco = False
    # Instanciación cuadriláteros
    cuadr1 = Cuadrilatero(Vertice(0, 0), Vertice(1, 0), Vertice(0, 1), Vertice(1, 1), 0, metexturizo)
    cuadr2 = Cuadrilatero(Vertice(1.1, 0), Vertice(2.1, 0), Vertice(1.1, 1), Vertice(2.1, 1), 1, metexturizo)
    cuadr3 = Cuadrilatero(Vertice(0, 1.1), Vertice(1, 1.1), Vertice(0, 2.1), Vertice(1, 2.1), 2, metexturizo)
    cuadrados = [cuadr1, cuadr2, cuadr3]
    circulo1 = Circulo(Vertice(3, 3), 0.3, circulo_aparezco)
    musica = ["enigma.wav", "freewoman.wav", "replay.wav"]

    # Para picking
    puntos = []
    punto = Vertice(9999, 9999)

    # Tamaño ventana pygame
    display = (1000, 600)

    # Para obtener coordenadas del mundo
    z = 10
    fov_y = 45
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluPerspective(fov_y, (display[0]/display[1]), 0.1, 40)
    # -> Parámetros línea de arriba: FOV, Aspect Ratio, Clipping Plane Closer, Clipping Plane Far
    # Acá es muy importante que el Clipping Plane Closer (el q es 0.1) no sea 0 porque para obtener la proyección de tu mouse
    # sobre el juego usa esa variable como denominador y cuando me tocó hacer el proyecto no entendía por qué y era por eso!!!

    glTranslatef(0.0, 0.0, -z) #xyz, derecha, arriba, pantalla



    while True:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t: # if key = t
                    if(metexturizo == True):
                        metexturizo = False
                        for cuadrado in cuadrados:
                            cuadrado.metexturizo = False
                    else:
                        metexturizo = True
                        for cuadrado in cuadrados:
                            cuadrado.metexturizo = True
                
                if event.key == pygame.K_a:
                    if(circulo_aparezco == True):
                        circulo_aparezco = False
                        circulo1.aparezco = False
                    else:
                        circulo_aparezco = True
                        circulo1.aparezco = True
                
                if circulo_aparezco:
                    shortest_distance = 99999
                    index_cuadrado_elegido = 0
                    cuadrado_elegido = 0
                    for cuadrado in cuadrados:
                        x_cuad, y_cuad = cuadrado.getCentroid()[0]
                        x_circulo, y_circulo = (circulo1.Centro.x, circulo1.Centro.y)
                        distancia = ( (x_cuad - x_circulo)**2 + (y_cuad - y_circulo)**2 )**(1/2)
                        if(distancia < shortest_distance):
                            shortest_distance = distancia
                            index_cuadrado_elegido = cuadrados.index(cuadrado)
                            cuadrado_elegido = cuadrado

                    if event.key == pygame.K_c:
                        if(cuadrado_elegido.metexturizo == True):
                            cuadrado_elegido.metexturizo = False
                        else:
                            cuadrado_elegido.metexturizo = True

                    if event.key == pygame.K_p:
                        pygame.mixer.music.load(musica[index_cuadrado_elegido])
                        pygame.mixer.music.set_volume(0.03)
                        pygame.mixer.music.play(0)

                    if event.key == pygame.K_s:
                        pygame.mixer.music.stop()
                    if event.key == pygame.K_m:
                        pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.02)
                    if event.key == pygame.K_n:
                        pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() - 0.02)


                if event.key == pygame.K_LEFT:
                    circulo1.Centro.x -= 0.2
                if event.key == pygame.K_RIGHT:
                    circulo1.Centro.x += 0.2
                if event.key == pygame.K_UP:
                    circulo1.Centro.y += 0.2
                if event.key == pygame.K_DOWN:
                    circulo1.Centro.y -= 0.2
            


            if event.type == pygame.MOUSEMOTION:
                if button_down == True:
                    viewPos = obtener_viewPos(z, display, fov_y)
                    # Acá puedes poner un print(viewPos) para cachar qué coordenadas te devuelve al mantener presionado click izq sobre la app
                    # distancia_mas_baja = 99999999 # Recién me doy cuenta que esto al parecer no se ocupa, no lo borro pq puede uqe sirva xd
                    for cuadrado in cuadrados:
                        for i in cuadrado.getPuntos():
                            puntos.append(i)
                    # Acá se hace el Picking, que es clickear un vértice y poder arrastrarlo con el mouse
                    punto = Punto_mas_cercano(puntos, viewPos[0], viewPos[1]) 
                    punto.x = viewPos[0] # Picking
                    punto.y = viewPos[1]

                if button_down_right == True:
                    viewPos = obtener_viewPos(z, display, fov_y)
                    circulo1.Centro.x = viewPos[0]
                    circulo1.Centro.y = viewPos[1]

        for event in pygame.mouse.get_pressed():
            if pygame.mouse.get_pressed()[0] == 1:
                button_down = True
            elif pygame.mouse.get_pressed()[0] == 0:
                button_down = False
            if pygame.mouse.get_pressed()[2] == 1:
                button_down_right = True
            elif pygame.mouse.get_pressed()[2] == 0:
                button_down_right = False
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        # En cada iteración se vuelve a dibujar los cuadrados y el círculo con sus coordenadas actualizadas
        cuadr1.draw()
        cuadr2.draw()
        cuadr3.draw()
        circulo1.draw()
        
        # No recuerdo para qué servían estas líneas, el pygame.time.wait(ms) me parece que son los ms que espera para volver a entrar en el while True
        pygame.display.flip()
        pygame.time.wait(10)

main()
pygame.quit()
quit()
