
from settings import *
import main
from pygame import *
import os, string, random, sys

mixer.pre_init(frequency=44100, channels=2, buffer=512)
mixer.init()
mixer.set_num_channels(32)
mixer.set_reserved(13)

instr = {i.replace(".ogg", "") : mixer.Sound("assets/sounds/instr/" + i) for i in os.listdir("assets/sounds/instr/")}
music = {i.replace(".ogg", "") : mixer.Sound("assets/sounds/" + i) for i in os.listdir("assets/sounds/") if os.path.isfile("assets/sounds/" + i)}
sfx = {}

for i in os.listdir("assets/sounds/sfx/"):
	name = i.replace(".ogg", "")
	if True in [d in name for d in string.digits]:
		if name[:-1] in sfx:
			sfx[name[:-1]].append(mixer.Sound("assets/sounds/sfx/" + i))
		else:
			sfx[name[:-1]] = [mixer.Sound("assets/sounds/sfx/" + i)]
		if name[:-1] in VOLUMES:
			sfx[name[:-1]][-1].set_volume(VOLUMES[name[:-1]])
	else:
		sfx[name] = [mixer.Sound("assets/sounds/sfx/" + i)]
	if name in VOLUMES:
		sfx[name][-1].set_volume(VOLUMES[name])

for k, v in music.items():
	if k in VOLUMES:
		v.set_volume(VOLUMES[k])

channels = {i : mixer.Channel(CHANNELS[i]) for i in instr.keys()}
channels["results"] = mixer.Channel(12)

channels["results"].set_endevent(25)

def build_mission_loop():
	types = ["base"]
	for t in main.tanks:
		if t.type not in types and t.type in THEME_VERSIONS:
			types.append(t.type)
	
	for i in instr.values():
		i.set_volume(0)
	
	for t in types:
		add = THEME_VERSIONS[t][0]
		sub = THEME_VERSIONS[t][1]
		for a in add:
			instr[a].set_volume(1)
		for s in sub:
			instr[s].set_volume(0)

def remove_mission_loop(type):
	types = []
	for t in main.tanks:
		if t.type not in types and t.type in THEME_VERSIONS and not t.dead:
			types.append(t.type)
	
	if type in types or type not in THEME_VERSIONS:
		return
	
	sub = THEME_VERSIONS[type][0]
	add = THEME_VERSIONS[type][1]
	for i in add:
		instr[i].set_volume(1)
	for i in sub:
		instr[i].fadeout(FADEOUTLENGTH)

def play_mission_loop():
	for i in instr:
		if not SOUNDMUTED:
			channels[i].play(instr[i], loops=-1)

def stop_mission_loop():
	for i in instr:
		channels[i].fadeout(FADEOUTLENGTH)

def play_mission_intro():
	if not SOUNDMUTED:
		music["mission_intro"].play()

def play_mission_win():
	if not SOUNDMUTED:
		music["mission_win"].play()
	stop_mission_loop()

def play_mission_lose():
	if not SOUNDMUTED:
		music["mission_lose"].play()
	stop_mission_loop()

def play_results():
	if not SOUNDMUTED:
		channels["results"].play(music["results_intro"])
		channels["results"].queue(music["results_loop"])

def play_results_loop():
	if not SOUNDMUTED:
		channels["results"].queue(music["results_loop"])

def play_sfx(name):
	if not SOUNDMUTED:
		random.choice(sfx[name]).play()

end_event = {
	25 : play_results_loop,
}
