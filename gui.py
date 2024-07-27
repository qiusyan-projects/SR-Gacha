import random
from ruamel.yaml import YAML
import os
import requests
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, StringVar, Toplevel, Label, Button, Entry, Listbox, END, BooleanVar, font, ttk

# Colors and other constants
PURPLE = '#BA55D3'
GOLD = '#FFD700'
GREEN = '#32CD32'
RED = '#FF4500'
RESET = '#FFFFFF'
CYAN = '#00CED1'
YELLOW = '#FFFF00'
BLUE = '#1E90FF'
DAY_BG = '#FFFFFF'
DAY_FG = '#000000'
NIGHT_BG = '#222222'
NIGHT_FG = '#FFFFFF'

BANNER_FILE = 'banners.yml'
GITHUB_PROXY = 'https://mirror.ghproxy.com'
BANNER_DOWNLOAD_URL = "https://raw.githubusercontent.com/qiusyan-projects/SR-Gacha/main/banners.yml"
TIPS = [
    "大保底时，下一个5星角色必定是UP角色。",
    "每10次抽卡必定至少有一个4星或以上角色/光锥。",
    "这个Tip我还没想好怎么写...",
    "你说得对，但是...",
    "来点Star叭！",
    "这是一个小Tip，只有聪明人才能看到它的内容",
    "可以修改卡池文件来实现其他游戏的抽卡效果，具体请移步项目README"
]

yaml = YAML()


