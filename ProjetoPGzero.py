# Simple Platformer - Plataformas Aéreas Funcionais
import random
from pygame import Rect
import pgzrun

# -------------------------
# SCREEN SETTINGS
# -------------------------
WIDTH = 800
HEIGHT = 600

# -------------------------
# GAME STATE
# -------------------------
game_state = "MENU"
music_on = True
REQUIRED_COINS = 5
coins_collected = 0

# -------------------------
# HERO SETTINGS
# -------------------------
HERO_SPEED = 6
GRAVITY = 0.6
JUMP_VELOCITY = -11

# -------------------------
# UI BUTTONS
# -------------------------
start_btn = Rect(300, 200, 200, 50)
music_btn = Rect(300, 270, 200, 50)
exit_btn = Rect(300, 340, 200, 50)
restart_btn = Rect(WIDTH-150, 10, 140, 36)

# -------------------------
# PLATFORMS
# -------------------------
class Platform:
    def __init__(self, x, y, w, h):
        self.rect = Rect(x, y, w, h)

platforms = [
    Platform(150, 450, 200, 20),
    Platform(450, 350, 200, 20),
    Platform(100, 250, 150, 20),
    Platform(500, 200, 180, 20),
    Platform(300, 150, 150, 20),
]

# -------------------------
# HERO CLASS
# -------------------------
class Hero:
    def __init__(self, x, y):
        self.actor = Actor("hero_idle_1", (x, y))
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True
        self.sprite_index = 0.0
        self.idle_r = ["hero_idle_1","hero_idle_2"]
        self.idle_l = ["hero_idle_left_1","hero_idle_left_2"]
        self.run_r = ["hero_run_1","hero_run_2"]
        self.run_l = ["hero_run_left_1","hero_run_left_2"]

    @property
    def x(self): return self.actor.x
    @x.setter
    def x(self, value): self.actor.x = value
    @property
    def y(self): return self.actor.y
    @y.setter
    def y(self, value): self.actor.y = value
    @property
    def rect(self):
        w,h = self.actor.width,self.actor.height
        return Rect(int(self.x-w/2), int(self.y-h/2), w,h)

    def update(self):
        self.vy += GRAVITY
        self.y += self.vy
        self.vx = 0

        if keyboard.left:
            self.vx=-HERO_SPEED; self.facing_right=False; self.animate_run()
        elif keyboard.right:
            self.vx=HERO_SPEED; self.facing_right=True; self.animate_run()
        else: self.animate_idle()
        self.x += self.vx

        # Morre se sair da tela
        if self.x<0 or self.x>WIDTH or self.y>HEIGHT+50:
            self.die()

        self.on_ground=False
        # Colisão aprimorada: permite pousar mesmo vindo de baixo
        for p in platforms:
            if self.rect.bottom + self.vy >= p.rect.top and \
               self.rect.bottom <= p.rect.top + 15 and \
               self.rect.right > p.rect.left and \
               self.rect.left < p.rect.right and self.vy >= -15:
                self.y = p.rect.top - self.actor.height/2
                self.vy = 0
                self.on_ground=True

    def jump(self):
        if self.on_ground: self.vy=JUMP_VELOCITY; self.on_ground=False; self.play_sound("jump")

    def animate_idle(self):
        frames=self.idle_r if self.facing_right else self.idle_l
        self.sprite_index=(self.sprite_index+0.08)%len(frames)
        self.actor.image=frames[int(self.sprite_index)]

    def animate_run(self):
        frames=self.run_r if self.facing_right else self.run_l
        self.sprite_index=(self.sprite_index+0.16)%len(frames)
        self.actor.image=frames[int(self.sprite_index)]

    def play_sound(self,name):
        try: getattr(sounds,name).play()
        except: pass

    def die(self):
        global game_state
        self.play_sound("hit")
        game_state="GAME_OVER"

# -------------------------
# ENEMY CLASS
# -------------------------
class Enemy:
    def __init__(self,x,y,l_bound,r_bound,speed=2):
        self.actor=Actor("enemy_walk_1",(x,y))
        self.left=l_bound; self.right=r_bound; self.speed=speed; self.dir=1; self.idx=0
        self.sprites=["enemy_walk_1","enemy_walk_2"]

    @property
    def x(self): return self.actor.x
    @x.setter
    def x(self,val): self.actor.x=val
    @property
    def y(self): return self.actor.y
    @property
    def rect(self):
        w,h=self.actor.width,self.actor.height
        return Rect(int(self.x-w/2), int(self.y-h/2), w,h)

    def update(self):
        self.x += self.speed*self.dir
        if self.x <= self.left: self.x=self.left; self.dir=1
        elif self.x >= self.right: self.x=self.right; self.dir=-1
        self.idx=(self.idx+0.12)%len(self.sprites)
        self.actor.image=self.sprites[int(self.idx)]

