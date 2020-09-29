
from settings import *
import main, ai, sound
from math import *

class Effect:
	frame = 0

	def __init__(self, name, x, y, top=True, offset=0, callback=lambda *_: None):
		self.name = name
		self.x = x
		self.y = y
		self.top = top
		self.frame = -offset
		self.callback = callback





class Mine:
	fuse = -ARMLENGTH

	def __init__(self, x, y, callback=lambda *_: None):
		self.x = x
		self.y = y
		self.callback = callback

	def tick(self):
		if self.fuse >= FUSELENGTH:
			self.explode()
		#if self.fuse == 0:
			#main.effects.append(Effect("particle1", self.x+0.5, self.y+0.5, False))
		self.fuse += 1

		self.detect = False
		for t in main.tanks:
			if not t.dead:
				if sqrt((self.x - t.x)**2 + (self.y - (t.y+1))**2) <= MINERANGE:
					self.detect = True
				if sqrt((self.x - t.x)**2 + (self.y - (t.y+1))**2) <= DETMINERANGE and self.fuse >= 0:
					self.explode()
					break

	def explode(self):
		main.effects.append(Effect("explosion2", self.x+0.5, self.y+0.5))
		for x in range(floor(-MINEWALLRANGE), ceil(MINEWALLRANGE+1)):
			for y in range(floor(-MINEWALLRANGE), ceil(MINEWALLRANGE+1)):
				tx = max(min(int(self.x+x), FIELDWIDTH-1), 0)
				ty = max(min(int(self.y+y-1), FIELDHEIGHT-1), 0)
				if sqrt(x**2 + y**2) <= MINEWALLRANGE and main.map[tx][ty] in [None, "dwall1", "dwall2", "dwall3"]:
					main.map[tx][ty] = None
					main.effects.append(Effect("smoke1", self.x+x+0.5, self.y+y-0.5, False, sqrt(x**2 + y**2)*3))

		main.mines.remove(self)
		main.draw_to_bg(main.assets["scorch_mine"], self.x+0.5, self.y+0.5)

		for m in main.mines:
			if sqrt((self.x - m.x)**2 + (self.y - m.y)**2) <= MINERANGE:
				m.explode()

		for t in main.tanks:
			if sqrt((self.x - t.x)**2 + (self.y - (t.y+1))**2) <= MINERANGE:
				t.destroy()

		self.callback()
		main.redraw_shadow()
		sound.play_sfx("explosion")





