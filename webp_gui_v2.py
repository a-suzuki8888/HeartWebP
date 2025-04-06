import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# === WebP変換関数 ===
def convert_images_to_webp(input_folder, output_folder, backup_folder=None, quality=80, alpha_q=100, method=6, multithread=True):
    supported_exts = ('.jpg', '.jpeg', '.png')
    converted = 0
    cwebp_path = "/opt/homebrew/bin/cwebp"

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(supported_exts):
                input_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, input_folder)
                out_dir = os.path.join(output_folder, rel_path)
                os.makedirs(out_dir, exist_ok=True)
                output_path = os.path.join(out_dir, os.path.splitext(file)[0] + '.webp')

                command = [
                    cwebp_path,
                    '-q', str(quality),
                    '-alpha_q', str(alpha_q),
                    '-m', str(method)
                ]
                if multithread:
                    command.append('-mt')
                command.extend([input_path, '-o', output_path])

                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                converted += 1

                if backup_folder:
                    backup_dir = os.path.join(backup_folder, rel_path)
                    os.makedirs(backup_dir, exist_ok=True)
                    os.rename(input_path, os.path.join(backup_dir, file))

    return converted

# === GUI部分 ===
def select_folder(entry):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry.delete(0, tk.END)
        entry.insert(0, folder_selected)

def start_conversion():
    input_folder = entry_input.get()
    output_folder = entry_output.get() if var_output.get() else input_folder
    backup_folder = entry_backup.get() if var_backup.get() else None

    if not os.path.isdir(input_folder):
        messagebox.showerror("エラー", "変換元フォルダが無効です。")
        return

    if var_output.get() and not os.path.isdir(output_folder):
        messagebox.showerror("エラー", "出力フォルダが無効です。")
        return

    if var_backup.get() and not os.path.isdir(backup_folder):
        messagebox.showerror("エラー", "退避先フォルダが無効です。")
        return

    quality = int(entry_quality.get())
    alpha_q = int(entry_alpha_q.get())
    method = int(entry_method.get())
    multithread = var_multithread.get()

    count = convert_images_to_webp(input_folder, output_folder, backup_folder, quality, alpha_q, method, multithread)
    messagebox.showinfo("完了", f"{count} 件の画像を WebP に変換しました。")

    if var_finder.get():
        subprocess.run(["open", output_folder])

root = tk.Tk()
root.title("WebP変換ツール v2 - Heart Stack")

# === フォルダ指定 ===
tk.Label(root, text="変換元フォルダ:").grid(row=0, column=0, sticky='e')
entry_input = tk.Entry(root, width=40)
entry_input.grid(row=0, column=1)
tk.Button(root, text="選択", command=lambda: select_folder(entry_input)).grid(row=0, column=2)

var_output = tk.BooleanVar()
tk.Checkbutton(root, text="別の出力先を使う", variable=var_output).grid(row=1, column=0, sticky='e')
entry_output = tk.Entry(root, width=40)
entry_output.grid(row=1, column=1)
tk.Button(root, text="選択", command=lambda: select_folder(entry_output)).grid(row=1, column=2)

var_backup = tk.BooleanVar()
tk.Checkbutton(root, text="元画像を退避する", variable=var_backup).grid(row=2, column=0, sticky='e')
entry_backup = tk.Entry(root, width=40)
entry_backup.grid(row=2, column=1)
tk.Button(root, text="選択", command=lambda: select_folder(entry_backup)).grid(row=2, column=2)

# === パラメータ設定 ===
tk.Label(root, text="品質 -q:").grid(row=3, column=0, sticky='e')
entry_quality = tk.Entry(root)
entry_quality.insert(0, "80")
entry_quality.grid(row=3, column=1, sticky='w')

tk.Label(root, text="透過品質 -alpha_q:").grid(row=4, column=0, sticky='e')
entry_alpha_q = tk.Entry(root)
entry_alpha_q.insert(0, "100")
entry_alpha_q.grid(row=4, column=1, sticky='w')

tk.Label(root, text="圧縮メソッド -m:").grid(row=5, column=0, sticky='e')
entry_method = tk.Entry(root)
entry_method.insert(0, "6")
entry_method.grid(row=5, column=1, sticky='w')

var_multithread = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="マルチスレッド処理（-mt）", variable=var_multithread).grid(row=6, columnspan=2, sticky='w', padx=10)

var_finder = tk.BooleanVar()
tk.Checkbutton(root, text="Finderで開く", variable=var_finder).grid(row=7, columnspan=2, sticky='w', padx=10)

# === 実行ボタン ===
tk.Button(root, text="WebPに変換", command=start_conversion, bg="#f08080", fg="white").grid(row=8, columnspan=3, pady=10)

root.mainloop()
