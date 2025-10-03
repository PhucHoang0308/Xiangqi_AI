# Xiangqi_AI
**Cấu trúc thư mục chi tiết và giải thích:**

```bash
Xiangqi_AI/
├── docs/
│   ├── rules_zh.md          # Luật chơi (规则 - Guīzé)
│   ├── design.md            # (Tùy chọn) Tài liệu thiết kế chi tiết (hệ thống, class,...)
│   ├── algorithms.md        # (Tùy chọn) Giải thích chi tiết thuật toán, công thức
│   └── usage.md             # Hướng dẫn sử dụng, cài đặt, ví dụ
├── src/
│   ├── board/
│   │   ├── palace.py         # Xử lý Cung điện (宫 - Gōng)
│   │   └── river.py          # Sông (河 - Hé) phân chia bàn cờ
│   ├── pieces/               # Định nghĩa các quân cờ  
│   │   ├── piece.py           # Lớp Piece (cha), định nghĩa các thuộc tính/phương thức chung
│   │   ├── jiang_shuai.py    # Tướng (将/帅)
│   │   ├── shi.py            # Sĩ (仕) 
│   │   ├── xiang.py          # Tượng (象)
│   │   ├── ma.py             # Mã (马)
│   │   ├── ju.py             # Xe (车)
│   │   ├── pao.py            # Pháo (炮)
│   │   └── bing_zu.py        # Tốt/Binh (兵/卒)
│   ├── search/
│   │   ├── shachou_search.py # Thuật toán săn Tướng (杀着搜索)
│   │   └── heuristics/
│   │       └── pingzhang.py  # Đánh giá thế trận (评仗)
│   │   ├── minimax.py         # Thuật toán Minimax cơ bản
│   │   ├── alphabeta.py      # Thuật toán Minimax với cắt tỉa Alpha-Beta
│   │   ├── negamax.py      # (Tùy chọn) Biến thể Negamax của Minimax
│   │   └── iterative_deepening.py  # (Tùy chọn) Tìm kiếm sâu dần lặp
│   └── evaluation/
│       └── shi_zhi.py        # Giá trị quân cờ (子力估值)
├── tests/
│   ├── test_jiang_checkmate.py # Kiểm tra chiếu bí (将死)
│   └── test_pao_skewer.py    # Test đòn Pháo (炮的牵制)
├── reports/
│   └── qipu_analysis.md      # Phân tích cờ thế (棋谱分析)
│   ├── report.md            # Báo cáo chính (Markdown)
│   ├── slides/
│   │   └── presentation.pdf # Slide thuyết trình
│   └── video_link.txt       # (Tùy chọn) Liên kết đến video demo/thuyết trình
├── README.md                  # Mô tả dự án, hướng dẫn cài đặt, chạy
├── .gitignore                 # Các file/thư mục bỏ qua khi dùng Git
├── requirements.txt         # (Tùy chọn) Các thư viện cần thiết (nếu có)
└── LICENSE                  # (Tùy chọn) Giấy phép sử dụng mã nguồn
```
```

**Giải thích thuật ngữ kết hợp:**

1. **Quân cờ (棋子 - Qízi):**
- Tướng: Jiàng (将) - Bên Đỏ, Shuài (帅) - Bên Đen
- Sĩ: Shì (仕) - Đỏ, Shì (士) - Đen
- Tượng: Xiàng (象) - Đỏ, Xiàng (相) - Đen
- Xe: Jū (车) - cả 2 bên
- Pháo: Pào (炮)
- Tốt: Bīng (兵) - Đỏ, Zú (卒) - Đen

2. **Vùng đặc biệt:**
- Cung điện: Jiǔgōng (九宫) - 3x3 ô mỗi bên
- Sông: Hé (河) - chia đôi bàn cờ

3. **Chiến thuật:**
- Chiếu (将军 - Jiāngjūn)
- Chiếu bí (将死 - Jiàngsǐ)
- Đổi quân (兑子 - Duìzǐ)
- Song Pháo (双炮 - Shuāng Pào)

**Ví dụ code với phiên âm:**
```python
# Trong file pao.py
class Pao(Piece):
    def get_valid_moves(self, board):
        """
        Pháo (炮) di chuyển theo đường thẳng, ăn quân phải nhảy qua 1 quân
        Bǎopào (包炮) - Pháo bọc
        """
        moves = []
        # Tìm các điểm không quân (Kōngbù - 空步)
        # Tìm điểm có quân để nhảy (Jiàntiáo - 箭跳)
        return moves
```

**Thành phần mới cho cờ Tướng:**
1. `palace.py`: Xử lý logic di chuyển Tướng/Sĩ trong Cửu Cung
2. `river.py`: Kiểm tra điều kiện qua sông cho Tốt và Tượng
3. `shi_zhi.py`: Hàm đánh giá theo giá trị quân:
   ```python
   # Giá trị quân theo Qián Hồng Bát (大师级估值)
   PIECE_VALUE = {
       'jiang': 20000,  # Tướng phải được bảo vệ
       'pao': 450,      # Pháo giá trị thay đổi theo thế trận
       'bing': 100      # Tốt qua sông tăng giá trị
   }
   ```

**Cải tiến thuật toán:**
```python
# Trong alphabeta.py
def evaluate(self, board):
    """
    Kết hợp đánh giá theo:
    - Zili (子力): Giá trị vật chất
    - Shizhan (势战): Thế trận
    - Kongjian (空间): Kiểm soát không gian
    """
    return self.material_eval(board) * 0.6 + self.positional_eval(board) * 0.4
