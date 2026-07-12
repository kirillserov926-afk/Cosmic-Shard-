"""
Игра: Cosmic Shard — космический тир
Платформа: Android (Pydroid + PyGame)
Версия: 1.3 — все исправления, чистая игра
"""

import pygame
import random
import math
import sys
import struct
import json

# ======================== ИНИЦИАЛИЗАЦИЯ ========================
pygame.init()

try:
    pygame.mixer.init()
    SOUND_ENABLED = True
except:
    SOUND_ENABLED = False

info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h

if WIDTH == 0 or HEIGHT == 0:
    WIDTH, HEIGHT = 720, 1280

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH = screen.get_width()
HEIGHT = screen.get_height()

pygame.display.set_caption("Cosmic Shard")
clock = pygame.time.Clock()
FPS = 60

# ======================== ЦВЕТА ========================
BG_DARK      = (8, 5, 20)
BG_MID       = (15, 10, 35)
WHITE        = (255, 255, 255)
NEON_PINK    = (255, 20, 147)
NEON_CYAN    = (0, 255, 255)
NEON_GREEN   = (57, 255, 20)
NEON_ORANGE  = (255, 140, 0)
NEON_PURPLE  = (180, 50, 255)
GOLD         = (255, 215, 0)
DARK_BLUE    = (10, 20, 50)
RED          = (255, 0, 0)
ICE_COLOR    = (100, 200, 255)

# ======================== ФАЙЛ НАСТРОЕК ========================
SETTINGS_FILE = "cosmic_shard_settings.json"

DEFAULT_SETTINGS = {
    "bg_theme": "cosmic",
    "music_theme": "ambient",
    "high_score": 0,
    "crystal_skin": "default",
    "unlocked_bgs": ["cosmic"],
    "unlocked_skins": ["default"]
}


def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            for key in DEFAULT_SETTINGS:
                if key not in data:
                    data[key] = DEFAULT_SETTINGS[key]
            return data
    except:
        return DEFAULT_SETTINGS.copy()


def save_settings(s):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f)
    except:
        pass

settings = load_settings()

# ======================== ШРИФТЫ ========================
def get_font(size, bold=False):
    try:
        return pygame.font.Font(None, size)
    except:
        return pygame.font.SysFont("arial", size, bold=bold)

scale_factor = min(WIDTH / 720, HEIGHT / 1280)

font_score    = get_font(int(80 * scale_factor), bold=True)
font_combo    = get_font(int(50 * scale_factor))
font_ui       = get_font(int(36 * scale_factor))
font_title    = get_font(int(100 * scale_factor), bold=True)
font_huge     = get_font(int(110 * scale_factor), bold=True)
font_small    = get_font(int(28 * scale_factor))
font_boss_hp  = get_font(int(24 * scale_factor))

# ======================== РУССКИЕ ТЕКСТЫ ========================
TEXT = {
    "game_title": "COSMIC SHARD",
    "play": "ИГРАТЬ",
    "settings": "НАСТРОЙКИ",
    "skins_bgs": "СКИНЫ И ФОНЫ",
    "best_score": "Рекорд",
    "skin": "Скин",
    "tap_crystals": "Тапай по кристаллам. Не пропускай.",
    "select_bg": "Выберите фон",
    "select_music": "Выберите музыку",
    "select_skin": "Выберите скин кристаллов",
    "bg_cosmic": "Космос",
    "bg_sky": "Небо",
    "bg_sunset": "Закат",
    "bg_forest": "Лес",
    "music_ambient": "Спокойная",
    "music_energy": "Энергичная",
    "music_mystic": "Мистическая",
    "skin_default": "Обычный",
    "skin_gold": "Золотой",
    "skin_ice": "Ледяной",
    "skin_rainbow": "Радужный",
    "combo": "КОМБО",
    "game_over": "ИГРА ОКОНЧЕНА",
    "score": "Счёт",
    "total": "Всего",
    "max_combo": "Макс. комбо",
    "play_again": "ЕЩЁ РАЗ",
    "menu": "МЕНЮ",
    "new_bg": "Новый фон",
    "new_skin": "Новый скин",
    "pts": "очк",
    "next": "ДАЛЕЕ",
    "back": "НАЗАД",
}

# ======================== СИСТЕМА РАЗБЛОКИРОВКИ ========================
UNLOCKABLES = {
    "bg": {
        "sky": {"name": TEXT["bg_sky"], "cost": 3000},
        "sunset": {"name": TEXT["bg_sunset"], "cost": 8000},
        "forest": {"name": TEXT["bg_forest"], "cost": 15000}
    },
    "skin": {
        "gold": {"name": TEXT["skin_gold"], "cost": 2000},
        "ice": {"name": TEXT["skin_ice"], "cost": 5000},
        "rainbow": {"name": TEXT["skin_rainbow"], "cost": 12000}
    }
}

CRYSTAL_SKINS = {
    "default": {"main": NEON_CYAN, "inner_bonus": 60, "glow_alpha": 25, "name": TEXT["skin_default"]},
    "gold": {"main": GOLD, "inner_bonus": 40, "glow_alpha": 40, "name": TEXT["skin_gold"]},
    "ice": {"main": ICE_COLOR, "inner_bonus": 80, "glow_alpha": 35, "name": TEXT["skin_ice"]},
    "rainbow": {"main": None, "inner_bonus": 60, "glow_alpha": 30, "name": TEXT["skin_rainbow"]}
}

