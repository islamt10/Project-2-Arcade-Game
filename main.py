# ==========================================
# UNIT 2 MATH & AI EXPLANATION
# ==========================================
# VECTORS:
# pygame.Vector2 stores positions, directions, velocity, and acceleration
# so movement and relative directions can be calculated
#
# DISTANCE:
# The game measures player to enemy distance for enemy detection and collision,
# and player to food distance to decide when food has been collected.
#
# NORMALIZATION:
# A direction toward a target is normalized to length 1 before it is used
# so movement direction does not depend on how far away it is.
#
# ANGLES / SINE / COSINE:
# The player's and enemies angles are converted to radians for cosine and
# sine to create unit direction vectors; atan2 converts a direction back
# into a rotation angle for enemies.
#
# VELOCITY AND ACCELERATION:
# Player thrust adds acceleration along its facing direction to velocity.
# Drag gradually slows the player, and a maximum speed limits velocity.
#
# DOT PRODUCT:
# An enemy dots its forward direction with the normalized direction to the
# player. A positive result means the player is in the enemy's forward
# half-plane; distance must also be within detection range to trigger pursuit.
#
# AI DECISION-MAKING:
# Enemies patrol while the player is outside their forward detection area.
# When both the dot-product and distance checks pass, they switch to ATTACK,
# turn toward the player, and move faster.

