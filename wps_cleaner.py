import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def parse_version(version_str):
    """将版本字符串解析为整数元组，以进行准确的大小比较"""
    try:
        return tuple(int(x) for x in version_str.split('.'))
    except ValueError:
        return (0,)

class WPSCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WPS 拓展包清理工具")
        self.root.geometry("650x500")
        self.root.configure(padx=15, pady=15)
        
        self.target_dir = tk.StringVar()
        default_path = os.path.expandvars(r"%APPDATA%\kingsoft\wps\addons\pool\win-i386")
        self.target_dir.set(default_path)
            
        self.redundant_paths = []
        self.create_widgets()

    def create_widgets(self):
        # 路径选择区
        path_frame = tk.Frame(self.root)
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(path_frame, text="目标目录: ", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
        tk.Entry(path_frame, textvariable=self.target_dir, font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        tk.Button(path_frame, text="浏览...", command=self.browse_dir, font=("Microsoft YaHei", 10), width=8).pack(side=tk.LEFT)
        
        # 按钮控制区
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Button(btn_frame, text="扫描冗余目录", command=self.scan_folders, bg="#f0f0f0", font=("Microsoft YaHei", 10, "bold"), width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.clean_btn = tk.Button(btn_frame, text="一键清理", command=self.clean_folders, bg="#ff4d4f", fg="white", font=("Microsoft YaHei", 10, "bold"), width=15, state=tk.DISABLED)
        self.clean_btn.pack(side=tk.LEFT)
        
        # 日志区
        tk.Label(self.root, text="运行日志:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.log_area = scrolledtext.ScrolledText(self.root, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", height=15)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        self.log("欢迎使用 WPS 拓展包清理工具。")
        self.log("该程序将自动比较插件的版本号，并仅保留最新版本。")
        self.log(f"默认路径: {self.target_dir.get()}")
        self.log("请确认目录后，点击【扫描冗余目录】开始。\n")

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def browse_dir(self):
        path = filedialog.askdirectory(initialdir=self.target_dir.get(), title="选择 WPS win-i386 文件夹")
        if path:
            self.target_dir.set(os.path.normpath(path))

    def scan_folders(self):
        directory = self.target_dir.get()
        if not os.path.isdir(directory):
            messagebox.showerror("错误", "指定的目录不存在！")
            return

        self.log(f"\n开始扫描: {directory} ...")
        self.clean_btn.config(state=tk.DISABLED)
        self.redundant_paths.clear()
        
        # 正则表达式提取名称和版本号，例如: advancedexportpdfv2_3.1.0.35141
        pattern = re.compile(r"^(.*)_([\d\.]+)$")
        
        groups = {}
        items = os.listdir(directory)
        
        for item in items:
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                match = pattern.match(item)
                if match:
                    base_name = match.group(1)
                    version = match.group(2)
                    if base_name not in groups:
                        groups[base_name] = []
                    groups[base_name].append((version, item))

        total_scanned = 0
        
        for base_name, versions in groups.items():
            if len(versions) > 1:
                # 按照版本号倒序排序 (第一项为最新版)
                versions.sort(key=lambda x: parse_version(x[0]), reverse=True)
                
                latest_version, latest_folder = versions[0]
                self.log(f"\n发现 [{base_name}] 的多个版本:")
                self.log(f"  -> 最新保留: {latest_folder}")
                
                for old_version, old_folder in versions[1:]:
                    old_path = os.path.join(directory, old_folder)
                    self.redundant_paths.append(old_path)
                    self.log(f"  -> 将要删除: {old_folder}")
                    total_scanned += 1

        if total_scanned == 0:
            self.log("\n扫描完成：未发现需要清理的冗余旧版本文件夹。")
        else:
            self.log(f"\n扫描完成：共发现 {total_scanned} 个冗余文件夹可以清理。")
            self.clean_btn.config(state=tk.NORMAL)

    def clean_folders(self):
        if not self.redundant_paths:
            return
            
        confirm = messagebox.askyesno("确认清理", f"即将永久删除 {len(self.redundant_paths)} 个冗余文件夹，此操作不可撤销，是否继续？")
        if not confirm:
            self.log("清理已取消。")
            return
            
        self.log("\n开始清理...")
        deleted_count = 0
        error_count = 0
        
        for path in self.redundant_paths:
            try:
                shutil.rmtree(path)
                self.log(f"已删除: {os.path.basename(path)}")
                deleted_count += 1
            except Exception as e:
                self.log(f"删除失败: {os.path.basename(path)} - 错误: {str(e)}")
                error_count += 1
                
        self.log(f"\n清理完成！成功删除 {deleted_count} 个文件夹。")
        if error_count > 0:
            self.log(f"其中 {error_count} 个文件夹由于权限或占用问题未能删除。")
            
        self.redundant_paths.clear()
        self.clean_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    # 解决部分高DPI屏幕模糊问题
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = WPSCleanerApp(root)
    root.mainloop()