bg_names = {
    "cosmic": TEXT["bg_cosmic"],
    "sky": TEXT["bg_sky"],
    "sunset": TEXT["bg_sunset"],
    "forest": TEXT["bg_forest"]
}

music_names = {
    "ambient": TEXT["music_ambient"],
    "energy": TEXT["music_energy"],
    "mystic": TEXT["music_mystic"]
}

# ======================== ЗВУКИ ========================
def make_sound(freq_start, freq_end, duration, wave_type="sine", volume=0.3):
    if not SOUND_ENABLED:
        return None
    sample_rate = 22050
    samples = int(sample_rate * duration)
    buf = []
    for i in range(samples):
        t = i / sample_rate
        progress = i / samples
        envelope = 1.0 - progress
        freq = freq_start + (freq_end - freq_start) * progress
        if wave_type == "sine":
            value = math.sin(2 * math.pi * freq * t)
        elif wave_type == "noise":
            value = random.uniform(-1, 1)
        elif wave_type == "mixed":
            value = math.sin(2 * math.pi * freq * t) * 0.6 + random.uniform(-1, 1) * 0.4
        value *= envelope * volume
        buf.append(int(value * 32767))
    sound_bytes = struct.pack('<' + 'h' * len(buf), *buf)
    return pygame.mixer.Sound(buffer=sound_bytes)


def play_sound(sound):
    if sound and SOUND_ENABLED:
        sound.play()

sound_explosion = make_sound(600, 200, 0.12, "mixed", 0.35)
sound_combo     = make_sound(400, 900, 0.15, "sine", 0.4)
sound_miss      = make_sound(150, 60, 0.35, "sine", 0.35)
sound_click     = make_sound(800, 600, 0.05, "sine", 0.3)
sound_heal      = make_sound(300, 600, 0.2, "sine", 0.4)
sound_boss_hit  = make_sound(100, 50, 0.1, "mixed", 0.5)
sound_unlock    = make_sound(500, 1000, 0.3, "sine", 0.5)

# ======================== МУЗЫКА ========================
def make_music_ambient():
    if not SOUND_ENABLED:
        return None
    sample_rate = 22050
    duration = 10.0
    samples = int(sample_rate * duration)
    notes = [261.63, 293.66, 329.63, 392.00, 440.00]
    buf = []
    prev = 0
    for i in range(samples):
        t = i / sample_rate
        note_index = int((t * 0.5) % len(notes))
        freq = notes[note_index]
        note_progress = (t * 0.5) % 1.0
        local_env = 1.0
        if note_progress < 0.1:
            local_env = note_progress / 0.1
        elif note_progress > 0.8:
            local_env = (1.0 - note_progress) / 0.2
        value = 0
        value += math.sin(2 * math.pi * freq * t) * 0.3
        value += math.sin(2 * math.pi * freq * 2 * t) * 0.1
        value += math.sin(2 * math.pi * freq * 0.5 * t) * 0.15
        value = prev * 0.6 + value * 0.4
        prev = value
        value *= local_env * 0.22
        buf.append(int(value * 32767))
    stereo = []
    for v in buf:
        stereo.append(v)
        stereo.append(v)
    music_bytes = struct.pack('<' + 'h' * len(stereo), *stereo)
    return pygame.mixer.Sound(buffer=music_bytes)


def make_music_energy():
    if not SOUND_ENABLED:
        return None
    sample_rate = 22050
    duration = 8.0
    samples = int(sample_rate * duration)
    notes = [330, 392, 440, 523, 587, 659, 784]
    buf = []
    prev = 0
    for i in range(samples):
        t = i / sample_rate
        note_index = int((t * 0.8) % len(notes))
        freq = notes[note_index]
        note_progress = (t * 0.8) % 1.0
        local_env = 1.0
        if note_progress < 0.05:
            local_env = note_progress / 0.05
        elif note_progress > 0.7:
            local_env = (1.0 - note_progress) / 0.3
        value = 0
        value += math.sin(2 * math.pi * freq * t) * 0.25
        value += math.sin(2 * math.pi * freq * 1.5 * t) * 0.15
        value = prev * 0.5 + value * 0.5
        prev = value
        value *= local_env * 0.25
        buf.append(int(value * 32767))
    stereo = []
    for v in buf:
        stereo.append(v)
        stereo.append(v)
    music_bytes = struct.pack('<' + 'h' * len(stereo), *stereo)
    return pygame.mixer.Sound(buffer=music_bytes)


def make_music_mystic():
    if not SOUND_ENABLED:
        return None
    sample_rate = 22050
    duration = 12.0
    samples = int(sample_rate * duration)
    notes = [196, 220, 246.94, 293.66, 329.63, 349.23]
    buf = []
    prev = 0
    for i in range(samples):
        t = i / sample_rate
        note_index = int((t * 0.3) % len(notes))
        freq = notes[note_index]
        note_progress = (t * 0.3) % 1.0
        local_env = 1.0
        if note_progress < 0.15:
            local_env = note_progress / 0.15
        elif note_progress > 0.85:
            local_env = (1.0 - note_progress) / 0.15
        value = 0
        value += math.sin(2 * math.pi * freq * t) * 0.25
        value += math.sin(2 * math.pi * freq * 0.25 * t) * 0.2
        value = prev * 0.7 + value * 0.3
        prev = value
        value *= local_env * 0.2
        buf.append(int(value * 32767))
    stereo = []
    for v in buf:
        stereo.append(v)
        stereo.append(v)
    music_bytes = struct.pack('<' + 'h' * len(stereo), *stereo)
    return pygame.mixer.Sound(buffer=music_bytes)

