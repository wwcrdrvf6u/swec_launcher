import os
import re
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from ctypes import windll

class ConfigEditor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("希沃视频展台启动器设置")
        self.window.geometry("800x450")  # 调整窗口尺寸
        
        # 配置参数
        self.base_path = "C:\\Program Files (x86)\\Seewo\\EasiCamera"
        self.version_pattern = re.compile("EasiCamera_(\d+\.\d+\.\d+\.\d+)$")
        self.versions = []
        
        # 初始化界面
        self.create_widgets()
        self.load_config()
        
        # Windows高DPI适配
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 路径选择部分
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="安装根目录:").pack(side=tk.LEFT)
        self.path_entry = ttk.Entry(path_frame, width=60)
        self.path_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        ttk.Button(
            path_frame,
            text="浏览...",
            command=self.browse_directory
        ).pack(side=tk.LEFT)
        
        # 版本扫描部分
        scan_frame = ttk.Frame(main_frame)
        scan_frame.pack(fill=tk.X, pady=10)
        
        self.scan_btn = ttk.Button(
            scan_frame,
            text="扫描版本",
            command=self.scan_versions,
            width=15
        )
        self.scan_btn.pack(side=tk.LEFT)
        self.scan_status = ttk.Label(scan_frame, text="就绪")
        self.scan_status.pack(side=tk.LEFT, padx=10)
        
        # 版本列表
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.version_list = ttk.Treeview(
            list_frame,
            columns=("version", "path"),
            show="headings",
            height=8,  # 增加列表高度
            selectmode="browse"
        )
        self.version_list.heading("version", text="版本号", anchor=tk.W)
        self.version_list.heading("path", text="完整路径", anchor=tk.W)
        self.version_list.column("version", width=150, anchor=tk.W)
        self.version_list.column("path", width=500, anchor=tk.W)
        
        # 滚动条
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.version_list.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.version_list.xview)
        self.version_list.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.version_list.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # 操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(
            btn_frame,
            text="保存配置",
            command=self.save_config,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=10)
        ttk.Button(
            btn_frame,
            text="退出",
            command=self.window.destroy
        ).pack(side=tk.LEFT, padx=10)
        ttk.Button(
            btn_frame,
            text="关于", 
            command=self.show_about
        ).pack(side=tk.LEFT, padx=10)
        
        # 配置样式
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#0078D4")

    def show_about(self):
        """显示关于信息"""
        about_text = (
            "希沃视频展台启动器配置工具\n\n"
            "版本：1.1.0\n"
            "关于：\n"
            "- 优点：我写的\n"
            "- 缺点：我写的\n"
            "- 可以自行设置启动版本（qwq）\n\n"
            "提示：请确保已正确安装视频展台程序"
        )
        messagebox.showinfo("关于本程序", about_text)

    def browse_directory(self):
        """选择安装目录"""
        path = filedialog.askdirectory(
            initialdir=self.base_path if os.path.exists(self.base_path) else "/",
            title="选择安装根目录"
        )
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.scan_versions()

    def validate_version(self, dir_path):
        """验证版本目录有效性"""
        exe_path = os.path.join(dir_path, "Main", "EasiCamera.exe")
        return os.path.isfile(exe_path)

    def natural_sort_key(self, version_str):
        """自然排序算法"""
        return [int(part) for part in version_str.split('.')]

    def scan_versions(self):
        """执行版本扫描"""
        base_path = self.path_entry.get().strip()
        self.versions.clear()
        self.version_list.delete(*self.version_list.get_children())
        
        if not base_path:
            messagebox.showwarning("提示", "请先选择安装根目录")
            return
            
        self.scan_btn.config(state=tk.DISABLED)
        self.scan_status.config(text="扫描中...")
        self.window.update()
        
        try:
            if not os.path.exists(base_path):
                raise FileNotFoundError(f"路径不存在: {base_path}")
                
            if not os.access(base_path, os.R_OK):
                raise PermissionError(f"无读取权限: {base_path}")
            
            # 扫描有效版本目录
            for entry in os.listdir(base_path):
                entry_path = os.path.join(base_path, entry)
                if os.path.isdir(entry_path):
                    match = self.version_pattern.match(entry)
                    if match and self.validate_version(entry_path):
                        version = match.group(1)
                        exe_path = os.path.join(entry_path, "Main", "EasiCamera.exe")
                        self.versions.append({
                            "version": version,
                            "exe_path": exe_path,
                            "dir_name": entry
                        })
            
            # 按版本号降序排序
            self.versions.sort(
                key=lambda x: self.natural_sort_key(x["version"]),
                reverse=True
            )
            
            # 更新列表
            for ver in self.versions:
                self.version_list.insert("", "end", values=(ver["version"], ver["exe_path"]))
            
            self.scan_status.config(text=f"找到 {len(self.versions)} 个有效版本")
            
        except Exception as e:
            messagebox.showerror("扫描错误", str(e))
        finally:
            self.scan_btn.config(state=tk.NORMAL)
            self.scan_status.config(text="就绪")

    def load_config(self):
        """加载现有配置"""
        config_file = "config.xml"
        if not os.path.exists(config_file):
            return
        
        try:
            tree = ET.parse(config_file)
            root = tree.getroot()
            
            # 读取配置
            install_path = root.findtext("InstallPath", "").strip()
            version = root.findtext("Version", "").strip()
            
            if install_path:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, install_path)
                self.scan_versions()
                
                # 自动选择配置版本
                if version:
                    for idx, ver in enumerate(self.versions):
                        if ver["version"] == version:
                            self.version_list.selection_set(self.version_list.get_children()[idx])
                            break
        
        except ET.ParseError:
            messagebox.showerror("配置错误", "配置文件格式不正确，已重置")
        except Exception as e:
            messagebox.showerror("加载错误", f"配置加载失败: {str(e)}")

    def save_config(self):
        """保存配置到XML"""
        # 获取输入
        base_path = self.path_entry.get().strip()
        selected = self.version_list.selection()
        
        # 输入验证
        error_msgs = []
        if not base_path:
            error_msgs.append("必须指定安装根目录")
        if not selected:
            error_msgs.append("请选择一个版本")
        if error_msgs:
            messagebox.showerror("保存错误", "\n".join(error_msgs))
            return
            
        # 获取选中版本
        item = self.version_list.item(selected[0])
        version = item["values"][0]
        exe_path = item["values"][1]
        
        # 二次验证
        if not os.path.exists(exe_path):
            messagebox.showerror("路径错误", f"主程序不存在:\n{exe_path}")
            return
        
        # 构建XML
        root = ET.Element("Configuration")
        ET.SubElement(root, "InstallPath").text = base_path
        ET.SubElement(root, "Version").text = version
        ET.SubElement(root, "ExecutablePath").text = exe_path
        
        try:
            tree = ET.ElementTree(root)
            tree.write("config.xml", encoding="utf-8", xml_declaration=True)
            messagebox.showinfo("保存成功", "配置已保存，启动器将使用以下路径：\n" + exe_path)
        except Exception as e:
            messagebox.showerror("保存失败", f"文件写入失败: {str(e)}")

if __name__ == "__main__":
    app = ConfigEditor()
    app.window.mainloop()