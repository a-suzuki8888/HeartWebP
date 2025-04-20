import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

# === WebP変換関数 ===
def convert_images_to_webp_from_list(file_list, output_folder, backup_folder=None, quality=80, alpha_q=100, method=6, multithread=True, preserve_structure=True):
    converted = 0
    cwebp_path = "/opt/homebrew/bin/cwebp"

    for file_path in file_list:
        if not os.path.isfile(file_path):
            continue
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png'):
            continue

        if preserve_structure:
            # フォルダ構造を保持する場合
            rel_path = os.path.relpath(os.path.dirname(file_path), os.path.commonpath(file_list))
            out_dir = os.path.join(output_folder, rel_path)
        else:
            # フォルダ構造を保持しない場合（ドラッグ&ドロップ時）
            out_dir = output_folder

        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, os.path.splitext(os.path.basename(file_path))[0] + '.webp')

        command = [
            cwebp_path,
            '-q', str(quality),
            '-alpha_q', str(alpha_q),
            '-m', str(method)
        ]
        if multithread:
            command.append('-mt')
        command.extend([file_path, '-o', output_path])

        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        converted += 1

        if backup_folder:
            if preserve_structure:
                backup_dir = os.path.join(backup_folder, rel_path)
            else:
                backup_dir = backup_folder
            os.makedirs(backup_dir, exist_ok=True)
            os.rename(file_path, os.path.join(backup_dir, os.path.basename(file_path)))

    return converted

# === ドラッグ&ドロップ対応 ===
def drop(event):
    dropped_files = root.tk.splitlist(event.data)
    
    # 対象画像のみ抽出（安全のため）
    image_files = [
        f for f in dropped_files
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    if not image_files:
        messagebox.showwarning("警告", "変換可能な画像ファイルが見つかりませんでした。")
        return

    # 出力・退避先などの取得
    output_folder = entry_output.get() if var_output.get() else os.path.dirname(image_files[0])
    backup_folder = entry_backup.get() if var_backup.get() else None
    quality = int(entry_quality.get())
    alpha_q = int(entry_alpha_q.get())
    method = int(entry_method.get())

    # ドラッグ&ドロップ時は常にマルチスレッド無効
    multithread = False

    # 変換実行（フォルダ構造を保持しない）
    count = convert_images_to_webp_from_list(
        image_files,
        output_folder,
        backup_folder,
        quality,
        alpha_q,
        method,
        multithread,
        preserve_structure=False
    )

    # 完了メッセージ
    messagebox.showinfo("完了", f"{count} 件の画像を WebP に変換しました。")

    # Finderで開くオプション
    if var_finder.get():
        subprocess.run(["open", output_folder])

# === 実行ボタンの処理 ===
def start_conversion():
    input_folder = entry_input.get()
    if not input_folder:
        messagebox.showerror("エラー", "変換元フォルダを指定してください。")
        return

    # ファイル一覧取得
    file_list = []
    for root_dir, _, files in os.walk(input_folder):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                file_list.append(os.path.join(root_dir, f))

    if not file_list:
        messagebox.showwarning("変換失敗", "対象画像が見つかりませんでした。")
        return

    # 出力・退避先などの取得
    output_folder = entry_output.get() if var_output.get() else input_folder
    backup_folder = entry_backup.get() if var_backup.get() else None
    quality = int(entry_quality.get())
    alpha_q = int(entry_alpha_q.get())
    method = int(entry_method.get())
    multithread = var_multithread.get()

    # 変換実行（フォルダ構造を保持）
    count = convert_images_to_webp_from_list(
        file_list,
        output_folder,
        backup_folder=backup_folder,
        quality=quality,
        alpha_q=alpha_q,
        method=method,
        multithread=multithread,
        preserve_structure=True
    )

    # Finder で開くオプション
    if var_finder.get():
        subprocess.run(["open", output_folder])

    messagebox.showinfo("変換完了", f"{count} 件の画像を WebP に変換しました！")

# === GUI部分 ===
root = TkinterDnD.Tk()
root.title("💖 HeartWebP v2.1")
root.geometry("600x700")  # 高さを増やす
root.configure(bg="#ffe4e1")

# メインフレーム
main_frame = tk.Frame(root, bg="#ffe4e1")
main_frame.pack(fill="both", expand=True, padx=10, pady=5)

# === フォルダ指定 ===
def select_folder(entry_widget):
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_path)

