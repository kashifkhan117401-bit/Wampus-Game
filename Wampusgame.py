import pygame
import random
import sys
import math
import threading
import http.server
import socketserver
import webbrowser
import os
import time

pygame.init()
pygame.mixer.init()

GRID_SIZE = 4
CELL_SIZE = 140
MARGIN = 8
MENU_HEIGHT = 90
WINDOW_WIDTH = (CELL_SIZE + MARGIN) * GRID_SIZE + MARGIN
WINDOW_HEIGHT = (CELL_SIZE + MARGIN) * GRID_SIZE + MARGIN + MENU_HEIGHT

# TACTICAL MILITARY PALETTE
COLOR_BG         = (20, 24, 20)
COLOR_GRID_LINE  = (40, 50, 38)
COLOR_HIDDEN     = (28, 34, 26)
COLOR_REVEALED   = (38, 48, 36)
COLOR_TEXT_GREEN = (144, 200, 100)
COLOR_TEXT_ORANGE= (220, 140, 50)
COLOR_TACT_LIME  = (120, 190, 60)
COLOR_TACT_RED   = (200, 60, 50)
COLOR_TACT_AMBER = (210, 155, 30)
COLOR_TACT_STEEL = (90, 120, 140)
COLOR_TACT_OLIVE = (100, 130, 70)

def generate_synth_sound(frequency, duration, wave_type="sine"):
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    buf = bytearray()
    for i in range(num_samples):
        t = float(i) / sample_rate
        if wave_type == "sine":
            v = math.sin(2.0 * math.pi * frequency * t)
        elif wave_type == "square":
            v = 1.0 if math.sin(2.0 * math.pi * frequency * t) > 0 else -1.0
        buf.append(max(0, min(255, int((v + 1.0) * 127.5))))
    try:
        sound = pygame.mixer.Sound(buffer=buf)
        sound.set_volume(0.15)
        return sound
    except:
        return None

SOUND_MOVE = generate_synth_sound(440, 0.06, "sine")
SOUND_GOLD = generate_synth_sound(660, 0.3,  "sine")
SOUND_DEAD = generate_synth_sound(110, 0.5,  "square")
SOUND_WIN  = generate_synth_sound(550, 0.4,  "sine")

def play_fx(fx):
    if fx: fx.play()

class Cell:
    def __init__(self, r, c):
        self.r, self.c = r, c
        self.has_wumpus = self.has_pit = self.has_gold = False
        self.has_breeze = self.has_stench = self.has_glitter = False
        self.is_revealed = False

