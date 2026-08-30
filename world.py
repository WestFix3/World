import pygame
import random
from collections import deque

pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("My Game")

clock = pygame.time.Clock()

height = screen.get_height()
width = screen.get_width()

isNight = False
dayTime = 0
shade = 0
nightSurface = pygame.Surface((width, height))
nightSurface.fill((0, 0, 0))
small_font = pygame.font.Font(None, 20)

gameMode = "Easy"

difficulties = {
    "Peaceful": {"target": 0, "current": 0},
    "Easy": {"target": 1, "current": 0},
    "Normal": {"target": 3, "current": 0},
    "Hard": {"target": 8, "current": 0}
}

EnemyList = []


TILE_SIZE = 32
CUT_SIZE = 16

worldMap = [[None for _ in range(width // TILE_SIZE)]
    for _ in range(height // TILE_SIZE)]

ScreenOffSetX = (width - (len(worldMap[0]) * TILE_SIZE)) // 2
ScreenOffSetY = (height - (len(worldMap) * TILE_SIZE)) // 2

def generateRiver():
    x = 0
    y = random.choice([i for i in range(0, height // TILE_SIZE)])
    while x < width // TILE_SIZE:
        side = random.choice([-1, 0, 1])
        while not (0 <= y + side < height // TILE_SIZE):
            side = random.choice([-1, 0, 1])
        if side == -1:
            worldMap[y][x] = Water(WaterCornerTileSet, x, y, 3, ScreenOffSetX, ScreenOffSetY)
            y += side
            worldMap[y][x] = Water(WaterCornerTileSet, x, y, 0, ScreenOffSetX, ScreenOffSetY)
        elif side == 1:
            worldMap[y][x] = Water(WaterCornerTileSet, x, y, 1, ScreenOffSetX, ScreenOffSetY)
            y += side
            worldMap[y][x] = Water(WaterCornerTileSet, x, y, 2, ScreenOffSetX, ScreenOffSetY)
        else:
            worldMap[y][x] = Water(WaterHorizontalFlowTileSet, x, y, 1, ScreenOffSetX, ScreenOffSetY)
        x += 1

def generateMap():
    for y in range(height // TILE_SIZE):
        for x in range(width // TILE_SIZE):
            if not isinstance(worldMap[y][x], Water):
                rnd = random.random()
                if rnd < 0.009:
                    worldMap[y][x] = Stone(StoneTile, x, y, ScreenOffSetX, ScreenOffSetY)
                elif rnd < 0.10:
                    worldMap[y][x] = Tree(TreeTile, x, y, ScreenOffSetX, ScreenOffSetY)
                else:
                    worldMap[y][x] = Grass(random.choice(GrassTiles), x, y, ScreenOffSetX, ScreenOffSetY)

def generateEnemy():
    while difficulties[gameMode]["current"] < difficulties[gameMode]["target"]:
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            x, y = 0, random.randint(0, height // TILE_SIZE - 1)

        elif side == "right":
            x, y = width // TILE_SIZE - 1, random.randint(0, height // TILE_SIZE - 1)

        elif side == "top":
            x, y = random.randint(0, width // TILE_SIZE - 1), 0

        else:
            x, y = random.randint(0, width // TILE_SIZE - 1), height // TILE_SIZE - 1
        if isinstance(worldMap[y][x], Grass):
            EnemyList.append(Enemy(EnemySheets, x, y, ScreenOffSetX, ScreenOffSetY))
            difficulties[gameMode]["current"] += 1

def cutScene(start, rowCol):
    lista = []
    width = rowCol[0] * 16
    height = rowCol[1] * 16

    for i in range(start[1], start[1] + height, 16):
        for j in range(start[0], start[0] + width, 16):
            lista.append(tilesheet.subsurface(pygame.Rect(j, i, 16, 16)))

    return lista

def cutCharacter(tilesheet, start, rows):
    lista = []
    cut_size = 16
    between = 16

    width = start[0] * (cut_size + between)
    height = start[1] * (cut_size + between)
    rows = width + rows * cut_size + ((rows - 1) * between)

    for row in range(width, rows, cut_size + between):
        lista.append(tilesheet.subsurface(pygame.Rect(row, height, cut_size * 2, cut_size * 2)))

    return lista
    

def checkTheCutScene(lista, rowCol):
    scale = 5
    for y in range(rowCol[1]):
        for x in range(rowCol[0]):
            image = pygame.transform.scale(lista[y * rowCol[0] + x],(TILE_SIZE * scale, TILE_SIZE * scale))
            screen.blit(image,(x * TILE_SIZE * scale, y * TILE_SIZE * scale))

def drawBackground(startX = 0, startY = 0, height = height // TILE_SIZE, width = width // TILE_SIZE):
    for y in range(startY, height):
        for x in range(startX, width):
            if isinstance(worldMap[y][x], Grass):
                worldMap[y][x].draw()

            if isinstance(worldMap[y][x], Tree):
                worldMap[y][x].draw()

            if isinstance(worldMap[y][x], Stone):
                worldMap[y][x].draw()
                
            if isinstance(worldMap[y][x], Water):
                worldMap[y][x].update()
                worldMap[y][x].draw()
                
            if isinstance(worldMap[y][x], CampFire):
                if worldMap[y][x].justPlaced:
                    worldMap[y][x].upgradeDraw()
                else:
                    worldMap[y][x].update()
                    worldMap[y][x].draw()
                    
            if isinstance(worldMap[y][x], Bridge):
                if worldMap[y][x].justPlaced:
                    worldMap[y][x].upgradeDraw()
                else:
                    worldMap[y][x].draw()

            if isinstance(worldMap[y][x], Tent):
                if worldMap[y][x].justPlaced:
                    worldMap[y][x].upgradeDraw()
                else:
                    worldMap[y][x].draw()

def drawUpBar():
    text = small_font.render("Place with (1)", True, (255, 255, 255))
    screen.blit(text, (10, 0))
    screen.blit(campFireTileSheet[0], (100, 0))

    text = small_font.render("Place with (2)", True, (255, 255, 255))
    screen.blit(text, (130, 0))
    screen.blit(BrideTile, (220, 0))

    text = small_font.render("Place with (3)", True, (255, 255, 255))
    screen.blit(text, (250, 0))
    screen.blit(TentTile, (340, 0))

    screen.blit(woodStuffTile,(width-120, 4))
    text = font.render(str(player.inventory["wood"]), True, (255, 255, 255))
    screen.blit(text, (width-100, 0))
    screen.blit(stoneStuffTile,(width-60, 4))
    text = font.render(str(player.inventory["stone"]), True, (255, 255, 255))
    screen.blit(text, (width-40, 0))

def drawDownBar():
    text = small_font.render("E (Get stuff/Build)", True, (255, 255, 255))
    screen.blit(text, (10, height-15))
    text = small_font.render("X (Pick up item)", True, (255, 255, 255))
    screen.blit(text, (130, height-15))
    text = small_font.render("Q (Attack)", True, (255, 255, 255))
    screen.blit(text, (240, height-15))
    text = small_font.render("R (Sleep)", True, (255, 255, 255))
    screen.blit(text, (310, height-15))

    text = small_font.render("HEALTH: ", True, (255, 255, 255))
    screen.blit(text, (width-170, height-15))
    for i in range(width-105, width-5, 20):
        screen.blit(heartTile, (i, height-15))

def updateObjects():
    for row in worldMap:
        for tile in row:
            if isinstance(tile, Tree) and tile.CutDownTree:
                tile.update()

            if isinstance(tile, Stone) and tile.CutDownStone:
                tile.update()

def updateLighting(shade, isNight, screen, nightSurface, worldMap):
    if isNight:
        if shade < 150:
            shade += 150 / (30 * 60)
    else:
        if shade > 0:
            shade -= 150 / (30 * 60)

    nightSurface.set_alpha(int(shade))
    screen.blit(nightSurface, (0, 0))

    for row in worldMap:
        for tile in row:
            if isinstance(tile, CampFire) and not tile.justPlaced:
                tile.illuminate()

    return shade

class WorldObject:
    def __init__(self, tileSheet, posX=None, posY=None, offset_x=0, offset_y=0):
        self.tileSheet = tileSheet
        if posX is not None and posY is not None:
            self.rect = pygame.Rect(
                posX * TILE_SIZE + offset_x,
                posY * TILE_SIZE + offset_y,
                TILE_SIZE,
                TILE_SIZE
            )
        else:
            self.rect = None

    def draw(self):
        pass

class Animation:
    def __init__(self, animation_speed=10):
        self.frame = 0
        self.animation_speed = animation_speed

    def update(self):
        self.frame += 1

    def get_frame(self, frames):
        return (self.frame // self.animation_speed) % len(frames)

class Build:
    def __init__(self, material, countNeed, justPlaced):
        self.material = material # wood OR stone
        self.count = 0
        self.countNeed = countNeed
        self.justPlaced = justPlaced

    def upgradeDraw(self):
        if self.count == self.countNeed:
            self.justPlaced = False
            return

        image = pygame.transform.scale(GrassTiles[0],(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

        if isinstance(self.tileSheet, list):
            image = pygame.transform.scale(self.tileSheet[0],(TILE_SIZE, TILE_SIZE))
            screen.blit(image, self.rect)
        else:
            image = pygame.transform.scale(self.tileSheet,(TILE_SIZE, TILE_SIZE))
            screen.blit(image, self.rect)
        
        image = pygame.transform.scale(buildTile,(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

        small_font = pygame.font.Font(None, 20)
        text = small_font.render(self.material.capitalize() + ": " + str(self.count) + "/" + str(self.countNeed), True, (255, 255, 255))
        screen.blit(text, (self.rect[0]-10, self.rect[1]-20))

class Player(WorldObject, Animation):
    def __init__(self, tileSheet):
        WorldObject.__init__(self, tileSheet)
        Animation.__init__(self)
        
        self.speed = 1
        self.moving = -1
        self.isUseAbility = -1
        self.direction = 1

        self.inventory = {"wood":0,
                     "stone": 0}

    def generate(self, offset_x=0, offset_y=0):
        sizeDown = len(worldMap)
        sizeLeft = len(worldMap[0])

        x = random.randint(sizeLeft // 4,sizeLeft // 2 + sizeLeft // 4)
        y = random.randint(sizeDown // 4,sizeDown // 2 + sizeDown // 4)

        while not isinstance(worldMap[y][x], Grass):
            x = random.randint(sizeLeft // 4,sizeLeft // 2 + sizeLeft // 4)
            y = random.randint(sizeDown // 4,sizeDown // 2 + sizeDown // 4)

        self.rect = pygame.Rect(x * TILE_SIZE + offset_x,y * TILE_SIZE + offset_y,TILE_SIZE,TILE_SIZE)

    def move(self):
        keys = pygame.key.get_pressed()

        self.moving = -1

        if keys[pygame.K_LEFT] and self.collide(2) is None:
            self.rect.x -= self.speed
            self.moving = 2

        if keys[pygame.K_RIGHT] and self.collide(3) is None:
            self.rect.x += self.speed
            self.moving = 3

        if keys[pygame.K_UP] and self.collide(0) is None:
            self.rect.y -= self.speed
            self.moving = 0

        if keys[pygame.K_DOWN] and self.collide(1) is None:
            self.rect.y += self.speed
            self.moving = 1

        if self.moving != -1:
            self.direction = self.moving

    def useAbility(self, event):
        side = self.collide(self.direction)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.isUseAbility = 0
                self.frame = 0
                if isinstance(side, (Tree, Stone)):
                    side.hit()
                    if side.destroyed:
                        x = (side.rect.centerx - ScreenOffSetX) // TILE_SIZE
                        y = (side.rect.centery - ScreenOffSetY) // TILE_SIZE
                        worldMap[y][x] = Grass(random.choice(GrassTiles), x, y, ScreenOffSetX, ScreenOffSetY)
                    
                if isinstance(side, CampFire) and side.justPlaced:
                    if self.inventory[side.material] > 0:
                        side.count += 1
                        self.inventory[side.material] -= 1

                if isinstance(side, Bridge) and side.justPlaced:
                    if self.inventory[side.material] > 0:
                        side.count += 1
                        self.inventory[side.material] -= 1

                if isinstance(side, Tent) and side.justPlaced:
                    if self.inventory[side.material] > 0:
                        side.count += 1
                        self.inventory[side.material] -= 1

            if event.key == pygame.K_x: # Felvenni valamit pl fa vagy kő (kiütött)
                if isinstance(side, Tree) and side.tileSheet == woodStuffTile:
                    side.cuttDown()
                    player.inventory["wood"] += 1

                if isinstance(side, Stone) and side.tileSheet == stoneStuffTile:
                    side.cuttDown()
                    player.inventory["stone"] += 1

            if event.key == pygame.K_q: # Támadás
                #Use sword later or bow
                pass

            rotation = {0: 0,1: 180,2: 90,3: 270}

            x = (self.rect.centerx - ScreenOffSetX) // TILE_SIZE
            y = (self.rect.centery - ScreenOffSetY) // TILE_SIZE

            if self.direction == 0:
                y -= 1
            if self.direction == 1:
                y += 1
            if self.direction == 2:
                x -= 1
            if self.direction == 3:
                x += 1
            if event.key == pygame.K_1: # Take obj (Campfire, később ház stb, de az már más számon!)
                if isinstance(worldMap[y][x], Grass):
                    worldMap[y][x] = CampFire(campFireTileSheet, x, y, ScreenOffSetX, ScreenOffSetY)
                
                elif isinstance(worldMap[y][x], CampFire):
                    worldMap[y][x] = Grass(random.choice(GrassTiles), x, y, ScreenOffSetX, ScreenOffSetY)

            if event.key == pygame.K_2:
                if isinstance(worldMap[y][x], Water) and worldMap[y][x].tileSheet is not WaterCornerTileSet:
                    worldMap[y][x] = Bridge(BrideTile, x, y, ScreenOffSetX, ScreenOffSetY)
                
                elif isinstance(worldMap[y][x], Bridge):
                    worldMap[y][x] = Water(WaterHorizontalFlowTileSet, x, y, 1, ScreenOffSetX, ScreenOffSetY)

            if event.key == pygame.K_3:
                if isinstance(worldMap[y][x], Grass):
                    rotated_image = pygame.transform.rotate(TentTile, rotation[self.direction])
                    worldMap[y][x] = Tent(rotated_image, x, y, ScreenOffSetX, ScreenOffSetY)
                
                elif isinstance(worldMap[y][x], Tent):
                    worldMap[y][x] = Grass(random.choice(GrassTiles), x, y, ScreenOffSetX, ScreenOffSetY)

            if event.key == pygame.K_r:
                if isinstance(worldMap[y][x], Tent) and isNight:
                    worldMap[y][x].rest()

    def collide(self, direction):
        rectCopy = self.rect.copy()
        x = rectCopy.x//TILE_SIZE
        y = rectCopy.y//TILE_SIZE

        if direction == 0:
            rectCopy.y -= self.speed
            y -= 1
        if direction == 1:
            rectCopy.y += self.speed
            y += 1
        if direction == 2:
            rectCopy.x -= self.speed
            x -= 1
        if direction == 3:
            rectCopy.x += self.speed
            x += 1

        x = (rectCopy.centerx - ScreenOffSetX) // TILE_SIZE
        y = (rectCopy.centery - ScreenOffSetY) // TILE_SIZE

        #Később ez (Ha Stonenak is lesz osztálya) if not isinstance(worldMap[y][x], Grass) and rectCopy.colliderect(worldMap[y][x].rect):        
        if isinstance(worldMap[y][x], Tree):
            pygame.draw.rect(screen, (255, 0, 0), worldMap[y][x].rect, 1)

            if rectCopy.colliderect(worldMap[y][x].rect):
                return worldMap[y][x]

        if isinstance(worldMap[y][x], Stone):
            pygame.draw.rect(screen, (255, 0, 0), worldMap[y][x].rect, 1)

            if rectCopy.colliderect(worldMap[y][x].rect):
                return worldMap[y][x]

        if isinstance(worldMap[y][x], CampFire):
            if rectCopy.colliderect(worldMap[y][x].rect):
                return worldMap[y][x]

        if isinstance(worldMap[y][x], Water):
            if rectCopy.colliderect(worldMap[y][x].rect):
                return worldMap[y][x]

        if isinstance(worldMap[y][x], Bridge) and worldMap[y][x].justPlaced:
            if rectCopy.colliderect(worldMap[y][x].rect):
                return worldMap[y][x]

        if isinstance(worldMap[y][x], Tent):
            if rectCopy.colliderect(worldMap[y][x].rect):
                return worldMap[y][x]

        pygame.draw.rect(screen, (0, 0, 255), rectCopy, 1)

        return None

    def draw(self):
        which = 0

        if self.isUseAbility != -1:
            which = 1

        frames = self.tileSheet[which][self.direction]

        if self.moving != -1 or self.isUseAbility != -1:
            current_frame = self.get_frame(frames)
        else:
            current_frame = 0

        if self.isUseAbility != -1 and self.frame // self.animation_speed >= len(frames):
            self.isUseAbility = -1
            self.frame = 0
            current_frame = 0

        image = frames[current_frame]
        screen.blit(image, self.rect)

class Enemy(WorldObject, Animation):
    def __init__(self, tileSheet, posX, posY, offset_x=0, offset_y=0):
        WorldObject.__init__(self, tileSheet, posX, posY, offset_x, offset_y)
        Animation.__init__(self)
        self.directions = ["up", "down", "left", "right"]
        self.pathToPlayer = []
        self.speed = 1
        self.steps = 0
        self.direction = None

    def move(self, direction):
        if direction == "up":
            self.rect.y -= self.speed
        elif direction == "down":
            self.rect.y += self.speed
        elif direction == "left":
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

        if player.rect.colliderect(self.rect):
            self.attack()

    def findPlayer(self):
        if self.steps == 0:

            if self.distance() <= 8:
                if not self.pathToPlayer:
                    self.pathToPlayer = self.PathToPlayer()

                if self.pathToPlayer:
                    direction = self.pathToPlayer[0]

                    if self.canMove(direction):
                        self.direction = self.pathToPlayer.pop(0)
                    else:
                        self.pathToPlayer = []
                        self.direction = None

            else:
                possibleDirections = self.inIntervalMap()

                if possibleDirections:
                    self.direction = random.choice(possibleDirections)

        if self.direction:
            self.move(self.direction)
            self.steps += self.speed

            if self.steps >= TILE_SIZE:
                self.steps = 0

    def inIntervalMap(self):
        directions = []

        for direction in self.directions:
            if self.canMove(direction):
                directions.append(direction)

        return directions

    def canMove(self, direction):
        x = (self.rect.centerx - ScreenOffSetX) // TILE_SIZE
        y = (self.rect.centery - ScreenOffSetY) // TILE_SIZE

        # Jelenlegi tile
        if not isinstance(worldMap[y][x], (Grass, Bridge)):
            return False

        if direction == "up":
            y -= 1
        elif direction == "down":
            y += 1
        elif direction == "left":
            x -= 1
        elif direction == "right":
            x += 1

        if not (0 <= x < len(worldMap[0]) and 0 <= y < len(worldMap)):
            return False

        return isinstance(worldMap[y][x], (Grass, Bridge))

    def distance(self):
        return (abs(self.rect.x - player.rect.x) + abs(self.rect.y - player.rect.y)) // TILE_SIZE

    def PathToPlayer(self):
        path = {}
        whereCanGo = deque()
        enemy_coord = (self.rect.x // TILE_SIZE,self.rect.y // TILE_SIZE)
        player_coord = (player.rect.x // TILE_SIZE,player.rect.y // TILE_SIZE)
        for i in self.directions:
            whereCanGo.append((enemy_coord, i))
        visited = []
        opposite = {
            "up" : "down",
            "down": "up",
            "left": "right",
            "right": "left"
        }

        while whereCanGo:
            direction = whereCanGo.popleft()
            x, y = direction[0][0], direction[0][1]

            if direction[1] == "up":
                y -= 1
            elif direction[1] == "down":
                y += 1
            elif direction[1] == "left":
                x -= 1
            else:
                x += 1

            """if playerCopy.colliderect(pygame.Rect(x * TILE_SIZE + offset_x,
            y * TILE_SIZE + offset_y,TILE_SIZE,TILE_SIZE):
                return reversePath(path)"""
            if (x, y) not in visited:
                if 0 <= x < len(worldMap[0]) and 0 <= y < len(worldMap):
                    if isinstance(worldMap[y][x], (Grass, Bridge)):
                        visited.append((x, y))
                        path[(x, y)] = (direction[0], direction[1])

                        if player_coord == (x, y):
                            return self.reversePath(path)

                        for i in self.directions:
                            if i != opposite[direction[1]]:
                                whereCanGo.append(((x, y), i))

    def reversePath(self, path):
        directions = []
        current = (player.rect.x//TILE_SIZE, player.rect.y//TILE_SIZE)

        while current != (self.rect.x // TILE_SIZE,self.rect.y // TILE_SIZE):
            previous, direction = path[current]
            directions.append(direction)
            current = previous

        directions.reverse()
        return directions

    def attack(self):
        print("TÁMADOM PLAYER-T")

    def draw(self):
        """grass = self.rect.copy()
        grass.x = (self.rect.x // TILE_SIZE) * TILE_SIZE
        grass.y = (self.rect.y // TILE_SIZE) * TILE_SIZE
        image = pygame.transform.scale(GrassTiles[0],(TILE_SIZE, TILE_SIZE))
        screen.blit(image, grass)"""
        #current_frame = self.get_frame(self.tileSheet)

        #image = pygame.transform.scale(self.tileSheet[current_frame],(TILE_SIZE, TILE_SIZE))
        image = pygame.transform.scale(self.tileSheet[0][0][0],(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

class Grass(WorldObject):
    #Lehetne egy onGrass, hogy mi van rajta, és a drawban ha az nem None
    #   akkor meghivjuk a Draw-ot arra ami a Grassen van (Optimalizáció)
    #   (Ellenőrizhetjük is ha valami rajta van, igy kevesebb kód/értelmezhetőbb)
    def __init__(self, tileSheet, posX, posY, offset_x=0, offset_y=0):
        super().__init__(tileSheet, posX, posY, offset_x, offset_y)

    def doRoad(self): #Ha füvet üssük akkor út lesz (KÉSŐBB)
        pass
        
    def draw(self):
        image = pygame.transform.scale(self.tileSheet,(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

class Water(WorldObject, Animation):
    def __init__(self, tileSheet, posX, posY, pos, offset_x=0, offset_y=0):
        WorldObject.__init__(self, tileSheet, posX, posY, offset_x, offset_y)
        Animation.__init__(self)
        self.position = pos

    def update(self):
        self.frame += 1

    def draw(self):
        current_frame = self.get_frame(self.tileSheet)

        image = pygame.transform.scale(
            self.tileSheet[current_frame][self.position],
            (TILE_SIZE, TILE_SIZE)
        )

        screen.blit(image, self.rect)

class Stone(WorldObject):
    def __init__(self, tileSheet, posX, posY, offset_x=0, offset_y=0):
        super().__init__(tileSheet, posX, posY, offset_x, offset_y)
        self.health = 5
        self.shake = 0
        self.CutDownStone = False
        self.destroyed = False

    def drop(self):
        self.health = 5
        self.tileSheet = stoneStuffTile

    def update(self):
        self.tileSheet = StoneTile
        self.health = 5
        self.shake = 0
        self.CutDownStone = False
        self.destroyed = False
        
    def plant(self):
        pass

    def hit(self):
        self.health -= 1
        self.shake = 10
        
        if self.health <= 0 and not self.CutDownStone:
            self.drop()
            self.CutDownStone = True

        elif self.health <= 0 and self.CutDownStone:
            self.destroyed = True

    def draw(self):
        image = pygame.transform.scale(GrassTiles[0],(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

        top = self.tileSheet.subsurface(pygame.Rect(0, 0, 16, 10))
        bottom = self.tileSheet.subsurface(pygame.Rect(0, 10, 16, 6))

        top = pygame.transform.scale(top, (TILE_SIZE, TILE_SIZE // 2))
        bottom = pygame.transform.scale(bottom, (TILE_SIZE, TILE_SIZE // 2))

        if self.shake > 0:
            offset = 1 if self.shake % 2 == 0 else -1
            self.shake -= 1
        else:
            offset = 0

        screen.blit(bottom, (self.rect[0],self.rect[1] + TILE_SIZE // 2))
        screen.blit(top, (self.rect[0] + offset,self.rect[1]))

    def cuttDown(self):
        self.tileSheet = CuttedStoneTile
        
class Tree(WorldObject):
    #Később a rönköt is kilehessen ütni + kell DROP IS!
    #Uj feature lehessen ültetni fát
    def __init__(self, tileSheet, posX, posY, offset_x=0, offset_y=0):
        super().__init__(tileSheet, posX, posY, offset_x, offset_y)
        self.health = 5
        self.shake = 0
        self.CutDownTree = False
        self.destroyed = False

    def drop(self):
        self.health = 5
        self.tileSheet = woodStuffTile

    def update(self):
        self.tileSheet = TreeTile
        self.health = 5
        self.shake = 0
        self.CutDownTree = False
        self.destroyed = False
        
    def plant(self):
        pass

    def hit(self):
        self.health -= 1
        self.shake = 10
        
        if self.health <= 0 and not self.CutDownTree:
            self.drop()
            self.CutDownTree = True

        elif self.health <= 0 and self.CutDownTree:
            self.destroyed = True

    def draw(self):
        image = pygame.transform.scale(GrassTiles[0],(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

        top = self.tileSheet.subsurface(pygame.Rect(0, 0, 16, 10))
        bottom = self.tileSheet.subsurface(pygame.Rect(0, 10, 16, 6))

        top = pygame.transform.scale(top, (TILE_SIZE, TILE_SIZE // 2))
        bottom = pygame.transform.scale(bottom, (TILE_SIZE, TILE_SIZE // 2))

        if self.shake > 0:
            offset = 1 if self.shake % 2 == 0 else -1
            self.shake -= 1
        else:
            offset = 0

        screen.blit(bottom, (self.rect[0],self.rect[1] + TILE_SIZE // 2))
        screen.blit(top, (self.rect[0] + offset,self.rect[1]))

    def cuttDown(self):
        self.tileSheet = CuttedTreeTile

class CampFire(WorldObject, Animation, Build):
    def __init__(self, tileSheet, posX, posY, offset_x=0, offset_y=0):
        WorldObject.__init__(self, tileSheet, posX, posY, offset_x, offset_y)
        Animation.__init__(self)
        Build.__init__(self, "wood", 5, True)

    def illuminate(self):
        map_x = (self.rect.x - ScreenOffSetX) // TILE_SIZE
        map_y = (self.rect.y - ScreenOffSetY) // TILE_SIZE

        startX = max(0, map_x - 2)
        startY = max(0, map_y - 2)

        endX = min(len(worldMap[0]), map_x + 3)
        endY = min(len(worldMap), map_y + 3)

        drawBackground(startX, startY, endY, endX)

        for dy in range(-2, 3):
            for dx in range(-2, 3):
                mx = map_x + dx
                my = map_y + dy
                if 0 <= my < len(worldMap) and 0 <= mx < len(worldMap[0]):
                    tile = worldMap[my][mx]
                    if tile is not None and not isinstance(tile, CampFire):
                        dark = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

                        if abs(dx) == 2 or abs(dy) == 2:
                            dark.fill((0, 0, 0, int(shade * 0.65)))
                        else:
                            dark.fill((0, 0, 0, int(shade * 0.50)))

                        screen.blit(dark, tile.rect)

        self.draw()

    def draw(self):
        image = pygame.transform.scale(GrassTiles[0],(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)
        current_frame = self.get_frame(self.tileSheet)

        image = pygame.transform.scale(self.tileSheet[current_frame],(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

class Bridge(WorldObject, Build):
    def __init__(self, tileSheet, posX, posY, offset_x=0, offset_y=0):
        WorldObject.__init__(self, tileSheet, posX, posY, offset_x, offset_y)
        Build.__init__(self, "wood", 5, True)

    def draw(self):
        image = pygame.transform.scale(WaterHorizontalFlowTileSet[0][0],(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

        image = pygame.transform.scale(self.tileSheet,(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

class Tent(WorldObject, Build):
    def __init__(self, tileSheet, posX, posY, offset_x=0, offset_y=0):
        WorldObject.__init__(self, tileSheet, posX, posY, offset_x, offset_y)
        Build.__init__(self, "wood", 5, True)

    def draw(self):
        image = pygame.transform.scale(GrassTiles[0],(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

        image = pygame.transform.scale(self.tileSheet,(TILE_SIZE, TILE_SIZE))
        screen.blit(image, self.rect)

    def rest(self):
        if not self.justPlaced:
            global isNight, shade, dayTime
            isNight = True
            shade = 1
            dayTime = 150

tilesheet = pygame.image.load("punyworld-overworld-tileset.png").convert_alpha()
ArcherTileSheet = pygame.image.load("Archer-Green.png").convert_alpha()
EnemyTileSheet = pygame.image.load("Soldier-Yellow.png").convert_alpha()
StuffTileSheet = pygame.image.load("Stuff.png").convert_alpha()
rawCampFire = pygame.image.load("campFire.png").convert_alpha()
heartTileSheet = pygame.image.load("heart.png").convert_alpha()

heartTile = heartTileSheet.subsurface(pygame.Rect(0, 0, 16, 16))
heartTile = pygame.transform.scale(heartTile, (16, 16))

breakedHeartTile = heartTileSheet.subsurface(pygame.Rect(16, 0, 16, 16))
breakedHeartTile = pygame.transform.scale(breakedHeartTile, (16, 16))

woodStuffTile = StuffTileSheet.subsurface(pygame.Rect(5, 5, 400, 280))
woodStuffTile = pygame.transform.scale(woodStuffTile, (16, 16))

stoneStuffTile = StuffTileSheet.subsurface(pygame.Rect(412, 5, 400, 265))
stoneStuffTile = pygame.transform.scale(stoneStuffTile, (16, 16))

campFireTileSheet = []

for i in range(0, 76, 19):
    #Mivel saját képet használtam teszteléshez és paramétereiben eltért
    #Teszteltem azt hogy mekkora mérete is legyen illetve nem sok ilyet
    #razoltam még életemben ezért nem a cutScene-el csináltam
    image = rawCampFire.subsurface(pygame.Rect(i, 0, 19, 19))
    image = pygame.transform.scale(image, (16, 16))
    campFireTileSheet.append(image)

Water1 = cutScene((16,208), (3,1))
Water2 = cutScene((16,272), (3,1))
Water3 = cutScene((16,336), (3,1))
Water4 = cutScene((16,400), (3,1))

WaterHorizontalFlowTileSet = [Water1, Water2, Water3, Water4]

Water1 = cutScene((0,160), (1,3))
Water2 = cutScene((0,224), (1,3))
Water3 = cutScene((0,288), (1,3))
Water4 = cutScene((0,352), (1,3))

WaterVerticalFlowTileSet = [Water1, Water2, Water3, Water4]

Fbal = cutScene((16,160), (1,1))[0]
Fjobb = cutScene((48,160), (1,1))[0]
Abal = cutScene((16,192), (1,1))[0]
Ajobb = cutScene((48,192), (1,1))[0]
Water1 = [Fbal, Fjobb, Abal, Ajobb]

Fbal = cutScene((16,224), (1,1))[0]
Fjobb = cutScene((48,224), (1,1))[0]
Abal = cutScene((16,256), (1,1))[0]
Ajobb = cutScene((48,256), (1,1))[0]
Water2 = [Fbal, Fjobb, Abal, Ajobb]

Fbal = cutScene((16,288), (1,1))[0]
Fjobb = cutScene((48,288), (1,1))[0]
Abal = cutScene((16,320), (1,1))[0]
Ajobb = cutScene((48,320), (1,1))[0]
Water3 = [Fbal, Fjobb, Abal, Ajobb]

Fbal = cutScene((16,352), (1,1))[0]
Fjobb = cutScene((48,352), (1,1))[0]
Abal = cutScene((16,384), (1,1))[0]
Ajobb = cutScene((48,384), (1,1))[0]
Water4 = [Fbal, Fjobb, Abal, Ajobb]

WaterCornerTileSet = [Water1, Water2, Water3, Water4]

BrideTile = cutScene((176, 496), (1,1))[0]
TentTile = cutScene((64, 416), (1,1))[0]

GrassTiles = cutScene((0,0), (3,3))
CircleTreeTiles = cutScene((0,112), (3,3))
RectTreeTiles = cutScene((48, 112), (3,3))
RowTreeTiles = cutScene((96, 112), (2,3))

buildTile = cutScene((336, 64), (1,1))[0]
destroyTile = cutScene((352, 64), (1,1))[0]

TreeTile = cutScene((128, 112), (1,1))[0]
CuttedTreeTile = cutScene((16, 432), (1,1))[0]
StoneTile = cutScene((0, 416), (1,1))[0]
CuttedStoneTile = cutScene((16, 416), (1,1))[0]

ArcherGoDown = cutCharacter(ArcherTileSheet, (0,0), 4)
ArcherGoRight = cutCharacter(ArcherTileSheet, (0,2), 4)
ArcherGoUp = cutCharacter(ArcherTileSheet, (0,4), 4)
ArcherGoLeft = cutCharacter(ArcherTileSheet, (0,6), 4)

ArcherAxeDown = cutCharacter(ArcherTileSheet, (12,0), 3)
ArcherAxeRight = cutCharacter(ArcherTileSheet, (12,2), 3)
ArcherAxeUp = cutCharacter(ArcherTileSheet, (12,4), 3)
ArcherAxeLeft = cutCharacter(ArcherTileSheet, (12,6), 3)

ArcherGo = [ArcherGoUp, ArcherGoDown, ArcherGoLeft, ArcherGoRight]
ArcherAxe = [ArcherAxeUp, ArcherAxeDown, ArcherAxeLeft, ArcherAxeRight]
ArcherSheets = [ArcherGo, ArcherAxe]

EnemyGoDown = cutCharacter(EnemyTileSheet, (0,0), 4)
EnemyGoRight = cutCharacter(EnemyTileSheet, (0,2), 4)
EnemyGoUp = cutCharacter(EnemyTileSheet, (0,4), 4)
EnemyGoLeft = cutCharacter(EnemyTileSheet, (0,6), 4)

EnemyAttackDown = cutCharacter(EnemyTileSheet, (4,0), 4)
EnemyAttackRight = cutCharacter(EnemyTileSheet, (4,2), 4)
EnemyAttackUp = cutCharacter(EnemyTileSheet, (4,4), 4)
EnemyAttackLeft = cutCharacter(EnemyTileSheet, (4,6), 4)

EnemyGo = [EnemyGoUp, EnemyGoDown, EnemyGoLeft, EnemyGoRight]
EnemyAttack = [EnemyAttackUp, EnemyAttackDown, EnemyAttackLeft, EnemyAttackRight]
EnemySheets = [EnemyGo, EnemyAttack]

generateRiver()
generateMap()

player = Player(ArcherSheets)
player.generate(ScreenOffSetX, ScreenOffSetY)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            player.useAbility(event)

    screen.fill((0, 128, 0))
    #screen.blit(breakedHeartTile, (0, 0))
    #checkTheCutScene(EnemyAttackLeft, (3,1))
    isNight = False
    dayTime = 150
    drawBackground()
    shade = updateLighting(shade, isNight, screen, nightSurface, worldMap)
    player.move()
    if player.moving != -1 or player.isUseAbility != -1:
        player.update()

    player.draw()
    for enemy in EnemyList:
        enemy.findPlayer()
        enemy.draw()
    drawUpBar()
    drawDownBar()
    pygame.display.flip()
    dayTime += clock.tick(60) / 1000

    if dayTime >= 150:
        isNight = not isNight
        dayTime = 0

        if not isNight:
            updateObjects()
        else:
            generateEnemy()
    #pygame.display.flip()

pygame.quit()
