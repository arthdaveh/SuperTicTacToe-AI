import pygame

# --- Constants ---
# Screen dimensions
WIDTH, HEIGHT = 800, 850
MARGIN = 40
GRID_SIZE = WIDTH - (MARGIN * 2)

BIG_CELL  = GRID_SIZE // 3   
SMALL_CELL = BIG_CELL // 3         


# Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

X_COLOR = (13, 135, 184) 
O_COLOR = (250, 7, 120)  

# --- Screen Setup ---
MAIN_W = 8
THIN_W = 3
GAP = MAIN_W // 2 + 10




def draw_grid(screen):
    screen.fill(BLACK)

    big = GRID_SIZE // 3

    # thick main grid
    for i in (1, 2):
        x = MARGIN + i * GRID_SIZE // 3
        pygame.draw.line(screen, WHITE, (x, MARGIN), (x, MARGIN + GRID_SIZE), MAIN_W)

        y = MARGIN + i * GRID_SIZE // 3
        pygame.draw.line(screen, WHITE, (MARGIN, y), (MARGIN + GRID_SIZE, y), MAIN_W)

    # mini grids
    for br in range(3):
        for bc in range(3):
            x0 = MARGIN + bc * big
            y0 = MARGIN + br * big

            # verticals
            for j in (1, 2):
                x = x0 + j * big // 3
                pygame.draw.line(screen, WHITE, (x, y0 + GAP), (x, y0 + big - GAP), THIN_W)

            # horizontals
            for j in (1, 2):
                y = y0 + j * big // 3
                pygame.draw.line(screen, WHITE, (x0 + GAP, y), (x0 + big - GAP, y), THIN_W)

def draw_marks(screen, boards):

    pad = SMALL_CELL // 6

    for b in range(9):
        br, bc = divmod(b, 3)
        x0 = MARGIN + bc * BIG_CELL
        y0 = MARGIN + br * BIG_CELL

        for c in range(9):
            cr, cc = divmod(c, 3)
            cx = x0 + cc * SMALL_CELL
            cy = y0 + cr * SMALL_CELL

            v = boards[b][c]
            if v == 0:
                continue

            if v == 1:  # draw X
                pygame.draw.line(screen, X_COLOR, (cx+pad, cy+pad), (cx+SMALL_CELL-pad, cy+SMALL_CELL-pad), 3)
                pygame.draw.line(screen, X_COLOR, (cx+SMALL_CELL-pad, cy+pad), (cx+pad,cy+SMALL_CELL-pad), 3)

            elif v == -1:  # draw O
                rect = pygame.Rect(cx+pad, cy+pad, SMALL_CELL - 2*pad, SMALL_CELL - 2*pad)
                pygame.draw.ellipse(screen, O_COLOR, rect, 3)

def draw_big_marks(screen, main_board):
    
    pad = SMALL_CELL // 8
    thick = 10

    for b in range(9):
        winner = main_board[b] 
        if winner == 0:
            continue      

        br, bc = divmod(b, 3)
        x0 = MARGIN + bc * BIG_CELL
        y0 = MARGIN + br * BIG_CELL

        left   = x0 + pad
        top    = y0 + pad
        right  = x0 + BIG_CELL - pad
        bottom = y0 + BIG_CELL - pad

        if winner == 1:
            # Big X (two thick diagonals)
            pygame.draw.line(screen, X_COLOR, (left,  top),    (right, bottom), thick)
            pygame.draw.line(screen, X_COLOR, (right, top),    (left,  bottom), thick)
        else:
            # Big O (thick circle outline)
            rect = pygame.Rect(left, top, right - left, bottom - top)
            pygame.draw.ellipse(screen, O_COLOR, rect, thick)

def draw_playable_tint(screen, boards_to_tint, alpha=64):
    """
    Draw a translucent fill over each playable big board.
    alpha: 0..255 (higher = more opaque). 64 is subtle.
    """
    inset = 2  # keep inside the thick borders
    for b in boards_to_tint:
        br, bc = divmod(b, 3)
        x0 = MARGIN + bc * BIG_CELL
        y0 = MARGIN + br * BIG_CELL

        w = BIG_CELL - 2*inset
        h = BIG_CELL - 2*inset

        # Make a per-pixel-alpha surface and fill with RGBA (white with alpha)
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, alpha))
        screen.blit(overlay, (x0 + inset, y0 + inset))

def draw_banner(screen, text):
    # Backdrop strip
    strip_h = 64
    overlay = pygame.Surface((WIDTH, strip_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))  # semi-transparent black
    screen.blit(overlay, (0, 0))

    # Text
    font = pygame.font.SysFont(None, 42)  # default font, size 42
    surf = font.render(text, True, WHITE)
    rect = surf.get_rect(center=(WIDTH // 2, strip_h // 2))
    screen.blit(surf, rect.topleft)