class World:
    def __init__(self):
        self.grid = [[Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.generate_world()
        self.generate_percepts()

    def generate_world(self):
        valid_slots = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if (r, c) != (0, 0)]
        g_slot = random.choice(valid_slots)
        for (r, c) in valid_slots:
            prob = random.random()
            if prob < 0.15 and (r, c) == g_slot:
                self.grid[r][c].has_gold = True
            elif prob < 0.15:
                self.grid[r][c].has_pit = True
        if not any(self.grid[r][c].has_gold for r in range(GRID_SIZE) for c in range(GRID_SIZE)):
            self.grid[g_slot[0]][g_slot[1]].has_gold = True
        w_slot = random.choice([s for s in valid_slots if s != g_slot])
        self.grid[w_slot[0]][w_slot[1]].has_wumpus = True

    def generate_percepts(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cell = self.grid[r][c]
                if cell.has_gold: cell.has_glitter = True
                for (nr, nc) in self.get_neighbors(r, c):
                    if self.grid[nr][nc].has_pit:    cell.has_breeze = True
                    if self.grid[nr][nc].has_wumpus: cell.has_stench = True

    def get_neighbors(self, r, c):
        nb = []
        if r > 0:           nb.append((r-1, c))
        if r < GRID_SIZE-1: nb.append((r+1, c))
        if c > 0:           nb.append((r, c-1))
        if c < GRID_SIZE-1: nb.append((r, c+1))
        return nb

class Agent:
    def __init__(self):
        self.r = self.c = self.score = 0
        self.is_dead = self.has_won = False
        self.visited = self.safe_cells = None
        self.visited = set([(0, 0)])
        self.safe_cells = set([(0, 0)])

    def move(self, dr, dc, world):
        if self.is_dead or self.has_won: return
        nr, nc = self.r + dr, self.c + dc
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            self.r, self.c = nr, nc
            self.score -= 1
            self.visited.add((nr, nc))
            play_fx(SOUND_MOVE)
            world.grid[nr][nc].is_revealed = True
            self.update_knowledge(world)
            self.check_status(world)

    def check_status(self, world):
        cell = world.grid[self.r][self.c]
        if cell.has_pit or cell.has_wumpus:
            self.is_dead = True; self.score -= 1000; play_fx(SOUND_DEAD)
        elif cell.has_gold:
            self.has_won = True; self.score += 1000; play_fx(SOUND_WIN)

    def update_knowledge(self, world):
        cell = world.grid[self.r][self.c]
        if not cell.has_breeze and not cell.has_stench:
            for (nr, nc) in world.get_neighbors(self.r, self.c):
                self.safe_cells.add((nr, nc))

    def decide_action(self, world):
        neighbors = world.get_neighbors(self.r, self.c)
        for (nr, nc) in neighbors:
            if world.grid[nr][nc].has_gold and (nr, nc) in self.safe_cells:
                return (nr - self.r, nc - self.c)
        unvisited_safe = [n for n in neighbors if n in self.safe_cells and n not in self.visited]
        if unvisited_safe:
            t = random.choice(unvisited_safe); return (t[0]-self.r, t[1]-self.c)
        visited_safe = [n for n in neighbors if n in self.safe_cells]
        if visited_safe:
            t = random.choice(visited_safe); return (t[0]-self.r, t[1]-self.c)
        t = random.choice(neighbors); return (t[0]-self.r, t[1]-self.c)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Wumpus World  |  Tactical Field Edition")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("Courier New", 30, bold=True)
        self.font_main  = pygame.font.SysFont("Courier New", 19, bold=True)
        self.font_sub   = pygame.font.SysFont("Courier New", 13)
        self.state = "MENU"
        self.auto_play = False
        self.reveal_all_at_end = True
        self.reset_game()

    def reset_game(self):
        self.world = World()
        self.agent = Agent()
        self.world.grid[0][0].is_revealed = True
        self.auto_play = False

    def run(self):
        running = True
        while running:
            self.clock.tick(15)
            running = self.handle_events()
            if self.state == "PLAYING" and self.auto_play and not self.agent.is_dead and not self.agent.has_won:
                dr, dc = self.agent.decide_action(self.world)
                self.agent.move(dr, dc, self.world)
                pygame.time.wait(180)
            self.draw()
        pygame.quit(); sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if self.state == "MENU":
                    if event.key == pygame.K_RETURN: self.state = "PLAYING"
                elif self.state == "PLAYING":
                    if   event.key == pygame.K_UP:    self.agent.move(-1, 0, self.world)
                    elif event.key == pygame.K_DOWN:  self.agent.move( 1, 0, self.world)
                    elif event.key == pygame.K_LEFT:  self.agent.move( 0,-1, self.world)
                    elif event.key == pygame.K_RIGHT: self.agent.move( 0, 1, self.world)
                    elif event.key == pygame.K_a:     self.auto_play = not self.auto_play
                    elif event.key == pygame.K_r:     self.reset_game()
                elif self.state == "GAME_OVER":
                    if event.key == pygame.K_r:
                        self.reset_game(); self.state = "PLAYING"
        if self.state == "PLAYING" and (self.agent.is_dead or self.agent.has_won):
            self.state = "GAME_OVER"
        return True

    def draw(self):
        self.screen.fill(COLOR_BG)
        if self.state == "MENU":
            for i in range(0, WINDOW_WIDTH, 35):
                pygame.draw.line(self.screen, (30, 38, 28), (i, 0), (i, WINDOW_HEIGHT), 1)
                pygame.draw.line(self.screen, (30, 38, 28), (0, i), (WINDOW_WIDTH, i), 1)
            pygame.draw.rect(self.screen, COLOR_TACT_OLIVE, (40, WINDOW_HEIGHT//3 - 40, WINDOW_WIDTH - 80, 70), 1)
            self.render_text("WUMPUS WORLD", WINDOW_WIDTH//2, WINDOW_HEIGHT//3 - 10, COLOR_TEXT_GREEN, center=True, font_type="title")
            self.render_text("TACTICAL FIELD EDITION", WINDOW_WIDTH//2, WINDOW_HEIGHT//3 + 28, COLOR_TACT_AMBER, center=True, size="small")
            self.render_text("[ ENTER ]  to deploy agent", WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 10, COLOR_TEXT_GREEN, center=True)
            self.render_text("ARROW KEYS: move   |   A: auto-pilot   |   R: reset", WINDOW_WIDTH//2, WINDOW_HEIGHT*2//3, COLOR_TACT_OLIVE, center=True, size="small")

        elif self.state in ["PLAYING", "GAME_OVER"]:
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    cell = self.world.grid[r][c]
                    x = c * (CELL_SIZE + MARGIN) + MARGIN
                    y = r * (CELL_SIZE + MARGIN) + MARGIN + MENU_HEIGHT
                    should_reveal = cell.is_revealed or (self.state == "GAME_OVER" and self.reveal_all_at_end)

                    if not should_reveal:
                        pygame.draw.rect(self.screen, COLOR_HIDDEN, (x, y, CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(self.screen, (45, 55, 42), (x, y, CELL_SIZE, CELL_SIZE), 1)
                    else:
                        pygame.draw.rect(self.screen, COLOR_REVEALED, (x, y, CELL_SIZE, CELL_SIZE))
                        border_col = (160, 100, 20) if (self.state == "GAME_OVER" and not cell.is_revealed) else COLOR_TACT_OLIVE
                        pygame.draw.rect(self.screen, border_col, (x, y, CELL_SIZE, CELL_SIZE), 2)

                        ly = y + 10
                        if cell.has_breeze:  self.render_text(">> WIND",   x+10, ly, COLOR_TACT_STEEL, size="small"); ly += 16
                        if cell.has_stench:  self.render_text("!! ODOR",   x+10, ly, COLOR_TEXT_ORANGE, size="small"); ly += 16
                        if cell.has_glitter: self.render_text("[TARGET]",  x+10, ly, COLOR_TACT_AMBER,  size="small")

                        cx, cy = x + CELL_SIZE//2, y + CELL_SIZE//2
                        if cell.has_pit:
                            for rad in [CELL_SIZE//3, CELL_SIZE//5, CELL_SIZE//9]:
                                pygame.draw.circle(self.screen, COLOR_TACT_STEEL, (cx, cy), rad, 2)
                            self.render_text("PIT", cx-12, cy-8, COLOR_TACT_STEEL, size="small")
                        elif cell.has_wumpus:
                            off = CELL_SIZE//4
                            pygame.draw.line(self.screen, COLOR_TACT_RED, (cx-off, cy-off), (cx+off, cy+off), 3)
                            pygame.draw.line(self.screen, COLOR_TACT_RED, (cx+off, cy-off), (cx-off, cy+off), 3)
                            pygame.draw.circle(self.screen, COLOR_TACT_RED, (cx, cy), off, 2)
                            self.render_text("HOSTILE", cx-25, cy+off+6, COLOR_TACT_RED, size="small")
                        elif cell.has_gold:
                            off = CELL_SIZE//4
                            pts = [(cx, cy-off), (cx+CELL_SIZE//5, cy), (cx, cy+off), (cx-CELL_SIZE//5, cy)]
                            pygame.draw.polygon(self.screen, COLOR_TACT_AMBER, pts, 3)
                            self.render_text("OBJ", cx-12, cy-8, COLOR_TACT_AMBER, size="small")

                    if self.agent.r == r and self.agent.c == c:
                        cx, cy = x + CELL_SIZE//2, y + CELL_SIZE//2
                        half = CELL_SIZE//5
                        pygame.draw.circle(self.screen, COLOR_TACT_LIME, (cx, cy), CELL_SIZE//6, 3)
                        pygame.draw.line(self.screen, COLOR_TACT_LIME, (cx-half, cy), (cx+half, cy), 1)
                        pygame.draw.line(self.screen, COLOR_TACT_LIME, (cx, cy-half), (cx, cy+half), 1)

            pygame.draw.line(self.screen, COLOR_TACT_OLIVE, (0, MENU_HEIGHT-10), (WINDOW_WIDTH, MENU_HEIGHT-10), 2)
            self.render_text(f"SCORE : {self.agent.score}", 20, 22, COLOR_TEXT_GREEN)
            self.render_text(f"POS [{self.agent.c},{self.agent.r}]", WINDOW_WIDTH//2 - 50, 22, COLOR_TACT_OLIVE)
            mode_txt = "MODE: AUTO-PILOT" if self.auto_play else "MODE: MANUAL"
            self.render_text(mode_txt, WINDOW_WIDTH-210, 22, COLOR_TACT_AMBER if self.auto_play else COLOR_TEXT_GREEN)

            if self.state == "GAME_OVER":
                msg, color = ("OBJECTIVE SECURED  >>  MISSION COMPLETE", COLOR_TACT_LIME) if self.agent.has_won else ("AGENT DOWN  >>  MISSION FAILED", COLOR_TACT_RED)
                box_y = WINDOW_HEIGHT//2 - 48
                pygame.draw.rect(self.screen, COLOR_BG, (0, box_y, WINDOW_WIDTH, 96))
                pygame.draw.rect(self.screen, color, (0, box_y, WINDOW_WIDTH, 96), 2)
                self.render_text(msg, WINDOW_WIDTH//2, box_y+28, color, center=True)
                self.render_text("Press  [ R ]  to redeploy", WINDOW_WIDTH//2, box_y+60, COLOR_TACT_AMBER, center=True, size="small")

        pygame.display.flip()

    def render_text(self, text, x, y, color, center=False, size="normal", font_type="main"):
        font = self.font_title if font_type == "title" else (self.font_main if size == "normal" else self.font_sub)
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y); self.screen.blit(surface, rect)
        else:
            self.screen.blit(surface, (x, y))

def serve_ui(port=8000):
    web_dir = os.path.join(os.path.dirname(__file__), "web")
    if not os.path.isdir(web_dir):
        print("web directory not found:", web_dir)
        return
    prev_cwd = os.getcwd()
    try:
        os.chdir(web_dir)
        handler = http.server.SimpleHTTPRequestHandler
        class ThreadedTCPServer(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
        server = ThreadedTCPServer(("", port), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://localhost:{port}/"
        webbrowser.open(url)
        print(f"Serving UI at {url}")
    finally:
        os.chdir(prev_cwd)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", action="store_true", help="Serve HTML/CSS UI and open browser")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.web:
        serve_ui(args.port)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping UI server")
            sys.exit(0)

    app = Game()
    app.run()
