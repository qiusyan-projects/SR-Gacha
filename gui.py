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
    # "可以使用 'info' 命令查看抽卡统计信息。",
    "大保底时，下一个5星角色必定是UP角色。",
    "每10次抽卡必定至少有一个4星或以上角色/光锥。",
    "这个Tip我还没想好怎么写...",
    # "为了防止抽卡记录过多导致数据读取缓慢，抽卡记录中没有三星的光锥获得记录",
    "你说得对，但是...",
    "来点Star叭！",
    "这是一个小Tip，只有聪明人才能看到它的内容",
    "可以修改卡池文件来实现其他游戏的抽卡效果，具体请移步项目README"
]

yaml = YAML()


class GachaSimulatorGUI:
    def __init__(self, root):
        self.root = root
        
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
        
        for banner_id, banner_name in all_banners:
            self.banner_id_map[banner_name] = banner_id
            self.banner_name_map[banner_id] = banner_name

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
        self.banner_listbox = tk.Listbox(self.left_frame, height=10)
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

        # Info button
        self.info_button = ttk.Button(self.left_frame, text="查看统计信息", command=self.on_show_info)
        self.info_button.pack(pady=5, padx=10, fill=tk.X)

        # Mode switch
        self.is_night_mode = BooleanVar(value=False)
        self.mode_button = ttk.Button(self.left_frame, text="切换到夜间模式", command=self.toggle_mode)
        self.mode_button.pack(pady=5, padx=10, fill=tk.X)


        # Random tip button
        self.random_tip_button = ttk.Button(self.left_frame, text="随机Tips", command=self.show_random_tip)
        self.random_tip_button.pack(pady=5, padx=10, fill=tk.X)

        # Font selection
        self.setup_font_selection()

        # Clear Data
        self.clear_data_button = ttk.Button(self.left_frame, text="清除抽卡统计数据", command=self.clear_gacha_data)
        self.clear_data_button.pack(pady=5, padx=10, fill=tk.X)

    def setup_right_frame(self):
        # Banner label
        self.banner_label_var = StringVar()
        self.banner_label = ttk.Label(self.right_frame, textvariable=self.banner_label_var, font=("Courier", 14))
        self.banner_label.pack(pady=10)
        self.update_gui_banner_name()

        # Pull history
        self.pull_history_text = scrolledtext.ScrolledText(self.right_frame, state='disabled', width=80, height=30, wrap=tk.WORD)
        self.pull_history_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.pull_history_text.tag_config('GOLD', foreground='#FFD700')
        self.pull_history_text.tag_config('PURPLE', foreground='#BA55D3')
        self.pull_history_text.tag_config('RESET', foreground='#000000')

        # Tips
        self.tip_label = ttk.Label(self.right_frame, text="", font=("Courier", 10), foreground="blue")
        self.tip_label.pack(pady=10)
        self.show_random_tip()

    def setup_font_selection(self):
        available_fonts = tk.font.families()
        self.font_var = StringVar(self.root)
        self.font_var.set("Courier")  # Default font

        self.font_menu = ttk.Combobox(self.left_frame, textvariable=self.font_var, values=available_fonts)
        self.font_menu.pack(pady=5, padx=10, fill=tk.X)
        self.font_menu.bind("<<ComboboxSelected>>", self.on_font_change)

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
        
        for banner_id, banner_name in banners_to_show:
            banner_info = self.gacha_system.pools['banners'][banner_id]
            if 'character_up_5_star' in banner_info:
                up_character = banner_info['character_up_5_star'][0]
                display_name = f"{banner_name} - UP: {up_character}"
            else:
                display_name = banner_name
            self.banner_listbox.insert(tk.END, display_name)
            if self.banner_id_map[banner_name] == self.gacha_system.current_banner:
                self.banner_listbox.selection_set(tk.END)

    def on_switch_banner(self):
        selected_indices = self.banner_listbox.curselection()
        if selected_indices:
            selected_banner_name = self.banner_listbox.get(selected_indices[0])
            selected_banner_id = self.banner_id_map.get(selected_banner_name)
            if selected_banner_id:
                if self.gacha_system.switch_banner(selected_banner_id):
                    self.update_banner_list()
                    self.update_gui_banner_name()
                    banner_info = self.gacha_system.pools['banners'].get(selected_banner_id, {})
                    banner_name = banner_info.get('name', selected_banner_name)
                    messagebox.showinfo("提示", f"已切换到卡池：{banner_name}")
                else:
                    messagebox.showerror("错误", f"切换到卡池 {selected_banner_name} 失败")
        else:
            messagebox.showinfo("提示", "请先选择一个卡池")

    def on_pull(self, num_pulls):
        pulls = self.gacha_system.perform_pull(num_pulls)
        if pulls:
            self.update_gui_pull_history(pulls)
            self.gacha_system.save_state()

    def on_show_info(self):
        self.gacha_system.show_info()

    def toggle_mode(self):
        self.is_night_mode.set(not self.is_night_mode.get())
        self.mode_button.config(text="切换到日间模式" if self.is_night_mode.get() else "切换到夜间模式")
        self.update_color_scheme()

    def update_color_scheme(self):
        bg_color = '#222222' if self.is_night_mode.get() else '#FFFFFF'
        fg_color = '#FFFFFF' if self.is_night_mode.get() else '#000000'
        self.right_frame.config(bg=bg_color)
        self.pull_history_text.config(bg=bg_color, fg=fg_color)
        self.pull_history_text.tag_config('RESET', foreground=fg_color)
        self.banner_label.config(background=bg_color, foreground=fg_color)
        self.tip_label.config(background=bg_color, foreground='lightblue' if self.is_night_mode.get() else 'blue')

    def on_font_change(self, event):
        selected_font = self.font_var.get()
        self.update_font(selected_font)

    def update_font(self, font_name):
        new_font = (font_name, 10)
        widgets = [
            self.banner_label, self.tip_label, self.pull_history_text, self.banner_listbox
        ]
        for widget in widgets:
            widget.config(font=new_font)
        
        self.pull_history_text.tag_config('GOLD', foreground='#FFD700', font=new_font)
        self.pull_history_text.tag_config('PURPLE', foreground='#BA55D3', font=new_font)
        self.pull_history_text.tag_config('RESET', font=new_font)

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
        self.pull_history_text.configure(state='normal')
        self.pull_history_text.insert(tk.END, f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for rarity, item_type, item in pulls:
            if rarity == '5_star':
                color = 'GOLD'
            elif rarity == '4_star':
                color = 'PURPLE'
            else:
                color = 'RESET'
            self.pull_history_text.insert(tk.END, f"{rarity} - {item_type}: {item}\n", color)
        self.pull_history_text.configure(state='disabled')
        self.pull_history_text.see(tk.END)

    def clear_gacha_data(self):
        confirm = messagebox.askyesno("确认", "您确定要清除所有抽卡统计数据吗？此操作不可逆。")
        if confirm:
            second_confirm = messagebox.askyesno("二次确认", "真的要清除所有数据吗？这将重置所有统计信息。")
            if second_confirm:
                self.gacha_system.reset_statistics()
                messagebox.showinfo("成功", "所有抽卡统计数据已被清除。")



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
            yaml_str += "# 为了防止抽卡记录过多导致数据读取缓慢，抽卡记录中没有三星的光锥获得记录\n\n"
            
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
        if banner_name not in self.banners:
            return False
        self.current_banner = banner_name
        self.save_state()
        return True

    def perform_pull(self, num_pulls):
        print(f"执行抽卡: {num_pulls} 次")
        if not self.current_banner:
            self.show_message("请先选择卡池。", RED)
            return

        banner = self.pools['banners'][self.current_banner]
        print(f"当前卡池: {self.current_banner}")
        print(f"卡池内容: {banner}")

        pool_type = banner.get('pool_type', 'standard')
        print(f"卡池类型: {pool_type}")

        # 使用公共池中的武器和角色
        weapon_3_star = self.pools['common_pools']['weapon_3_star']
        weapon_4_star = self.pools['common_pools']['weapon_4_star']
        weapon_5_star = self.pools['common_pools']['weapon_5_star']
        character_4_star = self.pools['common_pools']['character_4_star']
        character_5_star = self.pools['common_pools']['character_5_star']

        pulls = []
        for _ in range(num_pulls):
            self.total_pulls += 1
            self.banner_pulls[self.current_banner] = self.banner_pulls.get(self.current_banner, 0) + 1
            self.pulls_since_last_5star += 1

            self.pity_5 += 1
            self.pity_4 += 1

            if self.pity_5 >= 90:
                rarity = '5_star'
                self.pity_5 = 0
            elif self.pity_4 >= 10:
                rarity = '4_star'
                self.pity_4 = 0
            else:
                rarity = random.choices(['3_star', '4_star', '5_star'], weights=[94.3, 5.1, 0.6])[0]

            print(f"抽到的星级: {rarity}")

            if rarity == '3_star':
                item = random.choice(weapon_3_star)
                pulls.append((rarity, '光锥', item))
            elif rarity == '4_star':
                if pool_type == 'character' and random.random() < 0.5:
                    item = random.choice(banner.get('character_up_4_star', character_4_star))
                    pulls.append((rarity, '角色', item))
                else:
                    item = random.choice(weapon_4_star)
                    pulls.append((rarity, '光锥', item))
            elif rarity == '5_star':
                is_featured = random.random() < 0.5 or self.is_guaranteed
                if is_featured and pool_type != 'standard':
                    if pool_type == 'character':
                        item = random.choice(banner['character_up_5_star'])
                        pulls.append((rarity, '角色', item))
                    else:
                        item = random.choice(banner['weapon_up_5_star'])
                        pulls.append((rarity, '光锥', item))
                    self.is_guaranteed = False
                    self.successful_featured_5star += 1
                else:
                    if random.random() < 0.5:
                        item = random.choice(character_5_star)
                        pulls.append((rarity, '角色', item))
                    else:
                        item = random.choice(weapon_5_star)
                        pulls.append((rarity, '光锥', item))
                    self.failed_featured_pulls += 1
                    self.failed_featured_5star += 1
                    self.is_guaranteed = True
                self.gold_records.append(self.pity_5)
                self.pity_5 = 0

            print(f"抽到的物品: {item}")
            self.pull_history.append({'rarity': rarity, 'item_type': '角色' if '角色' in pulls[-1][1] else '光锥', 'item': item})

        return pulls

    def show_message(self, message, color=RESET):
        if color == RED:
            messagebox.showerror("错误", message)
        elif color == GREEN:
            messagebox.showinfo("成功", message)
        elif color == YELLOW:
            messagebox.showwarning("警告", message)
        else:
            messagebox.showinfo("提示", message)
        


    def show_info(self):
        info = f"""总抽卡次数: {self.total_pulls}
当前五星保底: {self.pity_5}
当前四星保底: {self.pity_4}
获得五星次数: {len(self.gold_records)}
获得四星次数: {len(self.purple_records)}
歪掉五星次数: {self.failed_featured_5star}
抽中UP五星次数: {self.successful_featured_5star}
距离上次五星: {self.pulls_since_last_5star}
大保底状态: {'是' if self.is_guaranteed else '否'}

各卡池抽卡次数:
"""
        for banner, pulls in self.banner_pulls.items():
            info += f"{banner}: {pulls}\n"

        messagebox.showinfo("抽卡统计信息", info)



    def categorize_banners(self):
        character_banners = []
        weapon_banners = []
        standard_banner = self.get_standard_banner()
        for banner_id, banner_info in self.pools['banners'].items():
            if banner_id != standard_banner:
                banner_name = banner_info.get('name', banner_id)
                if banner_info.get('pool_type') == 'character':
                    character_banners.append((banner_id, banner_name))
                elif banner_info.get('pool_type') == 'weapon':
                    weapon_banners.append((banner_id, banner_name))
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
        self.pull_history = []
        self.save_state()


# GachaSystem 部分结束


# GUI 部分
if __name__ == "__main__":
    root = tk.Tk()
    gui = GachaSimulatorGUI(root)
    root.mainloop()