import pygame
import math
import random
import asyncio
async def main():
    global player, enemies, foods, score, survival_time, game_over, next_enemy_score

    pygame.init()

    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zombie Survivors")
    clock = pygame.time.Clock()
    zombie_image = pygame.image.load("assets/zombie.png").convert_alpha()
    zombie_image = pygame.transform.scale(zombie_image, (50,50))
    player_image = pygame.image.load("assets/player.png").convert_alpha()
    player_image = pygame.transform.scale(player_image,(60,60))
    food_image = pygame.image.load("assets/food.png").convert_alpha()
    food_image = pygame.transform.scale(food_image, (30,30))

    score = 0
    survival_time = 0
    game_over = False
    intro_screen = True
    game_over_font = pygame.font.Font(None, 72)
    score_font = pygame.font.Font(None, 48)
    hud_font = pygame.font.Font(None, 32)
    instruction_font = pygame.font.Font(None, 40)

    class Food:
        HUNGER_RESTORE = 11

        def __init__(self, position, radius):
            self.position = position
            self.radius = radius
        def draw(self):
            pygame.draw.circle(screen, (255,255,0), self.position,self.radius)
            food_rect = food_image.get_rect(center=self.position)
            screen.blit(food_image, food_rect)

    class Player:
        def __init__(self, rad):
            self.position = pygame.Vector2(WIDTH/2, HEIGHT/2)
            self.direction = pygame.Vector2(1,0)
            self.velocity = pygame.Vector2(0,0)
            self.VELOCITYMAX = 1000
            self.angle = 0
            self.rotspeed = 3
            self.thrust = 0.15
            self.drag = .95
            self.acceleration =  self.direction * self.thrust
            self.radius = rad
            self.hunger = 100
            self.HUNGER_MAX = 100
            self.HUNGER_DRAIN_RATE = 4
        def move(self):
            self.direction = pygame.Vector2(math.cos(math.radians(self.angle)), -math.sin(math.radians(self.angle)))
            self.velocity *= self.drag
            self.position += self.velocity
            if self.position.x < -30:
                self.position.x = WIDTH + 30
            elif self.position.x > WIDTH + 30:
                self.position.x = -30
            if self.position.y < -30:
                self.position.y = HEIGHT + 30
            elif self.position.y > HEIGHT + 30:
                self.position.y = -30
        def moveUp(self):
            # Thrust changes velocity in the facing direction; clamping its
            # vector length keeps acceleration from producing unbounded speed.
            self.acceleration =  self.direction * self.thrust
            self.velocity += self.acceleration
            if self.velocity.length() > self.VELOCITYMAX:
                self.velocity = self.velocity.normalize() * self.VELOCITYMAX
        def draw(self):
            rotated_player = pygame.transform.rotate(player_image, self.angle)
            player_rect = rotated_player.get_rect(center=self.position)
            screen.blit(rotated_player, player_rect)


    class Enemy:
        def __init__(self, pos, player, angle):
            self.detrange = 120
            self.angle = angle
            self.direction = pygame.Vector2(math.cos(math.radians(self.angle)), -math.sin(math.radians(self.angle)))
            self.pos = pos
            self.speed = 1
            self.player = player
            self.playpos = self.player.position
            self.toplayer = self.playpos - self.pos
            self.dot = self.toplayer.normalize().dot(self.direction) if self.toplayer.length_squared() else 0
            self.distanceToPlayer = self.pos.distance_to(self.playpos)
            self.color = (255,0,0)
            self.state = "PATROL"
        def move(self):
            self.playpos = self.player.position
            self.pos += self.direction * self.speed
            self.toplayer = self.playpos - self.pos
            self.distanceToPlayer = self.pos.distance_to(self.playpos)
            # Compare normalized directions so the dot product measures
            # alignment, not distance; positive alignment means player is ahead.
            self.dot = self.toplayer.normalize().dot(self.direction) if self.distanceToPlayer else 0
            if self.dot > 0 and self.distanceToPlayer< self.detrange:
                self.state = "ATTACK"
                self.direction = self.toplayer.normalize()
                self.speed=2
                self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
            else: 
                self.state = "PATROL"
                self.speed = 1
            if self.state == "ATTACK":
                self.color = (255,0,0)
            else: self.color = (255,255,255)
            wrapped = False
            if self.pos.x < -30:
                self.pos.x = WIDTH + 30
                wrapped = True
            elif self.pos.x > WIDTH + 30:
                self.pos.x = -30
                wrapped = True
            if self.pos.y < -30:
                self.pos.y = HEIGHT + 30
                wrapped = True
            elif self.pos.y > HEIGHT + 30:
                self.pos.y = -30
                wrapped = True
            if wrapped:
                to_player = self.player.position - self.pos
                if to_player.length_squared():
                    target_angle = math.degrees(math.atan2(-to_player.y, to_player.x))
                    self.angle = target_angle + random.uniform(-35, 35)
                    self.direction = pygame.Vector2(
                        math.cos(math.radians(self.angle)),
                        -math.sin(math.radians(self.angle))
                    )
        def draw(self):
            rotated_enemy = pygame.transform.rotate(zombie_image, self.angle)
            enemy_rect = rotated_enemy.get_rect(center=enemy.pos)
            screen.blit(rotated_enemy, enemy_rect)


    def reset_game():
        global player, enemies, foods, score, survival_time, game_over, next_enemy_score
        player = Player(15)
        enemies = []
        foods = []
        score = 0
        survival_time = 0
        next_enemy_score = 10
        game_over = False
        for _ in range(5):
            enemy_position = pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
            while enemy_position.distance_to(player.position) < 200:
                enemy_position = pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
            enemies.append(Enemy(enemy_position, player, random.randint(0, 360)))
            foods.append(Food(pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT)),5))

    def spawnEnemy():
        side = random.choice(("left", "right", "top", "bottom"))
        if side == "left":
            position = pygame.Vector2(-30, random.randint(0, HEIGHT))
        elif side == "right":
            position = pygame.Vector2(WIDTH + 30, random.randint(0, HEIGHT))
        elif side == "top":
            position = pygame.Vector2(random.randint(0, WIDTH), -30)
        else:
            position = pygame.Vector2(random.randint(0, WIDTH), HEIGHT + 30)

        to_player = player.position - position
        angle = math.degrees(math.atan2(-to_player.y, to_player.x)) + random.uniform(-35, 35)
        enemies.append(Enemy(position, player, angle))

    reset_game()

    running = True
    while(running):
        delta_time = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif intro_screen and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                intro_screen = False
            elif game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()

        keys = pygame.key.get_pressed()
        if not intro_screen and not game_over:
            survival_time += delta_time
            score = int(survival_time)
            while score >= next_enemy_score:
                spawnEnemy()
                next_enemy_score += 15
            player.hunger = max(0, player.hunger - player.HUNGER_DRAIN_RATE * delta_time)
            if player.hunger == 0:
                game_over = True

        if not intro_screen and not game_over:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.angle += player.rotspeed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.angle -= player.rotspeed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player.moveUp()
            player.move()
            for enemy in enemies:
                enemy.move()
                if enemy.pos.distance_to(player.position) <= player.radius + 12:
                    game_over = True
                    break
            if not game_over:
                for food in foods[:]:
                    if (player.position - food.position).magnitude() < player.radius + food.radius:
                        foods.remove(food)
                        foods.append(Food(pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT)), 5))
                        player.hunger = min(player.HUNGER_MAX, player.hunger + food.HUNGER_RESTORE)

        screen.fill((20, 24, 40))
        if intro_screen:
            title = game_over_font.render("ZOMBIE SURVIVORS", True, (255, 80, 80))
            instructions = (
                "Avoid the zombies and collect the food to survive!",
                "Press W to move forwards, and A/D to turn left/right.",
                "Press SPACE to continue",
            )
            screen.blit(title, title.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 100)))
            for index, text in enumerate(instructions):
                line = instruction_font.render(text, True, (255, 255, 255))
                screen.blit(line, line.get_rect(center=(WIDTH / 2, HEIGHT / 2 + index * 55)))
        elif game_over:
            title = game_over_font.render("GAME OVER", True, (255, 80, 80))
            final_score = score_font.render(f"Score: {score}", True, (255, 255, 255))
            restart_text = score_font.render("Press R to restart", True, (255, 255, 255))
            screen.blit(title, title.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40)))
            screen.blit(final_score, final_score.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 25)))
            screen.blit(restart_text, restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50)))
        else:
            player.draw()
            for enemy in enemies:
                enemy.draw()
            for food in foods:
                food.draw()
            score_text = hud_font.render(f"Score: {score}", True, (255, 255, 255))
            hunger_label = hud_font.render("Hunger", True, (255, 255, 255))
            pygame.draw.rect(screen, (80, 80, 80), (WIDTH - 224, 48, 200, 20))
            hunger_color = (50, 220, 50) if player.hunger > 30 else (255, 70, 70)
            pygame.draw.rect(screen, hunger_color, (WIDTH - 224, 48, int(200 * player.hunger / player.HUNGER_MAX), 20))
            screen.blit(score_text, score_text.get_rect(topright=(WIDTH - 24, 12)))
            screen.blit(hunger_label, hunger_label.get_rect(midright=(WIDTH - 232, 58)))
        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()
asyncio.run(main())