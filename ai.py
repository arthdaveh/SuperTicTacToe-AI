import game_rules as do


#POV + big terminal scores 
AI = -1 #O
HUMAN = 1 #X
INF = 10**9

#Weights
W_CLAIM = 30
W_TWO = 10
W_ONE = 2

#Micro Board Weights
WM_TWO   = 3    # open 2-in-a-row in a mini
WM_ONE   = 1    # single-in-a-row in a mini
WM_FORK  = 8    # having a fork move available in a mini
POS_CENTER = 2  # owning mini center
POS_CORNER = 1  # owning mini corners
MICRO_FORCED_MULT = 1.5  # weight micro more on the forced mini
MICRO_SCALE = 1.0        # overall multiplier for micro part


def terminal_value(state):
    """Check if the game is over and return the score."""
    win = do.check_win(state.main_board)
    if win == AI:
        return True, +INF
    elif win == HUMAN:
        return True, -INF
    if do.all_mini_boards_done(state):
        return True, 0  # tie
    return False, 0

def legal_moves(state):
    moves = []
    for b in do.playable_boards_list(state):
        for c in range(9):
            if state.boards[b][c] == 0:
                moves.append((b, c))
    return moves

def evaluate_nonterminal(state):
    main_board = state.main_board

    #1) Claimed minibooards
    ai_claimed = sum(1 for v in main_board if v == AI)
    human_claimed = sum(1 for v in main_board if v == HUMAN)
    score = W_CLAIM * (ai_claimed - human_claimed)

    #2) Line Patterns 
    ai_two = hum_two = 0
    ai_one = hum_one = 0

    for a, b, c in do.WIN_LINES:
        line = (main_board[a], main_board[b], main_board[c])
        empty = line.count(0)
        ai_n = line.count(AI)
        hum_n = line.count(HUMAN)

        #1) Blocked Line
        if ai_n > 0 and hum_n > 0:
            continue

        #2) Two in a row
        if ai_n == 2 and empty == 1:
            ai_two += 1
        if hum_n == 2 and empty == 1:
            hum_two += 1

        #3) One in a row
        if ai_n == 1 and empty == 2:
            ai_one += 1
        if hum_n == 1 and empty == 2:
            hum_one += 1
        
    score = score + (W_TWO * (ai_two - hum_two))
    score = score + (W_ONE * (ai_one - hum_one))
    return score

def score_microBoard(cells):

    ai_two = hum_two = ai_one = hum_one = 0

    # line patterns
    for a, b, c in do.WIN_LINES:
        line  = (cells[a], cells[b], cells[c])
        empty = line.count(0)
        ai_n  = line.count(AI)
        hum_n = line.count(HUMAN)

        # blocked: both present -> no potential
        if ai_n and hum_n:
            continue

        if ai_n == 2 and empty == 1:
            ai_two += 1
        if hum_n == 2 and empty == 1:
            hum_two += 1

        if ai_n == 1 and empty == 2:
            ai_one += 1
        if hum_n == 1 and empty == 2:
            hum_one += 1

    # fork availability: does a single move create >=2 open-2s?
    def has_fork_for(player):
        for idx in range(9):
            if cells[idx] != 0:
                continue
            old = cells[idx]
            cells[idx] = player
            count = 0
            for a, b, c in do.WIN_LINES:
                line  = (cells[a], cells[b], cells[c])
                if line.count(player) == 2 and line.count(0) == 1:
                    count += 1
                    if count >= 2:  # fork created
                        cells[idx] = old
                        return True
            cells[idx] = old
        return False

    ai_fork  = 1 if has_fork_for(AI) else 0
    hum_fork = 1 if has_fork_for(HUMAN) else 0

    # positional: center and corners
    pos = 0
    if cells[4] == AI:      pos += POS_CENTER
    elif cells[4] == HUMAN: pos -= POS_CENTER

    for k in (0, 2, 6, 8):
        if cells[k] == AI:      pos += POS_CORNER
        elif cells[k] == HUMAN: pos -= POS_CORNER

    return (
        WM_TWO  * (ai_two - hum_two) +
        WM_ONE  * (ai_one - hum_one) +
        WM_FORK * (ai_fork - hum_fork) +
        pos
    )

def evaluate_micro(state):
    total = 0
    fb = state.forced_board
    for i in range(9):
        if state.main_board[i] != 0:
            continue
        if do.board_full(state.boards[i]):
            continue
        m = score_microBoard(state.boards[i])
        if fb is not None and i == fb:
            m *= MICRO_FORCED_MULT
        total += m
    return total

def evaluate(state):
    is_terminal, score = terminal_value(state)
    if is_terminal:
        return score
    macro = evaluate_nonterminal(state)
    micro = evaluate_micro(state)
    return macro + MICRO_SCALE * micro

def minimax(state, depth, alpha=-INF, beta=INF):
    is_term, val = terminal_value(state)
    if depth  == 0 or is_term:
        return None, evaluate(state)
    
    if state.current_turn == AI:
        max_eval = -INF
        best_move = None
        for move in legal_moves(state):
            b, c = move
            do.apply_move(state, b, c, state.current_turn)
            _, child_score = minimax(state, depth - 1, alpha, beta)
            do.undo_move(state)
              
            if child_score > max_eval:
                max_eval = child_score
                best_move = move

            # Alpha-Beta Pruning
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break

        return best_move, max_eval
    
    elif state.current_turn == HUMAN:
        min_eval = INF
        best_move = None
        for move in legal_moves(state):
            b, c = move
            do.apply_move(state, b, c, state.current_turn)
            _, child_score = minimax(state, depth - 1, alpha, beta)
            do.undo_move(state)
            if child_score < min_eval:
                min_eval = child_score
                best_move = move

            # Alpha-Beta Pruning
            beta = min(beta, min_eval)
            if beta <= alpha:
                break
        return best_move, min_eval
    
def best_move_minimax(state, depth=3):
    best_move, best_score = minimax(state, depth) 
    return best_move, best_score