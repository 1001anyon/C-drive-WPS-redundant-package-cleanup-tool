import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import datetime

LANGUAGES = {
    'zh_CN': {
        'title': "WPS 拓展包清理工具",
        'target_dir': "目标目录:",
        'browse': "浏览...",
        'scan': "扫描冗余目录",
        'clean': "一键清理已选",
        'log_title': "运行日志:",
        'list_title': "版本对比列表 ( 选中 [X] 标红=删除，未选 [ ] 标绿=保留 ) :",
        'welcome': "欢迎使用 WPS 拓展包清理工具。\n该程序将读取并比较同名插件的版本号，最新版默认保留，旧版默认将被删除。\n您可以直接在下面的列表中点击，直接修改哪些要保留、哪些要删除。\n",
        'error': "错误",
        'error_dir': "指定的目录不存在！",
        'scan_start': "\n开始扫描: {} ...",
        'found_group': "-> 发现组件 [{}] 的历史版本冲突:",
        'latest_keep': "  -> [最新] {} (修改时间: {})",
        'old_find': "  -> [旧版] {} (修改时间: {})",
        'no_redundant': "\n扫描完成：未发现任何多版本冗余的旧文件夹。",
        'scan_done': "\n扫描完成：共发现 {} 个组件存在不同版本，已在列表中列出供您核对即可。",
        'confirm_title': "确认清理",
        'confirm_msg': "即将永久删除列表中勾选的 {} 个文件夹，此操作不可撤销，是否继续？",
        'cancel': "清理已取消。",
        'clean_start': "\n开始清理...",
        'del_success': "已删除: {}",
        'del_fail': "删除失败: {} - 错误: {}",
        'clean_done': "\n清理完成！成功删除 {} 个文件夹。",
        'clean_err_cnt': "其中 {} 个文件夹未能删除。",
        'select_all': "全选(全删)",
        'deselect_all': "全不选(全留)",
        'mod_date_label': "修改时间",
        'latest_tag': "最新版",
        'old_tag': "旧版本"
    },
    'zh_TW': {
        'title': "WPS 擴展包清理工具",
        'target_dir': "目標目錄:",
        'browse': "瀏覽...",
        'scan': "掃描冗餘目錄",
        'clean': "一鍵清理已選",
        'log_title': "運行日誌:",
        'list_title': "版本對比列表 ( 選中 [X] 標紅=刪除，未選 [ ] 標綠=保留 ) :",
        'welcome': "歡迎使用 WPS 擴展包清理工具。\n該程式將讀取並比較同名插件的版本號，最新版預設保留，舊版預設將被刪除。\n您可以直接在下面的列表中點擊，直接修改哪些要保留、哪些要刪除。\n",
        'error': "錯誤",
        'error_dir': "指定的目錄不存在！",
        'scan_start': "\n開始掃描: {} ...",
        'found_group': "-> 發現組件 [{}] 的歷史版本衝突:",
        'latest_keep': "  -> [最新] {} (修改時間: {})",
        'old_find': "  -> [舊版] {} (修改時間: {})",
        'no_redundant': "\n掃描完成：未發現任何多版本冗餘的舊資料夾。",
        'scan_done': "\n掃描完成：共發現 {} 個組件存在不同版本，已在列表中列出供您核對即可。",
        'confirm_title': "確認清理",
        'confirm_msg': "即將永久刪除列表中勾選的 {} 個資料夾，此操作不可撤銷，是否繼續？",
        'cancel': "清理已取消。",
        'clean_start': "\n開始清理...",
        'del_success': "已刪除: {}",
        'del_fail': "刪除失敗: {} - 錯誤: {}",
        'clean_done': "\n清理完成！成功刪除 {} 個資料夾。",
        'clean_err_cnt': "其中 {} 個資料夾未能刪除。",
        'select_all': "全選(全刪)",
        'deselect_all': "全不選(全留)",
        'mod_date_label': "修改時間",
        'latest_tag': "最新版",
        'old_tag': "舊版本"
    },
    'en_US': {
        'title': "WPS Addons Cleaner",
        'target_dir': "Target Dir:",
        'browse': "Browse...",
        'scan': "Scan Redundant",
        'clean': "Clean Selected",
        'log_title': "Log:",
        'list_title': "Version Compare ( [X] Red = Delete, [ ] Green = Keep ) :",
        'welcome': "Welcome to WPS Addons Cleaner.\nWe compare plugin version numbers. The latest is kept by default, older ones are marked for deletion.\nYou can click in the list below to toggle keep/delete states freely.\n",
        'error': "Error",
        'error_dir': "The specified directory does not exist!",
        'scan_start': "\nScanning: {} ...",
        'found_group': "-> Found multiple versions for [{}]:",
        'latest_keep': "  -> [Latest] {} (Mod: {})",
        'old_find': "  -> [Old] {} (Mod: {})",
        'no_redundant': "\nScan complete: No redundant old folders found.",
        'scan_done': "\nScan complete: Found {} component(s) with redundancies. All versions listed below.",
        'confirm_title': "Confirm Clean",
        'confirm_msg': "You are about to permanently delete {} selected folders. Continue?",
        'cancel': "Clean cancelled.",
        'clean_start': "\nStarting cleanup...",
        'del_success': "Deleted: {}",
        'del_fail': "Failed to delete: {} - Error: {}",
        'clean_done': "\nCleanup finished! Successfully deleted {} folders.",
        'clean_err_cnt': "Failed to delete {} folders.",
        'select_all': "Sel. All (Del)",
        'deselect_all': "Desel. All (Keep)",
        'mod_date_label': "Mod Date",
        'latest_tag': "Latest",
        'old_tag': "Old"
    }
}