tk.Label(main_frame, text="変換元フォルダ:", bg="#ffe4e1").grid(row=0, column=0, sticky='e')
entry_input = tk.Entry(main_frame, width=40)
entry_input.grid(row=0, column=1)
tk.Button(main_frame, text="選択", command=lambda: select_folder(entry_input), bg="#ffb6c1").grid(row=0, column=2)

var_output = tk.BooleanVar()
tk.Checkbutton(main_frame, text="別の出力先を使う", variable=var_output, bg="#ffe4e1").grid(row=1, column=0, sticky='e')
entry_output = tk.Entry(main_frame, width=40)
entry_output.grid(row=1, column=1)
tk.Button(main_frame, text="選択", command=lambda: select_folder(entry_output), bg="#ffb6c1").grid(row=1, column=2)

var_backup = tk.BooleanVar()
tk.Checkbutton(main_frame, text="元画像を退避する", variable=var_backup, bg="#ffe4e1").grid(row=2, column=0, sticky='e')
entry_backup = tk.Entry(main_frame, width=40)
entry_backup.grid(row=2, column=1)
tk.Button(main_frame, text="選択", command=lambda: select_folder(entry_backup), bg="#ffb6c1").grid(row=2, column=2)

# === パラメータ設定 ===
tk.Label(main_frame, text="品質 -q:", bg="#ffe4e1").grid(row=3, column=0, sticky='e')
entry_quality = tk.Entry(main_frame)
entry_quality.insert(0, "80")
entry_quality.grid(row=3, column=1, sticky='w')

tk.Label(main_frame, text="透過品質 -alpha_q:", bg="#ffe4e1").grid(row=4, column=0, sticky='e')
entry_alpha_q = tk.Entry(main_frame)
entry_alpha_q.insert(0, "100")
entry_alpha_q.grid(row=4, column=1, sticky='w')

tk.Label(main_frame, text="圧縮メソッド -m:", bg="#ffe4e1").grid(row=5, column=0, sticky='e')
entry_method = tk.Entry(main_frame)
entry_method.insert(0, "6")
entry_method.grid(row=5, column=1, sticky='w')

var_multithread = tk.BooleanVar(value=True)
tk.Checkbutton(main_frame, text="マルチスレッド処理（-mt）", variable=var_multithread, bg="#ffe4e1").grid(row=6, columnspan=2, sticky='w', padx=10)
var_finder = tk.BooleanVar()
tk.Checkbutton(main_frame, text="Finderで開く", variable=var_finder, bg="#ffe4e1").grid(row=7, columnspan=2, sticky='w', padx=10)

# === 実行ボタン ===
tk.Button(main_frame, text="WebPに変換", command=start_conversion, bg="#ff69b4", fg="white", font=('Helvetica', 12, 'bold')).grid(row=8, columnspan=3, pady=10)

# === ドロップエリア ===
drop_frame = tk.Frame(main_frame, bg="#ffc0cb", relief="ridge", bd=2)
drop_frame.grid(row=9, column=0, columnspan=3, sticky="nsew", pady=20, padx=10)
main_frame.grid_rowconfigure(9, weight=1)

drop_label = tk.Label(
    drop_frame,
    text="🎀 ここに画像をドラッグ＆ドロップ！ 🎀\n\n※ドラッグ＆ドロップ時はマルチスレッド処理を行いません",
    bg="#ffc0cb",
    fg="#800000",
    font=('Helvetica', 14, 'bold'),
    height=8
)
drop_label.pack(fill="both", expand=True)
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', drop)

root.mainloop()

