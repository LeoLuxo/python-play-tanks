
from settings import *
import main
import time

from math import *

def map_out_tanks():
	global tank_mapout 
	tank_mapout = [[None for y in range(FIELDHEIGHT)] for x in range(FIELDWIDTH)]
	for i, t in enumerate(main.tanks):
		if not t.dead:
			tank_mapout[int(t.x)][int(t.y)] = i
			tank_mapout[int(t.x)][int(t.y+1)] = i
			tank_mapout[int(t.x+1)][int(t.y+1)] = i
			tank_mapout[int(t.x+1)][int(t.y)] = i
	for i, m in enumerate(main.mines):
		for x in range(floor(-MINEWALLRANGE), ceil(MINEWALLRANGE+1)):
			for y in range(floor(-MINEWALLRANGE), ceil(MINEWALLRANGE+1)):
				if sqrt(x**2 + y**2) <= MINEWALLRANGE and m.fuse >= 0:
					tank_mapout[max(min(int(m.x+x), FIELDWIDTH-1), 0)][max(min(int(m.y+y-1), FIELDHEIGHT-1), 0)] = "MINE"
	
	if DEBUGMODE:
		for x in range(FIELDWIDTH):
			for y in range(FIELDHEIGHT):
				if tank_mapout[x][y] != None:
					draw.rect(screen, (200, 200, 200), (int((x) * SCALEX), int((y+1) * SCALEY), SCALEX, SCALEY), 5)