class Bullet:
	bounces = 0

	def __init__(self, x, y, dir, bounce_limit, rocket=False, shooter_id=-1, callback=lambda *_: None):
		self.x = x
		self.y = y
		self.dir = dir
		self.bounce_limit = bounce_limit
		self.speed = ROCKETSPEED if rocket else BULLETSPEED
		self.rocket = rocket
		self.shooter_id = shooter_id
		self.callback = callback

	def get_dir_sheet(self):
		r = round(self.dir * (SHEETWIDTH*SHEETHEIGHT)) % (SHEETWIDTH*SHEETHEIGHT)
		return r % SHEETWIDTH, r // SHEETWIDTH

	def tick(self):
		self.move()

		for i, t in enumerate(main.tanks):
			if sqrt((self.x - t.x)**2 + (self.y - t.y - 0.2)**2) <= DETTANKRANGE and i != self.shooter_id and not t.dead:
				t.destroy()
				self.destroy()
				return

		for m in main.mines:
			if sqrt((self.x - m.x)**2 + (self.y - m.y + 0.5)**2) <= DETMINERANGE:
				m.explode()
				self.destroy()
				return

		for b in main.bullets:
			if sqrt((self.x - b.x)**2 + (self.y - b.y)**2) <= DETBULLETRANGE and b != self:
				b.destroy()
				self.destroy()
				return

	def move(self):
		nx = self.x + cos(self.dir*2*pi) * self.speed
		ny = self.y + sin(self.dir*2*pi) * self.speed
		ix = int(self.x+0.5)
		iy = int(self.y+0.5)
		inx = int(nx+0.5)
		iny = int(ny+0.5)
		ntile = main.map[max(min(inx, FIELDWIDTH-1), 0)][max(min(iny, FIELDHEIGHT-1), 0)]

		if ix == inx:
			self.x = nx
			if iy == iny:
				self.y = ny
			else:
				if ntile == None:
					self.y = ny
				else:
					intery = (iny + iy) / 2
					self.y = -(ny - intery) + intery
					self.dir = -self.dir
					self.ricochet()
		elif iy == iny:
			self.y = ny
			if ntile == None:
				self.x = nx
			else:
				interx = (inx + ix) / 2
				self.x = -(nx - interx) + interx
				self.dir = 0.5 - self.dir
				self.ricochet()
		else:
			p = (ny-self.y) / (nx-self.x)
			interx = (inx + ix) / 2
			intery = (iny + iy) / 2

			if abs(p * (interx - self.x)) > abs(intery - self.y):
				if main.map[max(min(ix, FIELDWIDTH-1), 0)][max(min(iy+int(copysign(1, ny-self.y)), FIELDHEIGHT-1), 0)] == None:
					if ntile == None:
						self.x = nx
						self.y = ny
					else:
						self.x = -(nx - interx) + interx
						self.dir = 0.5 - self.dir
						self.ricochet()
				else:
					self.y = -(ny - intery) + intery
					self.dir = -self.dir
					self.ricochet()
			else:
				if main.map[max(min(ix+int(copysign(1, nx-self.x)), FIELDWIDTH-1), 0)][max(min(iy, FIELDHEIGHT-1), 0)] == None:
					if ntile == None:
						self.x = nx
						self.y = ny
					else:
						self.y = -(ny - intery) + intery
						self.dir = -self.dir
						self.ricochet()
				else:
					self.x = -(nx - interx) + interx
					self.dir = 0.5 - self.dir
					self.ricochet()

	def destroy(self):
		main.effects.append(Effect("particle1", self.x+0.5, self.y+1, False))
		self.callback()
		main.bullets.remove(self)
		sound.play_sfx("bullet_crash")

	def ricochet(self):
		self.bounces += 1
		if self.bounces > self.bounce_limit:
			self.destroy()
		else:
			sound.play_sfx("bullet_bonk")
		self.shooter_id = -1





