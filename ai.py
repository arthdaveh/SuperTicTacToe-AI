import game_rules as do


#POV + big terminal scores 
AI = -1 #O
HUMAN = 1 #X
INF = 10**9

#Weights
W_CLAIM = 30
W_TWO = 10
W_ONE = 2

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

def evaluate(state):
    is_terminal, score = terminal_value(state)
    if is_terminal:
        return score
    return evaluate_nonterminal(state)

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