class GachaSimulatorGUI:
    def __init__(self, root):
        self.root = root
        
        # 设置默认字体为微软雅黑
        self.default_font_name = 'Microsoft YaHei'  # 如果这个不可用，Tkinter 会自动尝试下一个可用的系统字体
        self.default_font = (self.default_font_name, 10)
        self.large_font = (self.default_font_name, 14)
        # 更新确认
        if os.path.exists(BANNER_FILE):
            check_update = messagebox.askyesno("更新确认", "是否检查卡池文件更新？（修改卡池了的不要选更新）")
            no_update = not check_update
        else:
            no_update = False  # 如果文件不存在，强制更新
        
        self.gacha_system = GachaSystem(BANNER_FILE, no_update=no_update)
        self.banner_id_map = {}  # 用于存储名称到ID的映射
        self.banner_name_map = {}  # 用于存储ID到名称的映射
        self.initialize_banner_maps()
        self.setup_gui()


    def initialize_banner_maps(self):
        character_banners, weapon_banners = self.gacha_system.categorize_banners()
        all_banners = character_banners + weapon_banners
        
        print("初始化 banner_id_map:")  # 调试信息
        for banner_id, banner_name in all_banners:
            self.banner_id_map[banner_name] = banner_id
            self.banner_name_map[banner_id] = banner_name
            print(f"  {banner_name} -> {banner_id}")  # 调试信息
        
        print("banner_id_map 内容:")  # 调试信息
        for name, id in self.banner_id_map.items():
            print(f"  {name}: {id}")  # 调试信息

    def setup_gui(self):
        self.root.title("Gacha Simulator")
        self.root.geometry("1200x800")

        # Create main frames
        self.left_frame = tk.Frame(self.root, width=300, bg='#f0f0f0')
        self.right_frame = tk.Frame(self.root, bg='white')

        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left frame content
        self.setup_left_frame()

        # Right frame content
        self.setup_right_frame()

    def setup_left_frame(self):
        # Banner type toggle
        self.current_banner_type = StringVar(value="character")
        self.toggle_button = ttk.Button(self.left_frame, text="切换到光锥池", command=self.toggle_banner_type)
        self.toggle_button.pack(pady=5, padx=10, fill=tk.X)

        # Standard banner button
        self.standard_banner_button = ttk.Button(self.left_frame, text="选择常驻池", command=self.select_standard_banner)
        self.standard_banner_button.pack(pady=5, padx=10, fill=tk.X)

        # Banner listbox
        self.banner_listbox = tk.Listbox(self.left_frame, height=10, font=self.default_font)
        self.banner_listbox.pack(pady=10, padx=10, fill=tk.X)
        self.update_banner_list()

        # Switch banner button
        self.switch_banner_button = ttk.Button(self.left_frame, text="切换到选择的卡池", command=self.on_switch_banner)
        self.switch_banner_button.pack(pady=5, padx=10, fill=tk.X)

        # Pull buttons
        self.pull_1_button = ttk.Button(self.left_frame, text="抽一次", command=lambda: self.on_pull(1))
        self.pull_1_button.pack(pady=5, padx=10, fill=tk.X)

        self.pull_10_button = ttk.Button(self.left_frame, text="抽十次", command=lambda: self.on_pull(10))
        self.pull_10_button.pack(pady=5, padx=10, fill=tk.X)


        # # Mode switch
        # self.is_night_mode = BooleanVar(value=False)
        # self.mode_button = ttk.Button(self.left_frame, text="切换到夜间模式", command=self.toggle_mode)
        # self.mode_button.pack(pady=5, padx=10, fill=tk.X)


        # Random tip button
        self.random_tip_button = ttk.Button(self.left_frame, text="随机Tips", command=self.show_random_tip)
        self.random_tip_button.pack(pady=5, padx=10, fill=tk.X)

        # Font selection
        # self.setup_font_selection()

        # Clear Data
        self.clear_data_button = ttk.Button(self.left_frame, text="重置抽卡统计数据", command=self.clear_gacha_data)
        self.clear_data_button.pack(pady=5, padx=10, fill=tk.X)

        # Add statistics display
        self.stats_frame = ttk.Frame(self.left_frame)
        self.stats_frame.pack(side=tk.BOTTOM, pady=10, padx=10, fill=tk.X)

        self.stats_text = tk.Text(self.stats_frame, height=9, width=30, font=self.default_font, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        self.stats_text.config(state=tk.DISABLED)

        self.update_stats_display()

    def setup_right_frame(self):
        # Banner label and clear history button frame
        top_frame = ttk.Frame(self.right_frame)
        top_frame.pack(fill=tk.X, pady=10)

        # Banner label
        self.banner_label_var = StringVar()
        self.banner_label = ttk.Label(top_frame, textvariable=self.banner_label_var, font=self.large_font)
        self.banner_label.pack(side=tk.LEFT, padx=(10, 0))
        self.update_gui_banner_name()

        # Clear history button
        self.clear_history_button = ttk.Button(top_frame, text="清空抽卡记录", command=self.clear_pull_history)
        self.clear_history_button.pack(side=tk.RIGHT, padx=(0, 10))

        # Pull history table
        columns = ('时间', '星级', '类型', '物品', '卡池', '是否UP')
        self.pull_history_tree = ttk.Treeview(self.right_frame, columns=columns, show='headings')
        
        # Define column headings
        for col in columns:
            self.pull_history_tree.heading(col, text=col)
            self.pull_history_tree.column(col, width=100)  # Adjust width as needed
        
        self.pull_history_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.pull_history_tree.yview)
        self.pull_history_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tips
        self.tip_label = ttk.Label(self.right_frame, text="", font=self.default_font, foreground="blue")
        self.tip_label.pack(pady=10)
        self.show_random_tip()


    def toggle_banner_type(self):
        if self.current_banner_type.get() == "character":
            self.current_banner_type.set("weapon")
            self.toggle_button.config(text="切换到角色池")
        else:
            self.current_banner_type.set("character")
            self.toggle_button.config(text="切换到光锥池")
        self.update_banner_list()

    def select_standard_banner(self):
        standard_banner = self.gacha_system.get_standard_banner()
        if standard_banner:
            if self.gacha_system.switch_banner(standard_banner):
                banner_info = self.gacha_system.pools['banners'].get(standard_banner, {})
                banner_name = banner_info.get('name', standard_banner)
                self.update_gui_banner_name()
                self.update_banner_list()
                messagebox.showinfo("提示", f"已切换到常驻池：{banner_name}")
            else:
                messagebox.showerror("错误", f"切换到常驻池失败")
        else:
            messagebox.showinfo("提示", "未找到常驻池")

    def update_banner_list(self):
        self.banner_listbox.delete(0, tk.END)
        character_banners, weapon_banners = self.gacha_system.categorize_banners()
        banners_to_show = character_banners if self.current_banner_type.get() == "character" else weapon_banners
        
        print("更新卡池列表:")  # 调试信息
        for banner_id, banner_name in banners_to_show:
            banner_info = self.gacha_system.pools['banners'][banner_id]
            if 'character_up_5_star' in banner_info:
                up_character = banner_info['character_up_5_star'][0]
                display_name = f"{banner_name} - UP: {up_character}"
            else:
                display_name = banner_name
            print(f"  添加到列表: {display_name}")  # 调试信息
            self.banner_listbox.insert(tk.END, display_name)
            if banner_id == self.gacha_system.current_banner:
                self.banner_listbox.selection_set(tk.END)

    def on_switch_banner(self):
        print("开始切换卡池...")  # 调试信息
        selected_indices = self.banner_listbox.curselection()
        print(f"选中的索引: {selected_indices}")  # 调试信息
        if selected_indices:
            selected_banner_display_name = self.banner_listbox.get(selected_indices[0])
            print(f"选中的卡池显示名称: {selected_banner_display_name}")  # 调试信息
            
            # 提取原始卡池名称（去掉 " - UP: xxx" 部分）
            selected_banner_name = selected_banner_display_name.split(" - UP:")[0]
            print(f"提取的原始卡池名称: {selected_banner_name}")  # 调试信息
            
            selected_banner_id = self.banner_id_map.get(selected_banner_name)
            print(f"选中的卡池ID: {selected_banner_id}")  # 调试信息
            
            if selected_banner_id:
                print(f"尝试切换到卡池ID: {selected_banner_id}")  # 调试信息
                if self.gacha_system.switch_banner(selected_banner_id):
                    print("成功切换卡池")  # 调试信息
                    self.update_banner_list()
                    self.update_gui_banner_name()
                    self.update_stats_display()  # Update stats when switching banner
                    banner_info = self.gacha_system.pools['banners'].get(selected_banner_id, {})
                    banner_name = banner_info.get('name', selected_banner_name)
                    messagebox.showinfo("提示", f"已切换到卡池：{banner_name}")
                else:
                    print(f"切换卡池失败")  # 调试信息
                    messagebox.showerror("错误", f"切换到卡池 {selected_banner_name} 失败")
            else:
                print(f"未找到卡池ID")  # 调试信息
                messagebox.showerror("错误", f"未找到卡池 {selected_banner_name} 的ID")

    def on_pull(self, num_pulls):
        pulls = self.gacha_system.perform_pull(num_pulls)
        if pulls:
            self.update_gui_pull_history(pulls)
            self.gacha_system.save_state()
            self.update_stats_display()  # Update stats after each pull


    # 夜间模式相关代码
    # def toggle_mode(self):
    #     self.is_night_mode.set(not self.is_night_mode.get())
    #     self.mode_button.config(text="切换到日间模式" if self.is_night_mode.get() else "切换到夜间模式")
    #     self.update_color_scheme()

    # def update_color_scheme(self):
    #     bg_color = '#222222' if self.is_night_mode.get() else '#FFFFFF'
    #     fg_color = '#FFFFFF' if self.is_night_mode.get() else '#000000'
    #     self.right_frame.config(bg=bg_color)
    #     self.banner_label.config(background=bg_color, foreground=fg_color)
    #     self.tip_label.config(background=bg_color, foreground='lightblue' if self.is_night_mode.get() else 'blue')
        
    #     # Update Treeview colors
    #     style = ttk.Style()
    #     style.configure("Treeview", 
    #                     background=bg_color, 
    #                     foreground=fg_color, 
    #                     fieldbackground=bg_color)
    #     style.map('Treeview', background=[('selected', '#0078D7')])


    def show_random_tip(self):
        self.tip_label.config(text=random.choice(self.gacha_system.TIPS))

    def update_gui_banner_name(self):
        if self.gacha_system.current_banner:
            banner_info = self.gacha_system.pools['banners'].get(self.gacha_system.current_banner, {})
            banner_name = banner_info.get('name', self.gacha_system.current_banner)
            self.banner_label_var.set(f"当前卡池: {banner_name}")
        else:
            self.banner_label_var.set("当前卡池: 未选择")

    def update_gui_pull_history(self, pulls):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_banner_info = self.gacha_system.pools['banners'].get(self.gacha_system.current_banner, {})
        current_banner_name = current_banner_info.get('name', self.gacha_system.current_banner)
        is_standard_banner = current_banner_info.get('pool_type') == 'standard'

        print(f"Debug: Current banner: {current_banner_name}")
        print(f"Debug: Is standard banner: {is_standard_banner}")
        print(f"Debug: Current banner info: {current_banner_info}")

        for rarity, item_type, item in pulls:
            tag = rarity.replace('_star', '')  # '5_star' becomes '5'
            
            # Determine if it's an UP item
            is_up = "否"
            if not is_standard_banner and rarity in ['4_star', '5_star']:
                up_items = current_banner_info.get(f"{item_type}_up_{rarity}", [])
                if not up_items and item_type == '角色':
                    up_items = current_banner_info.get(f"character_up_{rarity}", [])
                elif not up_items and item_type == '光锥':
                    up_items = current_banner_info.get(f"weapon_up_{rarity}", [])
                
                print(f"Debug: UP items for {rarity} {item_type}: {up_items}")
                print(f"Debug: Current item: {item}")
                is_up = "是" if item in up_items else "否"
                print(f"Debug: Is UP: {is_up}")
            
            # For 3-star items and standard banner pulls, leave the UP column empty
            if rarity == '3_star' or is_standard_banner:
                is_up = ""

            print(f"Debug: Inserting item: {current_time}, {rarity}, {item_type}, {item}, {current_banner_name}, {is_up}")
            self.pull_history_tree.insert('', 0, values=(current_time, rarity, item_type, item, current_banner_name, is_up), tags=(tag,))
        
        # Set tag colors
        self.pull_history_tree.tag_configure('5', foreground='gold')
        self.pull_history_tree.tag_configure('4', foreground='purple')

    def clear_gacha_data(self):
        confirm = messagebox.askyesno("确认", "您确定要清除所有抽卡统计数据吗？此操作不可逆。")
        if confirm:
            second_confirm = messagebox.askyesno("二次确认", "真的要清除所有数据吗？这将重置所有统计信息。")
            if second_confirm:
                self.gacha_system.reset_statistics()
                self.update_stats_display()  # Update stats after clearing data
                messagebox.showinfo("成功", "所有抽卡统计数据已被清除。")

    def clear_pull_history(self):
        confirm = messagebox.askyesno("确认", "您确定要清空抽卡记录吗？此操作不可逆。")
        if confirm:
            self.pull_history_tree.delete(*self.pull_history_tree.get_children())
            self.gacha_system.pull_history = []
            self.gacha_system.save_state()
            messagebox.showinfo("成功", "抽卡记录已清空。")

    def update_stats_display(self):
        stats = f"""总抽卡次数: {self.gacha_system.total_pulls}
距离下一个五星保底的抽数: {90 - self.gacha_system.pity_5}
距离下一个四星保底: {10 - self.gacha_system.pity_4}
获得五星次数: {len(self.gacha_system.gold_records)}
获得四星次数: {len(self.gacha_system.purple_records)}
歪掉五星次数: {self.gacha_system.failed_featured_5star}
抽中UP五星次数: {self.gacha_system.successful_featured_5star}
距离上次五星: {self.gacha_system.pulls_since_last_5star}
大保底状态: {'是' if self.gacha_system.is_guaranteed else '否'}"""

        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)
        self.stats_text.config(state=tk.DISABLED)