music_tracks = {
    "ambient": make_music_ambient(),
    "energy": make_music_energy(),
    "mystic": make_music_mystic()
}

current_music_channel = None


def play_music(track_name):
    global current_music_channel
    if not SOUND_ENABLED:
        return
    stop_music()
    if track_name in music_tracks and music_tracks[track_name]:
        current_music_channel = music_tracks[track_name].play(loops=-1)


def stop_music():
    global current_music_channel
    if not SOUND_ENABLED:
        return
    for track in music_tracks.values():
        if track:
            track.stop()
    current_music_channel = None

# ======================== ФОНЫ ========================
def draw_bg_cosmic(surface):
    surface.fill(BG_DARK)
    for i in range(0, HEIGHT, 4):
        alpha = i / HEIGHT
        r = int(BG_DARK[0] + (BG_MID[0] - BG_DARK[0]) * alpha)
        g = int(BG_DARK[1] + (BG_MID[1] - BG_DARK[1]) * alpha)
        b = int(BG_DARK[2] + (BG_MID[2] - BG_DARK[2]) * alpha)
        pygame.draw.line(surface, (r, g, b), (0, i), (WIDTH, i))


def draw_bg_sky(surface):
    top_color = (20, 40, 100)
    bottom_color = (100, 160, 220)
    for i in range(0, HEIGHT, 2):
        alpha = i / HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * alpha)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * alpha)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * alpha)
        pygame.draw.line(surface, (r, g, b), (0, i), (WIDTH, i))


def draw_bg_sunset(surface):
    top_color = (60, 10, 40)
    mid_color = (200, 80, 40)
    bottom_color = (250, 180, 60)
    mid_height = HEIGHT // 2
    for i in range(0, HEIGHT, 2):
        if i < mid_height:
            alpha = i / mid_height
            r = int(top_color[0] + (mid_color[0] - top_color[0]) * alpha)
            g = int(top_color[1] + (mid_color[1] - top_color[1]) * alpha)
            b = int(top_color[2] + (mid_color[2] - top_color[2]) * alpha)
        else:
            alpha = (i - mid_height) / mid_height
            r = int(mid_color[0] + (bottom_color[0] - mid_color[0]) * alpha)
            g = int(mid_color[1] + (bottom_color[1] - mid_color[1]) * alpha)
            b = int(mid_color[2] + (bottom_color[2] - mid_color[2]) * alpha)
        pygame.draw.line(surface, (r, g, b), (0, i), (WIDTH, i))


def draw_bg_forest(surface):
    top_color = (5, 30, 10)
    bottom_color = (20, 80, 30)
    for i in range(0, HEIGHT, 2):
        alpha = i / HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * alpha)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * alpha)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * alpha)
        pygame.draw.line(surface, (r, g, b), (0, i), (WIDTH, i))

bg_themes = {
    "cosmic": draw_bg_cosmic,
    "sky": draw_bg_sky,
    "sunset": draw_bg_sunset,
    "forest": draw_bg_forest
}

# ======================== ЧАСТИЦЫ ========================
class Particle:
    def __init__(self, x, y, color, speed=None, life=None, size=None):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = speed or random.uniform(2, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = life or random.uniform(0.3, 0.8)
        self.max_life = self.life
        self.size = size or random.uniform(2, 6)

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.5
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, min(255, int(255 * (self.life / self.max_life))))
        size = max(1, self.size * (self.life / self.max_life))
        surf = pygame.Surface((int(size * 4), int(size * 4)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (int(size * 2), int(size * 2)), int(size))
        surface.blit(surf, (self.x - size * 2, self.y - size * 2))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=15, speed_range=(2, 10), life_range=(0.3, 0.8), size_range=(2, 6)):
        for _ in range(count):
            speed = random.uniform(*speed_range)
            life = random.uniform(*life_range)
            size = random.uniform(*size_range)
            self.particles.append(Particle(x, y, color, speed, life, size))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def clear(self):
        self.particles.clear()


# ======================== ЗВЁЗДЫ ========================
class StarField:
    def __init__(self, count=80):
        self.stars = []
        for _ in range(count):
            self.stars.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.uniform(0.5, 2.0),
                'speed': random.uniform(0.1, 0.6),
                'brightness': random.uniform(0.3, 1.0),
                'twinkle_speed': random.uniform(1.0, 4.0),
                'twinkle_offset': random.uniform(0, math.pi * 2)
            })

    def update(self, time_seconds):
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, WIDTH)
            star['brightness'] = 0.4 + 0.6 * abs(math.sin(time_seconds * star['twinkle_speed'] + star['twinkle_offset']))

    def draw(self, surface):
        for star in self.stars:
            brightness = int(255 * star['brightness'])
            color = (brightness, brightness, min(255, brightness + 40))
            pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), max(1, int(star['size'])))


