from typing import List, Tuple
import copy
# from local_driver import Alg3D, Board # ローカル検証用
from framework import Alg3D, Board # 本番用

size = 4

DIRECTIONS = [
    (1,0,0),(0,1,0),(0,0,1),
    (1,1,0),(1,-1,0),(1,0,1),(0,1,1),(0,-1,1),
    (1,1,1),(1,-1,1),(1,1,-1),(1,-1,-1)
]

class MyAI(Alg3D):
    def get_move(
        self,
        board: List[List[List[int]]], # 盤面情報
        player: int, # 先手(黒):1 後手(白):2
        last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
    ) -> Tuple[int, int]:
        # ここにアルゴリズムを書く
        print(self.best_move(board, player))
        # print(self.find_valid_moves(board))

        return self.best_move(board, player)


    def simulate_move(self, board, move, player):
        x, y, z = move
        new_board = copy.deepcopy(board)
        new_board[z][y][x] = player
        return new_board

    # スコアリングして返す
    def evaluate_board(self, board, player):
        # ここでは超簡単に：自分の石の数をスコアにする
        score = 0
        for z in range(size):
            for y in range(size):
                for x in range(size):
                    if board[z][y][x] == player:
                        score += 1
        return score
    


    #勝利判定
    def check_win(self, board, player, x, y, z):
        for dx, dy, dz in DIRECTIONS:
            count = 1  # 置いた石を含む
            # 正方向にチェック
            nx, ny, nz = x+dx, y+dy, z+dz
            while 0 <= nx < size and 0 <= ny < size and 0 <= nz < size and board[nz][ny][nx] == player:
                count += 1
                nx += dx; ny += dy; nz += dz
            # 逆方向にチェック
            nx, ny, nz = x-dx, y-dy, z-dz
            while 0 <= nx < size and 0 <= ny < size and 0 <= nz < size and board[nz][ny][nx] == player:
                count += 1
                nx -= dx; ny -= dy; nz -= dz
            if count >= 4:
                return True
        return False
    
    def block_move(self, board, player):
        block = None


        return 
    

    
    def best_move(self, board, player):
        moves = self.find_valid_moves(board)
        best_score = -9999
        best = None
        for move in moves:
            # 考えるべきこと　
            #    そこに置けば勝ち
            
            #　まずは、相手の上がりを阻止する手　最優先
            #　  危ない手は、あと一手で上がりになる手　→　相手が置いたら４つ揃ってる 
            #    次に危ない手は、あと一手で２以上のリーチになる手　→　相手がそこに置いたら２以上のリーチ →　置いたあとの盤面からさらにおける場所を探索する→あとで
            #　次に、自分の上がりを作る手
            #    禁じ手は自分がそこに置くと相手が上がりになる手
            #    禁じ手２は自分がそこに置くと相手が次の一手で２以上のリーチになる手
            #    クロスを取る→勝利
            #    角の隣を取る
            #    もうない　４隅のまんなかどこかを取る→その対角→その対面→その対面

            # まずは自分のパターン
            # 相手が置いたときのシミュレート

            new_selfboard = self.simulate_move(board, move, player) #自分が置いたときの盤面
            if check_win(self, board, player, move[0], move[1], move[2]):
                return 

            new_opositboard = self.simulate_move(board, move, 3 - player) #相手が置いたときの盤面



            
            score = self.evaluate_board(new_selfboard, player)
            if score > best_score:
                best_score = score
                best = move
        return best
        
    def find_valid_moves(self, board):
        moves = []
        # size = len(board)
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    if board[z][y][x] == 0:  # 空いてる
                        moves.append((x, y, z))
                        break  # その(x, y)には一番下の空きだけが有効
        return moves




def create_board() -> Board:
    return [[[0 for _ in range(4)] for _ in range(4)] for _ in range(4)]


# 実際にインスタンスを作って呼ぶ
if __name__ == "__main__":
    ai = MyAI()
    # ダミー盤面 (4x4x4 の空盤)

    dummy_board = create_board()
    # print(dummy_board)

    last_move = (1, 1, 1)
    player = 1
    move = ai.get_move(dummy_board, player, last_move)
    # print("AIが選んだ手:", move)