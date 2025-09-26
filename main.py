from typing import List, Tuple
import copy
from local_driver import Alg3D, Board # ローカル検証用
# from framework import Alg3D, Board # 本番用

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
        return self.best_move(board, player)


    # player: 自分
    # opponent: 相手
    # move: (x, y, z)
    # 戻り値: そのラインに自分と相手が何個あるか (my_count, opp_count)
    #         4個並べられるラインが存在しないなら (-1, -1)
    def check_line_counts(self, board, player, opponent, move):
        x, y, z = move
        results = []

        for dx, dy, dz in DIRECTIONS:
            line = [(x + dx*i, y + dy*i, z + dz*i) for i in range(-3, 4)]
            line = [(nx, ny, nz) for nx, ny, nz in line
                    if 0 <= nx < size and 0 <= ny < size and 0 <= nz < size]

            if len(line) < 4:
                continue

            # ラインのタイプ判定
            if dz != 0 and dx == 0 and dy == 0:
                line_type = 2 #垂直
            elif dz == 0 and (dx != 0 or dy != 0):
                line_type = 1 #水平
            else:
                line_type = 3 #ななめ

            for i in range(len(line)-3):
                segment = line[i:i+4]
                if (x, y, z) not in segment:
                    continue

                my_count = sum(1 for (nx, ny, nz) in segment if board[nz][ny][nx] == player)
                opp_count = sum(1 for (nx, ny, nz) in segment if board[nz][ny][nx] == opponent)

                results.append((my_count, opp_count, line_type))

        if not results:
            return [(-1, -1, 0)]
        return results


    def simulate_move(self, board, move, player):
        x, y, z = move
        new_board = copy.deepcopy(board)
        new_board[z][y][x] = player
        return new_board

    # 自分の盤面の場合スコアリングして返す
    def evaluate_board(self, board, player, move, flag, round, oppflag):
        #そこに置いたら勝てる→あがり
        if self.check_board_win(board, player) and (round == 0 or oppflag == 1):
            return 200000000
        x, y, z = move
        lines = self.check_line_counts(board, player, 3 - player, move)
        score = 0

        #ダブルリーチ検出
        reach_count = sum(1 for (my, opp, lt) in lines if my == 3 and opp == 0)
        if reach_count >= 2 and round == 0:
            return 40000000 * flag # ダブルリーチ

        for line in lines:
            zs, zo, zt = line

            if zo == 0:
                score += 100 * flag
            else:
                score -= 2000 * flag

            if zs == 3 and round == 0:
                score -= 2000000           
            elif zs == 2:
                score += 2000 * flag
            elif zs == 1:
                score += 100 * flag
            
            #列の向き
            if zt == 1:
                score += 300 * flag
            elif zt == 2:
                score += 20 * flag
            elif zt == 3:
                score += 10 * flag

            if (x == 0 or x == 3) and (y == 0 or y == 3):
                score -= 2000 * flag
            elif x == 0 or x == 3:
                score += 310 * flag
            elif x == 1 or x == 2:
                score += 50 * flag
            if y == 0 or y == 3:
                score += 310 * flag
            elif y == 1 or y == 2:
                score += 50 * flag

            if z == 0:
                score += 120 * flag
            elif z == 1:
                score += 50 * flag


            #自分が置いて相手が上がるのを排除できてない
            #もう一手読む
            if round < 1:
                nextmoves = self.find_valid_moves(board)
                best_score = -9999
                best = None
                for nextmove in nextmoves:
                    new_selfboard = self.simulate_move(board, nextmove, player) #相手が置いたときの盤面
                    score_self = self.evaluate_board(new_selfboard, player, nextmove, 0.5, round + 1, 1- oppflag)
                    new_opponentboard = self.simulate_move(board, nextmove, 3 - player) #相手が置いたときの盤面
                    score_opponent = self.evaluate_board(new_opponentboard, 3 - player, nextmove, 0.5, round + 1, 1 - oppflag)
                    if score_self > best_score:
                        best_score = score_self
                    if score_opponent > best_score:
                        best_score = score_opponent
                score += best_score                
        return score


    #勝利判定
    def check_board_win(self, board, player):
        for z in range(size):
            for y in range(size):
                for x in range(size):
                    if board[z][y][x] != player:
                        continue
                    for dx, dy, dz in DIRECTIONS:
                        count = 1
                        nx, ny, nz = x+dx, y+dy, z+dz
                        while (
                            0 <= nx < size and
                            0 <= ny < size and
                            0 <= nz < size and
                            board[nz][ny][nx] == player
                        ):
                            count += 1
                            nx += dx; ny += dy; nz += dz
                        if count >= 4:
                            return True
        return False    
        

    def best_move(self, board, player):
        moves = self.find_valid_moves(board)
        best_score = -9999
        best = None
        for move in moves:
            new_selfboard = self.simulate_move(board, move, player) #自分が置いたときの盤面0            
            score_self = self.evaluate_board(new_selfboard, player, move, 1, 0, 0)
            if score_self >= 150000000:
                x, y, z = move
                return (x, y)
            new_opponentboard = self.simulate_move(board, move, 3 - player) #相手が置いたときの盤面
            score_opponent = self.evaluate_board(new_opponentboard, 3 - player, move, 1, 0 , 1)
            if score_self >= 150000000:
                x, y, z = move
                return (x, y)            
            if score_self > score_opponent:
                score = score_self
            else:
                score = score_opponent
            if score > best_score:
                best_score = score
                best = move
        x, y, z = best
        return (x, y)

        
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
    print("AIが選んだ手:", move)