# ======================== КРИСТАЛЛЫ ========================
class Crystal:
    def __init__(self, speed_multiplier=1.0):
        base_radius = random.randint(25, 45)
        self.radius = int(base_radius * scale_factor)
        self.x = random.randint(self.radius + 10, WIDTH - self.radius - 10)
        self.y = -self.radius - random.randint(0, 150)
        base_speed = random.uniform(2.0, 4.5)
        self.speed = base_speed * speed_multiplier * scale_factor
        self.wobble_amp = random.uniform(0, 1.0)
        self.wobble_speed = random.uniform(0.3, 1.5)
        self.wobble_offset = random.uniform(0, math.pi * 2)
        self.start_x = self.x
        self.points = 10 if base_radius > 35 else 5
        self.scale = 0.0
        self.target_scale = 1.0
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)

        skin = CRYSTAL_SKINS[settings["crystal_skin"]]
        if skin["main"] is None:
            self.color = random.choice([NEON_CYAN, NEON_PINK, NEON_GREEN, NEON_ORANGE, NEON_PURPLE, GOLD])
        else:
            self.color = skin["main"]
        self.inner_bonus = skin["inner_bonus"]
        self.glow_alpha = skin["glow_alpha"]

    def update(self, time_seconds):
        self.y += self.speed
        self.x = self.start_x + math.sin(time_seconds * self.wobble_speed + self.wobble_offset) * self.wobble_amp * 25
        self.rotation += self.rotation_speed
        if self.scale < self.target_scale:
            self.scale = min(self.target_scale, self.scale + 0.12)
        return self.y > HEIGHT + self.radius + 50

    def draw(self, surface):
        if self.scale < 0.05:
            return
        cx, cy = int(self.x), int(self.y)
        r = int(self.radius * self.scale)
        angle = math.radians(self.rotation)
        points = []
        for i in range(4):
            base_angle = angle + (i * math.pi / 2)
            px = cx + math.cos(base_angle) * r
            py = cy + math.sin(base_angle) * r
            points.append((int(px), int(py)))
        glow_size = int(r * 1.3)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, self.glow_alpha), (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (cx - glow_size, cy - glow_size))
        pygame.draw.polygon(surface, self.color, points)
        inner_color = tuple(min(255, c + self.inner_bonus) for c in self.color)
        inner_points = []
        for i in range(4):
            base_angle = angle + (i * math.pi / 2)
            px = cx + math.cos(base_angle) * (r * 0.55)
            py = cy + math.sin(base_angle) * (r * 0.55)
            inner_points.append((int(px), int(py)))
        pygame.draw.polygon(surface, inner_color, inner_points)
        blink_x = int(cx + math.cos(angle + 0.5) * (r * 0.25))
        blink_y = int(cy + math.sin(angle + 0.5) * (r * 0.25))
        pygame.draw.circle(surface, WHITE, (blink_x, blink_y), max(2, int(r * 0.12)))

    def contains_point(self, px, py):
        dist = math.hypot(px - self.x, py - self.y)
        return dist < self.radius * self.scale * 1.3