def path_target(t, x, y, max=500):
	ignore = (0, main.tanks.index(t), None)
	dist = lambda a, b: sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
	
	def path(x1, y1, x2, y2):
		queue = [([(x1, y1)], dist((x1, y1), (x, y)))]
		done = []
		
		while len(queue) > 0 and len(done) <= max:
			queue.sort(key=lambda x: x[1])
			
			curr = queue.pop(0)
			path = curr[0]
			pos = path[-1]
			done.append(pos)
			
			if (pos[0], pos[1] + 1) == (x2, y2):
				return path + [(pos[0], pos[1] + 1)]
			elif (pos[0], pos[1] - 1) == (x2, y2):
				return path + [(pos[0], pos[1] - 1)]
			elif (pos[0] + 1, pos[1]) == (x2, y2):
				return path + [(pos[0] + 1, pos[1])]
			elif (pos[0] - 1, pos[1]) == (x2, y2):
				return path + [(pos[0] - 1, pos[1])]
			else:
				if main.map[pos[0]][pos[1] + 1] == None and tank_mapout[pos[0]][pos[1] + 1] in ignore and (pos[0], pos[1] + 1) not in done:
					queue.append((path + [(pos[0], pos[1] + 1)], dist((pos[0], pos[1] + 1), (x2, y2))))
				if main.map[pos[0]][pos[1] - 1] == None and tank_mapout[pos[0]][pos[1] - 1] in ignore and (pos[0], pos[1] - 1) not in done:
					queue.append((path + [(pos[0], pos[1] - 1)], dist((pos[0], pos[1] - 1), (x2, y2))))
				if main.map[pos[0] + 1][pos[1]] == None and tank_mapout[pos[0] + 1][pos[1]] in ignore and (pos[0] + 1, pos[1]) not in done:
					queue.append((path + [(pos[0] + 1, pos[1])], dist((pos[0] + 1, pos[1]), (x2, y2))))
				if main.map[pos[0] - 1][pos[1]] == None and tank_mapout[pos[0] - 1][pos[1]] in ignore and (pos[0] - 1, pos[1]) not in done:
					queue.append((path + [(pos[0] - 1, pos[1])], dist((pos[0] - 1, pos[1]), (x2, y2))))
		
		return []
	
	def path2(x1, y1, x2, y2):
		posx = x1
		posy = y1
		dx = cos(atan2(y2 - y1, x2 - x1)) * 0.5
		dy = sin(atan2(y2 - y1, x2 - x1)) * 0.5
		
		while not (abs(posx - x2) < 0.5 and abs(posy - y2) < 0.5):
			posx += dx
			posy += dy
			
			# draw.circle(screen, (255, 0, 0), (int((posx+0.5) * SCALEX), int((posy+1.5) * SCALEY)), 5)
			# draw.rect(screen, (200, 200, 200), (int(posx+0.5) * SCALEX, int(posy+1.5) * SCALEY, SCALEX, SCALEY), 5)
			# display.flip()
			# event.pump()
			# time.sleep(0.04)
			
			if (main.map[int(posx+0.5)][int(posy+0.5)] != None or tank_mapout[int(posx+0.5)][int(posy+0.5)] not in ignore or
				(abs(int(posx+0.5) - int(posx+0.5-dx)) == 1 and abs(int(posy+0.5) - int(posy+0.5-dy)) == 1 and
				(main.map[int(posx+0.5)][int(posy+0.5-dy)] != None or tank_mapout[int(posx+0.5)][int(posy+0.5-dy)] not in ignore or
				main.map[int(posx+0.5-dx)][int(posy+0.5)] != None or tank_mapout[int(posx+0.5-dx)][int(posy+0.5)] not in ignore))):
				return False
		return True
	
	if len(t.ai_move_targets) >= 1 and dist((int(t.x+0.5), int(t.y+0.5)), t.ai_move_targets[0]) < 2:
		ix = int(t.ai_move_targets[0][0])
		iy = int(t.ai_move_targets[0][1])
	else:
		ix = int(t.x+0.5)
		iy = int(t.y+0.5)
	
	t.ai_move_targets = path(ix, iy, int(x), int(y))
	
	if len(t.ai_move_targets) <= 0:
		t.ai_stuck = True
		return
	else:
		t.ai_stuck = False
	
	path_copy = t.ai_move_targets[:]
	t.ai_move_targets = []
	i = 0
	while i < len(path_copy)-2:
		if ((path_copy[i] == (path_copy[i+2][0]-1, path_copy[i+2][1]-1) and main.map[path_copy[i][0]+1][path_copy[i][1]] == None and main.map[path_copy[i][0]][path_copy[i][1]+1] == None and tank_mapout[path_copy[i][0]+1][path_copy[i][1]] in ignore and tank_mapout[path_copy[i][0]][path_copy[i][1]+1] in ignore and (path_copy[i] == (path_copy[i+1][0]-1, path_copy[i+1][1]) or path_copy[i] == (path_copy[i+1][0], path_copy[i+1][1]-1))) or
			(path_copy[i] == (path_copy[i+2][0]-1, path_copy[i+2][1]+1) and main.map[path_copy[i][0]+1][path_copy[i][1]] == None and main.map[path_copy[i][0]][path_copy[i][1]-1] == None and tank_mapout[path_copy[i][0]+1][path_copy[i][1]] in ignore and tank_mapout[path_copy[i][0]][path_copy[i][1]-1] in ignore and (path_copy[i] == (path_copy[i+1][0]-1, path_copy[i+1][1]) or path_copy[i] == (path_copy[i+1][0], path_copy[i+1][1]+1))) or
			(path_copy[i] == (path_copy[i+2][0]+1, path_copy[i+2][1]+1) and main.map[path_copy[i][0]-1][path_copy[i][1]] == None and main.map[path_copy[i][0]][path_copy[i][1]-1] == None and tank_mapout[path_copy[i][0]-1][path_copy[i][1]] in ignore and tank_mapout[path_copy[i][0]][path_copy[i][1]-1] in ignore and (path_copy[i] == (path_copy[i+1][0]+1, path_copy[i+1][1]) or path_copy[i] == (path_copy[i+1][0], path_copy[i+1][1]+1))) or
			(path_copy[i] == (path_copy[i+2][0]+1, path_copy[i+2][1]-1) and main.map[path_copy[i][0]-1][path_copy[i][1]] == None and main.map[path_copy[i][0]][path_copy[i][1]+1] == None and tank_mapout[path_copy[i][0]-1][path_copy[i][1]] in ignore and tank_mapout[path_copy[i][0]][path_copy[i][1]+1] in ignore and (path_copy[i] == (path_copy[i+1][0]+1, path_copy[i+1][1]) or path_copy[i] == (path_copy[i+1][0], path_copy[i+1][1]-1)))):
			i += 2
		else:
			i += 1
		t.ai_move_targets.append(path_copy[i])
	
	path_copy = t.ai_move_targets[:]
	t.ai_move_targets = []
	i = 0
	while i < len(path_copy)-1:
		delta = (path_copy[i][0] - path_copy[i+1][0], path_copy[i][1] - path_copy[i+1][1])
		j = 1
		while j + i < len(path_copy)-1 and delta == (path_copy[i+j][0] - path_copy[i+1+j][0], path_copy[i+j][1] - path_copy[i+1+j][1]):
			j += 1
		t.ai_move_targets.append(path_copy[i])
		i += j
	if len(path_copy) > 0:
		t.ai_move_targets.append(path_copy[-1])
	
	# tar_list = [(t.x, t.y)] + t.ai_move_targets
	# for i, tar in enumerate(tar_list):
	# 	if i > 0:
	# 		draw.line(screen, (0, 255, 100), ((tar[0]+0.5) * SCALEX, (tar[1]+1.5) * SCALEY), ((tar_list[i-1][0]+0.5) * SCALEX, (tar_list[i-1][1]+1.5) * SCALEY), 2)
	# 		draw.rect(screen, (0, 255, 0), ((tar[0]+0.5) * SCALEX-4, (tar[1]+1.5) * SCALEY-4, 8, 8))
	# display.flip()
	
	path_copy = t.ai_move_targets[:]
	t.ai_move_targets = []
	i = 0
	while i < len(path_copy):
		j = 1
		while j + i < len(path_copy)-1 and path2(*path_copy[i], *path_copy[i+1+j]):
			j += 1
		t.ai_move_targets.append(path_copy[i])
		i += j
	t.ai_move_targets.append(path_copy[-1])
	
	# time.sleep(3)





