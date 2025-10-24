$(document).ready(function() {
    var game = new Chess();
    var board = null;
    var $status = $('#status');
    var $whiteCaptured = $('#whiteCaptured');
    var $blackCaptured = $('#blackCaptured');

    // YENİ: Alınan taşları renklerine göre saklamak için bir nesne
    var capturedPieces = { w: [], b: [] };

    // YENİ: Taş tiplerini renklerine göre Unicode sembollerine çeviren harita
    var pieceUnicode = {
        b: { p: '♟', n: '♞', b: '♝', r: '♜', q: '♛' }, // Siyah Taşlar
        w: { p: '♙', n: '♘', b: '♗', r: '♖', q: '♕' }  // Beyaz Taşlar
    };

    // YENİ: Alınan taşlar panelini güncelleyen fonksiyon
    function renderCapturedPieces() {
        // Beyazın aldıkları (Siyah taşlar)
        var blackHtml = capturedPieces.b.map(function(p) {
            return pieceUnicode.b[p];
        }).join(' ');
        $blackCaptured.html(blackHtml);

        // Siyahın aldıkları (Beyaz taşlar)
        var whiteHtml = capturedPieces.w.map(function(p) {
            return pieceUnicode.w[p];
        }).join(' ');
        $whiteCaptured.html(whiteHtml);
    }

    function getAiMove() {
        if (game.turn() !== 'b') return;

        $.ajax({
            url: "http://127.0.0.1:5000/api/get_move", // HATA DÜZELTİLDİ: IP adresi doğru yazıldı
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ fen: game.fen() }),
            success: function(data) {
                if (data.move) {
                    var move = game.move(data.move, { sloppy: true });
                    // YENİ: AI hamlesinin de taş alıp almadığını ve rengini kontrol et
                    if (move && move.captured) {
                        // AI (Siyah), Beyaz'ın taşını aldı (w)
                        capturedPieces.w.push(move.captured);
                        renderCapturedPieces();
                    }
                    board.position(game.fen());
                    updateStatus();
                }
            },
            error: function(err) {
                console.error("API Hatası:", err);
            }
        });
    }

    function onDrop(source, target) {
        var move = game.move({
            from: source,
            to: target,
            promotion: 'q'
        });

        if (move === null) return 'snapback';

        // YENİ: Oyuncunun hamlesinin taş alıp almadığını ve rengini kontrol et
        if (move.captured) {
            // Oyuncu (Beyaz), Siyah'ın taşını aldı (b)
            capturedPieces.b.push(move.captured);
            renderCapturedPieces();
        }

        updateStatus();
        window.setTimeout(getAiMove, 250);
    }

    function onSnapEnd() {
        board.position(game.fen());
    }

    function updateStatus() {
        var status = '';
        var moveColor = (game.turn() === 'b') ? 'Siyah' : 'Beyaz';

        if (game.in_checkmate()) {
            status = 'Oyun bitti, ' + moveColor + ' mat oldu.';
        } else if (game.in_draw()) {
            status = 'Oyun bitti, berabere.';
        } else {
            status = moveColor + ' oynayacak.';
            if (game.in_check()) {
                status += ', ' + moveColor + ' şah çekiyor.';
            }
        }
        $status.html(status);
    }

    // YENİ: Oyunu yeniden başlatan fonksiyon
    function restartGame() {
        game.reset();
        board.start();
        capturedPieces = { w: [], b: [] }; // Alınan taşları sıfırla
        renderCapturedPieces();
        updateStatus();
    }

    var config = {
        draggable: true,
        position: 'start',
        onDrop: onDrop,
        onSnapEnd: onSnapEnd,
        pieceTheme: 'static/img/{piece}.png'
    };

    board = Chessboard('myBoard', config);
    updateStatus();

    $('#restartBtn').on('click', restartGame);
});