class Tank:
	aim = 0
	body = 0
	aim_target = 0
	body_target = 0
	
	track_counter = 0
	move_sound_counter = 0
	
	movement = [0, 0]
	
	moving = False
	dead = False
	
	mines_placed = 0
	bullets_shot = 0
	
	shot_queue = 0
	shot_cooldown = 0
	
	aim_speed = TANKAIMSPEED
	
	def __init__(self, type, x, y, no_ai=False, stop=False):
		self.type = type
		self.x = x
		self.y = y
		self.ai = getattr(ai, "ai_" + type, lambda *_: None) if not no_ai else lambda *_: None
		self.stop = stop
		
		self.bullet_limit, self.bullet_bounce, self.mine_limit, self.rocket, self.speed = TANKPROPERTIES[type]
		
		self.ai_move_targets = []
		self.ai_has_target = False
		self.ai_target_timeout = 0
		self.ai_shot_timer = 0
		self.ai_stuck = 0
	
	def tick(self, tick_time):
		if not self.dead:
			try:
				self.ai(self, tick_time)
			except:
				pass
		
		if self.shot_queue > 0 and self.shot_cooldown <= 0:
			self.shot_queue -= 1
			self.shoot()
			self.shot_cooldown = TANKSHOTCOOLDOWN
		else:
			self.shot_cooldown -= 1
		
		self.moving = self.movement != [0, 0]
		if self.moving:
			self.body_target = atan2(self.movement[1], self.movement[0]) / 2 / pi
		self.movement = [0, 0]

		if abs(self.body_target - self.body) > 0.25:
			self.body += copysign(0.5, self.body_target - self.body)
		if abs(self.body_target - self.body) < TANKBODYSPEED:
			self.body = self.body_target
		elif self.moving:
			self.body += copysign(TANKBODYSPEED, self.body_target - self.body)

		if abs(self.aim_target - self.aim) > 0.5:
			self.aim += copysign(1, self.aim_target - self.aim)
		self.aim += (self.aim_target - self.aim) * self.aim_speed

		if self.moving:
			self.track_counter += TRACKSPEED * self.speed
			self.move_sound_counter += MOVESOUNDSPEED * self.speed

		if self.move_sound_counter >= 1:
			self.move_sound_counter -= 1
			sound.play_sfx("tank_move")

	def get_aim_sheet(self):
		r = round(self.aim * (SHEETWIDTH*SHEETHEIGHT)) % (SHEETWIDTH*SHEETHEIGHT)
		return r % SHEETWIDTH, r // SHEETWIDTH

	def get_body_sheet(self):
		r = round(self.body * (SHEETWIDTH*SHEETHEIGHT)) % (SHEETWIDTH*SHEETHEIGHT)
		return r % SHEETWIDTH, r // SHEETWIDTH

	def move_x(self, x):
		if not self.dead and self.speed > 0 and not self.stop:
			TC = TANKCOLLISION
			TTC = TANKTANKCOLLISION

			r = copysign(TC, x)
			cx = self.x + r + x + 0.5
			if main.map[int(cx)][int(self.y + 0.5 - TC)] == None and main.map[int(cx)][int(self.y + 0.5 + TC)] == None:
				for i, t in enumerate(main.tanks):
					if i == main.tanks.index(self) or t.dead:
						continue
					if (t.x - TTC < self.x + r + x <= t.x + TTC and
						(t.y - TTC < self.y - TC <= t.y + TTC or t.y - TTC < self.y + TC <= t.y + TTC)):
						self.x = t.x - copysign(TTC + TC + 0.001, x)
						break
				else:
					self.x += x
					self.movement[0] = x
			else:
				self.x += copysign(int(cx) - self.x - r, x) - copysign(0.501, x)

	def move_y(self, y):
		if not self.dead and self.speed > 0 and not self.stop:
			TC = TANKCOLLISION
			TTC = TANKTANKCOLLISION
			

			r = copysign(TANKCOLLISION, y)
			cy = self.y + r + y + 0.5
			if main.map[int(self.x + 0.5 - TC)][int(cy)] == None and main.map[int(self.x + 0.5 + TC)][int(cy)] == None:
				for i, t in enumerate(main.tanks):
					if i == main.tanks.index(self) or t.dead:
						continue
					if (t.y - TTC < self.y + r + y <= t.y + TTC and
						(t.x - TTC < self.x - TC <= t.x + TTC or t.x - TTC < self.x + TC <= t.x + TTC)):
						self.y = t.y - copysign(TTC + TC + 0.001, y)
						break
				else:
					self.y += y
					self.movement[1] = y
			else:
				self.y += copysign(int(cy) - self.y - r, y) - copysign(0.501, y)
	
	def place_mine(self):
		if self.mines_placed < self.mine_limit and not self.dead and not self.stop and (int(self.x+0.5), int(self.y+1.5)) not in [(m.x, m.y) for m in main.mines] :
			main.mines.append(Mine(int(self.x+0.5), int(self.y+1.5), self.mine_callback))
			self.mines_placed += 1
			sound.play_sfx("mine_place")
	
	def destroy(self):
		# return
		if not self.dead:
			self.dead = True
			main.effects.append(Effect("explosion1", self.x+0.5, self.y+1))
			main.draw_to_bg(main.assets["scorch_tank"], self.x+0.5, self.y+1.5)
			sound.remove_mission_loop(self.type)
			sound.play_sfx("explosion")
			if main.tanks.index(self) != 0:
				sound.play_sfx("tank_hit")

	def shoot(self):
		x = self.x + cos(self.aim*2*pi)
		y = self.y + sin(self.aim*2*pi)
		if not self.dead and not self.stop and self.bullets_shot < self.bullet_limit and main.map[int(x+0.5)][int(y+0.5)] == None:
			if self.shot_cooldown <= 0:
				self.shot_cooldown = TANKSHOTCOOLDOWN
				main.bullets.append(Bullet(x, y, self.aim, self.bullet_bounce, self.rocket, main.tanks.index(self), self.bullet_callback))
				self.bullets_shot += 1
				sound.play_sfx("tank_shoot")
			else:
				self.shot_queue += 1

	def mine_callback(self):
		self.mines_placed -= 1

	def bullet_callback(self):
		self.bullets_shot -= 1
