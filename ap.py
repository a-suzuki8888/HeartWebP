import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_images_to_webp(folder_path, quality=80, alpha_q=100, method=6, multithread=True):
    supported_exts = ('.jpg', '.jpeg', '.png')
    converted = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(supported_exts):
                input_path = os.path.join(root, file)
                output_path = os.path.splitext(input_path)[0] + '.webp'

                command = [
                    'cwebp',
                    '-q', str(quality),
                    '-alpha_q', str(alpha_q),
                    '-m', str(method)
                ]
                if multithread:
                    command.append('-mt')
                command.extend([input_path, '-o', output_path])

                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                converted += 1
    return converted

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_folder.delete(0, tk.END)
        entry_folder.insert(0, folder_selected)

def start_conversion():
    folder_path = entry_folder.get()
    if not os.path.isdir(folder_path):
        messagebox.showerror("エラー", "有効なフォルダを選択してください。")
        return

    quality = int(entry_quality.get())
    alpha_q = int(entry_alpha_q.get())
    method = int(entry_method.get())
    multithread = var_multithread.get()

    count = convert_images_to_webp(folder_path, quality, alpha_q, method, multithread)
    messagebox.showinfo("完了", f"{count} 件の画像を WebP に変換しました。")

# GUI構築
root = tk.Tk()
root.title("WebP変換ツール - Heart Stack")

# フォルダ選択
tk.Label(root, text="変換フォルダ:").grid(row=0, column=0, sticky='e')
entry_folder = tk.Entry(root, width=40)
entry_folder.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="選択", command=select_folder).grid(row=0, column=2, padx=5)

# 設定
tk.Label(root, text="品質 -q (推奨80〜90):").grid(row=1, column=0, sticky='e')
entry_quality = tk.Entry(root)
entry_quality.insert(0, "80")
entry_quality.grid(row=1, column=1, pady=2, sticky='w')

tk.Label(root, text="透過品質 -alpha_q (推奨100):").grid(row=2, column=0, sticky='e')
entry_alpha_q = tk.Entry(root)
entry_alpha_q.insert(0, "100")
entry_alpha_q.grid(row=2, column=1, pady=2, sticky='w')

tk.Label(root, text="圧縮メソッド -m (0〜6):").grid(row=3, column=0, sticky='e')
entry_method = tk.Entry(root)
entry_method.insert(0, "6")
entry_method.grid(row=3, column=1, pady=2, sticky='w')

var_multithread = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="マルチスレッド処理 (-mt)", variable=var_multithread).grid(row=4, columnspan=2, sticky='w', padx=10)

# ボタン
tk.Button(root, text="WebPに変換", command=start_conversion, bg="#5bc0de").grid(row=5, columnspan=3, pady=10)

root.mainloop()
