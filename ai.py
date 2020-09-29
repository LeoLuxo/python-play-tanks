
from settings import *
from ai_math import *
import ai_math
import main, sound

from math import *
from random import seed, randint, uniform

seed(42)




def ai_grey(t, tick_time):
	if not t.ai_has_target:
		if abs(t.aim - t.aim_target) < 0.02:
			t.aim_speed = uniform(0.005, 0.02)
			t.aim_target = uniform(0, 1)
		
		if not t.stop and t.bullets_shot < t.bullet_limit:
			for _ in range(3):
				r = t.aim + uniform(-0.3, 0.3)
				try_res = try_bullet(t, r)
				if try_res[0] and ((try_res[1] == 0 and randint(0, 20) == 0) or (try_res[1] >= 1 and randint(0, 200) == 0)):
					t.ai_has_target = True
					t.aim_target = r
					t.aim_speed = 0.2
	elif abs(t.aim - t.aim_target) < 0.005:
		t.shoot()
		t.ai_has_target = False






def ai_yellow(t, tick_time):
	if has_sight(t):
		t.ai_has_target = True
		t.aim_speed = 0.2
		t.aim_target = sight_angle(t)
		if randint(0, 100) == 0 and abs(t.aim - t.aim_target) < 0.01:
			t.shoot()
	elif abs(t.aim - t.aim_target) < 0.1:
		t.ai_has_target = False
		t.aim_speed = 0.005
		t.aim_target = uniform(0, 1)
	
	t.ai_target_timeout -= 1
	
	if t.ai_target_timeout <= 0 or len(t.ai_move_targets) == 0:
		t.ai_target_timeout = randint(180, 420)
		tar = (randint(0, FIELDWIDTH-1), randint(0, FIELDHEIGHT-1))
		while main.map[tar[0]][tar[1]] != None or ai_math.tank_mapout[tar[0]][tar[1]] not in (0, main.tanks.index(t), None):
			tar = (randint(0, FIELDWIDTH-1), randint(0, FIELDHEIGHT-1))
		path_target(t, *tar)
	else:
		move_target(t)






def ai_blue(t, tick_time):
	if not has_sight(t):
		t.ai_has_target = False
		t.aim_speed = 0.2
		t.ai_shot_timer = -1
	elif has_sight(t) and randint(0, 300) == 0:
		t.ai_has_target = True
		t.aim_speed = 0.5
		t.ai_shot_timer = randint(0, 49)
		t.aim_target = sight_angle(t) + uniform(-0.02, 0.02)
	
	if t.ai_shot_timer % 10 == 0:
		t.shoot()
		t.aim_target = sight_angle(t) + uniform(-0.02, 0.02)
	
	if t.ai_shot_timer >= 0:
		t.ai_shot_timer -= 1
	else:
		t.aim_target = sight_angle(t)
	
	t.ai_target_timeout -= 1
	
	if t.ai_target_timeout <= 0 or (len(t.ai_move_targets) == 0 and not t.ai_stuck):
		t.ai_target_timeout = randint(60, 180)
		path_target(t, int(main.tanks[0].x + 0.5), int(main.tanks[0].y + 0.5))
	else:
		move_target(t)






def ai_green(t, tick_time):
	t.ai_has_target = False
	
	if abs(t.aim - t.aim_target) < 0.1:
		t.aim_speed = 0.05
		t.aim_target = uniform(0, 1)
	
	t.ai_target_timeout -= 1
	
	def find_tar():
		tar = (randint(1, FIELDWIDTH-2), randint(1, FIELDHEIGHT-2))
		while main.map[tar[0]][tar[1]] != None or ai_math.tank_mapout[tar[0]][tar[1]] not in (0, main.tanks.index(t), None):
			tar = (randint(1, FIELDWIDTH-2), randint(1, FIELDHEIGHT-2))
		for x in range(-2, 3):
			for y in range(-2, 3):
				if (main.map[max(min(tar[0]+x, FIELDWIDTH-1), 0)][max(min(tar[1]+y, FIELDHEIGHT-1), 0)] == None and
					(main.map[max(min(tar[0]+x+1, FIELDWIDTH-1), 0)][max(min(tar[1]+y, FIELDHEIGHT-1), 0)] in ["dwall1", "dwall2", "dwall3"] or main.map[tar[0]+x-1][tar[1]+y] in ["dwall1", "dwall2", "dwall3"] or main.map[tar[0]+x][tar[1]+y+1] in ["dwall1", "dwall2", "dwall3"] or main.map[tar[0]+x+1][tar[1]+y-1] in ["dwall1", "dwall2", "dwall3"])):
					return (tar[0]+x, tar[1]+y)
		return tar
	
	if t.ai_stuck:
		t.ai_target_timeout = randint(0, 5)
	if t.ai_target_timeout <= 0 or len(t.ai_move_targets) == 0:
		t.ai_target_timeout = randint(420, 540)
		path_target(t, *find_tar())
	else:
		tar_len = len(t.ai_move_targets)
		move_target(t)
		if len(t.ai_move_targets) == 0 and randint(0, 2) == 0:
			t.place_mine()
		if (tick_time % 100 == 0 or len(t.ai_move_targets) == tar_len - 1) and len(t.ai_move_targets) > 1:
			if ai_math.tank_mapout[t.ai_move_targets[-1][0]][t.ai_move_targets[-1][1]] == "MINE":
				path_target(t, *find_tar())
			else:
				path_target(t, *t.ai_move_targets[-1])
				
			
				