# -------------------------
# GAME OBJECTS
# -------------------------
player=Hero(200, 100)
enemies=[
    Enemy(200,430,150,350),
    Enemy(500,330,450,650),
    Enemy(320,130,300,450),
    Enemy(600,180,500,680)
]
coin_positions=[(250,410),(520,310),(120,210),(550,180),(350,140)]
coins=[Actor("coin",pos) for pos in coin_positions]

# -------------------------
# HELPERS
# -------------------------
def collect_coins():
    global coins_collected
    for c in coins[:]:
        if player.actor.colliderect(c):
            player.play_sound("collect")
            coins.remove(c)
            coins_collected+=1
            if coins_collected>=REQUIRED_COINS: reset_run()
            break

def check_enemy_hits():
    for e in enemies:
        if player.actor.colliderect(e.actor):
            player.die(); return

def reset_run():
    global coins,coins_collected,enemies,player
    coins_collected=0
    coins=[Actor("coin",pos) for pos in coin_positions]
    player.x=200; player.y=100; player.vx=0; player.vy=0; player.on_ground=False
    enemies=[
        Enemy(200,430,150,350),
        Enemy(500,330,450,650),
        Enemy(320,130,300,450),
        Enemy(600,180,500,680)
    ]

def draw_button(rect,text,color):
    screen.draw.filled_rect(rect,color)
    screen.draw.text(text,center=rect.center,fontsize=28,color="white")

def play_music():
    try:
        if music_on: music.play("background")
        else: music.stop()
    except: pass

# -------------------------
# PYGAME ZERO HOOKS
# -------------------------
def update():
    if game_state=="PLAYING":
        player.update()
        for e in enemies: e.update()
        collect_coins()
        check_enemy_hits()

def draw():
    screen.clear()
    if game_state=="MENU":
        screen.fill("gray")
        draw_button(start_btn,"START GAME",(40,120,80))
        draw_button(music_btn,"MUSIC ON" if music_on else "MUSIC OFF",(70,70,70))
        draw_button(exit_btn,"EXIT",(120,30,30))
        return
    elif game_state=="GAME_OVER":
        screen.fill("black")
        screen.draw.text("GAME OVER",center=(WIDTH//2,HEIGHT//2-30),fontsize=60,color="red")
        screen.draw.text("Click to return to MENU",center=(WIDTH//2,HEIGHT//2+30),fontsize=28,color="white")
        return

    try: screen.blit("background",(0,0))
    except: screen.fill("skyblue")

    for p in platforms:
        try:
            t=Actor("platform_tile"); t.pos=(p.rect.x+p.rect.width/2,p.rect.y+p.rect.height/2); t.draw()
        except: screen.draw.filled_rect(p.rect,(100,100,100))
    for c in coins: c.draw()
    for e in enemies: e.actor.draw()
    player.actor.draw()
    screen.draw.text(f"COINS: {coins_collected}/{REQUIRED_COINS}",(10,10),fontsize=32,color="yellow")
    screen.draw.text("RESTART",center=restart_btn.center,fontsize=22,color="white")

def on_key_down(key):
    global game_state,music_on
    if key==keys.RETURN:
        if game_state=="MENU": game_state="PLAYING"; play_music()
        elif game_state=="GAME_OVER": game_state="MENU"; reset_run()
    elif key==keys.SPACE and game_state=="PLAYING": player.jump()
    elif key==keys.M: music_on=not music_on; play_music()

def on_mouse_down(pos):
    global game_state,music_on
    if game_state=="MENU":
        if start_btn.collidepoint(pos): game_state="PLAYING"; play_music()
        elif music_btn.collidepoint(pos): music_on=not music_on; play_music()
        elif exit_btn.collidepoint(pos): exit()
    elif game_state=="PLAYING" and restart_btn.collidepoint(pos): reset_run()
    elif game_state=="GAME_OVER": game_state="MENU"; reset_run()

pgzrun.go()
