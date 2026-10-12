import pygame
import math
import random
import sys

pygame.init()
WIDTH, HEIGHT = 1000, 760
# Keep a stable game layout and let Pygame scale it to the display.
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("NEON FOUR | Connect Four AI")
clock = pygame.time.Clock()

BG = (10, 12, 22)
PANEL = (20, 25, 42)
BOARD_BLUE = (28, 43, 78)
BOARD_EDGE = (95, 116, 170)
PINK = (255, 64, 160)
PINK_LIGHT = (255, 174, 218)
CYAN = (45, 220, 245)
WHITE = (248, 250, 255)
MUTED = (174, 187, 207)
GREEN = (100, 255, 190)
ROWS, COLS = 6, 7
EMPTY, PLAYER, AI = 0, 1, 2
CELL = 76
BOARD_X, BOARD_Y = 220, 215
BOARD_W, BOARD_H = COLS * CELL, ROWS * CELL
font_title = pygame.font.SysFont("consolas", 42, bold=True)
font_heading = pygame.font.SysFont("consolas", 24, bold=True)
font = pygame.font.SysFont("consolas", 19, bold=True)
font_small = pygame.font.SysFont("consolas", 15)
font_tiny = pygame.font.SysFont("consolas", 12)

board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
game_mode, difficulty = "AI", "Medium"
current_player, game_over, winner = PLAYER, False, None
message = "Your turn — choose a column."
score_player = score_ai = score_draw = 0
ai_thinking, ai_due_time, hover_col = False, 0, None

def draw_text(text, used_font, color, x, y, center=False):
    surf = used_font.render(str(text), True, color)
    if center:
        x -= surf.get_width() // 2
    screen.blit(surf, (x, y))

def valid_columns(b):
    return [c for c in range(COLS) if b[0][c] == EMPTY]

def next_open_row(b, col):
    for r in range(ROWS - 1, -1, -1):
        if b[r][col] == EMPTY:
            return r
    return None

def winning_cells(b, piece):
    checks = []
    for r in range(ROWS):
        for c in range(COLS - 3):
            checks.append([(r, c+i) for i in range(4)])
    for c in range(COLS):
        for r in range(ROWS - 3):
            checks.append([(r+i, c) for i in range(4)])
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            checks.append([(r+i, c+i) for i in range(4)])
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            checks.append([(r-i, c+i) for i in range(4)])
    for cells in checks:
        if all(b[rr][cc] == piece for rr, cc in cells):
            return cells
    return None

def score_window(window, piece):
    opponent = PLAYER if piece == AI else AI
    score = 0
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 8
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 3
    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 10
    return score

