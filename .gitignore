#!/usr/bin/env python3
"""
Random Joke Generator (uses external JokeAPI)

Usage:
    1. Install dependencies:
        pip install requests

    2. Run:
        python random_joke_generator.py

This script opens a small Tkinter window with:
 - "Get Joke" button to fetch a random joke from https://v2.jokeapi.dev
 - A text area showing the joke (handles single-line and two-part jokes)
 - "Copy" button to copy the joke to clipboard
 - Basic error handling and retry button if network/API fails
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import threading
import sys

JOKEAPI_URL = "https://v2.jokeapi.dev/joke/Any"
# Avoid potentially offensive categories with blacklistFlags, accept both single & twopart
DEFAULT_PARAMS = {
    "blacklistFlags": "nsfw,religious,political,racist,sexist,explicit",
    # allow either single or twopart
    # (JokeAPI returns type field telling which one)
}

class JokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Joke Generator")
        self.root.geometry("520x300")
        self.root.resizable(False, False)

        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 8))

        self.get_btn = tk.Button(btn_frame, text="Get Joke", command=self.get_joke_thread, width=12)
        self.get_btn.pack(side=tk.LEFT)

        self.copy_btn = tk.Button(btn_frame, text="Copy", command=self.copy_joke, width=8, state=tk.DISABLED)
        self.copy_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_text, width=8)
        self.clear_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.status_label = tk.Label(btn_frame, text="Ready", anchor="w")
        self.status_label.pack(side=tk.LEFT, padx=(12,0))

        self.text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=12, font=("Segoe UI", 10))
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.configure(state=tk.DISABLED)

        # Allow Enter to fetch new joke
        root.bind("<Return>", lambda e: self.get_joke_thread())

    def set_status(self, txt):
        self.status_label.config(text=txt)

    def enable_buttons(self, enabled=True):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.get_btn.config(state=state)
        # copy enabled only if there's text
        self.copy_btn.config(state=tk.NORMAL if enabled and self.has_joke_text() else tk.DISABLED)

    def has_joke_text(self):
        return bool(self.get_text().strip())

    def get_text(self):
        return self.text.get("1.0", tk.END).rstrip("\n")

    def clear_text(self):
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.configure(state=tk.DISABLED)
        self.copy_btn.config(state=tk.DISABLED)
        self.set_status("Cleared")

    def copy_joke(self):
        joke = self.get_text()
        if not joke.strip():
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(joke)
            self.set_status("Copied to clipboard")
        except Exception as e:
            messagebox.showerror("오류", f"클립보드에 복사할 수 없습니다:\n{e}")

    def get_joke_thread(self):
        # run network call on background thread to avoid freezing UI
        thread = threading.Thread(target=self.fetch_and_display_joke, daemon=True)
        thread.start()

    def fetch_and_display_joke(self):
        self.enable_buttons(False)
        self.set_status("Fetching joke...")
        try:
            resp = requests.get(JOKEAPI_URL, params=DEFAULT_PARAMS, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            joke_text = self.render_joke_from_api(data)
            self.display_joke(joke_text)
            self.set_status("Fetched")
        except requests.RequestException as e:
            self.display_joke("")
            self.set_status("Network error")
            # show error and provide retry
            retry = messagebox.askretrycancel("네트워크 오류", f"농담을 가져오지 못했습니다:\n{e}\n\n다시 시도하시겠습니까?")
            if retry:
                self.get_joke_thread()
        except Exception as e:
            self.display_joke("")
            self.set_status("Error")
            messagebox.showerror("오류", f"예상치 못한 오류가 발생했습니다:\n{e}")
        finally:
            self.enable_buttons(True)

    def render_joke_from_api(self, data):
        """
        JokeAPI response structure examples:
            Single:
                { "category": "...", "type": "single", "joke": "...", ... }
            Two-part:
                { "category": "...", "type": "twopart", "setup": "...", "delivery": "...", ... }
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid API response")

        if data.get("error"):
            # API indicates error: return message field or raise
            return f"(API error) {data.get('message', 'Unknown error from API')}"

        typ = data.get("type", "")
        if typ == "single":
            return data.get("joke", "(no joke returned)")
        elif typ == "twopart":
            setup = data.get("setup", "")
            delivery = data.get("delivery", "")
            # Format with a blank line between setup and punchline
            return f"{setup}\n\n{delivery}"
        else:
            # fallback: try text fields
            return data.get("joke") or f"{data.get('setup', '')}\n\n{data.get('delivery', '')}" or str(data)

    def display_joke(self, joke_text):
        # UI updates must be done in main thread
        def _update():
            self.text.configure(state=tk.NORMAL)
            self.text.delete("1.0", tk.END)
            if joke_text:
                self.text.insert(tk.END, joke_text)
                self.copy_btn.config(state=tk.NORMAL)
            else:
                self.text.insert(tk.END, "(농담 없음)")
                self.copy_btn.config(state=tk.DISABLED)
            self.text.configure(state=tk.DISABLED)
        self.root.after(0, _update)


def main():
    # check requests availability
    try:
        import requests  # already imported above; this also ensures module is available
    except Exception:
        print("This program requires the 'requests' package. Install with:\n    pip install requests", file=sys.stderr)
        sys.exit(1)

    root = tk.Tk()
    app = JokeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
