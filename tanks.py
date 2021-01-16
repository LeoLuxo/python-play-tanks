
import os, sys

os.environ['SDL_VIDEO_CENTERED'] = "1"
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

from settings import *
from classes import *
from loader import *
import main, sound, ai_math

from pygame import *
import pygame.freetype
from math import *

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

init()
screen = display.set_mode((SCREENWIDTH, SCREENHEIGHT))
display.set_caption("Python Play Tanks!")
display.set_icon(load_icon())

clock = time.Clock()

secret_font = pygame.freetype.Font("assets/fonts/TopSecret.ttf", 80)
type_font = pygame.freetype.Font("assets/fonts/TravelingTypewriter.ttf", 80)
pixel_font = pygame.freetype.Font("assets/fonts/PressStart2P.ttf", 24)

pixel_font.render_to(screen, (10, SCREENHEIGHT - 30), "Loading..." + (" (SOUND MUTED)" if SOUNDMUTED else ""), (255, 255, 255))
display.flip()

text_cache = {}

def goto_stage(stage="1-1"):
	main.map = [[None for y in range(FIELDHEIGHT)] for x in range(FIELDWIDTH)]
	main.tanks = [Tank("white", 0, 0, no_ai=True, stop=True)]
	main.effects = []
	main.mines = []
	main.bullets = []
	main.stage = stage
	main.map, main.tanks = load_stage(main.stage, main.map, main.tanks)
	
	render_bg_layer()
	render_shadow_layer()
	
	global round_counter, intro_counter, win_counter, lose_counter, over_counter
	round_counter = 0
	intro_counter = INTROLENGTH
	win_counter = -1
	lose_counter = -1
	over_counter = -1
	
	text_cache.clear()
	
	sound.play_mission_intro()

def render_bg_layer():
	global bg_layer
	bg_layer = Surface((SCREENWIDTH, SCREENHEIGHT))
	
	for x in range(0, SCREENWIDTH, SCALEX):
		for y in range(0, SCREENHEIGHT, SCALEY):
			bg_layer.blit(main.assets["floor"], (x, y))

def render_shadow_layer():
	global shadow_layer
	shadow_layer = Surface((SCREENWIDTH, SCREENHEIGHT), SRCALPHA)
	
	for x in range(FIELDWIDTH):
		for y in range(FIELDHEIGHT):
			if not main.map[x][y] == None:
				shadow_layer.blit(main.assets["wall_shadow"], (int((x-0.5) * SCALEX), int((y+0.5) * SCALEY)))
	
	shadow_layer.fill((255, 255, 255, 120), special_flags=BLEND_RGBA_MULT)