def parse_version(version_str):
    try:
        return tuple(int(x) for x in version_str.split('.'))
    except ValueError:
        return (0,)

def get_mod_date(path):
    try:
        mtime = os.path.getmtime(path)
        return datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
    except Exception:
        return "Unknown"

class CheckListbox(tk.Listbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonRelease-1>", self._toggle)
        self.items_data = []

    def _toggle(self, event):
        idx = self.nearest(event.y)
        if idx >= 0:
            item = self.get(idx)
            if item.startswith("[X]"):
                self.delete(idx)
                self.insert(idx, "[ ]" + item[3:])
                self.itemconfig(idx, fg='#0B8A1C') # Green for keep
                self.items_data[idx]['selected'] = False
            elif item.startswith("[ ]"):
                self.delete(idx)
                self.insert(idx, "[X]" + item[3:])
                self.itemconfig(idx, fg='#D93025') # Red for delete
                self.items_data[idx]['selected'] = True
            
            self.event_generate("<<ListboxSelect>>")

    def add_item(self, text, path, selected=True):
        prefix = "[X] " if selected else "[ ] "
        self.insert(tk.END, prefix + text)
        idx = self.size() - 1
        self.itemconfig(idx, fg='#D93025' if selected else '#0B8A1C')
        self.items_data.append({'path': path, 'selected': selected})

    def get_selected_paths(self):
        return [item['path'] for item in self.items_data if item['selected']]
        
    def clear(self):
        self.delete(0, tk.END)
        self.items_data.clear()

    def set_all(self, state):
        for idx in range(self.size()):
            item = self.get(idx)
            self.delete(idx)
            prefix = "[X] " if state else "[ ] "
            self.insert(idx, prefix + item[4:])
            self.itemconfig(idx, fg='#D93025' if state else '#0B8A1C')
            self.items_data[idx]['selected'] = state
        self.event_generate("<<ListboxSelect>>")


class WPSCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x750")
        self.root.configure(padx=20, pady=20)
        
        self.target_dir = tk.StringVar()
        default_path = os.path.expandvars(r"%APPDATA%\kingsoft\wps\addons\pool\win-i386")
        self.target_dir.set(default_path)
            
        self.text_target_dir = tk.StringVar()
        self.text_browse = tk.StringVar()
        self.text_scan = tk.StringVar()
        self.text_clean = tk.StringVar()
        self.text_log_title = tk.StringVar()
        self.text_list_title = tk.StringVar()
        self.text_sel_all = tk.StringVar()
        self.text_desel_all = tk.StringVar()
        
        self.current_lang = 'zh_CN'
        self.create_widgets()
        self.update_language()
        
        t = LANGUAGES[self.current_lang]
        self.log(t['welcome'])

    def update_language(self, event=None):
        lang_map = {'简体中文': 'zh_CN', '繁體中文': 'zh_TW', 'English': 'en_US'}
        choice = self.lang_combo.get()
        self.current_lang = lang_map.get(choice, 'zh_CN')
        
        t = LANGUAGES[self.current_lang]
        self.root.title(t['title'])
        self.text_target_dir.set(t['target_dir'])
        self.text_browse.set(t['browse'])
        self.text_scan.set(t['scan'])
        self.text_clean.set(t['clean'])
        self.text_log_title.set(t['log_title'])
        self.text_list_title.set(t['list_title'])
        self.text_sel_all.set(t['select_all'])
        self.text_desel_all.set(t['deselect_all'])

    def create_widgets(self):
        font_main = ("Microsoft YaHei", 10)
        
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(top_frame, textvariable=self.text_target_dir, font=font_main).pack(side=tk.LEFT)
        tk.Entry(top_frame, textvariable=self.target_dir, font=font_main).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        tk.Button(top_frame, textvariable=self.text_browse, command=self.browse_dir, font=font_main, width=10).pack(side=tk.LEFT)
        
        ctrl_frame = tk.Frame(self.root)
        ctrl_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.lang_combo = ttk.Combobox(ctrl_frame, values=['简体中文', '繁體中文', 'English'], state='readonly', width=12, font=font_main)
        self.lang_combo.set('简体中文')
        self.lang_combo.bind('<<ComboboxSelected>>', self.update_language)
        self.lang_combo.pack(side=tk.RIGHT)
        
        tk.Button(ctrl_frame, textvariable=self.text_scan, command=self.scan_folders, bg="#f0f0f0", font=("Microsoft YaHei", 10, "bold"), width=15).pack(side=tk.LEFT, padx=(0, 10))
        self.clean_btn = tk.Button(ctrl_frame, textvariable=self.text_clean, command=self.clean_folders, bg="#ff4d4f", fg="white", font=("Microsoft YaHei", 10, "bold"), width=15, state=tk.DISABLED)
        self.clean_btn.pack(side=tk.LEFT)
        
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        list_header = tk.Frame(list_frame)
        list_header.pack(fill=tk.X, pady=(0, 5))
        tk.Label(list_header, textvariable=self.text_list_title, font=("Microsoft YaHei", 10, "bold")).pack(side=tk.LEFT)
        tk.Button(list_header, textvariable=self.text_desel_all, command=lambda: self.checklist.set_all(False), font=font_main).pack(side=tk.RIGHT, padx=5)
        tk.Button(list_header, textvariable=self.text_sel_all, command=lambda: self.checklist.set_all(True), font=font_main).pack(side=tk.RIGHT)
        
        list_scroll = tk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.checklist = CheckListbox(list_frame, font=("Consolas", 10), selectbackground="#e0e0e0", selectforeground="black", height=10, yscrollcommand=list_scroll.set)
        self.checklist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.checklist.bind("<<ListboxSelect>>", self.check_clean_btn_state)
        list_scroll.config(command=self.checklist.yview)
        
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(log_frame, textvariable=self.text_log_title, font=font_main).pack(anchor=tk.W, pady=(0, 5))
        self.log_area = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", height=8)
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def browse_dir(self):
        path = filedialog.askdirectory(initialdir=self.target_dir.get(), title="Select Directory")
        if path:
            self.target_dir.set(os.path.normpath(path))

    def check_clean_btn_state(self, event=None):
        if self.checklist.get_selected_paths():
            self.clean_btn.config(state=tk.NORMAL)
        else:
            self.clean_btn.config(state=tk.DISABLED)

    def scan_folders(self):
        t = LANGUAGES[self.current_lang]
        directory = self.target_dir.get()
        if not os.path.isdir(directory):
            messagebox.showerror(t['error'], t['error_dir'])
            return

        self.log(t['scan_start'].format(directory))
        self.clean_btn.config(state=tk.DISABLED)
        self.checklist.clear()
        
        pattern = re.compile(r"^(.*)_([\d\.]+)$")
        groups = {}
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                match = pattern.match(item)
                if match:
                    base_name = match.group(1)
                    version = match.group(2)
                    if base_name not in groups:
                        groups[base_name] = []
                    groups[base_name].append((version, item))

        conflict_groups = 0
        total_redundant = 0
        
        for base_name, versions in groups.items():
            if len(versions) > 1:
                versions.sort(key=lambda x: parse_version(x[0]), reverse=True)
                conflict_groups += 1
                self.log(t['found_group'].format(base_name))
                
                for i, (version, folder) in enumerate(versions):
                    is_latest = (i == 0)
                    path = os.path.join(directory, folder)
                    mod_date = get_mod_date(path)
                    
                    if is_latest:
                        self.log(t['latest_keep'].format(folder, mod_date))
                        tag_text = t['latest_tag']
                        will_delete = False
                    else:
                        self.log(t['old_find'].format(folder, mod_date))
                        tag_text = t['old_tag']
                        will_delete = True
                        total_redundant += 1
                        
                    # Build display text
                    text_display = f"{folder:<36} {tag_text}  [{t['mod_date_label']}: {mod_date}]"
                    self.checklist.add_item(text_display, path, selected=will_delete)

        if conflict_groups == 0:
            self.log(t['no_redundant'])
        else:
            self.log(t['scan_done'].format(conflict_groups))
            self.clean_btn.config(state=tk.NORMAL)

    def clean_folders(self):
        t = LANGUAGES[self.current_lang]
        paths_to_delete = self.checklist.get_selected_paths()
        
        if not paths_to_delete:
            return
            
        confirm = messagebox.askyesno(t['confirm_title'], t['confirm_msg'].format(len(paths_to_delete)))
        if not confirm:
            self.log(t['cancel'])
            return
            
        self.log(t['clean_start'])
        deleted_count = 0
        error_count = 0
        
        for path in paths_to_delete:
            try:
                shutil.rmtree(path)
                self.log(t['del_success'].format(os.path.basename(path)))
                deleted_count += 1
            except Exception as e:
                self.log(t['del_fail'].format(os.path.basename(path), str(e)))
                error_count += 1
                
        self.log(t['clean_done'].format(deleted_count))
        if error_count > 0:
            self.log(t['clean_err_cnt'].format(error_count))
            
        self.scan_folders()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = WPSCleanerApp(root)
    root.mainloop()