class BonusCrystal(Crystal):
    """Кристалл +1 жизнь"""
    def __init__(self, speed_multiplier=1.0):
        super().__init__(speed_multiplier)
        self.color = NEON_GREEN
        self.points = 0
        self.radius = int(30 * scale_factor)
        self.speed = 2.0 * scale_factor

    def draw(self, surface):
        if self.scale < 0.05:
            return
        cx, cy = int(self.x), int(self.y)
        r = int(self.radius * self.scale)
        glow_size = int(r * 1.5)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (50, 255, 50, 40), (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (cx - glow_size, cy - glow_size))
        pygame.draw.circle(surface, NEON_GREEN, (cx, cy), r)
        pygame.draw.circle(surface, (100, 255, 100), (cx, cy), int(r * 0.6))
        heart_size = int(r * 0.4)
        hx, hy = cx, cy
        pygame.draw.circle(surface, WHITE, (hx - heart_size//2, hy - heart_size//3), heart_size//2)
        pygame.draw.circle(surface, WHITE, (hx + heart_size//2, hy - heart_size//3), heart_size//2)
        pts = [(hx - heart_size, hy), (hx, hy + heart_size), (hx + heart_size, hy)]
        pygame.draw.polygon(surface, WHITE, pts)


class BossCrystal(Crystal):
    """Босс-кристалл"""
    def __init__(self, speed_multiplier=1.0):
        super().__init__(speed_multiplier)
        self.color = RED
        self.radius = int(65 * scale_factor)
        self.speed = 1.2 * scale_factor
        self.max_hp = 15
        self.hp = self.max_hp
        self.points = 200
        self.wobble_amp = 0.3

    def draw(self, surface):
        if self.scale < 0.05:
            return
        cx, cy = int(self.x), int(self.y)
        r = int(self.radius * self.scale)
        angle = math.radians(self.rotation)
        pulse = 0.7 + 0.3 * math.sin(self.rotation * 0.1)
        glow_size = int(r * 1.6)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 0, 0, int(60 * pulse)), (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (cx - glow_size, cy - glow_size))
        points = []
        for i in range(6):
            a = angle + (i * math.pi / 3)
            px = cx + math.cos(a) * r
            py = cy + math.sin(a) * r
            points.append((int(px), int(py)))
        pygame.draw.polygon(surface, RED, points)
        pygame.draw.polygon(surface, (200, 0, 0), points, 4)
        bar_w = int(r * 1.5)
        bar_h = int(12 * scale_factor)
        bar_x = cx - bar_w // 2
        bar_y = cy - r - int(20 * scale_factor)
        pygame.draw.rect(surface, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        hp_width = int(bar_w * (self.hp / self.max_hp))
        pygame.draw.rect(surface, RED, (bar_x, bar_y, hp_width, bar_h))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
        hp_text = font_boss_hp.render(str(self.hp), True, WHITE)
        hp_rect = hp_text.get_rect(center=(cx, bar_y + bar_h // 2))
        surface.blit(hp_text, hp_rect)

    def hit(self):
        self.hp -= 1
        return self.hp <= 0


# ======================== КНОПКА ========================
class Button:
    def __init__(self, x, y, w, h, text, color, text_color=WHITE, font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = font or font_ui
        self.hovered = False
        self.pressed = False

    def update(self, mx, my, clicked):
        self.hovered = self.rect.collidepoint(mx, my)
        if self.hovered and clicked:
            self.pressed = True
            return True
        self.pressed = False
        return False

    def draw(self, surface):
        color = self.color
        if self.hovered:
            color = tuple(min(255, c + 40) for c in color)
        if self.pressed:
            color = tuple(max(0, c - 30) for c in color)
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=15)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


# ======================== УВЕДОМЛЕНИЕ ========================
class UnlockNotification:
    def __init__(self, text):
        self.text = text
        self.life = 2.5
        self.max_life = 2.5
        self.y_offset = 0

    def update(self, dt):
        self.life -= dt
        self.y_offset -= dt * 30
        return self.life > 0

    def draw(self, surface):
        alpha = min(255, int(255 * (self.life / self.max_life)))
        if alpha < 10:
            return
        text_surf = font_ui.render(self.text, True, GOLD)
        text_surf.set_alpha(alpha)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, int(100 * scale_factor) + self.y_offset))
        surface.blit(text_surf, text_rect)


# ======================== ИГРА ========================
class Game:
    def __init__(self):
        self.unlock_notifications = []
        self.particles = ParticleSystem()
        self.starfield = StarField(80)
        self.reset()

    def reset(self):
        self.crystals = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.lives = 3
        self.max_lives = 5
        self.game_over = False
        self.particles.clear()
        self.time = 0.0
        self.speed_multiplier = 1.0
        self.spawn_timer = 0.0
        self.spawn_interval = 1.2
        self.screen_shake = 0.0
        self.boss_spawn_timer = 0.0
        self.boss_interval = random.uniform(25, 40)
        self.total_score_ever = settings["high_score"]
        self.new_unlocks = []
        self._go_buttons = []

    def check_unlocks(self):
        total = self.total_score_ever + self.score
        unlocked_anything = False

        for key, data in UNLOCKABLES["bg"].items():
            if key not in settings["unlocked_bgs"] and total >= data["cost"]:
                settings["unlocked_bgs"].append(key)
                self.unlock_notifications.append(UnlockNotification(f"{TEXT['new_bg']}: {data['name']}!"))
                play_sound(sound_unlock)
                unlocked_anything = True

        for key, data in UNLOCKABLES["skin"].items():
            if key not in settings["unlocked_skins"] and total >= data["cost"]:
                settings["unlocked_skins"].append(key)
                self.unlock_notifications.append(UnlockNotification(f"{TEXT['new_skin']}: {data['name']}!"))
                play_sound(sound_unlock)
                unlocked_anything = True

        if unlocked_anything:
            save_settings(settings)

    def get_speed_multiplier(self):
        level = 1 + self.score // 200
        return 1.0 + (level - 1) * 0.2

    def get_spawn_interval(self):
        level = 1 + self.score // 200
        base = 1.2
        reduction = (level - 1) * 0.05
        return max(0.5, base - reduction)

    def spawn_crystal(self):
        max_crystals = 4
        if random.random() < 0.05:
            self.crystals.append(BonusCrystal(speed_multiplier=self.speed_multiplier))
            return

        if len(self.crystals) < max_crystals:
            self.crystals.append(Crystal(speed_multiplier=self.speed_multiplier))

    def spawn_boss(self):
        self.crystals.append(BossCrystal(speed_multiplier=self.speed_multiplier))

    def tap(self, x, y):
        if self.game_over:
            for btn in self._go_buttons:
                if btn.update(x, y, True):
                    play_sound(sound_click)
                    return btn.text
            return None

        hit = False

        for crystal in sorted(self.crystals, key=lambda c: c.y, reverse=True):
            if crystal.contains_point(x, y):

                if isinstance(crystal, BossCrystal):
                    dead = crystal.hit()
                    play_sound(sound_boss_hit)
                    self.particles.emit(crystal.x, crystal.y, RED, count=8, speed_range=(1, 5))
                    self.screen_shake = max(self.screen_shake, 2.0)

                    if dead:
                        self.crystals.remove(crystal)
                        self.score += crystal.points
                        self.particles.emit(crystal.x, crystal.y, RED, count=40, speed_range=(3, 15), life_range=(0.5, 1.5))
                        self.particles.emit(crystal.x, crystal.y, GOLD, count=20, speed_range=(2, 10))
                        self.screen_shake = max(self.screen_shake, 12.0)
                        self.combo += 3
                        play_sound(sound_combo)

                    hit = True
                    break

                elif isinstance(crystal, BonusCrystal):
                    self.crystals.remove(crystal)
                    if self.lives < self.max_lives:
                        self.lives += 1
                    self.particles.emit(crystal.x, crystal.y, NEON_GREEN, count=25, speed_range=(2, 8))
                    play_sound(sound_heal)
                    hit = True
                    break

                else:
                    self.crystals.remove(crystal)
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)

                    if self.combo >= 30:
                        combo_mult = 5
                    elif self.combo >= 20:
                        combo_mult = 4
                    elif self.combo >= 12:
                        combo_mult = 3
                    elif self.combo >= 5:
                        combo_mult = 2
                    else:
                        combo_mult = 1

                    points = crystal.points * combo_mult
                    self.score += points

                    self.particles.emit(crystal.x, crystal.y, crystal.color,
                                       count=12 + self.combo,
                                       speed_range=(2, 8),
                                       life_range=(0.2, 0.7))
                    self.screen_shake = max(self.screen_shake, 2.0 + self.combo * 0.3)

                    if self.combo >= 5:
                        play_sound(sound_combo)
                    else:
                        play_sound(sound_explosion)

                    hit = True
                    break

        if not hit:
            self.combo = 0

        self.check_unlocks()
        return None

    def update(self, dt):
        self.unlock_notifications = [n for n in self.unlock_notifications if n.update(dt)]

        if self.game_over:
            self.particles.update(dt)
            self.starfield.update(self.time)
            self.crystals.clear()
            return

        self.time += dt
        self.speed_multiplier = self.get_speed_multiplier()
        self.spawn_interval = self.get_spawn_interval()
        self.starfield.update(self.time)

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_crystal()

        self.boss_spawn_timer += dt
        if self.boss_spawn_timer >= self.boss_interval:
            self.boss_spawn_timer = 0
            self.boss_interval = random.uniform(25, 40)
            self.spawn_boss()

        for crystal in self.crystals[:]:
            off_screen = crystal.update(self.time)
            if off_screen:
                self.crystals.remove(crystal)

                if isinstance(crystal, BossCrystal):
                    self.combo = 0
                elif isinstance(crystal, BonusCrystal):
                    pass
                else:
                    self.combo = 0
                    self.lives -= 1
                    self.screen_shake = max(self.screen_shake, 6.0)
                    play_sound(sound_miss)

                    if self.lives <= 0:
                        self.game_over = True
                        self.crystals.clear()
                        self.particles.clear()
                        total = self.total_score_ever + self.score
                        if total > settings["high_score"]:
                            settings["high_score"] = total
                            save_settings(settings)

        self.particles.update(dt)
        self.screen_shake = max(0, self.screen_shake - dt * 12)

    def draw(self, surface):
        surface.fill((0, 0, 0))
        bg_themes[settings["bg_theme"]](surface)

        if settings["bg_theme"] == "cosmic":
            self.starfield.draw(surface)

        for crystal in self.crystals:
            crystal.draw(surface)

        self.particles.draw(surface)
        self.draw_ui(surface)

        for notif in self.unlock_notifications:
            notif.draw(surface)

        if self.game_over:
            self.draw_game_over(surface)

    def draw_ui(self, surface):
        padding_x = int(30 * scale_factor)
        padding_y = int(50 * scale_factor)

        score_text = font_score.render(str(self.score), True, WHITE)
        surface.blit(score_text, (padding_x, padding_y))

        high_text = font_small.render(f"{TEXT['best_score']}: {settings['high_score']}", True, GOLD)
        surface.blit(high_text, (padding_x, padding_y + int(70 * scale_factor)))

        if self.combo >= 3:
            if self.combo >= 30:
                combo_color = GOLD
                combo_label = f"x5 {TEXT['combo']}!"
            elif self.combo >= 20:
                combo_color = NEON_PINK
                combo_label = f"x4 {TEXT['combo']}!"
            elif self.combo >= 12:
                combo_color = NEON_ORANGE
                combo_label = f"x3 {TEXT['combo']}!"
            elif self.combo >= 5:
                combo_color = NEON_CYAN
                combo_label = f"x2 {TEXT['combo']}!"
            else:
                combo_color = WHITE
                combo_label = f"x{self.combo} {TEXT['combo']}!"

            combo_text = font_combo.render(combo_label, True, combo_color)
            surface.blit(combo_text, (padding_x, int(150 * scale_factor)))

        heart_spacing = int(50 * scale_factor)
        heart_size = max(3, int(10 * scale_factor))
        for i in range(self.lives):
            heart_x = WIDTH - padding_x - i * heart_spacing
            heart_y = padding_y
            r = heart_size
            pygame.draw.circle(surface, NEON_PINK, (heart_x - int(8 * scale_factor), heart_y + int(8 * scale_factor)), r)
            pygame.draw.circle(surface, NEON_PINK, (heart_x + int(8 * scale_factor), heart_y + int(8 * scale_factor)), r)
            pts = [
                (heart_x - int(18 * scale_factor), heart_y + int(12 * scale_factor)),
                (heart_x, heart_y + int(26 * scale_factor)),
                (heart_x + int(18 * scale_factor), heart_y + int(12 * scale_factor))
            ]
            pygame.draw.polygon(surface, NEON_PINK, pts)

    def draw_game_over(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title = font_title.render(TEXT["game_over"], True, NEON_PINK)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - int(160 * scale_factor)))
        surface.blit(title, title_rect)

        score_text = font_score.render(f"{TEXT['score']}: {self.score}", True, GOLD)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - int(60 * scale_factor)))
        surface.blit(score_text, score_rect)

        total_score = self.total_score_ever + self.score
        high_text = font_ui.render(f"{TEXT['total']}: {total_score}  |  {TEXT['best_score']}: {settings['high_score']}", True, NEON_CYAN)
        high_rect = high_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        surface.blit(high_text, high_rect)

        combo_text = font_ui.render(f"{TEXT['max_combo']}: x{self.max_combo}", True, NEON_GREEN)
        combo_rect = combo_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + int(50 * scale_factor)))
        surface.blit(combo_text, combo_rect)

        btn_w = int(260 * scale_factor)
        btn_h = int(70 * scale_factor)
        btn_spacing = int(20 * scale_factor)

        again_x = WIDTH // 2 - btn_w - btn_spacing // 2
        again_y = HEIGHT // 2 + int(130 * scale_factor)
        again_btn = Button(again_x, again_y, btn_w, btn_h, TEXT["play_again"], NEON_GREEN, WHITE, font_ui)
        again_btn.draw(surface)

        menu_x = WIDTH // 2 + btn_spacing // 2
        menu_y = HEIGHT // 2 + int(130 * scale_factor)
        menu_btn = Button(menu_x, menu_y, btn_w, btn_h, TEXT["menu"], NEON_PURPLE, WHITE, font_ui)
        menu_btn.draw(surface)

        self._go_buttons = [again_btn, menu_btn]