def draw_to_bg(img, x, y):
	global bg_layer
	bg_layer.blit(img, (x * SCALEX - img.get_width()//2, y * SCALEY - img.get_height()//2))

def draw_text(font, text, x, y, centered=False, border=2, color=(255, 255, 255), rotation=0):
	global screen
	global text_cache
	rect = font.get_rect(text, rotation=rotation)
	
	if text.strip() == "":
		return
	
	if (text, border, color, rotation) not in text_cache:
		surf = Surface((rect[2]+border*2, rect[3]+border*2), pygame.SRCALPHA)
		for i in range(-border, border+1):
			for j in range(-border, border+1):
				font.render_to(surf, (i + border, j + border), None, (0, 0, 0), rotation=rotation)
		font.render_to(surf, (border, border), None, color, rotation=rotation)
		text_cache[(text, border, color, rotation)] = surf
	screen.blit(text_cache[(text, border, color, rotation)], (x - (rect[2]/2 if centered else 0), y - (rect[3]/2 if centered else 0)))

main.assets = {}
main.assets.update(load_tiles())
main.assets.update(load_effects())
main.assets.update(load_tanks())
main.assets.update(load_extra())

main.lives = PLAYER_LIVES

main.redraw_bg = render_bg_layer
main.redraw_shadow = render_shadow_layer
main.draw_to_bg = draw_to_bg

transition_surf = Surface((SCREENWIDTH, SCREENHEIGHT))
transition_surf.fill((0, 0, 0))

transition_counter = -1

goto_stage(STAGES[0])

stop = False
while not stop:
	for e in event.get():
		if e.type == QUIT:
			stop = True
		if e.type == MOUSEBUTTONDOWN:
			main.tanks[0].shoot()
		if e.type == KEYDOWN:
			if e.key == K_SPACE:
				main.tanks[0].place_mine()
		if e.type in sound.end_event:
			sound.end_event[e.type]()
	
	screen.blit(bg_layer, (0, 0))
	screen.blit(shadow_layer, (0, 0))
	
	win_test = True
	for t in main.tanks[1:]:
		if not t.dead:
			win_test = False
			break
	if win_counter <= -1 and lose_counter <= -1 and intro_counter <= -1 and over_counter <= -1:
		round_counter += 1
		if (main.tanks[0].dead and main.lives <= 0) or (win_test and STAGES.index(main.stage) == len(STAGES)-1):
			for t in main.tanks:
				t.stop = True
			sound.stop_mission_loop()
			sound.play_results()
			over_counter = 0
		elif main.tanks[0].dead:
			sound.play_mission_lose()
			lose_counter = LOSELENGTH
		elif win_test:
			main.tanks[0].stop = True
			sound.play_mission_win()
			win_counter = WINLENGTH
	if lose_counter > 0:
		lose_counter -= 1
	if win_counter > 0:
		win_counter -= 1
	if over_counter >= 0:
		over_counter += 1
	if (lose_counter == 0 or win_counter == 0 or over_counter >= 0) and transition_counter == -1:
		transition_counter = 0
	if transition_counter >= 0 and transition_counter < TRANSITIONLENGTH*2:
		transition_counter += 1
		if transition_counter == TRANSITIONLENGTH:
			if win_counter == 0:
				goto_stage(STAGES[STAGES.index(main.stage)+1])
			else:
				main.lives -= 1
				goto_stage(main.stage)
	if transition_counter >= TRANSITIONLENGTH*2:
		transition_counter = -1
	if over_counter >= 0 and transition_counter / TRANSITIONLENGTH >= 0.5:
		transition_counter = int(TRANSITIONLENGTH * 0.5)
	
	if intro_counter > 0:
		intro_counter -= 1
	elif intro_counter == 0:
		intro_counter = -1
		round_counter = 0
		sound.build_mission_loop()
		sound.play_mission_loop()
		for t in main.tanks:
			t.stop = False
		text_cache.clear()
	
	main.tanks[0].aim_target = atan2(mouse.get_pos()[1]/3 - (main.tanks[0].y+1)*SCALE, mouse.get_pos()[0]/4 - (main.tanks[0].x+0.5)*SCALE) / pi / 2
	
	pressed = key.get_pressed()
	
	movex = 0
	if pressed[K_a]:
		movex = -main.tanks[0].speed
	if pressed[K_d]:
		movex = main.tanks[0].speed
	
	movey = 0
	if pressed[K_w]:
		movey = -main.tanks[0].speed
	if pressed[K_s]:
		movey = main.tanks[0].speed
	
	if movex != 0 and movey != 0:
		main.tanks[0].move_x(movex / sqrt(2))
		main.tanks[0].move_y(movey / sqrt(2))
	elif movex != 0:
		main.tanks[0].move_x(movex)
	elif movey != 0:
		main.tanks[0].move_y(movey)
	
	if DEBUGMODE:
		ai_math.screen = screen
		ai_math.display = display
		ai_math.draw = draw
		ai_math.event = event
	
	ai.map_out_tanks()
	
	for t in main.tanks:
		t.tick(round_counter if intro_counter <= -1 else (-2 if intro_counter == INTROLENGTH-1 else -1))
		if t.track_counter >= 1:
			t.track_counter -= 1
			bg_layer.blit(main.assets["tracks"], ((t.x+0.5)*SCALEX - (TRACKTILEX//2), (t.y+1.5)*SCALEY - (TRACKTILEY//2)), Rect(t.get_body_sheet()[0]*TRACKTILEX, t.get_body_sheet()[1]*TRACKTILEY, TRACKTILEX, TRACKTILEY))
	
	for m in main.mines[:]:
		m.tick()
		if m.fuse < 0:
			screen.blit(main.assets["mine_unarmed"], ((m.x) * SCALEX, (m.y) * SCALEY))
		else:
			if DEBUGMODE:
				draw.ellipse(screen, (255, 0, 0) if m.detect else (0, 0, 255), ((m.x+0.5-MINERANGE) * SCALEX, (m.y+0.5-MINERANGE) * SCALEY, MINERANGE*2 * SCALEX, MINERANGE*2 * SCALEY), 10)
			screen.blit(main.assets["mine" if int(log(FUSELENGTH-m.fuse+10) * 10) % 2 == 1 else "mine_lit"], ((m.x) * SCALEX, (m.y) * SCALEY))
	
	for b in main.bullets:
		b.tick()
	
	for y in range(FIELDHEIGHT):
		for t in main.tanks:
			if int(t.y+0.5) == y and not t.dead:
				screen.blit(main.assets["tank_body_shadow"], ((t.x+0.5)*SCALEX - (BODYTILEX//2), (t.y+1.5)*SCALEY - (BODYTILEY//2)), Rect(t.get_body_sheet()[0]*BODYTILEX, t.get_body_sheet()[1]*BODYTILEY, BODYTILEX, BODYTILEY))
				screen.blit(main.assets["tank_head_shadow"], ((t.x+0.5)*SCALEX - (HEADTILEX//2), (t.y+1.5)*SCALEY - (HEADTILEY//2)), Rect(t.get_aim_sheet()[0]*HEADTILEX, t.get_aim_sheet()[1]*HEADTILEY, HEADTILEX, HEADTILEY))
		for t in main.tanks:
			if int(t.y+0.5) == y and not t.dead:
				screen.blit(main.assets["tank_" + t.type + "_body"], ((t.x+0.5)*SCALEX - (BODYTILEX//2), (t.y+1.5)*SCALEY - (BODYTILEY//2)), Rect(t.get_body_sheet()[0]*BODYTILEX, t.get_body_sheet()[1]*BODYTILEY, BODYTILEX, BODYTILEY))
		for t in main.tanks:
			if int(t.y+0.5) == y and not t.dead:
				screen.blit(main.assets["tank_" + t.type + "_head"], ((t.x+0.5)*SCALEX - (HEADTILEX//2), (t.y+1.5)*SCALEY - (HEADTILEY//2)), Rect(t.get_aim_sheet()[0]*HEADTILEX, t.get_aim_sheet()[1]*HEADTILEY, HEADTILEX, HEADTILEY))
				
		
		for b in main.bullets:
			if int(b.y+0.5) == y:
				screen.blit(main.assets["rocket"] if b.rocket else main.assets["bullet"], ((b.x+0.5)*SCALEX - (BULLETTILEX//2), (b.y+1.5)*SCALEY - (BULLETTILEY//2)), Rect(b.get_dir_sheet()[0]*BULLETTILEX, b.get_dir_sheet()[1]*BULLETTILEY, BULLETTILEX, BULLETTILEY))
		
		for e in main.effects:
			if int(e.y) == y and not e.top and e.frame >= 0:
				screen.blit(main.assets[e.name], (e.x * SCALEX - (EFFECTSCALE//2), e.y * SCALEY - (EFFECTSCALE//2)), Rect(int(e.frame) * EFFECTSCALE, 0, EFFECTSCALE, EFFECTSCALE))
		
		for x in range(FIELDWIDTH):
			if not main.map[x][y] == None:
				screen.blit(main.assets[main.map[x][y]], (x * SCALEX, (y+2) * SCALEY - main.assets[main.map[x][y]].get_height()))
	
	for e in main.effects[:]:
		if e.top and e.frame >= 0:
			screen.blit(main.assets[e.name], (e.x * SCALEX - (EFFECTSCALE//2), e.y * SCALEY - (EFFECTSCALE//2)), Rect(int(e.frame) * EFFECTSCALE, 0, EFFECTSCALE, EFFECTSCALE))
		if int(e.frame) * EFFECTSCALE >= main.assets[e.name].get_width():
			main.effects.remove(e)
		e.frame += EFFECTSPEED
	
	if DEBUGMODE:
		for t in main.tanks:
			draw.line(screen, (0, 255, 0), ((t.x + 0.5) * SCALEX, (t.y + 1) * SCALEY), ((t.x + 0.5 + cos(t.aim_target*2*pi)) * SCALEX , (t.y + 1 + sin(t.aim_target*2*pi)) * SCALEY), 4)
			if t.ai_has_target:
				draw.line(screen, (255, 0, 0), ((t.x + 0.5) * SCALEX, (t.y + 1) * SCALEY), ((t.x + 0.5 + cos(t.aim_target*2*pi)) * SCALEX , (t.y + 1 + sin(t.aim_target*2*pi)) * SCALEY), 4)
			tar_list = [(t.x, t.y)] + t.ai_move_targets
			for i, tar in enumerate(tar_list):
				if i > 0:
					draw.line(screen, (0, 100, 255), ((tar[0]+0.5) * SCALEX, (tar[1]+1.5) * SCALEY), ((tar_list[i-1][0]+0.5) * SCALEX, (tar_list[i-1][1]+1.5) * SCALEY), 2)
					draw.rect(screen, (0, 255, 255), ((tar[0]+0.5) * SCALEX-4, (tar[1]+1.5) * SCALEY-4, 8, 8))
	
	draw_text(type_font, f"MISSION {main.stage} "[round_counter:min((-intro_counter + 150)//5, -1)], SCREENWIDTH/2, SCREENHEIGHT/2-90, True)
	draw_text(type_font, f"ENEMY TANKS: {len(main.tanks)-1} "[round_counter:min((-intro_counter + 50)//5, -1)], SCREENWIDTH/2, SCREENHEIGHT/2, True)
	
	if lose_counter > -1:
		draw_text(type_font, f"MISSION {main.stage} "[:min((-lose_counter + 60)//5, -1)], SCREENWIDTH/2, SCREENHEIGHT/2-90, True)
		draw_text(secret_font, "FAILED", SCREENWIDTH/2+140, SCREENHEIGHT/2-20, True, color=(255, 0, 0), rotation=20)
	if win_counter > -1:
		draw_text(type_font, f"MISSION {main.stage} "[:min((-win_counter + 60)//5, -1)], SCREENWIDTH/2, SCREENHEIGHT/2-90, True)
		draw_text(secret_font, "PASSED", SCREENWIDTH/2+140, SCREENHEIGHT/2-20, True, color=(255, 0, 0), rotation=20)
	
	draw_text(pixel_font, f"Lives: {main.lives}", 10, 10)
	
	if transition_counter >= 0:
		transition_surf.set_alpha(int((1-abs(transition_counter / TRANSITIONLENGTH - 1)) * 255), RLEACCEL)
		screen.blit(transition_surf, (0, 0))
	
	if over_counter > -1:
		draw_text(type_font, "GAME OVER"[:max(over_counter - 60, 0)//8], SCREENWIDTH/2, SCREENHEIGHT/2-150, True)
		draw_text(type_font, "THANKS FOR PLAYING!"[:max(over_counter - 140, 0)//5], SCREENWIDTH/2, SCREENHEIGHT/2+200, True)
	
	display.flip()
	clock.tick(60)
