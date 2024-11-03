import pygame
import random
import math

pygame.init()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Dimensions de la fenêtre
WIDTH, HEIGHT = 600, 600
DIS = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu de Tir - Esquivez les cibles")

# Chargement des sons
shoot_sound = pygame.mixer.Sound("shoot.mp3")
hit_sound = pygame.mixer.Sound("hit.mp3")

# Vitesse du jeu
FPS = 60
clock = pygame.time.Clock()

# Classe pour les cibles
class Target:
    def __init__(self):
        self.radius = 20
        self.color = GREEN
        self.speed = 2
        self.alive = True
        self.x, self.y = self.spawn_outside()
        self.shoot_interval = random.randint(1000, 3000)  # intervalle de tir entre 1 et 3 secondes
        self.last_shot_time = pygame.time.get_ticks()

    def spawn_outside(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return random.randint(0, WIDTH), -self.radius
        elif side == 'bottom':
            return random.randint(0, WIDTH), HEIGHT + self.radius
        elif side == 'left':
            return -self.radius, random.randint(0, HEIGHT)
        elif side == 'right':
            return WIDTH + self.radius, random.randint(0, HEIGHT)

    def draw(self):
        if self.alive:
            pygame.draw.circle(DIS, self.color, (self.x, self.y), self.radius)

    def move(self, player_pos):
        if self.alive:
            angle = math.atan2(player_pos[1] - self.y, player_pos[0] - self.x)
            self.x += self.speed * math.cos(angle)
            self.y += self.speed * math.sin(angle)

    def shoot(self, player_pos):
        # Vérifie si l'intervalle de tir est atteint
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_interval:
            angle = math.atan2(player_pos[1] - self.y, player_pos[0] - self.x)
            self.last_shot_time = current_time
            return EnemyBullet(self.x, self.y, angle)
        return None

# Classe pour les balles du joueur
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 7
        self.angle = angle
        self.alive = True

    def move(self):
        if self.alive:
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
            if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
                self.alive = False

    def draw(self):
        if self.alive:
            pygame.draw.circle(DIS, YELLOW, (int(self.x), int(self.y)), 5)
            pygame.draw.circle(DIS, WHITE, (int(self.x), int(self.y)), 5, 1)

# Classe pour les balles des ennemis
class EnemyBullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 5
        self.angle = angle
        self.alive = True

    def move(self):
        if self.alive:
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
            if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
                self.alive = False

    def draw(self):
        if self.alive:
            pygame.draw.circle(DIS, RED, (int(self.x), int(self.y)), 5)

# Fonction pour calculer la distance entre deux points
def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# Fonction pour afficher le compte à rebours
def show_countdown():
    font = pygame.font.SysFont(None, 100)
    for i in range(3, 0, -1):
        DIS.fill(WHITE)
        countdown_text = font.render(str(i), True, BLUE)
        text_rect = countdown_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        DIS.blit(countdown_text, text_rect)
        pygame.display.flip()
        pygame.time.delay(1000)

# Fonction pour trouver la cible la plus proche
def find_closest_target(player_pos, targets):
    closest_target = None
    min_distance = float("inf")
    for target in targets:
        if target.alive:
            dist = distance(player_pos, (target.x, target.y))
            if dist < min_distance:
                min_distance = dist
                closest_target = target
    return closest_target

# Boucle principale du jeu
def game_loop():
    running = True
    targets = [Target() for _ in range(5)]
    player_pos = [WIDTH // 2, HEIGHT // 2]
    bullets = []
    enemy_bullets = []
    player_life = 3
    score = 0
    can_shoot = True  # Variable pour contrôler la cadence de tir

    show_countdown()

    while running:
        DIS.fill(WHITE)
        pygame.draw.circle(DIS, BLUE, (player_pos[0], player_pos[1]), 15)

        font = pygame.font.SysFont(None, 36)
        life_text = font.render(f'Vies: {player_life}', True, (0, 0, 0))
        DIS.blit(life_text, (10, 50))

        score_text = font.render(f'Score: {score}', True, (0, 0, 0))
        DIS.blit(score_text, (10, 100))

        # Déplacement et affichage des cibles
        for target in targets:
            target.move(player_pos)
            target.draw()

            # Vérifier si la cible atteint le joueur
            if target.alive and distance(player_pos, (target.x, target.y)) < target.radius + 15:
                player_life -= 1
                target.alive = False
                if player_life == 0:
                    running = False

            # Les ennemis tirent vers le joueur
            enemy_bullet = target.shoot(player_pos)
            if enemy_bullet:
                enemy_bullets.append(enemy_bullet)

        # Mise à jour et dessin des balles des ennemis
        for bullet in enemy_bullets:
            bullet.move()
            bullet.draw()
            if bullet.alive and distance(player_pos, (bullet.x, bullet.y)) < 15:  # Collision avec le joueur
                player_life -= 1
                bullet.alive = False
                if player_life == 0:
                    running = False

        # Mise à jour et dessin des balles du joueur
        for bullet in bullets:
            bullet.move()
            bullet.draw()
            if bullet.alive:
                for target in targets:
                    if target.alive and distance((bullet.x, bullet.y), (target.x, target.y)) < target.radius:
                        target.alive = False
                        bullet.alive = False
                        hit_sound.play()
                        score += 1

        bullets = [bullet for bullet in bullets if bullet.alive]
        enemy_bullets = [bullet for bullet in enemy_bullets if bullet.alive]
        targets = [target for target in targets if target.alive] + [Target() for _ in range(5 - len([t for t in targets if t.alive]))]

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                can_shoot = True  # Autorise un nouveau tir lorsque Espace est relâché

        # Mouvements du joueur
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_pos[0] -= 5
        if keys[pygame.K_RIGHT]:
            player_pos[0] += 5
        if keys[pygame.K_UP]:
            player_pos[1] -= 5
        if keys[pygame.K_DOWN]:
            player_pos[1] += 5

        # Tirer vers la cible la plus proche si le joueur appuie sur Espace
        if keys[pygame.K_SPACE] and can_shoot:
            can_shoot            = False  # Désactiver temporairement le tir pour contrôler la cadence de tir
            closest_target = find_closest_target(player_pos, targets)
            if closest_target:
                angle = math.atan2(closest_target.y - player_pos[1], closest_target.x - player_pos[0])
                bullets.append(Bullet(player_pos[0], player_pos[1], angle))
                shoot_sound.play()

        # Assurer que le joueur reste dans la fenêtre
        player_pos[0] = max(15, min(WIDTH - 15, player_pos[0]))
        player_pos[1] = max(15, min(HEIGHT - 15, player_pos[1]))

        # Rafraîchir l'écran
        pygame.display.flip()
        clock.tick(FPS)

    # Affichage de l'écran de fin de jeu
    DIS.fill(WHITE)
    end_font = pygame.font.SysFont(None, 72)
    end_text = end_font.render("Game Over", True, RED)
    score_text = font.render(f"Final Score: {score}", True, (0, 0, 0))
    DIS.blit(end_text, end_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
    DIS.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
    pygame.display.flip()
    pygame.time.delay(3000)  # Délai avant de fermer la fenêtre de jeu

# Lancer la boucle principale du jeu
game_loop()
pygame.quit()

