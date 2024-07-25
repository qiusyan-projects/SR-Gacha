import random
from ruamel.yaml import YAML
import os
import requests
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, StringVar, Toplevel, Label, Button, Entry, Listbox, END, BooleanVar

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
    "可以使用 'info' 命令查看抽卡统计信息。",
    "大保底时，下一个5星角色必定是UP角色。",
    "每10次抽卡必定至少有一个4星或以上角色/光锥。",
    "这个Tip我还没想好怎么写...",
    "为了防止抽卡记录过多导致数据读取缓慢，抽卡记录中没有三星的光锥获得记录",
    "你说得对，但是...",
    "来点Star叭！",
    "这是一个小Tip，只有聪明人才能看到它的内容",
    "可以修改卡池文件来实现其他游戏的抽卡效果，具体请移步项目README"
]

yaml = YAML()

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
            self.show_message(f"卡池 '{banner_name}' 不存在。", RED)
            return

        self.current_banner = banner_name
        self.show_message(f"已切换到卡池: {banner_name}", BLUE)
        self.update_gui_banner_name()
        self.save_state()

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
        
    def update_gui_banner_name(self):
        banner_label_var.set(f"当前卡池: {self.current_banner}" if self.current_banner else "当前卡池: 未选择")

    def update_gui_pull_history(self, pulls):
        pull_history_text.configure(state='normal')
        pull_history_text.insert(tk.END, f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for rarity, item_type, item in pulls:
            if rarity == '5_star':
                color = GOLD
            elif rarity == '4_star':
                color = PURPLE
            else:
                color = RESET
            pull_history_text.insert(tk.END, f"{rarity} - {item_type}: {item}\n", color)
        pull_history_text.configure(state='disabled')
        pull_history_text.see(tk.END)

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


    def toggle_mode(self, is_night_mode):
        bg_color = NIGHT_BG if is_night_mode else DAY_BG
        fg_color = NIGHT_FG if is_night_mode else DAY_FG
        root.configure(bg=bg_color)
        pull_history_text.configure(bg=bg_color, fg=fg_color)
        pull_history_text.tag_config(RESET, foreground=fg_color)
        banner_label.configure(bg=bg_color, fg=fg_color)
        tip_label.configure(bg=bg_color, fg=fg_color)
        for widget in [banner_listbox, switch_banner_button, pull_1_button, pull_10_button, info_button, mode_button]:
            widget.configure(bg=bg_color, fg=fg_color)

def show_random_tip():
    tip_label.config(text=random.choice(TIPS))

def on_pull(num_pulls):
    pulls = gacha_system.perform_pull(num_pulls)
    if pulls:
        gacha_system.update_gui_pull_history(pulls)
        gacha_system.save_state()

def on_switch_banner():
    selected_indices = banner_listbox.curselection()
    if selected_indices:
        selected_banner = banner_listbox.get(selected_indices[0])
        gacha_system.switch_banner(selected_banner)

def on_show_info():
    gacha_system.show_info()

# Initialize the GachaSystem
gacha_system = GachaSystem(BANNER_FILE)

# Initialize GUI
root = tk.Tk()
root.title("Gacha Simulator")
root.geometry("1024x900")

# Banner label
banner_label_var = StringVar()
banner_label = Label(root, textvariable=banner_label_var, font=("Arial", 14))
banner_label.pack(pady=10)
gacha_system.update_gui_banner_name()

# Mode switch
def toggle_mode():
    is_night_mode.set(not is_night_mode.get())
    mode_button.config(text="切换到日间模式" if is_night_mode.get() else "切换到夜间模式")
    gacha_system.toggle_mode(is_night_mode.get())

is_night_mode = BooleanVar(value=False)
mode_button = Button(root, text="切换到夜间模式", command=lambda: toggle_mode())
mode_button.pack(pady=5)



# Banner listbox
banner_listbox = Listbox(root, height=10)
for banner in gacha_system.banners:
    banner_listbox.insert(END, banner)
banner_listbox.pack(pady=10)

switch_banner_button = Button(root, text="切换卡池", command=on_switch_banner)
switch_banner_button.pack(pady=5)

# Pull buttons
pull_1_button = Button(root, text="抽一次", command=lambda: on_pull(1))
pull_1_button.pack(pady=5)

pull_10_button = Button(root, text="抽十次", command=lambda: on_pull(10))
pull_10_button.pack(pady=5)

# Info button
info_button = Button(root, text="查看统计信息", command=on_show_info)
info_button.pack(pady=5)

# Pull history
pull_history_text = scrolledtext.ScrolledText(root, state='disabled', width=80, height=20, wrap=tk.WORD)
pull_history_text.pack(pady=10)
pull_history_text.tag_config(GOLD, foreground=GOLD)
pull_history_text.tag_config(PURPLE, foreground=PURPLE)
pull_history_text.tag_config(RESET, foreground=RESET)

# Tips
tip_label = Label(root, text="", font=("Arial", 10), fg="blue")
tip_label.pack(pady=10)
show_random_tip()
info_button = Button(root, text="随机Tips", command=show_random_tip)
info_button.pack(pady=5)

# Start the main loop
root.mainloop()