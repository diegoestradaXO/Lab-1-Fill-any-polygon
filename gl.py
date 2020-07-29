#Escritor de Imagenes BMP
#Author: Diego Estrada

# Errores comunes:
# "index out of range" puede suceder cuando el vertex esta fuera del viewport

import struct
from obj import Obj


def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(c):
    return struct.pack('=h', c)

def dword(c):
    return struct.pack('=l', c)

def color(r, g, b):
    return bytes([b,g,r])

class Render(object):
    def __init__(self):
        self.clear_color = color(0,0,0)
        self.draw_color = color(255,0,0)
    
    def glClear(self):
        self.framebuffer = [
            [self.clear_color for x in range(self.width)]
            for y in range(self.height)
        ]

    def glCreateWindow(self, width, height): #el width y height del window es el del Render()
        self.width = width
        self.height = height
        self.framebuffer = []
        self.glClear()
    
    def point(self, x,y):
        self.framebuffer[y][x] = self.draw_color

    def glInit(self):
        pass

    def glViewPort(self, x, y, width, height):
        self.x_VP = x
        self.y_VP = y
        self.width_VP = width
        self.height_VP = height

    def glClearColor(self, r, g, b):
        self.clear_color = color(int(round(r*255)),int(round(g*255)),int(round(b*255)))

    def glColor(self, r,g,b):
        self.draw_color = color(int(round(r*255)),int(round(g*255)),int(round(b*255)))

    def glVertex(self, x, y):
        xPixel = round((x+1)*(self.width_VP/2)+self.x_VP)
        yPixel = round((y+1)*(self.height_VP/2)+self.y_VP)
        self.point(xPixel, yPixel)
    
    def glLine(self,x1, y1, x2, y2):
        x1 = int(round((x1+1) * self.width / 2))
        y1 = int(round((y1+1) * self.height / 2))
        x2 = int(round((x2+1) * self.width / 2))
        y2 = int(round((y2+1) * self.height / 2))
        steep=abs(y2 - y1)>abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if x1>x2:
            x1,x2 = x2,x1
            y1,y2 = y2,y1

        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        y = y1
        offset = 0
        threshold = dx

        for x in range(x1, x2):
            if offset>=threshold:
                y += 1 if y1 < y2 else -1
                threshold += 2*dx
            if steep:
                self.framebuffer[x][y] = self.draw_color
            else:
                self.framebuffer[y][x] = self.draw_color
            offset += 2*dy

    def load(self, filename, translate=(0, 0, 0), scale=(1, 1, 1)):
        """
        Loads an obj file in the screen
        wireframe only
        Input: 
        filename: the full path of the obj file
        translate: (translateX, translateY) how much the model will be translated during render
        scale: (scaleX, scaleY) how much the model should be scaled
        """
        model = Obj(filename)

        for face in model.vfaces:
            vcount = len(face)

            if vcount == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                a = self.transform(model.vertices[f1], translate, scale)
                b = self.transform(model.vertices[f2], translate, scale)
                c = self.transform(model.vertices[f3], translate, scale)

                self.triangle(a, b, c,
                    glColor(
                    random.randint(0, 1),
                    random.randint(0, 1),
                    random.randint(0, 1)
                    )
            )
            else:
                # assuming 4
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1   

            vertices = [
                self.transform(model.vertices[f1], translate, scale),
                self.transform(model.vertices[f2], translate, scale),
                self.transform(model.vertices[f3], translate, scale),
                self.transform(model.vertices[f4], translate, scale)
            ]

            A, B, C, D = vertices

            self.triangle(A, B, C,
                glColor(
                random.randint(0, 1),
                random.randint(0, 1),
                random.randint(0, 1)
                )
            )
            self.triangle(A, C, D,
                glColor(
                random.randint(0, 1),
                random.randint(0, 1),
                random.randint(0, 1)
                )
            )


    def glFinish(self, filename):
        f = open(filename, 'bw')

        #file header
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        #image header
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))   
        f.write(dword(0))
        f.write(dword(24))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0)) 
        f.write(dword(0))

        # pixel data

        for x in range(self.width):
            for y in range(self.height):
                f.write(self.framebuffer[y][x])
        
        f.close()
    
    def glFill(self, polygon):
        for y in range(self.height):
            for x in range(self.width):
                i = 0
                j = len(polygon) - 1
                inside = False
                for i in range(len(polygon)):
                    if (polygon[i][1] < y and polygon[j][1] >= y) or (polygon[j][1] < y and polygon[i][1] >= y):
                        if polygon[i][0] + (y - polygon[i][1]) / (polygon[j][1] - polygon[i][1]) * (polygon[j][0] - polygon[i][0]) < x:
                            inside = not inside
                    j = i
                if inside:
                    self.point(y,x)

    def transform(self, vertex, translate=(0, 0, 0), scale=(1, 1, 1)):
        # returns a vertex 3, translated and transformed
        return V3(
        round((vertex[0] + translate[0]) * scale[0]),
        round((vertex[1] + translate[1]) * scale[1]),
        round((vertex[2] + translate[2]) * scale[2])
        )

r = Render()

r.glCreateWindow(800,800)


p1 =((165, 380), (185, 360), (180, 330), (207, 345), (233, 330), (230, 360), (250, 380), (220, 385), (205, 410), (193, 383))
r.glFill(p1)
p2 = ((321, 335), (288, 286) ,(339, 251), (374, 302))
r.glFill(p2)
p3 = ((377, 249) ,(411, 197) ,(436, 249))
r.glFill(p3)
p4 = ((413, 177) ,(448, 159), (502, 88), (553, 53) ,(535, 36) ,(676, 37) ,(660, 52),
(750, 145) ,(761, 179) ,(672, 192) ,(659, 214) ,(615, 214), (632, 230), (580, 230),
(597, 215) ,(552, 214) ,(517, 144) ,(466, 180))
r.glFill(p4)
p5 = ((682, 175), (708, 120), (735, 148) ,(739, 170))
r.glFill(p5)
r.glFinish('out.bmp')