def move_target(t):
	if len(t.ai_move_targets) == 0:
		return
	d = sqrt((t.ai_move_targets[0][0]-t.x)**2 + (t.ai_move_targets[0][1]-t.y)**2)
	if d <= t.speed:
		t.move_x(t.ai_move_targets[0][0]-t.x)
		t.move_y(t.ai_move_targets[0][1]-t.y)
		del t.ai_move_targets[0]
	else:
		t.move_x((t.ai_move_targets[0][0]-t.x) / d * t.speed)
		t.move_y((t.ai_move_targets[0][1]-t.y) / d * t.speed)


def sight_angle(t):
	return atan2(main.tanks[0].y - t.y, main.tanks[0].x - t.x) / pi / 2


def has_sight(t):
	try_res = try_bullet(t, sight_angle(t))
	return try_res[0] and try_res[1] == 0


def try_bullet(t, angle):
	speed = 0.5
	maxd = 50
	d = maxd
	b = t.bullet_bounce
	x = t.x
	y = t.y
	
	while d >= 0 and b >= 0:
		d -= speed
		nx = x + cos(angle*2*pi) * speed
		ny = y + sin(angle*2*pi) * speed
		ix = int(x+0.5)
		iy = int(y+0.5)
		inx = int(nx+0.5)
		iny = int(ny+0.5)
		ntile = main.map[max(min(inx, FIELDWIDTH-1), 0)][max(min(iny, FIELDHEIGHT-1), 0)]
		
		if ix == inx:
			x = nx
			if iy == iny:
				y = ny
			else:
				if ntile == None:
					y = ny
				else:
					intery = (iny + iy) / 2
					y = -(ny - intery) + intery
					angle = -angle
					b -= 1
					d = maxd
		elif iy == iny:
			y = ny
			if ntile == None:
				x = nx
			else:
				interx = (inx + ix) / 2
				x = -(nx - interx) + interx
				angle = 0.5 - angle
				b -= 1
				d = maxd
		else:
			p = (ny-y) / (nx-x)
			interx = (inx + ix) / 2
			intery = (iny + iy) / 2
			
			if abs(p * (interx - x)) > abs(intery - y):
				if main.map[max(min(ix, FIELDWIDTH-1), 0)][max(min(iy+int(copysign(1, ny-y)), FIELDHEIGHT-1), 0)] == None:
					if ntile == None:
						x = nx
						y = ny
					else:
						x = -(nx - interx) + interx
						angle = 0.5 - angle
						b -= 1
						d = maxd
				else:
					y = -(ny - intery) + intery
					angle = -angle
					b -= 1
					d = maxd
			else:
				if main.map[max(min(ix+int(copysign(1, nx-x)), FIELDWIDTH-1), 0)][max(min(iy, FIELDHEIGHT-1), 0)] == None:
					if ntile == None:
						x = nx
						y = ny
					else:
						y = -(ny - intery) + intery
						angle = -angle
						b -= 1
						d = maxd
				else:
					x = -(nx - interx) + interx
					angle = 0.5 - angle
					b -= 1
					d = maxd
		
		
		if sqrt((x - main.tanks[0].x)**2 + (y - main.tanks[0].y - 0.2)**2) <= DETTANKRANGE:
			return True, t.bullet_bounce - b
		
		for ti in main.tanks[1:]:
			if sqrt((x - ti.x)**2 + (y - ti.y - 0.2)**2) <= DETTANKRANGE*2 and not ti.dead:
				if ti != t:
					return False, -1
				elif ti == t and b < t.bullet_bounce:
					return False, -1
	return False, -1
