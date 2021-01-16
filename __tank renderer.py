
#! This file isn't actually part of the main game,
#! but is used to create the spritesheets for the tanks, the tracks and the bullets.

from settings import *
from PIL import Image, ImageDraw
from math import cos, sin, pi, sqrt
import sys

if len(sys.argv) <= 1:
	print("Missing args")
	sys.exit()

colors = {
	"white" : (250, 250, 250),
	"grey" : (128, 128, 128),
	"yellow" : (255, 252, 0),
	
	"black" : (59, 56, 48),
	"green" : (94, 160, 89),
	"blue" : (10, 150, 200),
	"red" : (255, 0, 0),
}

color = "black"
if len(sys.argv) > 1:
	if sys.argv[1] in colors.keys():
		draw = "tank"
		color = sys.argv[1]
	else:
		draw = sys.argv[1]

color_1 = colors[color]
color_2 = (int(color_1[0]*0.85), int(color_1[1]*0.85), int(color_1[2]*0.85))
color_brown_1 = (196, 146, 80)
color_brown_2 = (175, 128, 70)
color_brown_3 = (64, 48, 28)
color_white_1 = (250, 250, 250)

color_tracks = (10, 10, 10, 120)

angles = SHEETWIDTH*SHEETHEIGHT

border = 3

tank_body = [
	([(8, 7, 0), (8, -7, 0), (9, -7, 2), (9, 7, 2)], color_brown_3), #under front
	([(-8, 7, 0), (-8, -7, 0), (-9, -7, 2), (-9, 7, 2)], color_brown_3), #under back
	([(-8, -7, 0), (8, -7, 0), (9, -7, 2), (8, -7, 4), (-8, -7, 4), (-9, -7, 2)], color_brown_3), #side 1
	([(-8, 7, 0), (8, 7, 0), (9, 7, 2), (8, 7, 4), (-8, 7, 4), (-9, 7, 2)], color_brown_3), #side 2
	([(8, 7, 4), (8, -7, 4), (9, -7, 2), (9, 7, 2)], color_brown_2), #upper front
	([(-8, 7, 4), (-8, -7, 4), (-9, -7, 2), (-9, 7, 2)], color_brown_2), #upper back
	([(-8, -7, 4), (8, -7, 4), (8, 7, 4), (-8, 7, 4)], color_brown_1), #upper
	([(8, 5, 4.5), (8, -5, 4.5), (9.3, -5, 2), (9.3, 5, 2)], color_2), #color upper front
	([(-8, 5, 4.5), (-8, -5, 4.5), (-9.2, -5, 2), (-9.2, 5, 2)], color_2), #color upper back
	([(-8.1, -5, 4.5), (8.1, -5, 4.5), (8.1, 5, 4.5), (-8.1, 5, 4.5)], color_1), #color upper
]

tank_head = [
	([(-4, -4, 10), (4, -4, 10), (4, 4, 10), (-4, 4, 10)], color_1), #top
	([(-4, -4, 4), (4, -4, 4), (4, -4, 10), (-4, -4, 10)], color_2), #north
	([(-4, 4, 4), (4, 4, 4), (4, 4, 10), (-4, 4, 10)], color_2), #south
	([(-4, -4, 4), (-4, 4, 4), (-4, 4, 10), (-4, -4, 10)], color_2), #left
	([(4, -4, 4), (4, 4, 4), (4, 4, 10), (4, -4, 10)], color_2), #right
	([(4, -1, 8), (4, 1, 8), (16, 1, 8), (16, -1, 8)], color_brown_1), #canon top
	([(16, -1, 6), (16, 1, 6), (16, 1, 8), (16, -1, 8)], color_brown_2), #canon tip
	([(4, -1, 6), (16, -1, 6), (16, -1, 8), (4, -1, 8)], color_brown_2), #canon north
	([(4, 1, 6), (16, 1, 6), (16, 1, 8), (4, 1, 8)], color_brown_2), #canon south
]

tank_track = [
	([(-1, -7, 0), (1, -7, 0), (1, -3, 0), (-1, -3, 0)], color_tracks),
	([(-1, 7, 0), (1, 7, 0), (1, 3, 0), (-1, 3, 0)], color_tracks),
]

edges = 8
ang = 2*pi/edges
thi = 1.2
tank_bullet = []
tank_bullet.extend([([(-2, cos(ang*i)*thi, sin(ang*i)*thi+7), (2, cos(ang*i)*thi, sin(ang*i)*thi+7), (2, cos(ang*(i+1)*thi), sin(ang*(i+1))*thi+7), (-2, cos(ang*(i+1)*thi), sin(ang*(i+1))*thi+7)], color_white_1) for i in range(edges)])
tank_bullet.extend([([(2, cos(ang*i)*thi, sin(ang*i)*thi+7), (2, cos(ang*(i+1)*thi), sin(ang*(i+1))*thi+7), (4, 0, 7), (4, 0, 7)], color_white_1) for i in range(edges)])

img_body = Image.new("RGB", (BODYTILE*4*SHEETWIDTH, BODYTILE*3*SHEETHEIGHT), COLORKEY)
draw_body = ImageDraw.Draw(img_body, "RGB")

img_head = Image.new("RGB", (HEADTILE*4*SHEETWIDTH, HEADTILE*3*SHEETHEIGHT), COLORKEY)
draw_head = ImageDraw.Draw(img_head, "RGB")

