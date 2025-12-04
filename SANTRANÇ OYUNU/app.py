from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import chess
import chess.polyglot
import random

# --- GELİŞTİRİLMİŞ YAPAY ZEKA MOTORU (DENGELİ SEVİYE) ---

# Parça-Kare Tabloları (Değişiklik yok)
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0, 50, 50, 50, 50, 50, 50, 50, 50, 10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,  0,  0,  0, 20, 20,  0,  0,  0,  5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,  0,  0,  0,  0,  0,  0,  0,  0
]
KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50, -40,-20,  0,  0,  0,  0,-20,-40, -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30, -30,  0, 15, 20, 20, 15,  0,-30, -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40, -50,-40,-30,-30,-30,-30,-40,-50
]
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20, -10,  0,  0,  0,  0,  0,  0,-10, -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10, -10,  0, 10, 10, 10, 10,  0,-10, -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10, -20,-10,-10,-10,-10,-10,-10,-20
]
ROOK_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,  5, 10, 10, 10, 10, 10, 10,  5, -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5, -5,  0,  0,  0,  0,  0,  0, -5, -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,  0,  0,  0,  5,  5,  0,  0,  0
]
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20, -10,  0,  0,  0,  0,  0,  0,-10, -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,  0,  0,  5,  5,  5,  5,  0, -5, -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10, -20,-10,-10, -5, -5,-10,-10,-20
]
KING_MIDDLE_GAME_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30, -20,-30,-30,-40,-40,-30,-30,-20, -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,  20, 30, 10,  0,  0, 10, 30, 20
]
KING_END_GAME_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50, -30,-20,-10,  0,  0,-10,-20,-30, -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30, -30,-10, 30, 40, 40, 30,-10,-30, -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30, -50,-30,-30,-30,-30,-30,-30,-50
]

tas_degerleri = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
}

def evaluate_board(board):
    if board.is_checkmate():
        return -999999 if board.turn == chess.WHITE else 999999
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        return 0

    is_endgame = (not board.pieces(chess.QUEEN, chess.WHITE) and not board.pieces(chess.QUEEN, chess.BLACK)) or \
                 (len(board.piece_map()) < 10)

    puan = 0
    for kare_indeksi in chess.SQUARES:
        tas = board.piece_at(kare_indeksi)
        if not tas:
            continue

        deger = tas_degerleri[tas.piece_type]
        if tas.color == chess.WHITE:
            if tas.piece_type == chess.PAWN:   pozisyon_degeri = PAWN_TABLE[kare_indeksi]
            elif tas.piece_type == chess.KNIGHT: pozisyon_degeri = KNIGHT_TABLE[kare_indeksi]
            elif tas.piece_type == chess.BISHOP: pozisyon_degeri = BISHOP_TABLE[kare_indeksi]
            elif tas.piece_type == chess.ROOK:   pozisyon_degeri = ROOK_TABLE[kare_indeksi]
            elif tas.piece_type == chess.QUEEN:  pozisyon_degeri = QUEEN_TABLE[kare_indeksi]
            elif tas.piece_type == chess.KING:   pozisyon_degeri = KING_END_GAME_TABLE[kare_indeksi] if is_endgame else KING_MIDDLE_GAME_TABLE[kare_indeksi]
            puan += deger + pozisyon_degeri
        else:
            mirrored_square = chess.square_mirror(kare_indeksi)
            if tas.piece_type == chess.PAWN:   pozisyon_degeri = PAWN_TABLE[mirrored_square]
            elif tas.piece_type == chess.KNIGHT: pozisyon_degeri = KNIGHT_TABLE[mirrored_square]
            elif tas.piece_type == chess.BISHOP: pozisyon_degeri = BISHOP_TABLE[mirrored_square]
            elif tas.piece_type == chess.ROOK:   pozisyon_degeri = ROOK_TABLE[mirrored_square]
            elif tas.piece_type == chess.QUEEN:  pozisyon_degeri = QUEEN_TABLE[mirrored_square]
            elif tas.piece_type == chess.KING:   pozisyon_degeri = KING_END_GAME_TABLE[mirrored_square] if is_endgame else KING_MIDDLE_GAME_TABLE[mirrored_square]
            puan -= deger + pozisyon_degeri
            
    original_turn = board.turn
    board.turn = chess.WHITE
    white_moves = board.legal_moves.count()
    board.turn = chess.BLACK
    black_moves = board.legal_moves.count()
    board.turn = original_turn
    
    mobility_score = 2 * (white_moves - black_moves) 
    puan += mobility_score
            
    return puan

def minimax(board, depth, alpha, beta, is_maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if is_maximizing_player:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha: break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha: break
        return min_eval

def find_best_move(board, depth):
   try:
    with chess.polyglot.open_reader(BOOK_PATH) as reader:
        entries = list(reader.find_all(board))
        if entries:
            move = random.choices(
                [entry.move for entry in entries],
                [entry.weight for entry in entries],
                k=1
            )[0]
            print(f"Hamle açılış kitabından bulundu: {move.uci()}")
            return move
except FileNotFoundError:
    print("Açılış kitabı bulunamadı, Minimax'a geçiliyor.")

        pass
    
    print("Açılış kitabında hamle yok, Minimax ile hesaplanıyor...")
    best_move = None
    is_maximizing_player = board.turn == chess.WHITE

    if is_maximizing_player:
        best_value = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            board_value = minimax(board, depth - 1, -float('inf'), float('inf'), False)
            board.pop()
            if board_value > best_value:
                best_value = board_value
                best_move = move
    else:
        best_value = float('inf')
        for move in board.legal_moves:
            board.push(move)
            board_value = minimax(board, depth - 1, -float('inf'), float('inf'), True)
            board.pop()
            if board_value < best_value:
                best_value = board_value
                best_move = move
                
    return best_move

# --- FLASK API KISMI ---

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_move', methods=['POST'])
def get_move():
    data = request.json
    fen = data.get('fen')
    
    if not fen:
        return jsonify({'error': 'FEN stringi eksik'}), 400

    try:
        board = chess.Board(fen)
        if board.is_game_over():
            return jsonify({'move': None, 'status': 'Oyun bitti'})

        # GÜNCELLENDİ: Hız ve güç dengesi için Minimax derinliği 3'e ayarlandı.
        # Motor hala akıllı değerlendirme özelliklerini kullanır ama daha hızlı yanıt verir.
        best_move = find_best_move(board, 3) 
        
        if best_move:
            return jsonify({'move': best_move.uci()})
        else:
            return jsonify({'move': None, 'status': 'Uygun hamle bulunamadı'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