# ======================== МЕНЮ ========================
class Menu:
    def __init__(self):
        self.buttons = []
        self.state = "main"
        self.create_main_buttons()

    def create_main_buttons(self):
        self.buttons = []
        btn_w = int(340 * scale_factor)
        btn_h = int(80 * scale_factor)
        cx = WIDTH // 2 - btn_w // 2

        self.buttons.append(Button(cx, HEIGHT // 2 - int(70 * scale_factor), btn_w, btn_h, TEXT["play"], NEON_GREEN, WHITE, font_score))
        self.buttons.append(Button(cx, HEIGHT // 2 + int(30 * scale_factor), btn_w, btn_h, TEXT["settings"], NEON_CYAN, WHITE, font_ui))
        self.buttons.append(Button(cx, HEIGHT // 2 + int(130 * scale_factor), btn_w, btn_h, TEXT["skins_bgs"], NEON_ORANGE, WHITE, font_ui))

    def create_bg_settings(self):
        self.buttons = []
        btn_w = int(360 * scale_factor)
        btn_h = int(60 * scale_factor)
        cx = WIDTH // 2 - btn_w // 2
        start_y = int(220 * scale_factor)
        spacing = int(80 * scale_factor)

        for i, (key, name) in enumerate(bg_names.items()):
            if key in settings["unlocked_bgs"]:
                color = NEON_CYAN if key == settings["bg_theme"] else DARK_BLUE
                label = f"{name}"
            else:
                cost = UNLOCKABLES["bg"].get(key, {}).get("cost", "???")
                color = (30, 30, 30)
                label = f"{name} ({cost} {TEXT['pts']})"
            self.buttons.append(Button(cx, start_y + i * spacing, btn_w, btn_h, label, color, WHITE, font_ui))
            if key in settings["unlocked_bgs"]:
                self.buttons[-1].bg_key = key

        back_y = start_y + len(bg_names) * spacing + int(40 * scale_factor)
        self.buttons.append(Button(cx, back_y, btn_w, btn_h, TEXT["next"], NEON_ORANGE, WHITE, font_ui))

    def create_music_settings(self):
        self.buttons = []
        btn_w = int(360 * scale_factor)
        btn_h = int(60 * scale_factor)
        cx = WIDTH // 2 - btn_w // 2
        start_y = int(220 * scale_factor)
        spacing = int(80 * scale_factor)

        for i, (key, name) in enumerate(music_names.items()):
            color = NEON_PURPLE if key == settings["music_theme"] else DARK_BLUE
            self.buttons.append(Button(cx, start_y + i * spacing, btn_w, btn_h, name, color, WHITE, font_ui))
            self.buttons[-1].music_key = key

        back_y = start_y + len(music_names) * spacing + int(40 * scale_factor)
        self.buttons.append(Button(cx, back_y, btn_w, btn_h, TEXT["back"], NEON_PINK, WHITE, font_ui))

    def create_skin_settings(self):
        self.buttons = []
        btn_w = int(360 * scale_factor)
        btn_h = int(60 * scale_factor)
        cx = WIDTH // 2 - btn_w // 2
        start_y = int(220 * scale_factor)
        spacing = int(80 * scale_factor)

        for i, (key, data) in enumerate(CRYSTAL_SKINS.items()):
            if key == "default" or key in settings["unlocked_skins"]:
                color = NEON_GREEN if key == settings["crystal_skin"] else DARK_BLUE
                label = data["name"]
            else:
                cost = UNLOCKABLES["skin"].get(key, {}).get("cost", "???")
                color = (30, 30, 30)
                label = f"{data['name']} ({cost} {TEXT['pts']})"
            self.buttons.append(Button(cx, start_y + i * spacing, btn_w, btn_h, label, color, WHITE, font_ui))
            if key == "default" or key in settings["unlocked_skins"]:
                self.buttons[-1].skin_key = key

        back_y = start_y + len(CRYSTAL_SKINS) * spacing + int(40 * scale_factor)
        self.buttons.append(Button(cx, back_y, btn_w, btn_h, TEXT["back"], NEON_PINK, WHITE, font_ui))

    def handle_click(self, x, y):
        mx, my = x, y
        for btn in self.buttons:
            if btn.update(mx, my, True):
                play_sound(sound_click)
                return btn
        return None

    def update_hover(self, x, y):
        for btn in self.buttons:
            btn.update(x, y, False)

    def draw(self, surface):
        surface.fill((0, 0, 0))
        bg_themes[settings["bg_theme"]](surface)

        title = font_huge.render(TEXT["game_title"], True, GOLD)
        title_rect = title.get_rect(center=(WIDTH // 2, int(100 * scale_factor)))
        surface.blit(title, title_rect)

        if self.state == "main":
            sub = font_small.render(TEXT["tap_crystals"], True, NEON_CYAN)
            sub_rect = sub.get_rect(center=(WIDTH // 2, int(180 * scale_factor)))
            surface.blit(sub, sub_rect)

            high_text = font_ui.render(f"{TEXT['best_score']}: {settings['high_score']}", True, GOLD)
            high_rect = high_text.get_rect(center=(WIDTH // 2, int(230 * scale_factor)))
            surface.blit(high_text, high_rect)

            skin_name = CRYSTAL_SKINS[settings["crystal_skin"]]["name"]
            skin_text = font_small.render(f"{TEXT['skin']}: {skin_name}", True, NEON_PURPLE)
            skin_rect = skin_text.get_rect(center=(WIDTH // 2, int(270 * scale_factor)))
            surface.blit(skin_text, skin_rect)

        elif self.state == "settings_bg":
            sub = font_small.render(TEXT["select_bg"], True, NEON_CYAN)
            sub_rect = sub.get_rect(center=(WIDTH // 2, int(170 * scale_factor)))
            surface.blit(sub, sub_rect)

        elif self.state == "settings_music":
            sub = font_small.render(TEXT["select_music"], True, NEON_PURPLE)
            sub_rect = sub.get_rect(center=(WIDTH // 2, int(170 * scale_factor)))
            surface.blit(sub, sub_rect)

        elif self.state == "settings_skin":
            sub = font_small.render(TEXT["select_skin"], True, NEON_GREEN)
            sub_rect = sub.get_rect(center=(WIDTH // 2, int(170 * scale_factor)))
            surface.blit(sub, sub_rect)

        for btn in self.buttons:
            btn.draw(surface)


# ======================== ГЛАВНЫЙ ЦИКЛ ========================
def main():
    game = None
    menu = Menu()
    current_screen = "menu"
    running = True

    play_music(settings["music_theme"])

    while running:
        dt = clock.tick(FPS) / 1000.0

        mx, my = 0, 0
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    clicked = True

        if current_screen == "menu":
            menu.update_hover(mx, my)

            if clicked:
                btn = menu.handle_click(mx, my)

                if btn:
                    if menu.state == "main":
                        if TEXT["play"] in btn.text:
                            current_screen = "game"
                            game = Game()
                            play_music(settings["music_theme"])
                        elif TEXT["settings"] in btn.text:
                            menu.state = "settings_bg"
                            menu.create_bg_settings()
                        elif TEXT["skins_bgs"] in btn.text:
                            menu.state = "settings_skin"
                            menu.create_skin_settings()

                    elif menu.state == "settings_bg":
                        if TEXT["next"] in btn.text:
                            menu.state = "settings_music"
                            menu.create_music_settings()
                        elif hasattr(btn, 'bg_key'):
                            settings["bg_theme"] = btn.bg_key
                            save_settings(settings)
                            menu.create_bg_settings()

                    elif menu.state == "settings_music":
                        if TEXT["back"] in btn.text:
                            menu.state = "main"
                            menu.create_main_buttons()
                        elif hasattr(btn, 'music_key'):
                            settings["music_theme"] = btn.music_key
                            save_settings(settings)
                            play_music(settings["music_theme"])
                            menu.create_music_settings()

                    elif menu.state == "settings_skin":
                        if TEXT["back"] in btn.text:
                            menu.state = "main"
                            menu.create_main_buttons()
                        elif hasattr(btn, 'skin_key'):
                            settings["crystal_skin"] = btn.skin_key
                            save_settings(settings)
                            menu.create_skin_settings()

            menu.draw(screen)

        elif current_screen == "game":
            if clicked:
                result = game.tap(mx, my)

                if result == TEXT["play_again"]:
                    game = Game()
                    play_music(settings["music_theme"])
                elif result == TEXT["menu"]:
                    current_screen = "menu"
                    menu.state = "main"
                    menu.create_main_buttons()
                    play_music(settings["music_theme"])

            game.update(dt)
            game.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
