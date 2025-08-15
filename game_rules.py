class State:

    def __init__(self) -> None:
        self.boards = [[0 for c in range(9)] for b in range(9)]
        self.current_turn = 1    
        self.main_board = [0] * 9
        self.forced_board = None  
        self.game_over = False
        self.game_result = 0
        self.move_stack = []


WIN_LINES = [
    (0,1,2),(3,4,5),(6,7,8),   # rows
    (0,3,6),(1,4,7),(2,5,8),   # columns
    (0,4,8),(2,4,6) ]          # diagonals



#Helper Functions
def board_full(arr):
    return all(v != 0 for v in arr)

def check_win(arr):
    for a,b,c in WIN_LINES:
        s = arr[a] + arr[b] + arr[c]
        if s == 3:   
            return 1
        if s == -3:  
            return -1
    return 0


## Game Functions
def new_game():
    return State()

def mini_board_done(s, i):
    """A mini-board is 'done' if someone claimed it or it's full."""
    return (s.main_board[i] != 0) or board_full(s.boards[i])

def playable_boards_list(s):

    if s.forced_board is not None:
        # Is the forced board still playable?
        if s.main_board[s.forced_board] == 0 and not board_full(s.boards[s.forced_board]):
            return [s.forced_board]
        # otherwise force is lifted (won or full) -> fall through to "free move"

    # Free move: any board that isn't claimed and isn't full
    return [i for i in range(9) if s.main_board[i] == 0 and not board_full(s.boards[i])]

def all_mini_boards_done(s):
    """True if every mini-board is either claimed or full (no more moves anywhere)."""
    return all(mini_board_done(s, i) for i in range(9))

def check_game_over(s):
  
    if s.game_over:
        return  # already decided

    winner = check_win(s.main_board)
    if winner != 0:
        s.game_result = winner
        s.game_over = True 
        return 
    
    if all_mini_boards_done(s):
        s.game_over = True
        s.game_result = 0  #tie

def reset_game(s):
    """commit genocide on the game state""" 

    s.current_turn = 1
    s.forced_board = None
    s.game_over = False
    s.game_result = 0
    s.boards[:] = [[0]*9 for _ in range(9)]
    s.main_board[:] = [0]*9

def undo_move(s):
    global move_stack, boards, main_board, forced_board, current_turn, game_over, game_result

    if s.move_stack:
        b, c, player, prev_forced, prev_main_val = s.move_stack.pop()
        s.boards[b][c] = 0
        s.main_board[b] = prev_main_val

        s.forced_board  = prev_forced
        s.current_turn  = player
        s.game_over   = False
        s.game_result = 0

def is_legal_move(s, board_idx, cell_idx) -> bool :
    # 1) If there IS a forced board, you must play there...
    if s.forced_board is not None and board_idx != s.forced_board:
        # ...unless that forced board is already won or full (then it's "free move" or smth this is getting confusing)
        if s.main_board[s.forced_board] == 0 and (not board_full(s.boards[s.forced_board])):
            return False

    # 2) You can't play in a mini-board that's already been claimed.
    if s.main_board[board_idx] != 0:
        return False

    # 3) Cell must be empty.
    return s.boards[board_idx][cell_idx] == 0

def apply_move(s, board_idx, cell_idx, player):

    assert player == s.current_turn, "player must match s.current_turn"

    record = (board_idx, cell_idx, s.current_turn, s.forced_board, s.main_board[board_idx])
    s.move_stack.append(record)  # save the move for potential undo

    # 1) Place the mark.
    s.boards[board_idx][cell_idx] = player

    # 2) Did this win that mini-board?
    w = check_win(s.boards[board_idx])     # returns 1 (X), -1 (O), or 0 (no win)
    if w != 0:
        s.main_board[board_idx] = w

    # 3) Choose the next forced board.
    target = cell_idx
    if s.main_board[target] == 0 and not board_full(s.boards[target]):
        s.forced_board = target
    else:
        s.forced_board = None

    # 4) Flip the turn.
    s.current_turn *= -1

