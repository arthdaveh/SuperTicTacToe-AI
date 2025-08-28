import pygame
from pygame import Rect
from view import WIDTH, HEIGHT, MARGIN, GRID_SIZE, BIG_CELL, SMALL_CELL
from view import draw_grid, draw_marks, draw_big_marks, draw_playable_tint, draw_banner
import game_rules as do
import ai



EASY_DEPTH = 2
MEDIUM_DEPTH = 4
HARD_DEPTH = 6

# -------------------------
# Helpers: pixels -> board
# -------------------------
def clamp_grid(x, y):
    """
    If (x, y) is outside the big square board area, return None.
    Otherwise return coordinates relative to the board's top-left corner.
    """
    if not (MARGIN <= x < MARGIN + GRID_SIZE and MARGIN <= y < MARGIN + GRID_SIZE):
        return None
    return x - MARGIN, y - MARGIN

def pixel_to_board_cell(px, py):
    g = clamp_grid(px, py)
    if g is None:
        return None
    gx, gy = g

    br = gy // BIG_CELL
    bc = gx // BIG_CELL

    cr = (gy % BIG_CELL) // SMALL_CELL
    cc = (gx % BIG_CELL) // SMALL_CELL

    board_idx = br * 3 + bc
    cell_idx  = cr * 3 + cc
    return board_idx, cell_idx


def run():
    # -------------
    # Initialize
    # -------------
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Super Tic-Tac-Toe")

    # game rules state
    state = do.new_game()

    # -------------------
    # Menu / mode state
    # -------------------
    GAME_STATE = "MENU"     # "MENU" or "PLAY"
    MENU_PAGE  = "root"     # "root" or "ai"
    VS_AI      = False

    # AI settings (used when VS_AI=True)
    AI_DEPTH    = 2
    USE_MINIMAX = True      

    # fonts
    pygame.font.init()
    FONT_TITLE = pygame.font.SysFont(None, 64)
    FONT_BTN   = pygame.font.SysFont(None, 40)

    def update_caption():
        mode = "AI" if VS_AI else "2-Player"
        alg  = "minimax" if USE_MINIMAX else "greedy"
        extra = f" — {mode}" + (f" ({alg}, depth {AI_DEPTH})" if VS_AI else "")
        pygame.display.set_caption("Super Tic-Tac-Toe" + extra)

    update_caption()

    # -------------------
    # Menu helpers
    def draw_text_center(surf, text, font, color, center):
        img = font.render(text, True, color)
        rect = img.get_rect(center=center)
        surf.blit(img, rect)

    def make_button(x, y, w, h, label, on_click):
        return {"rect": Rect(x, y, w, h), "label": label, "on_click": on_click}

    menu_buttons = []

    def build_menu():
        nonlocal menu_buttons
        menu_buttons = []
        bw, bh = 320, 60
        x = (WIDTH - bw) // 2
        top = 240
        gap = 80

        if MENU_PAGE == "root":
            menu_buttons.append(make_button(x, top + 0*gap, bw, bh, "1 Player (vs AI)", lambda: set_menu_page("ai")))
            menu_buttons.append(make_button(x, top + 1*gap, bw, bh, "2 Players", start_pvp))
        else:
            # AI difficulty submenu
            menu_buttons.append(make_button(x, top + 0*gap, bw, bh, "Easy",   lambda: start_ai(depth=EASY_DEPTH, use_minimax=True)))  # greedy
            menu_buttons.append(make_button(x, top + 1*gap, bw, bh, "Medium", lambda: start_ai(depth=MEDIUM_DEPTH, use_minimax=True)))   # minimax d2
            menu_buttons.append(make_button(x, top + 2*gap, bw, bh, "Hard",   lambda: start_ai(depth=HARD_DEPTH, use_minimax=True)))   # minimax d3
            menu_buttons.append(make_button(x, top + 3*gap, bw, bh, "Back",   lambda: set_menu_page("root")))

    def draw_menu():
        screen.fill((0, 0, 0))
        draw_text_center(screen, "Super Tic-Tac-Toe", FONT_TITLE, (255, 255, 255), (WIDTH // 2, 120))
        subtitle = "Choose difficulty" if MENU_PAGE == "ai" else "Click a mode"
        draw_text_center(screen, subtitle, FONT_BTN, (200, 200, 200), (WIDTH // 2, 190))

        mouse = pygame.mouse.get_pos()
        for btn in menu_buttons:
            r = btn["rect"]
            hover = r.collidepoint(mouse)
            # button rects
            pygame.draw.rect(screen, (40, 40, 40), r)
            pygame.draw.rect(screen, (255, 255, 255) if hover else (190, 190, 190), r, 3 if hover else 2)
            draw_text_center(screen, btn["label"], FONT_BTN, (255, 255, 255), r.center)

        # hint
        draw_text_center(screen, "Press R to return here anytime", FONT_BTN, (160, 160, 160), (WIDTH // 2, HEIGHT - 40))

    def set_menu_page(page):
        nonlocal MENU_PAGE
        MENU_PAGE = page
        build_menu()

    def start_pvp():
        nonlocal GAME_STATE, VS_AI
        VS_AI = False
        do.reset_game(state)
        GAME_STATE = "PLAY"
        update_caption()

    def start_ai(depth, use_minimax=True):
        nonlocal GAME_STATE, VS_AI, AI_DEPTH, USE_MINIMAX
        VS_AI = True
        AI_DEPTH = depth
        USE_MINIMAX = use_minimax
        do.reset_game(state)
        GAME_STATE = "PLAY"
        update_caption()

    build_menu()

    # small helper to avoid repeating two lines
    def commit_move_and_check(s, b, c):
        do.apply_move(s, b, c, s.current_turn)
        do.check_game_over(s)

    # ---------------
    # Main loop
    # ---------------
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # R anywhere -> go back to MENU and reset the board
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                GAME_STATE = "MENU"
                set_menu_page("root")
                do.reset_game(state)
                update_caption()

            # MENU interactions
            elif GAME_STATE == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    for btn in menu_buttons:
                        if btn["rect"].collidepoint(pos):
                            btn["on_click"]()
                            break

            # GAME interactions
            else:
                # Human click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if state.game_over:
                        continue
                    px, py = pygame.mouse.get_pos()
                    hit = pixel_to_board_cell(px, py)
                    if hit is not None:
                        b_idx, c_idx = hit
                        if do.is_legal_move(state, b_idx, c_idx):
                            commit_move_and_check(state, b_idx, c_idx)

                # undo
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                    do.undo_move(state)

        # -------------
        # Drawing
        # -------------
        if GAME_STATE == "MENU":
            draw_menu()
        else:
            draw_grid(screen)
            draw_marks(screen, state.boards)
            draw_big_marks(screen, state.main_board)

            playable = do.playable_boards_list(state)

            if state.game_over:
                playable = []
                if state.game_result == 1:
                    draw_banner(screen, "X wins! Press R for menu")
                elif state.game_result == -1:
                    draw_banner(screen, "O wins! Press R for menu")
                else:
                    draw_banner(screen, "Tie game. Press R for menu")

            draw_playable_tint(screen, playable, alpha=64)

            # AI move (only when playing vs AI and it's AI's turn)
            if not state.game_over and VS_AI and state.current_turn == ai.AI:
                best_move, _ = ai.best_move_minimax(state, depth=AI_DEPTH)
                if best_move:
                    b, c = best_move
                    commit_move_and_check(state, b, c)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run()