class GachaSystem:
    def __init__(self, pool_file, no_update=False):
        self.pool_file = pool_file
        self.is_first_download = not os.path.exists(self.pool_file)
        self.ensure_pool_file_exists()
        if not self.is_first_download and not no_update:
            update_result = self.check_and_update_pool_file()
            if update_result == "current":
                self.show_message("卡池文件已是最新版本。", CYAN)
            elif update_result == "updated":
                self.show_message("卡池文件已自动更新到最新版本。", GREEN)
            else:
                self.show_message(f"检查更新时发生错误: {update_result}。使用当前版本的卡池文件。", YELLOW)
        elif no_update:
            self.show_message("已跳过更新检查。", GREEN)
        else:
            return
        self.load_pools(pool_file)
        self.current_banner = None
        self.pity_5 = 0
        self.pity_4 = 0
        self.failed_featured_pulls = 0
        self.total_pulls = 0
        self.banner_pulls = {}
        self.gold_records = []
        self.purple_records = []
        self.failed_featured_5star = 0 
        self.successful_featured_5star = 0
        self.pulls_since_last_5star = 0
        self.is_guaranteed = False
        self.pull_history = []
        self.TIPS = TIPS
        self.load_state()

    def load_pools(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            self.pools = yaml.load(f)
        self.banners = list(self.pools['banners'].keys())

    def save_state(self):
        try:
            state = {
                'current_banner': self.current_banner,
                'pity_5': self.pity_5,
                'pity_4': self.pity_4,
                'failed_featured_pulls': self.failed_featured_pulls,
                'total_pulls': self.total_pulls,
                'banner_pulls': self.banner_pulls,
                'gold_records': self.gold_records,
                'purple_records': self.purple_records,
                'failed_featured_5star': self.failed_featured_5star,
                'successful_featured_5star': self.successful_featured_5star,
                'pulls_since_last_5star': self.pulls_since_last_5star,
                'is_guaranteed': self.is_guaranteed,
                'pull_history': self.pull_history
            }

            yaml.default_flow_style = False
            yaml.width = 4096
            yaml.indent(mapping=2, sequence=4, offset=2)

            yaml_str = "# 抽卡模拟器数据文件\n"
            yaml_str += "# 请勿手动修改，除非你知道自己在做什么\n"
            
            from io import StringIO
            string_stream = StringIO()
            yaml.dump(state, string_stream)
            data_str = string_stream.getvalue()
            
            data_str = data_str.replace('current_banner:', '# 当前选择的卡池\ncurrent_banner:')
            data_str = data_str.replace('pity_5:', '# 距离保底5星的抽数\npity_5:')
            data_str = data_str.replace('pity_4:', '# 距离保底4星的抽数\npity_4:')
            data_str = data_str.replace('failed_featured_pulls:', '# 未抽中UP角色/光锥的次数\nfailed_featured_pulls:')
            data_str = data_str.replace('total_pulls:', '# 总抽卡次数\ntotal_pulls:')
            data_str = data_str.replace('banner_pulls:', '# 每个卡池的抽卡次数\nbanner_pulls:')
            data_str = data_str.replace('gold_records:', '# 获得5星的抽数记录\ngold_records:')
            data_str = data_str.replace('purple_records:', '# 获得4星的抽数记录\npurple_records:')
            data_str = data_str.replace('failed_featured_5star:', '# 歪掉的5星次数\nfailed_featured_5star:')
            data_str = data_str.replace('successful_featured_5star:', '# 抽中UP的5星次数\nsuccessful_featured_5star:')
            data_str = data_str.replace('pulls_since_last_5star:', '# 距离上次5星的抽数\npulls_since_last_5star:')
            data_str = data_str.replace('pull_history:', '# 抽卡历史记录\npull_history:')
            
            yaml_str += data_str

            with open('gacha_data.yaml', 'w', encoding='utf-8') as f:
                f.write(yaml_str)
        except Exception as e:
            self.show_message(f"无法保存数据: {e}", RED)

    def load_state(self):
        try:
            with open('gacha_data.yaml', 'r', encoding='utf-8') as f:
                state = yaml.load(f)
                self.current_banner = state.get('current_banner')
                self.pity_5 = state.get('pity_5', 0)
                self.pity_4 = state.get('pity_4', 0)
                self.failed_featured_pulls = state.get('failed_featured_pulls', 0)
                self.total_pulls = state.get('total_pulls', 0)
                self.banner_pulls = state.get('banner_pulls', {})
                self.gold_records = state.get('gold_records', [])
                self.purple_records = state.get('purple_records', [])
                self.failed_featured_5star = state.get('failed_featured_5star', 0)
                self.successful_featured_5star = state.get('successful_featured_5star', 0)
                self.pulls_since_last_5star = state.get('pulls_since_last_5star', 0)
                self.is_guaranteed = state.get('is_guaranteed', False)
                self.pull_history = state.get('pull_history', [])
                for pull in self.pull_history:
                    if pull['item_type'] == 'character':
                        pull['item_type'] = '角色'
                    elif pull['item_type'] == 'weapon':
                        pull['item_type'] = '光锥'
        except FileNotFoundError:
            return
        except Exception as e:
            self.show_message(f"无法加载数据: {e}", RED)

    def ensure_pool_file_exists(self):
        if not os.path.exists(self.pool_file):
            download = messagebox.askyesno("错误", f"'{self.pool_file}' 文件不存在。是否从GitHub下载最新的banners.yml?")
            if download:
                try:
                    proxy_url = f"{GITHUB_PROXY}/{BANNER_DOWNLOAD_URL}"
                    response = requests.get(proxy_url)
                    response.raise_for_status()
                    with open(self.pool_file, 'wb') as f:
                        f.write(response.content)
                    self.show_message("成功下载 'banners.yml'！", GREEN)
                    self.is_first_download = True
                except requests.RequestException as e:
                    self.show_message(f"下载失败: {e}", RED)
                    exit(1)
            else:
                self.show_message(f"请提供 '{self.pool_file}' 文件。", RED)
                exit(1)

    def check_and_update_pool_file(self):
        try:
            proxy_url = f"{GITHUB_PROXY}/{BANNER_DOWNLOAD_URL}"
            response = requests.get(proxy_url)
            response.raise_for_status()
            remote_content = response.content

            with open(self.pool_file, 'rb') as f:
                local_content = f.read()

            if local_content == remote_content:
                return "current"
            else:
                with open(self.pool_file, 'wb') as f:
                    f.write(remote_content)
                return "updated"
        except requests.RequestException as e:
            return str(e)

    def switch_banner(self, banner_name):
        print(f"尝试切换到卡池: {banner_name}")  # 调试信息
        print(f"可用的卡池: {self.banners}")  # 调试信息
        if banner_name not in self.banners:
            print(f"卡池 {banner_name} 不在可用卡池列表中")  # 调试信息
            return False
        self.current_banner = banner_name
        print(f"成功切换到卡池: {self.current_banner}")  # 调试信息
        self.save_state()
        return True

    def perform_pull(self, num_pulls):
        print(f"执行抽卡: {num_pulls} 次")
        if not self.current_banner:
            self.show_message("请先选择一个卡池。", RED)
            return

        banner = self.pools['banners'][self.current_banner]
        print(f"当前卡池: {self.current_banner}")
        print(f"卡池内容: {banner}")

        pool_type = banner.get('pool_type', 'standard')
        print(f"卡池类型: {pool_type}")

        pulls = []
        summary = {'5星': 0, '5星UP': 0, '4星': 0, '4星UP': 0, '3星': 0}
        guaranteed_4_star = False

        for i in range(num_pulls):
            self.total_pulls += 1
            self.banner_pulls[self.current_banner] = self.banner_pulls.get(self.current_banner, 0) + 1

            # 确定是否出五星
            if self.pity_5 >= 89 or random.randint(1, 10000) <= 60 + min(self.pity_5 * 600 // 73, 7300):
                result = self.pull_5_star(pool_type)
                self.gold_records.append(self.pity_5 + 1)  # 记录出金抽数
                self.pity_5 = 0
                self.pity_4 = 0  # 重置4星保底
                self.pulls_since_last_5star = 0  # 重置距离上次五星的抽数
                summary['5星'] += 1
                if self.current_banner != 'standard':
                    if result['is_up']:
                        self.successful_featured_5star += 1
                        summary['5星UP'] += 1
                    else:
                        self.failed_featured_5star += 1
                guaranteed_4_star = False
            # 确定是否出四星
            elif self.pity_4 >= 9 or random.randint(1, 10000) <= 510 + min(self.pity_4 * 790 // 8, 7390) or (i + 1) % 10 == 0 and not guaranteed_4_star:
                result = self.pull_4_star(pool_type)
                self.purple_records.append(self.pity_4 + 1)  # 记录出紫抽数
                self.pity_5 += 1
                self.pity_4 = 0
                self.pulls_since_last_5star += 1  # 增加距离上次五星的抽数
                summary['4星'] += 1
                if self.current_banner != 'standard' and result['is_up']:
                    summary['4星UP'] += 1
                guaranteed_4_star = True
            else:
                result = self.pull_3_star()
                self.pity_5 += 1
                self.pity_4 += 1
                self.pulls_since_last_5star += 1  # 增加距离上次五星的抽数
                summary['3星'] += 1

            pulls.append((result['rarity'], result['type'], result['item']))
            self.pull_history.append({'rarity': result['rarity'], 'item_type': result['type'], 'item': result['item']})

        print(f"抽卡结果统计: {summary}")
        return pulls

    def pull_5_star(self, pool_type):
        is_up = random.random() < 0.5 or self.is_guaranteed
        if pool_type == 'character':
            if is_up:
                item = random.choice(self.pools['banners'][self.current_banner]['character_up_5_star'])
                self.is_guaranteed = False
            else:
                item = random.choice(self.pools['common_pools']['character_5_star'])
                self.is_guaranteed = True
            return {'rarity': '5_star', 'type': '角色', 'item': item, 'is_up': is_up}
        elif pool_type == 'weapon':
            if is_up:
                item = random.choice(self.pools['banners'][self.current_banner]['weapon_up_5_star'])
                self.is_guaranteed = False
            else:
                item = random.choice(self.pools['common_pools']['weapon_5_star'])
                self.is_guaranteed = True
            return {'rarity': '5_star', 'type': '光锥', 'item': item, 'is_up': is_up}
        else:  # standard pool
            if random.random() < 0.5:
                item = random.choice(self.pools['common_pools']['character_5_star'])
                return {'rarity': '5_star', 'type': '角色', 'item': item, 'is_up': False}
            else:
                item = random.choice(self.pools['common_pools']['weapon_5_star'])
                return {'rarity': '5_star', 'type': '光锥', 'item': item, 'is_up': False}

    def pull_4_star(self, pool_type):
        is_up = random.random() < 0.5
        if is_up and pool_type != 'standard':
            if pool_type == 'character':
                item = random.choice(self.pools['banners'][self.current_banner].get('character_up_4_star', []))
                return {'rarity': '4_star', 'type': '角色', 'item': item, 'is_up': True}
            else:  # weapon pool
                item = random.choice(self.pools['banners'][self.current_banner].get('weapon_up_4_star', []))
                return {'rarity': '4_star', 'type': '光锥', 'item': item, 'is_up': True}
        else:
            if random.random() < 0.5:
                item = random.choice(self.pools['common_pools']['character_4_star'])
                return {'rarity': '4_star', 'type': '角色', 'item': item, 'is_up': False}
            else:
                item = random.choice(self.pools['common_pools']['weapon_4_star'])
                return {'rarity': '4_star', 'type': '光锥', 'item': item, 'is_up': False}

    def pull_3_star(self):
        item = random.choice(self.pools['common_pools']['weapon_3_star'])
        return {'rarity': '3_star', 'type': '光锥', 'item': item, 'is_up': False}

    def show_message(self, message, color=RESET):
        if color == RED:
            messagebox.showerror("错误", message)
        elif color == GREEN:
            messagebox.showinfo("成功", message)
        elif color == YELLOW:
            messagebox.showwarning("警告", message)
        else:
            messagebox.showinfo("提示", message)
        




    def categorize_banners(self):
        character_banners = []
        weapon_banners = []
        standard_banner = self.get_standard_banner()
        print("分类卡池:")  # 调试信息
        for banner_id, banner_info in self.pools['banners'].items():
            if banner_id != standard_banner:
                banner_name = banner_info.get('name', banner_id)
                print(f"  处理卡池: {banner_id} - {banner_name}")  # 调试信息
                if banner_info.get('pool_type') == 'character':
                    character_banners.append((banner_id, banner_name))
                    print(f"    添加到角色卡池")  # 调试信息
                elif banner_info.get('pool_type') == 'weapon':
                    weapon_banners.append((banner_id, banner_name))
                    print(f"    添加到武器卡池")  # 调试信息
        print(f"角色卡池: {character_banners}")  # 调试信息
        print(f"武器卡池: {weapon_banners}")  # 调试信息
        return character_banners, weapon_banners
    
    def get_standard_banner(self):
        return next((banner_id for banner_id, banner_info in self.pools['banners'].items() if banner_info.get('name') == '群星跃迁'), None)
    

    def reset_statistics(self):
        self.pity_5 = 0
        self.pity_4 = 0
        self.failed_featured_pulls = 0
        self.total_pulls = 0
        self.banner_pulls = {}
        self.gold_records = []
        self.purple_records = []
        self.failed_featured_5star = 0
        self.successful_featured_5star = 0
        self.pulls_since_last_5star = 0
        self.is_guaranteed = False
        # self.pull_history = []
        self.save_state()


# GachaSystem 部分结束


# GUI 部分
if __name__ == "__main__":
    root = tk.Tk()
    gui = GachaSimulatorGUI(root)
    root.mainloop()