import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re
import webbrowser  # 导入用于打开浏览器的模块

# 支持的所有哈希算法
SUPPORTED_ALGORITHMS = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']

# 定义哈希计算函数
def calculate_hash(filename, algorithm='md5'):
    """计算给定文件的哈希值"""
    hash_constructor = getattr(hashlib, algorithm, None)
    if not hash_constructor:
        messagebox.showerror("错误", f"不支持的哈希算法: {algorithm}")
        return None

    try:
        # 创建哈希算法的实例
        hash_func = hash_constructor()
        with open(filename, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                hash_func.update(byte_block)
        return hash_func.hexdigest()
    except FileNotFoundError:
        messagebox.showerror("错误", "文件未找到")
        return None
    except Exception as e:
        messagebox.showerror("错误", str(e))
        return None

# 选择文件
def select_file(label):
    """打开文件选择对话框，并更新标签显示所选文件路径"""
    file_path = filedialog.askopenfilename(
        title="选择文件",
        filetypes=[("所有文件", "*.*")]
    )
    if file_path:
        label.config(text=file_path)

# 自动检测哈希算法并更新选项菜单
def detect_and_update_algorithm(hash_file_label):
    """从哈希文件中读取哈希值，并自动设置相应的哈希算法"""
    hash_file = hash_file_label.cget("text")

    if not hash_file:
        messagebox.showwarning("警告", "请选择一个哈希文件")
        return

    try:
        with open(hash_file, 'r') as f:
            lines = f.readlines()

            # 检查文件是否为空
            if not lines:
                messagebox.showerror("错误", "哈希文件为空")
                return
            
            detected_algorithm = None

            # 尝试逐行解析，直到成功检测到算法
            for line in lines:
                match = re.match(r'^([a-fA-F0-9]+)\s+', line.strip())
                if match:
                    expected_hash = match.group(1)
                    detected_algorithm = detect_hash_algorithm(expected_hash, lines)
                    if detected_algorithm:
                        break

            if not detected_algorithm:
                messagebox.showwarning("警告", "无法识别的哈希算法，请手动选择")
                return

            # 更新选择哈希算法的选项
            algorithm_var.set(detected_algorithm)
            messagebox.showinfo("信息", f"检测到的哈希算法已更新为: {detected_algorithm.upper()}")

    except Exception as e:
        messagebox.showerror("错误", f"无法读取哈希文件: {e}")

# 检测哈希算法
def detect_hash_algorithm(hash_value, lines=None):
    """根据哈希值的长度和其他特征推断哈希算法"""
    length_to_algorithm = {
        32: 'md5',
        40: 'sha1',
        56: 'sha224',
        64: 'sha256',
        96: 'sha384',
        128: 'sha512'
    }

    hash_length = len(hash_value)
    detected_algorithm = length_to_algorithm.get(hash_length)

    if not detected_algorithm:
        return None

    return detected_algorithm

# 对比哈希值
def compare_hashes():
    """读取并比较两个文件的哈希值"""
    target_file = file_label.cget("text")
    hash_file = hash_file_label.cget("text")

    if not target_file or not hash_file:
        messagebox.showwarning("警告", "请选择两个文件")
        return

    # 获取检测到的哈希算法
    detected_algorithm = algorithm_var.get()

    # 计算目标文件的哈希值
    target_hash = calculate_hash(target_file, detected_algorithm)
    if target_hash is None:
        return

    # 从哈希文件中读取预期的哈希值
    try:
        with open(hash_file, 'r') as f:
            lines = f.readlines()
            if not lines:
                messagebox.showerror("错误", "哈希文件为空")
                return
            
            expected_hash = None

            # 尝试逐行解析，直到成功获取哈希值
            for line in lines:
                match = re.match(r'^([a-fA-F0-9]+)\s+', line.strip())
                if match:
                    expected_hash = match.group(1)
                    break

            if not expected_hash:
                messagebox.showerror("错误", "无效的哈希文件格式")
                return

            # 比较两个哈希值
            if target_hash.lower() == expected_hash.lower():
                messagebox.showinfo("结果", f"{detected_algorithm.upper()} 值一致")
            else:
                messagebox.showerror("结果", f"{detected_algorithm.upper()} 值不一致")

    except Exception as e:
        messagebox.showerror("错误", f"无法读取哈希文件: {e}")

# 生成哈希文件
def generate_hash_file():
    """为选定文件生成哈希文件"""
    file_path = file_label.cget("text")

    if not file_path:
        messagebox.showwarning("警告", "请选择一个文件")
        return

    # 获取用户选择的哈希算法
    algorithm = algorithm_var.get()

    # 计算文件的哈希值
    hash_value = calculate_hash(file_path, algorithm)
    if hash_value is None:
        return

    # 确定保存哈希文件的位置和名称
    hash_filename = filedialog.asksaveasfilename(
        defaultextension=f".{algorithm}",
        filetypes=[(f"{algorithm.upper()} 文件", f"*.{algorithm}"), ("所有文件", "*.*")],
        initialfile=os.path.basename(file_path) + f".{algorithm}"
    )

    if hash_filename:
        try:
            with open(hash_filename, 'w') as f:
                f.write(f"# Generated using {algorithm}\n")
                f.write(f"{hash_value}  {os.path.basename(file_path)}\n")
            messagebox.showinfo("成功", f"{algorithm.upper()} 文件已生成: {hash_filename}")
        except Exception as e:
            messagebox.showerror("错误", f"无法生成 {algorithm.upper()} 文件: {e}")

# 设置窗口图标
def set_window_icon(root, icon_path):
    """设置主窗口的图标"""
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        print(f"Icon file not found: {icon_path}")

# 打开GitHub项目页面
def open_github_link(event=None):
    webbrowser.open_new_tab('https://github.com/MQ-H/Python-Multi-Hash-Algorithm-Tool-Build-Compare')

# 主程序入口
def main():
    # 创建主窗口
    root = tk.Tk()
    root.title("多哈希算法工具 - 生成 & 对比")

    # 设置窗口图标
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "my_icon.ico")
    set_window_icon(root, icon_path)

    # 设置窗口大小（这里我们使用屏幕高度或宽度的较小值作为正方形窗口的边长）
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算窗口的边长为屏幕高度和宽度的较小值的60%
    window_size = min(screen_width, screen_height) * 0.6

    # 计算窗口位置以居中显示
    position_top = int((screen_height - window_size) / 2)
    position_right = int((screen_width - window_size) / 2)

    # 设置窗口几何参数，保持正方形比例但允许拉伸
    root.geometry(f'{int(window_size)}x{int(window_size)}+{position_right}+{position_top}')
    root.minsize(width=300, height=300)  # 设置最小尺寸，避免窗口过小
    root.resizable(True, True)  # 允许窗口调整大小

    # 配置网格权重，使所有列和行可以扩展
    for i in range(6):  # 行
        root.grid_rowconfigure(i, weight=1)
    for i in range(3):  # 列
        root.grid_columnconfigure(i, weight=1)

    # 创建并放置选项菜单
    tk.Label(root, text="选择哈希算法:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
    global algorithm_var
    algorithm_var = tk.StringVar(value=SUPPORTED_ALGORITHMS[0])
    option_menu = tk.OptionMenu(root, algorithm_var, *SUPPORTED_ALGORITHMS)
    option_menu.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky='ew')

    # 创建并放置标签和按钮 - 文件选择
    tk.Label(root, text="选择文件:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
    global file_label
    file_label = tk.Label(root, text="", wraplength=300)
    file_label.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
    tk.Button(root, text="选择文件", command=lambda: select_file(file_label)).grid(row=1, column=2, padx=10, pady=10, sticky='ew')

    # 创建并放置“生成哈希文件”按钮
    tk.Button(root, text="生成哈希文件", command=generate_hash_file).grid(row=2, column=0, columnspan=3, pady=10, sticky='ew')

    # 创建并放置标签和按钮 - 哈希文件选择
    tk.Label(root, text="选择哈希文件:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
    global hash_file_label
    hash_file_label = tk.Label(root, text="", wraplength=300)
    hash_file_label.grid(row=3, column=1, padx=10, pady=10, sticky='ew')
    tk.Button(root, text="选择文件", command=lambda: [select_file(hash_file_label), detect_and_update_algorithm(hash_file_label)]).grid(row=3, column=2, padx=10, pady=10, sticky='ew')

    # 创建并放置“开始对比”按钮
    tk.Button(root, text="开始对比", command=compare_hashes).grid(row=4, column=0, columnspan=3, pady=20, sticky='ew')

    # 创建GitHub链接标签，并绑定点击事件
    github_link = tk.Label(root, text="GitHub", fg="blue", cursor="hand2")
    github_link.grid(row=5, column=0, padx=10, pady=10, sticky=tk.SW)
    github_link.bind("<Button-1>", open_github_link)

    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()
