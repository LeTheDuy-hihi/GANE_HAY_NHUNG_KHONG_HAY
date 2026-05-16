import pygame
import math
import random
import os
from constants import *

class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.speed = PLAYER_SPEED
        
        self.hp = PLAYER_HP_MAX
        self.max_hp = PLAYER_HP_MAX
        self.armor = 0
        self.max_armor = PLAYER_ARMOR_MAX
        
        self.angle = 0.0
        self.torso_angle = 0.0
        self.head_angle = 0.0
        self.target_angle = 0.0
        
        # Physics & Movement State
        self.accel = PLAYER_ACCEL
        self.friction = PLAYER_FRICTION
        self.is_sprinting = False
        self.is_aiming = False
        self.under_fire_timer = 0
        self.is_under_fire = False
        
        # Animations
        self.breath_timer = 0.0
        self.lean_amount = 0.0
        self.idle_shift_timer = 0
        self.flinch_vec = [0.0, 0.0]
        
        # Weapon state
        self.ak_cooldown = 0
        self.grenades = 3
        self.grenade_cooldown = 0
        self.ammo = 150
        
        # Visuals
        self.radius = 12
        self.step_timer = 0
        
        # Upgrades
        self.damage_mult = 1.0
        
        # New Mechanics
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.is_dashing = False
        self.focus = FOCUS_MAX
        self.is_focusing = False
        self.recoil = 0.0
        self.tilt = 0.0
        self.dash_dir = (0, 0)
        
        # Load custom image
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, "ANH", "player_clean.png")
        
        if os.path.exists(img_path):
            try:
                # Load with alpha support for PNG
                img = pygame.image.load(img_path).convert_alpha()
                # Scale to fit player size (slightly larger than radius for better look)
                self.image = pygame.transform.smoothscale(img, (48, 48))
            except Exception as e:
                print(f"Error loading player image: {e}")
                pass

    def update(self, keys_dict, mouse_pos, cam_x, cam_y, game_map, bullet_manager, effect_manager, sound_manager):
        # ── 1. Input Handling (Bypass Unikey via Windows API) ────────────────
        pygame_keys = keys_dict["pygame_keys"]
        raw_keys = keys_dict["raw_keys"]
        mouse_btns = pygame.mouse.get_pressed()
        
        # Direct hardware key polling — Windows GetAsyncKeyState
        # This ALWAYS works regardless of Unikey/Telex/VNI
        import ctypes
        def key_down(vk_code):
            return ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000 != 0
        
        # Virtual key codes for WASD and others
        VK_W, VK_A, VK_S, VK_D = 0x57, 0x41, 0x53, 0x44
        VK_Q, VK_R, VK_G = 0x51, 0x52, 0x47
        VK_SHIFT = 0x10
        VK_UP, VK_DOWN, VK_LEFT, VK_RIGHT = 0x26, 0x28, 0x25, 0x27
        
        w_pressed = key_down(VK_W) or key_down(VK_UP)
        a_pressed = key_down(VK_A) or key_down(VK_LEFT)
        s_pressed = key_down(VK_S) or key_down(VK_DOWN)
        d_pressed = key_down(VK_D) or key_down(VK_RIGHT)
        shift_pressed = key_down(VK_SHIFT)
        q_pressed = key_down(VK_Q)
        
        # ── 2. Movement States ───────────────────────────────────────────────
        self.is_aiming = mouse_btns[2] # Right click to aim
        self.is_sprinting = shift_pressed and not self.is_aiming
        self.is_under_fire = self.under_fire_timer > 0
        if self.under_fire_timer > 0: self.under_fire_timer -= 1
        
        # Calculate Target Speed
        current_max_speed = PLAYER_SPEED
        if self.is_sprinting: current_max_speed *= PLAYER_SPRINT_MUL
        if self.is_aiming:    current_max_speed *= PLAYER_AIM_MUL
        if self.is_under_fire: current_max_speed *= UNDER_FIRE_SPEED_MUL
        
        # ── 3. Physics (Accel / Friction) ──────────────────────────────────
        target_vx, target_vy = 0.0, 0.0
        if w_pressed: target_vy -= 1
        if s_pressed: target_vy += 1
        if a_pressed: target_vx -= 1
        if d_pressed: target_vx += 1
        
        if target_vx != 0 and target_vy != 0:
            norm = math.hypot(target_vx, target_vy)
            target_vx, target_vy = (target_vx/norm), (target_vy/norm)
            
        target_vx *= current_max_speed
        target_vy *= current_max_speed
        
        # Smooth Accel/Decel
        self.vx += (target_vx - self.vx) * self.accel
        self.vy += (target_vy - self.vy) * self.accel
        
        # Friction when no input
        if target_vx == 0 and target_vy == 0:
            self.vx *= (1.0 - self.friction)
            self.vy *= (1.0 - self.friction)

        # ── 4. Collision ───────────────────────────────────────────────────
        if not game_map.is_wall_pixel_radius(self.x + self.vx, self.y, self.radius):
            self.x += self.vx
        if not game_map.is_wall_pixel_radius(self.x, self.y + self.vy, self.radius):
            self.y += self.vy
            
        # ── 5. Rotation & Tactical Aiming ──────────────────────────────────
        mx, my = mouse_pos
        world_mx, world_my = mx + cam_x, my + cam_y
        self.target_angle = math.atan2(world_my - self.y, world_mx - self.x)
        
        # Torso rotates first, then head follows with a slight lag
        # But for top-down, let's make torso follow target_angle smoothly
        angle_diff = (self.target_angle - self.torso_angle + math.pi) % (2 * math.pi) - math.pi
        self.torso_angle += angle_diff * 0.15 # Torso speed
        
        angle_diff_head = (self.target_angle - self.head_angle + math.pi) % (2 * math.pi) - math.pi
        self.head_angle += angle_diff_head * 0.25 # Head is faster but lags behind torso? 
        # Actually head usually snaps faster. Let's make head snap, torso lag.
        
        self.angle = self.torso_angle # Current aim angle
        
        # ── 6. Animations (Breathing, Flinching, Lean) ─────────────────────
        self.breath_timer += BREATH_ANIM_SPEED
        self.flinch_vec[0] *= 0.85
        self.flinch_vec[1] *= 0.85
        
        if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
            self.step_timer += WALK_ANIM_SPEED * (current_max_speed / PLAYER_SPEED)
            # Lean into movement
            self.lean_amount += (self.vx * LEAN_INTENSITY - self.lean_amount) * 0.1
        else:
            self.lean_amount *= 0.9
            self.idle_shift_timer += 1
            
        # ── 7. Combat Mechanics ────────────────────────────────────────────
        if self.ak_cooldown > 0: self.ak_cooldown -= 1
        if mouse_btns[0] and self.ak_cooldown <= 0 and self.ammo > 0:
            self.shoot(world_mx, world_my, bullet_manager, effect_manager, sound_manager)
            
        # ── Focus Update ──────────────────────────────────────────────────
        self.is_focusing = q_pressed and self.focus > 5
        if self.is_focusing:
            self.focus -= FOCUS_DRAIN
        else:
            self.focus = min(FOCUS_MAX, self.focus + FOCUS_REGEN)
            
    def shoot(self, tx, ty, bullet_manager, effect_manager, sound_manager):
        self.ak_cooldown = AK_COOLDOWN
        self.ammo -= 1
        sound_manager.play('ak_shot')
        
        # Muzzle offset
        nx = math.cos(self.angle)
        ny = math.sin(self.angle)
        mx = self.x + nx * 18
        my = self.y + ny * 18
        
        # Spread
        spread = random.uniform(-0.05, 0.05)
        final_angle = self.angle + spread
        ftx = mx + math.cos(final_angle) * 100
        fty = my + math.sin(final_angle) * 100
        
        dmg = AK_DAMAGE * self.damage_mult
        bullet_manager.add_bullet(mx, my, ftx, fty, is_enemy=False, damage=dmg)
        effect_manager.add_muzzle_flash(mx, my, self.angle)
        effect_manager.add_shell(self.x, self.y, self.angle)
        effect_manager.shake.trigger(4, 5)
        self.recoil = 6.0

    def dash(self, sound_manager, dx, dy):
        self.is_dashing = True
        self.dash_timer = DASH_DURATION
        self.dash_cooldown = DASH_COOLDOWN
        self.dash_dir = (dx, dy)
        sound_manager.play('step') # Use step sound for now

    def throw_grenade(self, tx, ty, bullet_manager, sound_manager):
        self.grenades -= 1
        self.grenade_cooldown = GRENADE_COOLDOWN
        sound_manager.play('grenade_throw')
        bullet_manager.add_grenade(self.x, self.y, tx, ty)

    def take_damage(self, amount, effect_manager, sound_manager):
        if self.is_dashing: return # Invulnerable while dashing
        
        sound_manager.play('hurt')
        effect_manager.add_blood(self.x, self.y)
        effect_manager.shake.trigger(10, 15)
        
        # Tactical: Suppression & Flinch
        self.under_fire_timer = 90 # 1.5 seconds of nervousness
        self.flinch_vec = [random.uniform(-1, 1) * FLINCH_INTENSITY, random.uniform(-1, 1) * FLINCH_INTENSITY]
        
        if self.armor > 0:
            if self.armor >= amount:
                self.armor -= amount
                return
            else:
                amount -= self.armor
                self.armor = 0
                
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def draw(self, screen, cam_x, cam_y):
        # ── 1. Calculate Offsets & Scale ───────────────────────────────────
        # Flinch and breathing effects
        fx, fy = self.flinch_vec
        breath_scale = 1.0 + math.sin(self.breath_timer) * 0.02
        
        sx = int(self.x - cam_x + fx)
        sy = int(self.y - cam_y + fy)
        
        # Determine movement direction for legs
        is_moving = abs(self.vx) > 0.5 or abs(self.vy) > 0.5
        move_dir = math.atan2(self.vy, self.vx) if is_moving else self.torso_angle
        
        # ── 2. Draw Legs (Tactical Swing) ──────────────────────────────────
        swing = math.sin(self.step_timer * 8) * 12 if is_moving else 0
        side = 7
        
        # Tactical: Lean into movement
        lean_x = self.vx * 2
        lean_y = self.vy * 2
        
        for i in [-1, 1]: # Left/Right legs
            s = swing if i == 1 else -swing
            lx = sx + math.cos(move_dir) * s + math.cos(move_dir + i * math.pi/2) * side
            ly = sy + math.sin(move_dir) * s + math.sin(move_dir + i * math.pi/2) * side
            pygame.draw.circle(screen, (20, 25, 20), (int(lx), int(ly)), 6) # Boot
            pygame.draw.circle(screen, (40, 50, 40), (int(lx), int(ly)), 4) # Detail
            
        # ── 3. Draw Body (Torso) ───────────────────────────────────────────
        if hasattr(self, 'image') and self.image is not None:
            # Scale for breathing
            size = int(48 * breath_scale)
            scaled_img = pygame.transform.smoothscale(self.image, (size, size))
            # Rotate torso
            angle_deg = math.degrees(-self.torso_angle)
            rotated_img = pygame.transform.rotate(scaled_img, angle_deg)
            rect = rotated_img.get_rect(center=(sx + lean_x, sy + lean_y))
            screen.blit(rotated_img, rect.topleft)
        else:
            pygame.draw.circle(screen, PLAYER_DARK, (sx, sy), int(self.radius * breath_scale))
            
        # ── 4. Draw Aiming & Laser (Head/Gun) ──────────────────────────────
        nx = math.cos(self.angle)
        ny = math.sin(self.angle)
        
        # Laser Sight (Tactical)
        if self.is_aiming:
            laser_end = (sx + nx * 500, sy + ny * 500)
            pygame.draw.line(screen, (255, 0, 0, 100), (sx, sy), laser_end, 1)
            
        # Gun (Coupled to Torso but pointing to mouse)
        gx = sx + nx * 24 + lean_x
        gy = sy + ny * 24 + lean_y
        pygame.draw.line(screen, (30, 30, 30), (sx + lean_x, sy + lean_y), (gx, gy), 6)
        pygame.draw.line(screen, (60, 60, 60), (sx + lean_x, sy + lean_y), (gx, gy), 2)
        
        # Head (Independent Rotation)
        head_x = sx + math.cos(self.head_angle) * 3 + lean_x
        head_y = sy + math.sin(self.head_angle) * 3 + lean_y
        pygame.draw.circle(screen, (50, 70, 50), (int(head_x), int(head_y)), 9) # Helmet
        pygame.draw.circle(screen, (80, 100, 80), (int(head_x), int(head_y)), 7) # Detail
