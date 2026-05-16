import pygame
import math
import array
import random
from constants import *


class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            self.enabled = True
        except Exception as e:
            print(f"Failed to init pygame.mixer: {e}")
            self.enabled = False

        self.sounds = {}
        self.bg_channel = None
        self.music_volume = 1.0
        self.sfx_volume   = 0.5
        
        if self.enabled:
            pygame.mixer.set_num_channels(16)
            self.bg_channel = pygame.mixer.Channel(15)
            self.bg_channel.set_volume(self.music_volume)
            self._generate_sounds()

    def _generate_sound(self, name, freq, duration, vol=0.1, wave_type="square"):
        if not self.enabled:
            return
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        max_amplitude = int(32767 * vol)

        for i in range(n_samples):
            t = float(i) / sample_rate
            if wave_type == "square":
                val = max_amplitude if math.sin(2 * math.pi * freq * t) > 0 else -max_amplitude
            elif wave_type == "sine":
                val = int(max_amplitude * math.sin(2 * math.pi * freq * t))
            elif wave_type == "saw":
                val = int(max_amplitude * (2 * (t * freq - math.floor(t * freq + 0.5))))
            elif wave_type == "noise":
                val = int(max_amplitude * (2 * random.random() - 1))
            else:
                val = 0
            
            # Envelope (fade out)
            env = 1.0 - (i / n_samples)
            val = int(val * env)
            
            buf.append(val)
            buf.append(val)

        self.sounds[name] = pygame.mixer.Sound(buffer=buf)

    def _generate_complex_sound(self):
        if not self.enabled:
            return
        sr = 44100
        
        # AK Shot - Loud, punchy, metallic crack
        dur = 0.3
        buf = array.array('h')
        for i in range(int(sr * dur)):
            t = i / sr
            # Sharp explosive envelope
            env = math.exp(-25 * t)
            # White noise crack
            noise = (2 * random.random() - 1)
            # Heavy bass punch (150Hz sweeping down to 40Hz)
            bass = math.sin(2 * math.pi * (150 - 600*t) * t) if t < 0.15 else 0
            # Mix with high volume (0.8) for "to đùng" effect
            val = int(32767 * 0.8 * env * (0.6*noise + 0.4*bass))
            # Clamp to prevent distortion overflow
            val = max(-32767, min(32767, val))
            buf.append(val); buf.append(val)
        self.sounds["ak_shot"] = pygame.mixer.Sound(buffer=buf)
        
        # Sniper Shot
        dur = 0.3
        buf = array.array('h')
        for i in range(int(sr * dur)):
            t = i / sr
            env = math.exp(-15 * t)
            noise = (2 * random.random() - 1)
            bass = math.sin(2 * math.pi * (200 - 1500*t) * t) if t < 0.1 else 0
            val = int(32767 * 0.2 * env * (0.6*noise + 0.4*bass))
            buf.append(val); buf.append(val)
        self.sounds["sniper_shot"] = pygame.mixer.Sound(buffer=buf)
        
        # Enemy Shot
        dur = 0.1
        buf = array.array('h')
        for i in range(int(sr * dur)):
            t = i / sr
            env = math.exp(-40 * t)
            noise = (2 * random.random() - 1)
            val = int(32767 * 0.08 * env * noise)
            buf.append(val); buf.append(val)
        self.sounds["enemy_shot"] = pygame.mixer.Sound(buffer=buf)

        # Explosion
        dur = 0.8
        buf = array.array('h')
        for i in range(int(sr * dur)):
            t = i / sr
            env = math.exp(-5 * t)
            noise = (2 * random.random() - 1)
            # Rumble bass
            bass = math.sin(2 * math.pi * (50 + 10*math.sin(50*t)) * t)
            val = int(32767 * 0.25 * env * (0.6*noise + 0.4*bass))
            buf.append(val); buf.append(val)
        self.sounds["explosion"] = pygame.mixer.Sound(buffer=buf)
        
        # Step
        dur = 0.05
        buf = array.array('h')
        for i in range(int(sr * dur)):
            t = i / sr
            env = math.exp(-50 * t)
            val = int(32767 * 0.02 * env * (2 * random.random() - 1))
            buf.append(val); buf.append(val)
        self.sounds["step"] = pygame.mixer.Sound(buffer=buf)

        # Hurt / Death
        dur = 0.4
        buf = array.array('h')
        for i in range(int(sr * dur)):
            t = i / sr
            env = math.exp(-10 * t)
            freq = 300 - 400 * t
            val = int(32767 * 0.1 * env * math.sin(2 * math.pi * freq * t))
            buf.append(val); buf.append(val)
        self.sounds["death"] = pygame.mixer.Sound(buffer=buf)
        
        # Pickup
        dur = 0.2
        buf = array.array('h')
        for i in range(int(sr * dur)):
            t = i / sr
            env = math.exp(-15 * t)
            freq = 800 + 1000 * t
            val = int(32767 * 0.05 * env * math.sin(2 * math.pi * freq * t))
            buf.append(val); buf.append(val)
        self.sounds["pickup"] = pygame.mixer.Sound(buffer=buf)
        
        # Grenade Throw (Chiuuuuuuuuu)
        dur = 0.6
        buf = array.array('h')
        for i in range(int(sr * dur)):
            t = i / sr
            env = 1.0 - (t / dur)
            freq = 1500 - 1800 * t
            val = int(32767 * 0.15 * env * math.sin(2 * math.pi * freq * t))
            buf.append(val); buf.append(val)
        self.sounds["grenade_throw"] = pygame.mixer.Sound(buffer=buf)
        
        # Music - Intense Jungle Beat
        dur = 2.0
        buf = array.array('h')
        for i in range(int(sr * dur)):
            t = i / sr
            
            # Kick on 0, 0.5, 1.0, 1.5
            k_t = t % 0.5
            kick = 0.15 * math.exp(-20 * k_t) * math.sin(2 * math.pi * 60 * k_t)
            
            # Hat
            h_t = t % 0.25
            hat = 0.05 * math.exp(-40 * h_t) * (2*random.random()-1) if h_t < 0.05 else 0
            
            # Bass pulse
            b_t = t % 0.25
            bass = 0.08 * math.sin(2 * math.pi * 40 * t) * (1 - b_t/0.25)
            
            val = int(32767 * max(-1.0, min(1.0, kick + hat + bass)))
            buf.append(val); buf.append(val)
        self.sounds["bgm_jungle"] = pygame.mixer.Sound(buffer=buf)

    def _generate_sounds(self):
        self._generate_complex_sound()

    def play(self, name):
        if not self.enabled:
            return
        if name in self.sounds:
            self.sounds[name].set_volume(self.sfx_volume)
            self.sounds[name].play()

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except: pass
        if self.bg_channel:
            self.bg_channel.set_volume(self.music_volume)

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))

    def play_bg_music(self, track="bgm_jungle"):
        if not self.enabled:
            return
            
        import os
        # Lấy đường dẫn thư mục chứa file sound_manager.py này
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Kiểm tra file nhạc nền (thử cả hai tên phổ biến)
        custom_music = os.path.join(base_dir, "ANH", "Nhac_nen.mp3")
        if not os.path.exists(custom_music):
            custom_music = os.path.join(base_dir, "ANH", "NHAC_NEN_.mp3")
        
        if os.path.exists(custom_music):
            try:
                pygame.mixer.music.load(custom_music)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                return
            except Exception as e:
                print("Failed to load custom music:", e)
                
        if track in self.sounds:
            if self.bg_channel:
                self.bg_channel.play(self.sounds[track], loops=-1)

    def stop_bg_music(self):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except: pass
        if self.bg_channel:
            self.bg_channel.stop()

# Global instance
sound_manager = SoundManager()