```

**Chạy benchmark với tình huống cờ Tướng kinh điển:**
```bash
# Test thế trận "Thất Tinh Tụ Hội" (七星聚会)
python benchmarks/time_benchmark.py --position qixing
```

Cấu trúc này phản ánh đặc thù cờ Tướng Trung Hoa với các yếu tố:
- Sự phân biệt tên quân theo màu (将/帅)
- Luật đặc biệt cho Pháo (炮) và Tượng (象)
- Cơ chế tính điểm đặc thù cho Tốt qua sông (兵过河顶车)

**Giải thích chi tiết các file/thư mục quan trọng:**

*   **`src/`**:
    *   **`board/`**:
        *   `board.py`: Lớp `Board` sẽ quản lý trạng thái bàn cờ (vị trí các quân cờ), cung cấp các phương thức để:
            *   Khởi tạo bàn cờ ban đầu.
            *   Thực hiện nước đi (cập nhật vị trí quân cờ).
            *   Kiểm tra tính hợp lệ của nước đi.
            *   Kiểm tra trạng thái kết thúc ván cờ (chiếu tướng, hết cờ,...).
            *   Lấy danh sách các nước đi hợp lệ (có thể chuyển sang `utils/`).
            *   Undo/redo nước đi (tùy chọn, phục vụ cho việc tìm kiếm).
        *    `board_contants.py`: Lưu các thông số của game.
    *   **`pieces/`**:
        *   `piece.py`: Lớp cơ sở `Piece` định nghĩa các thuộc tính chung (màu quân, ký hiệu,...) và các phương thức có thể được ghi đè (ví dụ: `get_possible_moves()`).
        *   Các lớp con (`Pawn`, `Rook`,...): Kế thừa từ `Piece`, định nghĩa cụ thể cách di chuyển của từng quân cờ.
    *   **`search/`**:
        *   `minimax.py`, `alphabeta.py`: Cài đặt các thuật toán tìm kiếm.  Các hàm này sẽ nhận vào trạng thái bàn cờ hiện tại, độ sâu tìm kiếm, và có thể là các tham số khác (như alpha, beta cho cắt tỉa).
    *   **`evaluation/`**:
        *   `evaluator.py`: Hàm `evaluate(board)` trả về một giá trị số đánh giá độ tốt/xấu của trạng thái bàn cờ `board` từ góc nhìn của một người chơi.  Đây là hàm *heuristic*, tức là ước lượng dựa trên kinh nghiệm, không phải là giá trị chính xác tuyệt đối.
    *   **`engine.py`**:
        *   Lớp `Engine` là "bộ não" của AI.  Nó sẽ:
            *   Nhận trạng thái bàn cờ.
            *   Sử dụng các thuật toán tìm kiếm (`search/`) và hàm đánh giá (`evaluation/`) để chọn nước đi tốt nhất.
            *   Trả về nước đi được chọn.
            *   Có thể có các phương thức để thiết lập độ khó, quản lý thời gian,...
    *   **`main.py`**:
        *   Tạo giao diện (nếu có), cho phép người dùng chơi với AI.
        *   Nếu không có giao diện, `main.py` có thể dùng để chạy các ván cờ tự động (AI vs AI) để kiểm tra và đánh giá.
    * **`utils`**: Chứa các hàm hỗ trợ cho việc tính toán
*   **`tests/`**:  Rất quan trọng để đảm bảo mã của bạn hoạt động đúng.  Sử dụng thư viện như `unittest` (có sẵn trong Python) hoặc `pytest` để viết các test case.
*   **`reports/`, `README.md`, `.gitignore`, ...**: Các file hỗ trợ, tài liệu.

**Ví dụ code (minh họa):**

```python
# src/pieces/pawn.py

from .piece import Piece

class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'P' if color == 'red' else 'p'

    def get_possible_moves(self, board):
        # ... (Cài đặt logic di chuyển của Tốt) ...
        moves = []
        # 1. Đi thẳng 1 ô
          #...
        # 2. Nếu qua sông tốt có thể đi ngang.
          #...

        return moves

# src/search/alphabeta.py
import math
from src.utils import move_generation

def alphabeta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluator.evaluate(board)

    if maximizing_player:
        max_eval = -math.inf
        for move in move_generation.generate_legal_moves(board): # Nên có hàm tạo moves riêng.
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in move_generation.generate_legal_moves(board):
            board.push(move)
            eval = alphabeta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# src/evaluation/evaluator.py
def evaluate(board):
  # Đơn giản: Đếm điểm dựa trên giá trị các quân cờ.
  # Phức tạp: Tính thêm vị trí, mobility, ...
  # ...
    score = 0
    #Cân bằng giá trị các quân cờ,
    # Tính điểm dựa trên vị trí quân cờ (ví dụ: Tốt qua sông có giá trị cao hơn)
    # Tính điểm dựa trên số lượng nước đi có thể thực hiện của mỗi quân cờ (mobility)
    return score
```