img_body_outline = Image.new("RGB", (BODYTILE*4*SHEETWIDTH, BODYTILE*3*SHEETHEIGHT), COLORKEY)
img_head_outline = Image.new("RGB", (HEADTILE*4*SHEETWIDTH, HEADTILE*3*SHEETHEIGHT), COLORKEY)

img_track = Image.new("RGBA", (TRACKTILE*4*SHEETWIDTH, TRACKTILE*3*SHEETHEIGHT), (255, 255, 255, 0))
draw_track = ImageDraw.Draw(img_track, "RGBA")

img_bullet = Image.new("RGB", (BULLETTILE*4*SHEETWIDTH, BULLETTILE*3*SHEETHEIGHT), COLORKEY)
draw_bullet = ImageDraw.Draw(img_bullet, "RGB")

def pos(x, y, z, a, o, s):
	return int((x*s*cos(a) - y*s*sin(a) + o) * 4), int((x*s*sin(a) + y*s*cos(a) - z*s + o) * 3)

for a in range(angles):
	ang = a/angles*pi*2
	
	tank_body.sort(key=lambda x: sum([sqrt((i[2]-100)**2 + (i[0]*sin(ang) + i[1]*cos(ang)-100)**2) for i in x[0]]), reverse=True)
	tank_head.sort(key=lambda x: sum([sqrt((i[2]-100)**2 + (i[0]*sin(ang) + i[1]*cos(ang)-100)**2) for i in x[0]]), reverse=True)
	
	if draw == "tank" or draw == "outline":
		for i, p in enumerate(tank_body):
			tp = []
			for j in p[0]:
				po = pos(j[0], j[1], j[2], ang, BODYTILE//2, 0.9)
				tp.append((po[0]+(a%SHEETWIDTH)*BODYTILE*4, po[1]+(a//SHEETWIDTH)*BODYTILE*3))
			draw_body.polygon(tp, p[1])
		
		for i, p in enumerate(tank_head):
			tp = []
			for j in p[0]:
				po = pos(j[0], j[1], j[2], ang, HEADTILE//2, 0.9)
				tp.append((po[0]+(a%SHEETWIDTH)*HEADTILE*4, po[1]+(a//SHEETWIDTH)*HEADTILE*3))
			draw_head.polygon(tp, p[1])
	
	if draw == "tracks":
		for i, p in enumerate(tank_track):
			tp = []
			for j in p[0]:
				po = pos(j[0], j[1], j[2], ang, TRACKTILE//2, 0.9)
				tp.append((po[0]+(a%SHEETWIDTH)*TRACKTILE*4, po[1]+(a//SHEETWIDTH)*TRACKTILE*3))
			draw_track.polygon(tp, p[1])
	
	if draw == "bullet":
		for i, p in enumerate(tank_bullet):
			tp = []
			for j in p[0]:
				po = pos(j[0], j[1], j[2], ang, BULLETTILE//2, 0.9)
				tp.append((po[0]+(a%SHEETWIDTH)*BULLETTILE*4, po[1]+(a//SHEETWIDTH)*BULLETTILE*3))
			draw_bullet.polygon(tp, p[1])

if draw == "outline":
	pix_body = img_body_outline.load()
	pix_body_copy = img_body.copy().load()
	for x in range(SHEETWIDTH*BODYTILE*4):
		for y in range(SHEETHEIGHT*BODYTILE*3):
			if pix_body_copy[x, y] != COLORKEY:
				for i in range(-border, border+1):
					for j in range(-border, border+1):
						if pix_body[x+i, y+j] == COLORKEY:
							pix_body[x+i, y+j] = (0, 0, 0)

	pix_head = img_head_outline.load()
	pix_head_copy = img_head.copy().load()
	for x in range(SHEETWIDTH*HEADTILE*4):
		for y in range(SHEETHEIGHT*HEADTILE*3):
			if pix_head_copy[x, y] != COLORKEY:
				for i in range(-border, border+1):
					for j in range(-border, border+1):
						if pix_head[x+i, y+j] == COLORKEY:
							pix_head[x+i, y+j] = (0, 0, 0)

if draw == "bullet":
	pix_bullet = img_bullet.load()
	pix_bullet_copy = img_bullet.copy().load()
	for x in range(SHEETWIDTH*BULLETTILE*4):
		for y in range(SHEETHEIGHT*BULLETTILE*3):
			if pix_bullet_copy[x, y] != COLORKEY:
				for i in range(-border, border+1):
					for j in range(-border, border+1):
						if pix_bullet[x+i, y+j] == COLORKEY:
							pix_bullet[x+i, y+j] = (0, 0, 0)

if draw == "tank":
	img_body.save("assets/graphics/tanks/" + color + "_body.png", "PNG")
	img_head.save("assets/graphics/tanks/" + color + "_head.png", "PNG")
if draw == "outline":
	img_body_outline.save("assets/graphics/tank_body_outline.png", "PNG")
	img_head_outline.save("assets/graphics/tank_head_outline.png", "PNG")
if draw == "tracks":
	img_track.save("assets/graphics/tank_tracks.png", "PNG")
if draw == "bullet":
	img_bullet.save("assets/graphics/bullet.png", "PNG")

if len(sys.argv) > 2 and sys.argv[2] in "preview":
	pass
	img_body.show()
	img_head.show()
	img_body_outline.show()
	img_head_outline.show()
	img_track.show()
	img_bullet.show()
