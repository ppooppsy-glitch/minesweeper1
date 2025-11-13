#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows용 파이썬 지뢰찾기 (tkinter)
사용법:
    1) Python 3.x 설치 (권장: 3.7+)
    2) 파일을 minesweeper.py 로 저장
    3) 명령 프롬프트에서: python minesweeper.py
기본 기능:
 - 초급/중급/고급/사용자 지정 난이도
 - 왼쪽 클릭: 오픈
 - 오른쪽 클릭: 깃발 토글
 - 더블클릭(또는 숫자 클릭): 주변 자동 오픈 (주변 깃발 수가 숫자와 같으면)
 - 첫 클릭은 무조건 안전
 - 타이머, 남은 지뢰 표시, 승리/패배 처리
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import sys

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("지뢰찾기")
        # 상태 기본값 (초급)
        self.rows = 9
        self.cols = 9
        self.mines_total = 10

        self.top_frame = tk.Frame(root)
        self.top_frame.pack(padx=6, pady=6, anchor="w")
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(padx=6, pady=(0,6))

        self.create_top_controls()
        self.new_game()

    def create_top_controls(self):
        # 난이도 옵션
        self.difficulty_var = tk.StringVar(value="초급")
        diff_menu = tk.OptionMenu(self.top_frame, self.difficulty_var, "초급", "중급", "고급", "사용자 지정", command=self.change_difficulty)
        diff_menu.config(width=10)
        diff_menu.pack(side=tk.LEFT, padx=(0,6))

        # 리셋 버튼 (스마일)
        self.reset_button = tk.Button(self.top_frame, text="🙂", width=3, command=self.new_game)
        self.reset_button.pack(side=tk.LEFT, padx=(0,6))

        # 지뢰 카운터
        self.mines_label = tk.Label(self.top_frame, text="지뢰: 0", width=12)
        self.mines_label.pack(side=tk.LEFT, padx=(0,6))

        # 타이머
        self.time_label = tk.Label(self.top_frame, text="시간: 0", width=12)
        self.time_label.pack(side=tk.LEFT)

    def change_difficulty(self, choice):
        if choice == "초급":
            self.rows, self.cols, self.mines_total = 9, 9, 10
        elif choice == "중급":
            self.rows, self.cols, self.mines_total = 16, 16, 40
        elif choice == "고급":
            self.rows, self.cols, self.mines_total = 16, 30, 99
        elif choice == "사용자 지정":
            r = simpledialog.askinteger("행", "행 개수 입력 (5-30)", minvalue=5, maxvalue=30, parent=self.root)
            if r is None:
                return
            c = simpledialog.askinteger("열", "열 개수 입력 (5-50)", minvalue=5, maxvalue=50, parent=self.root)
            if c is None:
                return
            max_m = r * c - 1
            m = simpledialog.askinteger("지뢰", f"지뢰 개수 입력 (1-{max_m})", minvalue=1, maxvalue=max_m, parent=self.root)
            if m is None:
                return
            self.rows, self.cols, self.mines_total = r, c, m
        self.new_game()

    def new_game(self):
        # 게임 상태 초기화
        self.first_click = True
        self.game_over = False
        self.flags = 0
        self.revealed_count = 0
        self.start_time = None
        self.timer_job = None

        # 내부 배열
        self.mines = [[False]*self.cols for _ in range(self.rows)]
        self.counts = [[0]*self.cols for _ in range(self.rows)]
        self.revealed = [[False]*self.cols for _ in range(self.rows)]
        self.flagged = [[False]*self.cols for _ in range(self.rows)]

        # UI 초기화
        self.reset_button.config(text="🙂")
        self.update_mines_label()
        self.update_time_label(0)

        # 기존 보드 제거
        for child in self.board_frame.winfo_children():
            child.destroy()

        # 버튼 그리드 생성
        self.buttons = [[None]*self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                b = tk.Button(self.board_frame, width=2, height=1, relief=tk.RAISED, bg="lightgrey", font=("Helvetica", 12, "bold"))
                b.grid(row=r, column=c, padx=0, pady=0, sticky="nsew")
                b.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_left_click(rr, cc))
                # Windows: Button-3 이 우클릭
                b.bind("<Button-3>", lambda e, rr=r, cc=c: self.on_right_click(rr, cc))
                # 더블클릭(빠른 오픈)
                b.bind("<Double-Button-1>", lambda e, rr=r, cc=c: self.on_double_left(rr, cc))
                self.buttons[r][c] = b

        # 그리드 확장 설정
        for c in range(self.cols):
            self.board_frame.columnconfigure(c, weight=1)
        for r in range(self.rows):
            self.board_frame.rowconfigure(r, weight=1)

    def place_mines(self, first_r, first_c):
        # 첫 클릭 위치와 인접 8칸은 제외하고 지뢰 배치 (첫 클릭 안전)
        cells = [(r,c) for r in range(self.rows) for c in range(self.cols)]
        excluded = set()
        for rr in range(first_r-1, first_r+2):
            for cc in range(first_c-1, first_c+2):
                if 0 <= rr < self.rows and 0 <= cc < self.cols:
                    excluded.add((rr,cc))
        candidates = [p for p in cells if p not in excluded]
        # 샘플링
        mines = random.sample(candidates, self.mines_total)
        for (r,c) in mines:
            self.mines[r][c] = True

        # 인접 지뢰 수 계산
        for r in range(self.rows):
            for c in range(self.cols):
                if self.mines[r][c]:
                    self.counts[r][c] = -1
                else:
                    cnt = 0
                    for rr in range(r-1, r+2):
                        for cc in range(c-1, c+2):
                            if 0 <= rr < self.rows and 0 <= cc < self.cols:
                                if self.mines[rr][cc]:
                                    cnt += 1
                    self.counts[r][c] = cnt

    def on_left_click(self, r, c):
        if self.game_over or self.flagged[r][c]:
            return

        if self.first_click:
            self.place_mines(r, c)
            self.first_click = False
            self.start_timer()

        if self.mines[r][c]:
            # 지뢰 밟음
            self.reveal_mine(r, c)
            self.finish_game(False)
            return

        self.reveal_cell(r, c)
        if self.check_win():
            self.finish_game(True)

    def on_right_click(self, r, c):
        if self.game_over or self.revealed[r][c]:
            return
        # 플래그 토글
        self.flagged[r][c] = not self.flagged[r][c]
        b = self.buttons[r][c]
        if self.flagged[r][c]:
            b.config(text="⚑", fg="red")
            self.flags += 1
        else:
            b.config(text="", fg="black")
            self.flags -= 1
        self.update_mines_label()

    def on_double_left(self, r, c):
        # 숫자 칸의 주변 플래그 수가 숫자와 같으면 주변 오픈
        if not self.revealed[r][c] or self.counts[r][c] <= 0 or self.game_over:
            return
        needed = self.counts[r][c]
        flagged = 0
        for rr in range(r-1, r+2):
            for cc in range(c-1, c+2):
                if 0 <= rr < self.rows and 0 <= cc < self.cols:
                    if self.flagged[rr][cc]:
                        flagged += 1
        if flagged == needed:
            for rr in range(r-1, r+2):
                for cc in range(c-1, c+2):
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        if not self.flagged[rr][cc] and not self.revealed[rr][cc]:
                            if self.mines[rr][cc]:
                                self.reveal_mine(rr, cc)
                                self.finish_game(False)
                                return
                            else:
                                self.reveal_cell(rr, cc)
            if self.check_win():
                self.finish_game(True)

    def reveal_cell(self, r, c):
        if self.revealed[r][c] or self.flagged[r][c]:
            return
        b = self.buttons[r][c]
        self.revealed[r][c] = True
        self.revealed_count += 1
        b.config(relief=tk.SUNKEN, bg="white")
        val = self.counts[r][c]
        if val > 0:
            colors = ["", "blue", "green", "red", "darkblue", "darkred", "cyan", "black", "grey"]
            b.config(text=str(val), fg=colors[val] if val < len(colors) else "black")
        else:
            # 0이면 주변 자동 오픈 (재귀)
            for rr in range(r-1, r+2):
                for cc in range(c-1, c+2):
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        if not self.revealed[rr][cc] and not self.flagged[rr][cc]:
                            self.reveal_cell(rr, cc)

    def reveal_mine(self, clicked_r, clicked_c):
        # 모든 지뢰 표시 (클릭한 지뢰는 빨갛게)
        for r in range(self.rows):
            for c in range(self.cols):
                if self.mines[r][c]:
                    b = self.buttons[r][c]
                    if r == clicked_r and c == clicked_c:
                        b.config(text="*", bg="red", fg="black", relief=tk.SUNKEN)
                    else:
                        b.config(text="*", bg="orange", fg="black", relief=tk.SUNKEN)
        self.reset_button.config(text="😵")
        self.game_over = True
        self.stop_timer()

    def check_win(self):
        total_cells = self.rows * self.cols
        return (self.revealed_count == total_cells - self.mines_total)

    def finish_game(self, won):
        self.game_over = True
        self.stop_timer()
        if won:
            self.reset_button.config(text="😎")
            elapsed = int(time.time() - self.start_time) if self.start_time else 0
            messagebox.showinfo("승리!", f"축하합니다! {elapsed}초 걸렸습니다.")
        else:
            messagebox.showinfo("패배", "지뢰를 밟았습니다. 다시 시도하세요.")

    def update_mines_label(self):
        remaining = max(0, self.mines_total - self.flags)
        self.mines_label.config(text=f"지뢰: {remaining}")

    def update_time_label(self, seconds):
        self.time_label.config(text=f"시간: {seconds}")

    def start_timer(self):
        if self.start_time is None:
            self.start_time = time.time()
            self.schedule_timer()

    def schedule_timer(self):
        if self.game_over:
            return
        now = int(time.time() - self.start_time)
        self.update_time_label(now)
        self.timer_job = self.root.after(1000, self.schedule_timer)

    def stop_timer(self):
        if self.timer_job:
            try:
                self.root.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None

def main():
    root = tk.Tk()
    app = Minesweeper(root)
    root.mainloop()

if __name__ == "__main__":
    main()
