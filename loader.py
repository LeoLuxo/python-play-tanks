
from settings import *
from classes import *

import os
from pygame import *

tile_map = {
	" " : None,
	"_" : "spike",
	"0" : "wall0",
	"1" : "wall1",
	"2" : "wall2",
	"3" : "wall3",
	"4" : "wall4",
	"5" : "wall5",
	"6" : "dwall1",
	"7" : "dwall2",
	"8" : "dwall3",
}

tank_map = {
	"A" : "grey",
	"B" : "yellow",
	"C" : "blue",
	"D" : "green",
	"E" : "red",
	"F" : "black",
}

def load_tiles():
	assets = {i.replace(".png", "") : image.load("assets/graphics/tiles/" + i).convert_alpha() for i in os.listdir("assets/graphics/tiles/")}
	assets = {k : transform.scale(i, (int(i.get_width() / WALLTILE * SCALEX), int(i.get_height() / WALLTILE * SCALEY))) for k,i in assets.items()}
	return assets

def load_effects():
	assets = {i.replace(".png", "") : image.load("assets/graphics/effects/" + i).convert_alpha() for i in os.listdir("assets/graphics/effects/")}
	assets = {k : transform.scale(i, (i.get_width() // EFFECTTILE * EFFECTSCALE, i.get_height() // EFFECTTILE * EFFECTSCALE)) for k,i in assets.items()}
	return assets

def load_tanks():
	assets = {"tank_" + i.replace(".png", "") : image.load("assets/graphics/tanks/" + i).convert() for i in os.listdir("assets/graphics/tanks/")}
	[i.set_colorkey(COLORKEY) for i in assets.values()]
	return assets

def load_extra():
	assets = {}
	assets["wall_shadow"] = transform.scale(image.load("assets/graphics/wall_shadow.png").convert_alpha(), (2 * SCALEX, 2 * SCALEY))
	assets["tracks"] = image.load("assets/graphics/tank_tracks.png").convert_alpha()
	assets["mine"] = transform.scale(image.load("assets/graphics/mine.png").convert_alpha(), (SCALEX, SCALEY))
	assets["mine_lit"] = transform.scale(image.load("assets/graphics/mine_lit.png").convert_alpha(), (SCALEX, SCALEY))
	assets["mine_unarmed"] = transform.scale(image.load("assets/graphics/mine_unarmed.png").convert_alpha(), (SCALEX, SCALEY))
	assets["scorch_tank"] = transform.scale(image.load("assets/graphics/tank_mark.png").convert_alpha(), (int(SCALEX*1.5), int(SCALEY*1.5)))
	assets["scorch_mine"] = transform.scale(image.load("assets/graphics/mine_mark.png").convert_alpha(), (int(SCALEX*MINERANGE*2), int(SCALEY*MINERANGE*2)))
	
	assets["bullet"] = image.load("assets/graphics/bullet.png").convert()
	assets["bullet"].set_colorkey(COLORKEY)
	assets["rocket"] = image.load("assets/graphics/bullet2.png").convert()
	assets["rocket"].set_colorkey(COLORKEY)
	assets["tank_body_shadow"] = image.load("assets/graphics/tank_body_shadow.png").convert()
	assets["tank_body_shadow"].set_colorkey(COLORKEY)
	assets["tank_head_shadow"] = image.load("assets/graphics/tank_head_shadow.png").convert()
	assets["tank_head_shadow"].set_colorkey(COLORKEY)
	
	return assets

def load_icon():
	icon = image.load("assets/icon.png")
	return icon

def load_stage(stage, map, tanks):
	with open("stages/" + stage + ".txt", "r") as s:
		m = [i.replace("\n", "") + (" " * (FIELDWIDTH - len(i.replace("\n", "")))) for i in s.readlines()]
		m += [" " * FIELDWIDTH] * (FIELDHEIGHT - len(m))
		for y,i in enumerate(m):
			for x,j in enumerate(i):
				if j in tile_map.keys():
					map[x][y] = tile_map[j]
				elif j in tank_map.keys():
					tanks.append(Tank(tank_map[j], x, y, stop=True))
				elif j == ".":
					tanks[0].x = x
					tanks[0].y = y
	return map, tanks

