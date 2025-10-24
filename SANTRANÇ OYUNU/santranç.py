import chess
import os
import platform
from colorama import init, Fore, Style

# colorama'yı başlat (Windows'ta düzgün çalışması için önemli)
init(autoreset=True)

# Taş değerleri aynı kalıyor.
tas_degerleri = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

# --- GÖRSEL İYİLEŞTİRMELER ---

def clear_screen():
    """Her hamleden sonra konsolu temizler."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_pretty_board(board):
    """Tahtayı Unicode karakterler ve ek bilgilerle daha güzel bir şekilde yazdırır."""
    print(Fore.YELLOW + "   a b c d e f g h")
    print(Fore.YELLOW + "  -----------------")
    # board.unicode() metodu, unicode satranç sembollerini kullanır.
    # Çıktıyı satır satır bölüp yanına satır numaralarını ekliyoruz.
    board_str_lines = str(board.unicode()).split('\n')
    for i, line in enumerate(board_str_lines):
        print(Fore.YELLOW + f"{8 - i} | " + Style.RESET_ALL + f"{line}" + Fore.YELLOW + f" | {8 - i}")
    print(Fore.YELLOW + "  -----------------")
    print(Fore.YELLOW + "   a b c d e f g h")

    # Oyun durumu hakkında ek bilgi ver
    if board.is_check():
        print(Fore.RED + Style.BRIGHT + "\nUYARI: ŞAH ÇEKİLDİ!")


# --- DEĞERLENDİRME VE AI MANTIĞI (DEĞİŞİKLİK YOK) ---

def evaluate_board(board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -float('inf')
        else:
            return float('inf')
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    toplam_puan = 0
    for kare in chess.SQUARES:
        tas = board.piece_at(kare)
        if tas:
            deger = tas_degerleri[tas.piece_type]
            if tas.color == chess.WHITE:
                toplam_puan += deger
            else:
                toplam_puan -= deger
    return toplam_puan

def minimax(board, depth, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False)
            board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True)
            board.pop()
            min_eval = min(min_eval, eval)
        return min_eval

def find_best_move_minimax(board):
    en_iyi_hamle = None
    en_iyi_skor = float('inf')
    
    # Derinliği 3'e çıkarmak, AI'ı biraz daha akıllı yapar ama yavaşlatabilir.
    # Başlangıç için 2 veya 3 idealdir.
    depth = 3 

    for move in board.legal_moves:
        board.push(move)
        skor = minimax(board, depth - 1, True)
        board.pop()
        
        if skor < en_iyi_skor:
            en_iyi_skor = skor
            en_iyi_hamle = move
            
    return en_iyi_hamle


# --- ANA OYUN DÖNGÜSÜ (GÖRSEL DEĞİŞİKLİKLERLE) ---

board = chess.Board()

while not board.is_game_over():
    clear_screen()
    print_pretty_board(board)
    
    if board.turn == chess.WHITE:
        print(Fore.GREEN + "\nSıra sizde (Beyaz)")
        is_move_valid = False
        while not is_move_valid:
            hamle = input("Lütfen hamlenizi girin (örn: e2e4): ")
            try:
                move_obj = chess.Move.from_uci(hamle)
                if move_obj in board.legal_moves:
                    board.push(move_obj)
                    is_move_valid = True
                else:
                    print(Fore.RED + "Geçersiz hamle! Lütfen tekrar deneyin.")
            except:
                print(Fore.RED + "Hatalı format! Lütfen 'e2e4' gibi bir formatta girin.")
    
    else:  # Sıra Siyahta (Yapay Zeka)
        print(Fore.CYAN + "\nBilgisayarın (Siyah) sırası, düşünüyor...")
        
        bilgisayar_hamlesi = find_best_move_minimax(board)
        
        if bilgisayar_hamlesi is None:
            print("Bilgisayar hamle bulamadı, oyun bitmiş olabilir.")
        else:
            # Hamleyi daha okunabilir Standart Cebirsel Notasyon'da gösterelim (örn: Nf3)
            print(Fore.CYAN + f"Bilgisayarın hamlesi: {board.san(bilgisayar_hamlesi)}")
            board.push(bilgisayar_hamlesi)
            # Yapay zekanın hamlesinden sonra kısa bir bekleme, kullanıcıya hamleyi görme fırsatı verir.
            # import time dedikten sonra time.sleep(1) ekleyebilirsiniz.
            
# --- OYUN SONU ---
clear_screen()
print(Style.BRIGHT + "\nOYUN BİTTİ!")
print_pretty_board(board)
print(Fore.MAGENTA + "Sonuç: " + board.result())

# Oyunun neden bittiğini daha açık bir şekilde belirt
if board.is_checkmate():
    kazanan = "Beyaz" if board.turn == chess.BLACK else "Siyah"
    print(Fore.MAGENTA + f"Sebep: Şah Mat! Kazanan: {kazanan}")
elif board.is_stalemate():
    print(Fore.MAGENTA + "Sebep: Pat! (Beraberlik)")
elif board.is_insufficient_material():
    print(Fore.MAGENTA + "Sebep: Yetersiz Materyal (Beraberlik)")
elif board.is_seventyfive_moves():
     print(Fore.MAGENTA + "Sebep: 75 Hamle Kuralı (Beraberlik)")
elif board.is_fivefold_repetition():
    print(Fore.MAGENTA + "Sebep: Beş Kez Tekrar Kuralı (Beraberlik)")