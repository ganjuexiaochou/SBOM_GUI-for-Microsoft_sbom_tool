import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import threading
import os
import sys

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class SbomGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Microsoft SBOM Tool 可视化生成器 (支持软件/IoT/OS)")
        self.root.geometry("800x850") # 再次调大窗口以容纳更详细的提示
        
        self.tool_exe = get_resource_path("sbom-tool-win-x64.exe")
        self.create_widgets()

    def create_widgets(self):
        # --- 必填参数区 ---
        lf_req = tk.LabelFrame(self.root, text="必填参数 (Required)", padx=10, pady=10, font=("Arial", 10, "bold"))
        lf_req.pack(fill="x", padx=10, pady=5)

        self.b_var = tk.StringVar()
        self.add_path_input(
            lf_req, "构建产物路径 (-b):", self.b_var, 
            "软件场景：存放生成的 exe/dll/jar 的目录 (如 dist, build)\n"
            "IoT/OS场景：存放最终固件(.bin/.hex)或系统镜像(.img/.iso)的输出目录"
        )

        self.bc_var = tk.StringVar()
        self.add_path_input(
            lf_req, "构建组件/源码路径 (-bc):", self.bc_var, 
            "软件场景：项目源码根目录 (包含 package.json, pom.xml 等)\n"
            "IoT/OS场景：包含源码、第三方库(third_party)或构建配置(CMake/Yocto)的根目录"
        )

        self.pn_var = tk.StringVar()
        self.add_text_input(
            lf_req, "产品/软件包名称 (-pn):", self.pn_var, 
            "示例：SmartRouter_Firmware 或 Ubuntu_Custom_Image"
        )

        self.pv_var = tk.StringVar()
        self.add_text_input(
            lf_req, "版本号 (-pv):", self.pv_var, 
            "示例：v1.0.0_build20231025"
        )

        self.ps_var = tk.StringVar()
        self.add_text_input(
            lf_req, "供应商/厂商名称 (-ps):", self.ps_var, 
            "示例：MyIoTCompany 或 ACME_Corp"
        )

        # --- 可选参数区 ---
        lf_opt = tk.LabelFrame(self.root, text="可选参数 (Optional)", padx=10, pady=10, font=("Arial", 10, "bold"))
        lf_opt.pack(fill="x", padx=10, pady=5)

        self.m_var = tk.StringVar()
        self.add_path_input(
            lf_opt, "输出目录路径 (-m):", self.m_var, 
            "提示：留空则默认在【构建产物路径】下新建 _manifest 文件夹保存 SBOM 文件"
        )

        self.nsb_var = tk.StringVar()
        self.add_text_input(
            lf_opt, "命名空间基础URI (-nsb):", self.nsb_var, 
            "示例：https://myiotcompany.com/sbom/routers"
        )

        # 杂项参数
        frame_misc = tk.Frame(lf_opt)
        frame_misc.pack(fill="x", pady=5)
        
        self.li_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame_misc, text="获取许可证信息 (-li)", variable=self.li_var).pack(side="left", padx=5)

        tk.Label(frame_misc, text="线程数 (-P):").pack(side="left", padx=(20, 5))
        self.p_var = tk.StringVar(value="4")
        tk.Entry(frame_misc, textvariable=self.p_var, width=5).pack(side="left")

        tk.Label(frame_misc, text="日志级别 (-V):").pack(side="left", padx=(20, 5))
        self.v_var = tk.StringVar(value="Information")
        ttk.Combobox(frame_misc, textvariable=self.v_var, values=["Verbose", "Debug", "Information", "Warning", "Error"], width=12, state="readonly").pack(side="left")

        # --- 按钮区 ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.run_btn = tk.Button(btn_frame, text="🚀 开始生成 SBOM", command=self.run_tool, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=20, pady=5)
        self.run_btn.pack()

        # --- 输出日志区 ---
        tk.Label(self.root, text="运行日志:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        self.log_text = tk.Text(self.root, height=12, state="disabled", bg="#1E1E1E", fg="#00FF00", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def add_path_input(self, parent, label_text, var, hint_text):
        container = tk.Frame(parent)
        container.pack(fill="x", pady=5) # 增加了一点间距容纳多行提示
        
        input_frame = tk.Frame(container)
        input_frame.pack(fill="x")
        tk.Label(input_frame, text=label_text, width=25, anchor="e").pack(side="left")
        tk.Entry(input_frame, textvariable=var).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(input_frame, text="浏览...", command=lambda: var.set(filedialog.askdirectory())).pack(side="right")
        
        hint_frame = tk.Frame(container)
        hint_frame.pack(fill="x")
        # 支持多行提示，左对齐
        tk.Label(hint_frame, text=hint_text, fg="#808080", font=("Microsoft YaHei", 8), justify="left").pack(side="left", padx=(180, 0))

    def add_text_input(self, parent, label_text, var, hint_text):
        container = tk.Frame(parent)
        container.pack(fill="x", pady=2)
        
        input_frame = tk.Frame(container)
        input_frame.pack(fill="x")
        tk.Label(input_frame, text=label_text, width=25, anchor="e").pack(side="left")
        tk.Entry(input_frame, textvariable=var).pack(side="left", fill="x", expand=True, padx=5)
        
        hint_frame = tk.Frame(container)
        hint_frame.pack(fill="x")
        tk.Label(hint_frame, text=hint_text, fg="#808080", font=("Microsoft YaHei", 8)).pack(side="left", padx=(180, 0))

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def run_tool(self):
        if not os.path.exists(self.tool_exe):
            messagebox.showerror("错误", f"找不到工具文件：\n{self.tool_exe}\n\n请确保 sbom-tool-win-x64.exe 与本程序在同一目录下！")
            return

        if not all([self.b_var.get(), self.bc_var.get(), self.pn_var.get(), self.pv_var.get(), self.ps_var.get()]):
            messagebox.showwarning("警告", "请填写所有【必填参数】！")
            return

        cmd = [self.tool_exe, "Generate"]
        cmd.extend(["-b", self.b_var.get()])
        cmd.extend(["-bc", self.bc_var.get()])
        cmd.extend(["-pn", self.pn_var.get()])
        cmd.extend(["-pv", self.pv_var.get()])
        cmd.extend(["-ps", self.ps_var.get()])

        if self.m_var.get():
            cmd.extend(["-m", self.m_var.get()])
        if self.nsb_var.get():
            cmd.extend(["-nsb", self.nsb_var.get()])
        if self.li_var.get():
            cmd.extend(["-li", "true"])
        if self.p_var.get():
            cmd.extend(["-P", self.p_var.get()])
        if self.v_var.get():
            cmd.extend(["-V", self.v_var.get()])

        self.log("="*60)
        self.log(f"执行命令: {' '.join(cmd)}")
        self.log("="*60)

        self.run_btn.config(state="disabled", text="生成中，请稍候...")
        threading.Thread(target=self.execute_subprocess, args=(cmd,), daemon=True).start()

    def execute_subprocess(self, cmd):
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for line in process.stdout:
                self.log(line.strip())

            process.wait()
            if process.returncode == 0:
                self.log("\n✅ SBOM 生成成功！")
            else:
                self.log(f"\n❌ SBOM 生成失败，返回码：{process.returncode}")

        except Exception as e:
            self.log(f"\n❌ 发生异常: {str(e)}")
        
        finally:
            self.run_btn.config(state="normal", text="🚀 开始生成 SBOM")

if __name__ == "__main__":
    root = tk.Tk()
    app = SbomGuiApp(root)
    root.mainloop()