def evaluate(b, piece):
    score = [b[r][COLS//2] for r in range(ROWS)].count(piece) * 6
    for r in range(ROWS):
        for c in range(COLS-3):
            score += score_window([b[r][c+i] for i in range(4)], piece)
    for c in range(COLS):
        for r in range(ROWS-3):
            score += score_window([b[r+i][c] for i in range(4)], piece)
    for r in range(ROWS-3):
        for c in range(COLS-3):
            score += score_window([b[r+i][c+i] for i in range(4)], piece)
    for r in range(3, ROWS):
        for c in range(COLS-3):
            score += score_window([b[r-i][c+i] for i in range(4)], piece)
    return score

def terminal(b):
    return winning_cells(b, PLAYER) or winning_cells(b, AI) or not valid_columns(b)

def minimax(b, depth, alpha, beta, maximizing):
    valid = valid_columns(b)
    if depth == 0 or terminal(b):
        if winning_cells(b, AI):
            return None, 100000 + depth
        if winning_cells(b, PLAYER):
            return None, -100000 - depth
        if not valid:
            return None, 0
        return None, evaluate(b, AI)
    valid.sort(key=lambda c: abs(COLS//2 - c))
    if maximizing:
        value, best = -math.inf, valid[0]
        for col in valid:
            row = next_open_row(b, col)
            b[row][col] = AI
            new_score = minimax(b, depth-1, alpha, beta, False)[1]
            b[row][col] = EMPTY
            if new_score > value:
                value, best = new_score, col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best, value
    value, best = math.inf, valid[0]
    for col in valid:
        row = next_open_row(b, col)
        b[row][col] = PLAYER
        new_score = minimax(b, depth-1, alpha, beta, True)[1]
        b[row][col] = EMPTY
        if new_score < value:
            value, best = new_score, col
        beta = min(beta, value)
        if alpha >= beta:
            break
    return best, value

def choose_ai_move():
    valid = valid_columns(board)
    if not valid:
        return None
    if difficulty == "Easy":
        if random.random() < 0.55:
            return random.choice(valid)
        depth = 2
    elif difficulty == "Hard":
        depth = 5
    else:
        depth = 4
    col, _ = minimax(board, depth, -math.inf, math.inf, True)
    return col if col in valid else valid[0]

def reset_game():
    global board, current_player, game_over, winner, message, ai_thinking
    board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    current_player, game_over, winner, ai_thinking = PLAYER, False, None, False
    message = "Your turn — choose a column." if game_mode == "AI" else "Player 1's turn."

def make_move(col, piece):
    global current_player, game_over, winner, message
    if game_over or col not in valid_columns(board):
        return False
    row = next_open_row(board, col)
    board[row][col] = piece
    if winning_cells(board, piece):
        game_over, winner = True, piece
        message = ("YOU WIN! NICE MOVES." if game_mode == "AI" else "PLAYER 1 WINS!") if piece == PLAYER else ("AI WINS — TRY AGAIN!" if game_mode == "AI" else "PLAYER 2 WINS!")
        return True
    if not valid_columns(board):
        game_over, winner, message = True, 0, "IT'S A DRAW!"
        return True
    if game_mode == "PVP":
        current_player = AI if piece == PLAYER else PLAYER
        message = "Player 2's turn." if current_player == AI else "Player 1's turn."
    else:
        current_player = AI if piece == PLAYER else PLAYER
        message = "AI is thinking..." if current_player == AI else "Your turn — choose a column."
    return True

def button(rect, label, active=False):
    fill = (47, 34, 70) if active else (25, 31, 49)
    border = PINK if active else (77, 92, 133)
    pygame.draw.rect(screen, fill, rect, border_radius=9)
    pygame.draw.rect(screen, border, rect, 2, border_radius=9)
    draw_text(label, font_small, WHITE if active else MUTED, rect[0]+rect[2]//2, rect[1]+(rect[3]-font_small.get_height())//2, True)

def draw_background():
    screen.fill(BG)
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (25, 31, 48), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (25, 31, 48), (0, y), (WIDTH, y))

def draw_board():
    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(glow, (255, 64, 160, 20), (BOARD_X-8, BOARD_Y-8, BOARD_W+16, BOARD_H+16), border_radius=18)
    screen.blit(glow, (0, 0))
    pygame.draw.rect(screen, BOARD_BLUE, (BOARD_X, BOARD_Y, BOARD_W, BOARD_H), border_radius=14)
    pygame.draw.rect(screen, BOARD_EDGE, (BOARD_X, BOARD_Y, BOARD_W, BOARD_H), 2, border_radius=14)
    wins = winning_cells(board, winner) if winner in (PLAYER, AI) else None
    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = BOARD_X+c*CELL+CELL//2, BOARD_Y+r*CELL+CELL//2
            piece = board[r][c]
            pygame.draw.circle(screen, (10, 12, 22), (cx, cy), 28)
            if piece == PLAYER:
                pygame.draw.circle(screen, PINK, (cx, cy), 25)
                pygame.draw.circle(screen, PINK_LIGHT, (cx-7, cy-8), 7)
                pygame.draw.circle(screen, (255, 190, 225), (cx, cy), 25, 2)
            elif piece == AI:
                pygame.draw.circle(screen, CYAN, (cx, cy), 25)
                pygame.draw.circle(screen, (175, 250, 255), (cx-7, cy-8), 7)
                pygame.draw.circle(screen, WHITE, (cx, cy), 25, 2)
            else:
                pygame.draw.circle(screen, (13, 18, 32), (cx, cy), 25)
                pygame.draw.circle(screen, (45, 55, 78), (cx, cy), 25, 1)
            if wins and (r, c) in wins:
                pygame.draw.circle(screen, GREEN, (cx, cy), 29, 3)
    if hover_col is not None and not game_over and current_player == PLAYER and not ai_thinking:
        if board[0][hover_col] == EMPTY:
            cx = BOARD_X+hover_col*CELL+CELL//2
            pygame.draw.circle(screen, PINK, (cx, BOARD_Y-22), 9)
            pygame.draw.circle(screen, WHITE, (cx, BOARD_Y-22), 3)

def draw_ui():
    draw_background()
    draw_text("NEON FOUR", font_title, PINK, 35, 25)
    draw_text("CONNECT FOUR  /  AI CHALLENGE", font_small, MUTED, 38, 73)
    draw_text("PLAYER  ●", font_small, PINK, 745, 35)
    draw_text("AI  ●", font_small, CYAN, 875, 35)
    pygame.draw.line(screen, (70, 83, 120), (32, 105), (WIDTH-32, 105), 2)

    rect = (35, 135, 160, 515)
    pygame.draw.rect(screen, PANEL, rect, border_radius=13)
    pygame.draw.rect(screen, (70, 83, 120), rect, 2, border_radius=13)
    draw_text("GAME MODE", font_small, MUTED, 50, 155)
    button((48, 182, 134, 39), "PLAYER vs AI", game_mode == "AI")
    button((48, 228, 134, 39), "2 PLAYERS", game_mode == "PVP")
    draw_text("AI LEVEL", font_small, MUTED, 50, 290)
    button((48, 317, 134, 35), "EASY", difficulty == "Easy")
    button((48, 359, 134, 35), "MEDIUM", difficulty == "Medium")
    button((48, 401, 134, 35), "HARD", difficulty == "Hard")
    draw_text("SCORES", font_small, MUTED, 50, 462)
    draw_text(f"You/P1: {score_player}", font_small, PINK, 50, 488)
    draw_text(f"AI/P2: {score_ai}", font_small, CYAN, 50, 512)
    draw_text(f"Draws: {score_draw}", font_small, WHITE, 50, 536)
    button((48, 574, 134, 40), "NEW GAME", True)
    draw_text("Click a column", font_tiny, MUTED, 50, 625)
    draw_text("to drop a disc.", font_tiny, MUTED, 50, 641)

    draw_board()
    color = GREEN if game_over and winner == PLAYER else (CYAN if current_player == AI and not game_over else WHITE)
    draw_text(message, font, color, BOARD_X+BOARD_W//2, 700, True)
    draw_text("PINK = YOU / PLAYER 1     CYAN = AI / PLAYER 2", font_tiny, MUTED, BOARD_X+BOARD_W//2, 730, True)

def finish_score():
    global score_player, score_ai, score_draw
    if winner == PLAYER:
        score_player += 1
    elif winner == AI:
        score_ai += 1
    else:
        score_draw += 1

def click_column(mx):
    global ai_thinking, ai_due_time
    col = (mx-BOARD_X)//CELL
    if not 0 <= col < COLS or game_over or ai_thinking:
        return
    piece = current_player if game_mode == "PVP" else PLAYER
    old_over = game_over
    if make_move(col, piece) and game_over and not old_over:
        finish_score()
    elif game_mode == "AI" and current_player == AI and not game_over:
        ai_thinking = True
        ai_due_time = pygame.time.get_ticks()+350

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_F11:
                # F11 toggles between fullscreen and a normal window.
                if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            hover_col = (mx-BOARD_X)//CELL if BOARD_X <= mx < BOARD_X+BOARD_W else None
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if 48 <= mx <= 182:
                if 182 <= my <= 221:
                    game_mode = "AI"; reset_game()
                elif 228 <= my <= 267:
                    game_mode = "PVP"; reset_game()
                elif 317 <= my <= 352:
                    difficulty = "Easy"; reset_game()
                elif 359 <= my <= 394:
                    difficulty = "Medium"; reset_game()
                elif 401 <= my <= 436:
                    difficulty = "Hard"; reset_game()
                elif 574 <= my <= 614:
                    reset_game()
            if BOARD_X <= mx < BOARD_X+BOARD_W and BOARD_Y-35 <= my <= BOARD_Y+BOARD_H:
                click_column(mx)

    if ai_thinking and pygame.time.get_ticks() >= ai_due_time and not game_over:
        col = choose_ai_move()
        if col is not None:
            old_over = game_over
            make_move(col, AI)
            if game_over and not old_over:
                finish_score()
        ai_thinking = False

    draw_ui()
    pygame.display.flip()

pygame.quit()
sys.exit()