def ai_red(t, tick_time):
	if not t.ai_has_target:
		if abs(t.aim - t.aim_target) < 0.02:
			t.aim_speed = 0.5
			t.aim_target = sight_angle(t)
		
		if not t.stop and t.bullets_shot < t.bullet_limit:
			for _ in range(5):
				r = t.aim + uniform(-0.5, 0.5)
				try_res = try_bullet(t, r)
				if try_res[0] and (try_res[1] >= 3 and randint(0, 10) == 0):
					t.ai_has_target = True
					t.aim_target = r
					t.aim_speed = 0.5
	elif abs(t.aim - t.aim_target) < 0.002:
		t.shoot()
		t.ai_has_target = False







def ai_black(t, tick_time):
	if not t.ai_has_target:
		if abs(t.aim - t.aim_target) < 0.02:
			t.aim_speed = 0.5
			t.aim_target = sight_angle(t)
		
		if not t.stop and t.bullets_shot < t.bullet_limit:
			for _ in range(5):
				r = t.aim + uniform(-0.5, 0.5)
				try_res = try_bullet(t, r)
				if try_res[0] and (try_res[1] >= 1 and randint(0, 10) == 0):
					t.ai_has_target = True
					t.aim_target = r
					t.aim_speed = 0.5
	elif abs(t.aim - t.aim_target) < 0.002:
		t.shoot()
		t.ai_has_target = False
	
	t.ai_target_timeout -= 1
	
	def find_tar():
		tar = (randint(1, FIELDWIDTH-2), randint(1, FIELDHEIGHT-2))
		while main.map[tar[0]][tar[1]] != None or ai_math.tank_mapout[tar[0]][tar[1]] not in (0, main.tanks.index(t), None):
			tar = (randint(1, FIELDWIDTH-2), randint(1, FIELDHEIGHT-2))
		for x in range(-2, 3):
			for y in range(-2, 3):
				if (main.map[max(min(tar[0]+x, FIELDWIDTH-1), 0)][max(min(tar[1]+y, FIELDHEIGHT-1), 0)] == None and
					(main.map[max(min(tar[0]+x+1, FIELDWIDTH-1), 0)][max(min(tar[1]+y, FIELDHEIGHT-1), 0)] in ["dwall1", "dwall2", "dwall3"] or main.map[tar[0]+x-1][tar[1]+y] in ["dwall1", "dwall2", "dwall3"] or main.map[tar[0]+x][tar[1]+y+1] in ["dwall1", "dwall2", "dwall3"] or main.map[tar[0]+x+1][tar[1]+y-1] in ["dwall1", "dwall2", "dwall3"])):
					return (tar[0]+x, tar[1]+y)
		return tar
	
	if t.ai_target_timeout <= 0 or len(t.ai_move_targets) == 0:
		t.ai_target_timeout = randint(180, 420)
		path_target(t, *find_tar())
	else:
		tar_len = len(t.ai_move_targets)
		move_target(t)
		if len(t.ai_move_targets) == 0 and randint(0, 2) == 0:
				t.place_mine()
		if len(t.ai_move_targets) == tar_len - 1 and len(t.ai_move_targets) > 1:
			if ai_math.tank_mapout[t.ai_move_targets[-1][0]][t.ai_move_targets[-1][1]] == "MINE":
				path_target(t, *find_tar())
			else:
				path_target(t, *t.ai_move_targets[-1])
	