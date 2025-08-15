import pygame
from view import WIDTH, HEIGHT,  MARGIN, GRID_SIZE, BIG_CELL, SMALL_CELL
from view import draw_grid, draw_marks, draw_big_marks, draw_playable_tint, draw_banner
import game_rules as do

#Initialize
pygame.init() 
clock = pygame.time.Clock() 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Tic-Tac-Toe") 
state = do.new_game()

#Functions
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

    board_idx = br*3 + bc  
    cell_idx  = cr*3 + cc  
    return board_idx, cell_idx

# --- Main Game Loop ---
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state.game_over:
                continue   

            px, py = pygame.mouse.get_pos()          # mouse position in window pixels
            hit = pixel_to_board_cell(px, py)        # map pixels -> (board, cell)
            if hit is not None:
                b_idx, c_idx = hit
                if do.is_legal_move(state, b_idx, c_idx):   
                    do.apply_move(state, b_idx, c_idx, state.current_turn)     # only place on empty cells
                    do.check_game_over(state)

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            # reset all state to a new game
            do.reset_game(state)

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            # killer queen, bites the dust
            do.undo_move(state) 

        
    # --- Drawing ---
    draw_grid(screen)
    draw_marks(screen, state.boards)
    draw_big_marks(screen, state.main_board)   

    playable = do.playable_boards_list(state)

    if state.game_over:
        playable = []
        if state.game_result == 1:
            draw_banner(screen, "X wins! Press R to restart")
        elif state.game_result == -1:
            draw_banner(screen, "O wins! Press R to restart")
        else:
            draw_banner(screen, "Tie game. Press R to restart")

    
    draw_playable_tint(screen, playable, alpha=64)    

    pygame.display.flip()
    clock.tick(60)

# --- Quit Pygame ---
pygame.quit()