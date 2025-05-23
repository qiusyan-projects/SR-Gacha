import random
from ruamel.yaml import YAML
import os
import requests
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, StringVar, Toplevel, Label, Button, Entry, Listbox, END, BooleanVar, font, ttk, simpledialog, PhotoImage
from PIL import Image, ImageTk
import re
import sys
import base64
import io
# from ttkthemes import ThemedTk

# Colors and other constants
PURPLE = '#BA55D3'
GOLD = '#FFD700'
GREEN = '#32CD32'
RED = '#FF4500'
RESET = '#FFFFFF'
CYAN = '#00CED1'
YELLOW = '#FFFF00'
BLUE = '#1E90FF'
CHARACTER_DISPLAY_NAME = '角色'
WEAPON_DISPLAY_NAME = '光锥'

BANNER_FILE = 'banners.yml'
GITHUB_PROXY = ''
BANNER_DOWNLOAD_URL = "https://raw.gh.qiusyan.top/qiusyan-projects/SR-Gacha/main/banners.yml"
TIPS = [
    "大保底时，下一个5星角色必定是UP角色。",
    "每10次抽卡必定至少有一个4星或以上角色/光锥。",
    "这个Tip我还没想好怎么写...",
    "你说得对，但是...",
    "来点Star叭！",
    "这是一个小Tip，只有聪明人才能看到它的内容",
    "可以修改卡池文件来实现其他游戏的抽卡效果",
    "本来我是想整个主题的，但是好像加上之后会变得很卡我就删了",
    "你看什么看！",
    "双击抽卡记录可以查看物品的详细信息",
    "双击卡池可以查看卡池的信息",
    "角色池的保底和概率跟光锥池的都不一样",
    "可以通过修改抽卡概率来达成任意抽卡效果"
]

yaml = YAML()


class GachaSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # 隐藏主窗口

        self.root.title("崩坏：星穹铁道抽卡模拟器")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)  # 设置最小窗口大小
        
        # 设置默认字体为微软雅黑
        self.default_font_name = 'Microsoft YaHei'
        self.default_font = (self.default_font_name, 10)
        self.large_font = (self.default_font_name, 14)

        # 检查更新
        self.check_for_updates()

        self.character_five_star_small_pity_var_random = BooleanVar()
        self.character_five_star_small_pity_var_must_waste = BooleanVar()
        self.character_five_star_small_pity_var_must_not_waste = BooleanVar()
        self.weapon_five_star_small_pity_var_random = BooleanVar()
        self.weapon_five_star_small_pity_var_must_waste = BooleanVar()
        self.weapon_five_star_small_pity_var_must_not_waste = BooleanVar()
        self.character_four_star_small_pity_var_random = BooleanVar()
        self.character_four_star_small_pity_var_must_waste = BooleanVar()
        self.character_four_star_small_pity_var_must_not_waste = BooleanVar()
        self.weapon_four_star_small_pity_var_random = BooleanVar()
        self.weapon_four_star_small_pity_var_must_waste = BooleanVar()
        self.weapon_four_star_small_pity_var_must_not_waste = BooleanVar()

        # 初始化主题选择        
        # self.setup_theme_selection()

        # 确保 GachaSystem 已正确初始化
        if not hasattr(self.gacha_system, 'pools'):
            messagebox.showerror("错误", "无法加载卡池数据。请重新启动程序。")
            sys.exit(1)

        # 初始化其他GUI组件
        self.initialize_gui_components()
        
        # 显示主窗口
        self.root.deiconify()
        

    def check_for_updates(self):
        if os.path.exists(BANNER_FILE):
            check_update = messagebox.askyesno("更新确认", "是否检查卡池文件更新？（修改卡池了的不要选更新）")
            no_update = not check_update
        else:
            no_update = False  # 如果文件不存在，强制更新
        
        self.gacha_system = GachaSystem(BANNER_FILE, no_update=no_update)

    def initialize_gui_components(self):
        self.banner_id_map = {}
        self.banner_name_map = {}
        self.initialize_banner_maps()
        self.setup_gui()

    def initialize_banner_maps(self):
        character_banners, weapon_banners = self.gacha_system.categorize_banners()
        all_banners = character_banners + weapon_banners
        
        # print("初始化 banner_id_map:")  # 调试信息
        for banner_id, banner_name in all_banners:
            self.banner_id_map[banner_name] = banner_id
            self.banner_name_map[banner_id] = banner_name
            # print(f"  {banner_name} -> {banner_id}")  # 调试信息
        
        # print("banner_id_map 内容:")  # 调试信息
        # for name, id in self.banner_id_map.items():
            # print(f"  {name}: {id}")  # 调试信息

    def setup_gui(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        # Create left and right frames
        self.left_frame = ttk.Frame(self.main_frame, width=250)
        self.right_frame = ttk.Frame(self.main_frame)

        # Pack frames
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Ensure the left frame maintains its width
        self.left_frame.pack_propagate(False)

        # Left frame content
        self.setup_left_frame()

        # Right frame content
        self.setup_right_frame()

    def setup_left_frame(self):
        # Banner controls
        banner_frame = ttk.LabelFrame(self.left_frame, text="卡池切换")
        banner_frame.pack(pady=2, padx=5, fill=tk.X)

        self.toggle_button = ttk.Button(banner_frame, text=f"切换到{WEAPON_DISPLAY_NAME}池列表", command=self.toggle_banner_type)
        self.toggle_button.grid(row=0, column=0, pady=2, padx=2, sticky="ew")

        self.standard_banner_button = ttk.Button(banner_frame, text="切换到常驻池", command=self.select_standard_banner)
        self.standard_banner_button.grid(row=0, column=1, pady=2, padx=2, sticky="ew")

        self.banner_listbox = tk.Listbox(banner_frame, height=8, font=self.default_font)
        self.banner_listbox.grid(row=1, column=0, columnspan=2, pady=2, padx=2, sticky="nsew")
        
        self.switch_banner_button = ttk.Button(banner_frame, text="切换到选择的卡池", command=self.on_switch_banner)
        self.switch_banner_button.grid(row=2, column=0, columnspan=2, pady=2, padx=2, sticky="ew")

        banner_frame.columnconfigure(0, weight=1)
        banner_frame.columnconfigure(1, weight=1)

        # Gacha controls
        gacha_frame = ttk.LabelFrame(self.left_frame, text="抽卡")
        gacha_frame.pack(pady=2, padx=5, fill=tk.X)

        self.pull_1_button = ttk.Button(gacha_frame, text="抽一次", command=lambda: self.on_pull(1))
        self.pull_1_button.grid(row=0, column=0, pady=2, padx=2, sticky="ew")

        self.pull_10_button = ttk.Button(gacha_frame, text="十连抽！", command=lambda: self.on_pull(10))
        self.pull_10_button.grid(row=0, column=1, pady=2, padx=2, sticky="ew")

        self.pull_pity_button = ttk.Button(gacha_frame, text="抽一个小保底", command=lambda: self.on_pull(self.get_current_pity()))
        self.pull_pity_button.grid(row=1, column=0, columnspan=2, pady=2, padx=2, sticky="ew")

        gacha_frame.columnconfigure(0, weight=1)
        gacha_frame.columnconfigure(1, weight=1)

        # Utility controls
        util_frame = ttk.LabelFrame(self.left_frame, text="工具箱")
        util_frame.pack(pady=2, padx=5, fill=tk.X)

        self.random_tip_button = ttk.Button(util_frame, text="随机Tips", command=self.show_random_tip)
        self.random_tip_button.grid(row=0, column=0, pady=2, padx=2, sticky="ew")

        self.clear_data_button = ttk.Button(util_frame, text="修改当前卡池概率", command=self.open_probability_settings)
        self.clear_data_button.grid(row=0, column=1, pady=2, padx=2, sticky="ew")

        self.prob_settings_button = ttk.Button(util_frame, text="重置抽卡统计数据", command=self.clear_gacha_data)
        self.prob_settings_button.grid(row=2, column=0, columnspan=2, pady=2, padx=2, sticky="ew")

        self.version_button = ttk.Button(util_frame, text="查看当前版本", command=self.show_version)
        self.version_button.grid(row=1, column=0, pady=2, padx=2, sticky="ew")

        self.update_button = ttk.Button(util_frame, text="检查卡池更新", command=self.check_pool_update)
        self.update_button.grid(row=1, column=1, pady=2, padx=2, sticky="ew")

        util_frame.columnconfigure(0, weight=1)
        util_frame.columnconfigure(1, weight=1)

        # Statistics display
        self.stats_frame = ttk.LabelFrame(self.left_frame, text="统计信息")
        self.stats_frame.pack(pady=2, padx=5, fill=tk.X)

        self.current_stats_label = ttk.Label(self.stats_frame, text="当前显示的是角色池的数据", font=self.default_font)
        self.current_stats_label.pack(pady=2)
        self.current_banner_type = StringVar(value="character")

        self.stats_text = tk.Text(self.stats_frame, width=25, font=self.default_font, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.X, expand=True)
        self.stats_text.config(state=tk.DISABLED)

        # 将双击指令绑定到Listbox
        self.banner_listbox.bind("<Double-1>", self.show_banner_details)

        self.update_banner_list()
        self.update_stats_display()

    def setup_right_frame(self):
        # Banner info frame
        banner_info_frame = ttk.Frame(self.right_frame)
        banner_info_frame.pack(fill=tk.X, pady=10, padx=10)

        self.banner_label_var = StringVar()
        self.banner_label = ttk.Label(banner_info_frame, textvariable=self.banner_label_var, font=self.large_font)
        self.banner_label.pack(side=tk.LEFT)

        self.clear_history_button = ttk.Button(banner_info_frame, text="清空抽卡记录", command=self.clear_pull_history)
        self.clear_history_button.pack(side=tk.RIGHT)

        # Pull history frame
        history_frame = ttk.LabelFrame(self.right_frame, text="抽卡历史")
        history_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Pull history table
        columns = ('时间', '星级', '类型', '名称', '卡池', '是否UP')
        self.pull_history_tree = ttk.Treeview(history_frame, columns=columns, show='headings')
        
        # Define column headings and widths
        column_widths = {'时间': 150, '星级': 50, '类型': 50, '名称': 150, '卡池': 150, '是否UP': 50}
        for col in columns:
            self.pull_history_tree.heading(col, text=col, anchor='center')
            self.pull_history_tree.column(col, width=column_widths[col], anchor='center')
        
        # Add vertical scrollbar
        vsb = ttk.Scrollbar(history_frame, orient="vertical", command=self.pull_history_tree.yview)
        self.pull_history_tree.configure(yscrollcommand=vsb.set)
        
        # Add horizontal scrollbar
        hsb = ttk.Scrollbar(history_frame, orient="horizontal", command=self.pull_history_tree.xview)
        self.pull_history_tree.configure(xscrollcommand=hsb.set)

        # Grid layout for Treeview and scrollbars
        self.pull_history_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)

        # Tips frame
        tips_frame = ttk.LabelFrame(self.right_frame, text="Tips")
        tips_frame.pack(pady=10, padx=10, fill=tk.X)

        self.tip_label = ttk.Label(tips_frame, text="", font=self.default_font, foreground="blue", wraplength=500)
        self.tip_label.pack(pady=5, padx=5)

        self.update_gui_banner_name()
        self.show_random_tip()

        # Bind double click event to Treeview for item details
        self.pull_history_tree.bind("<Double-1>", self.show_item_details)


    def toggle_banner_type(self):
        if self.current_banner_type.get() == "character":
            self.current_banner_type.set("weapon")
            self.toggle_button.config(text=f"切换到{CHARACTER_DISPLAY_NAME}池列表")
        else:
            self.current_banner_type.set("character")
            self.toggle_button.config(text=f"切换到{WEAPON_DISPLAY_NAME}池列表")
        self.update_banner_list()

    def select_standard_banner(self):
        standard_banner = self.gacha_system.get_standard_banner()
        if standard_banner:
            if self.gacha_system.switch_banner(standard_banner):
                banner_info = self.gacha_system.pools['banners'].get(standard_banner, {})
                banner_name = banner_info.get('name', standard_banner)
                self.update_gui_banner_name()
                self.update_banner_list()
                self.update_stats_display('standard')  
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
            elif 'weapon_up_5_star' in banner_info:
                up_weapon = banner_info['weapon_up_5_star'][0]
                display_name = f"{banner_name} - UP: {up_weapon}"
            else:
                display_name = banner_name
            self.banner_listbox.insert(tk.END, display_name)
            if self.gacha_system.current_banner is not None and banner_id == self.gacha_system.current_banner:
                self.banner_listbox.selection_set(tk.END)

    def on_switch_banner(self):
        # print("开始切换卡池...")  # 调试信息
        selected_indices = self.banner_listbox.curselection()
        # print(f"选中的索引: {selected_indices}")  # 调试信息
        
        if not selected_indices:
            messagebox.showinfo("提示", "你还没有选择一个卡池")
            return
        
        selected_banner_display_name = self.banner_listbox.get(selected_indices[0])
        selected_banner_name = selected_banner_display_name.split(" - UP:")[0]
        selected_banner_id = self.banner_id_map.get(selected_banner_name)
        # print(f"选中的卡池ID: {selected_banner_id}")  # 调试信息
        
        if selected_banner_id:
            if self.gacha_system.switch_banner(selected_banner_id):
                self.update_banner_list()
                self.update_gui_banner_name()
                
                # 获取新卡池的类型并更新统计显示
                new_pool_type = self.gacha_system.pools['banners'][selected_banner_id].get('pool_type', 'standard')
                self.update_stats_display(new_pool_type)
                
                banner_info = self.gacha_system.pools['banners'].get(selected_banner_id, {})
                banner_name = banner_info.get('name', selected_banner_name)
                messagebox.showinfo("提示", f"已切换到卡池：{banner_name}")
            else:
                messagebox.showerror("错误", f"切换到卡池 {selected_banner_name} 失败")
        else:
            messagebox.showerror("错误", f"未找到卡池 {selected_banner_name} 的ID")

        self.update_stats_display()

    def show_banner_details(self, event):
        # 获取双击事件中的选中项
        selected_index = event.widget.nearest(event.y)
        selected_banner_display_name = self.banner_listbox.get(selected_index)
        
        # 从显示名称中提取卡池名称（去除UP信息）
        selected_banner_name = selected_banner_display_name.split(" - UP:")[0]
        
        # 通过卡池名称获取卡池ID
        selected_banner_id = self.banner_id_map.get(selected_banner_name)
        
        # 使用卡池ID获取卡池详细信息
        if selected_banner_id:
            banner_info = self.gacha_system.pools['banners'].get(selected_banner_id, {})
        else:
            banner_info = {}
        
        # 根据卡池类型确定显示的文本
        pool_type = banner_info.get('pool_type', 'standard')  # 默认为'standard'，如果未指定类型
        pool_type_display = WEAPON_DISPLAY_NAME if pool_type == 'weapon' else CHARACTER_DISPLAY_NAME
        
        # 获取UP的五星和四星项目信息
        up_5_star_key = f'{pool_type}_up_5_star'
        up_4_star_key = f'{pool_type}_up_4_star'
        up_5_star_info = banner_info.get(up_5_star_key, [])
        up_4_star_info = banner_info.get(up_4_star_key, [])

        # 构造详细信息字符串
        details = f"卡池名称: {banner_info.get('name', '未知')}\n" \
                f"卡池类型: {pool_type_display}\n" \
                f"UP的五星{pool_type_display}: {' | '.join(up_5_star_info) if up_5_star_info else '无'}\n" \
                f"UP的四星{pool_type_display}: {' | '.join(up_4_star_info) if up_4_star_info else '无'}"
        
        # 显示详细信息
        messagebox.showinfo("卡池详情", details)

    def on_pull(self, num_pulls):
        pulls = self.gacha_system.perform_pull(num_pulls)
        if pulls:
            self.update_gui_pull_history(pulls)
            self.gacha_system.save_state()
            
            # 获取当前卡池类型并更新统计显示
            current_pool_type = self.gacha_system.pools['banners'][self.gacha_system.current_banner].get('pool_type', 'standard')
            self.update_stats_display(current_pool_type)


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

        for rarity, item_type, item in pulls:
            # Convert rarity to display format
            display_rarity = rarity.replace('_star', '星')
            tag = display_rarity.split('星')[0]  # '5星' becomes '5'
            
            # Determine if it's an UP item
            is_up = "否"
            if not is_standard_banner and rarity in ['4_star', '5_star']:
                up_items = current_banner_info.get(f"{item_type}_up_{rarity}", [])
                if not up_items and item_type == CHARACTER_DISPLAY_NAME:
                    up_items = current_banner_info.get(f"character_up_{rarity}", [])
                elif not up_items and item_type == WEAPON_DISPLAY_NAME:
                    up_items = current_banner_info.get(f"weapon_up_{rarity}", [])
                
                is_up = "是" if item in up_items else "否"
            
            # For 3-star items and standard banner pulls, leave the UP column empty
            if rarity == '3_star' or is_standard_banner:
                is_up = ""

            self.pull_history_tree.insert('', 0, values=(current_time, display_rarity, item_type, item, current_banner_name, is_up), tags=(tag,))
        
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

    def update_stats_display(self, pool_type=None):
        if pool_type is None:
            if self.gacha_system.current_banner:
                banner_info = self.gacha_system.pools['banners'].get(self.gacha_system.current_banner, {})
                pool_type = banner_info.get('pool_type', 'standard')
            else:
                pool_type = 'standard'

        if pool_type == 'character':
            pity_5 = self.gacha_system.character_pity_5
            pity_4 = self.gacha_system.character_pity_4
            gold_records = self.gacha_system.character_gold_records
            purple_records = self.gacha_system.character_purple_records
            failed_featured_5star = self.gacha_system.character_failed_featured_5star
            successful_featured_5star = self.gacha_system.character_successful_featured_5star
            pulls_since_last_5star = self.gacha_system.character_pulls_since_last_5star
            is_guaranteed = self.gacha_system.character_is_guaranteed
            stats_type = f"{CHARACTER_DISPLAY_NAME}池"
            pool_pulls = self.gacha_system.character_pulls
            five_star_pity = self.gacha_system.current_prob['character_five_star_pity']
            four_star_pity = self.gacha_system.current_prob['character_four_star_pity']
            five_star_small_pity_mechanism = self.gacha_system.current_prob['character_five_star_small_pity_mechanism']
            four_star_small_pity_mechanism = self.gacha_system.current_prob['character_four_star_small_pity_mechanism']
            five_star_big_pity_enabled = self.gacha_system.current_prob['character_five_star_big_pity_enabled']
            four_star_big_pity_enabled = self.gacha_system.current_prob['character_four_star_big_pity_enabled']
            four_star_guaranteed = self.gacha_system.character_four_star_guaranteed
        elif pool_type == 'weapon':
            pity_5 = self.gacha_system.weapon_pity_5
            pity_4 = self.gacha_system.weapon_pity_4
            gold_records = self.gacha_system.weapon_gold_records
            purple_records = self.gacha_system.weapon_purple_records
            failed_featured_5star = self.gacha_system.weapon_failed_featured_5star
            successful_featured_5star = self.gacha_system.weapon_successful_featured_5star
            pulls_since_last_5star = self.gacha_system.weapon_pulls_since_last_5star
            is_guaranteed = self.gacha_system.weapon_is_guaranteed
            stats_type = f"{WEAPON_DISPLAY_NAME}池"
            pool_pulls = self.gacha_system.weapon_pulls
            five_star_pity = self.gacha_system.current_prob['weapon_five_star_pity']
            four_star_pity = self.gacha_system.current_prob['weapon_four_star_pity']
            five_star_small_pity_mechanism = self.gacha_system.current_prob['weapon_five_star_small_pity_mechanism']
            four_star_small_pity_mechanism = self.gacha_system.current_prob['weapon_four_star_small_pity_mechanism']
            five_star_big_pity_enabled = self.gacha_system.current_prob['weapon_five_star_big_pity_enabled']
            four_star_big_pity_enabled = self.gacha_system.current_prob['weapon_four_star_big_pity_enabled']
            four_star_guaranteed = self.gacha_system.weapon_four_star_guaranteed
        else:
            pity_5 = self.gacha_system.pity_5
            pity_4 = self.gacha_system.pity_4
            gold_records = self.gacha_system.gold_records
            purple_records = self.gacha_system.purple_records
            failed_featured_5star = self.gacha_system.failed_featured_5star
            successful_featured_5star = self.gacha_system.successful_featured_5star
            pulls_since_last_5star = self.gacha_system.pulls_since_last_5star
            is_guaranteed = self.gacha_system.is_guaranteed
            stats_type = "常驻池"
            pool_pulls = self.gacha_system.standard_pulls
            five_star_pity = self.gacha_system.current_prob['standard_five_star_pity']
            four_star_pity = self.gacha_system.current_prob['standard_four_star_pity']
            five_star_big_pity_enabled = True
            four_star_big_pity_enabled = True
            four_star_guaranteed = self.gacha_system.four_star_guaranteed

        luck_rating = self.gacha_system.calculate_luck(pool_type)

        self.current_stats_label.config(text=f"当前显示的是{stats_type}的数据")


        if len(gold_records) > 0: # 如果出金次数大于1，执行计算
            avg_gold_pulls = sum(gold_records) / len(gold_records)  # 平均抽数出金
        else: 
            avg_gold_pulls = "暂无数据"

        if gold_records: # 如果列表不为空
            min_gold_records = min(gold_records)
            max_gold_records = max(gold_records)
        else:
            min_gold_records = "暂无数据"
            max_gold_records = "暂无数据"
        
        total_featured_5star = successful_featured_5star + failed_featured_5star
        if total_featured_5star > 0: # 如果总数大于0
            success_rate = successful_featured_5star / total_featured_5star * 100
        else:
            success_rate = "暂无数据"
            

        pool_pulls_str = f"{stats_type}的抽取次数: {pool_pulls}"
        next_pity_5_str = f"距离下一个5星保底的抽数: {five_star_pity - pity_5}" 
        next_pity_4_str = f"距离下一个4星保底: {four_star_pity - pity_4}" 
        get_gold_records_str = f"获得5星次数: {len(gold_records)}"
        get_purple_records_str = f"获得4星次数: {len(purple_records)}"
        min_gold_records_str = f"最少抽数出金: {min_gold_records}"
        max_gold_records_str = f"最多抽数出金: {max_gold_records}"

        if isinstance(avg_gold_pulls, (int, float)):  # 检查 avg_gold_pulls 是否是数字类型
            avg_gold_pulls_str = f"平均出金抽数: {avg_gold_pulls:.2f}"
        else:
            avg_gold_pulls_str = f"平均出金抽数: {avg_gold_pulls}" 

        if pool_type != 'standard':
            failed_featured_5star_str = f"歪掉5星次数: {failed_featured_5star}"
        else:
            failed_featured_5star_str = f"歪掉5星次数: 无"

        if pool_type != 'standard':
            if isinstance(success_rate, (int, float)):  # 检查 success_rate 是否是数字类型
                success_rate_str = f"小保底不歪概率: {success_rate:.2f}%"
            else:
                success_rate_str = f"小保底不歪概率: {success_rate}"
        else:
            success_rate_str = f"小保底不歪概率: 无"

        pulls_since_last_5star_str = f"距离上次5星: {pulls_since_last_5star}"

        if five_star_big_pity_enabled:
            if pool_type != 'standard': 
                five_star_is_guaranteed_str = f"5星大保底状态: {'是' if is_guaranteed else '否'}"
            else:
                five_star_is_guaranteed_str = f"5星大保底状态: 无"
        else:
            five_star_is_guaranteed_str = f"5星大保底状态: 你没有启用大保底机制"


        if four_star_big_pity_enabled:
            if pool_type != 'standard': 
                four_star_guaranteed_str = f"4星大保底状态: {'是' if four_star_guaranteed else '否'}"
            else:
                four_star_guaranteed_str = f"4星大保底状态: 无"
        else:
            four_star_guaranteed_str = f"4星大保底状态: 你没有启用大保底机制"



        if pool_type != 'standard': 
            if five_star_small_pity_mechanism == 'random':
                five_star_small_pity_mechanism_str = f"5星小保底机制: 默认"
            elif five_star_small_pity_mechanism == 'must_not_waste':
                five_star_small_pity_mechanism_str = f"5星小保底机制: 必不歪"
            else:
                five_star_small_pity_mechanism_str = f"5星小保底机制: 必歪"
        else:
            five_star_small_pity_mechanism_str = f"5星小保底机制: 无"

        if pool_type != 'standard': 
            if four_star_small_pity_mechanism == 'random':
                four_star_small_pity_mechanism_str = f"4星小保底机制: 默认"
            elif four_star_small_pity_mechanism == 'must_not_waste':
                four_star_small_pity_mechanism_str = f"4星小保底机制: 必不歪"
            else:
                four_star_small_pity_mechanism_str = f"4星小保底机制: 必歪"
        else:
            four_star_small_pity_mechanism_str = f"4星小保底机制: 无"

        luck_rating_str = f"抽卡运势: {luck_rating}"

        # 使用变量控制输出
        stats = (
            f"{pool_pulls_str}\n"
            f"{next_pity_5_str}\n"
            f"{next_pity_4_str}\n"
            f"{get_gold_records_str}\n"
            f"{get_purple_records_str}\n"
            f"{min_gold_records_str}\n"
            f"{max_gold_records_str}\n"
            f"{avg_gold_pulls_str}\n"
            f"{success_rate_str}\n"
            f"{pulls_since_last_5star_str}\n"
            f"{five_star_small_pity_mechanism_str}\n"
            f"{four_star_small_pity_mechanism_str}\n"
            f"{five_star_is_guaranteed_str}\n"
            f"{four_star_guaranteed_str}\n"
            f"{luck_rating_str}"
        )

        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)
        self.stats_text.config(state=tk.DISABLED)

        # 动态调整高度
        self.stats_text.update_idletasks()
        height = self.stats_text.count('1.0', 'end', 'displaylines')
        self.stats_text.config(height=height)

    def show_version(self):
        version = "2.2.11" 
        author = "QiuSYan & Claude"
        github = "qiusyan-projects/SR-Gacha"
        other = "来点Star叭~💖"
        messagebox.showinfo("版本信息", f"当前版本: {version}\n作者：{author}\nGithub：{github}\n{other}")   
        try:
            response = requests.get(f"https://api.github.com/repos/{github}/releases/latest")
            response.raise_for_status()
        except requests.exceptions.SSLError:
            print("发生SSL错误，尝试不验证证书进行请求...")
            response = requests.get(f"https://api.github.com/repos/{github}/releases/latest", verify=False)
            response.raise_for_status()
        except requests.RequestException as e:
            messagebox.showerror("错误", f"检查更新时发生错误: {e}")

        latest_release = response.json()
        latest_version = latest_release['tag_name']
            
        # 版本号比较
        if self.compare_versions(latest_version, version):
            messagebox.showinfo("更新提示", f"检测到新版本 {latest_version}，请及时更新！")
        else:
            messagebox.showinfo("已是最新版本", "你的程序已是最新版本。")


    def compare_versions(self, version1, version2):
        # 使用正则表达式去除版本号前的非数字字符（如 'v'）
        version1 = re.sub(r'^[^0-9]+', '', version1)
        version2 = re.sub(r'^[^0-9]+', '', version2)

        # 将版本号字符串分割并转换为整数元组
        v1 = tuple(map(int, version1.split('.')))
        v2 = tuple(map(int, version2.split('.')))

        # 比较两个版本号
        return v1 > v2

    def check_pool_update(self):
        # status, message = self.gacha_system.check_and_update_pool_file()
        status = self.gacha_system.check_and_update_pool_file()
        try:
            if status == "updated":
                self.gacha_system.load_pools(self.gacha_system.pool_file)
                self.update_banner_list()
                message = "卡池文件已更新到最新版本。"
            elif status == "current":
                self.gacha_system.load_pools(self.gacha_system.pool_file)
                self.update_banner_list()
                message = "卡池文件已是最新版本。"
        except requests.RequestException as e:
            message = f"检查更新时发生错误: {e}"
        messagebox.showinfo("检查更新", message)

    def show_item_details(self, event):
        selected_items = self.pull_history_tree.selection()
        if not selected_items:  # 如果没有选中任何项目
            return  # 直接返回，不执行任何操作
        
        item = selected_items[0]  # 获取选中的第一个项目
        item_details = self.pull_history_tree.item(item, "values")
        messagebox.showinfo("物品详情", f"名称: {item_details[3]}\n类型: {item_details[2]}\n星级: {item_details[1]}\n是否UP: {item_details[5]}")


    def open_probability_settings(self, pool_type=None):
        # 创建一个新的顶级窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("概率设置")
        settings_window.geometry("450x500")  # 窗口大小，宽x长

        # 创建 Notebook 并添加到窗口
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill="both", expand=True)

        # 创建角色池、光锥池和常驻池的标签页
        tab_character = ttk.Frame(notebook, padding="30")
        tab_weapon = ttk.Frame(notebook, padding="30")
        tab_standard = ttk.Frame(notebook, padding="30")

        # 添加标签页到 Notebook
        notebook.add(tab_character, text=f"{CHARACTER_DISPLAY_NAME}池")
        notebook.add(tab_weapon, text=f"{WEAPON_DISPLAY_NAME}池")
        notebook.add(tab_standard, text="常驻池")

        if pool_type is None:
            if self.gacha_system.current_banner:
                banner_info = self.gacha_system.pools['banners'].get(self.gacha_system.current_banner, {})
                pool_type = banner_info.get('pool_type', 'standard')
            else:
                pool_type = 'standard'

        # 根据pool_type设置Notebook的当前标签页
        if pool_type == 'character':
            notebook.select(tab_character)
        elif pool_type == 'weapon':
            notebook.select(tab_weapon)
        else:  
            notebook.select(tab_standard)

        # print(f"当前卡池类型：{pool_type}") # Debug

        # 角色池概率设置
        def setup_character_prob_tab(self, tab):
            self.character_five_star_prob = tk.StringVar(value=str(self.gacha_system.current_prob['character_five_star_base']))
            ttk.Label(tab, text="5星基础概率:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.character_five_star_prob, width=10).grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(0.006 = 0.6%)").grid(row=0, column=2, sticky="w", padx=5, pady=5)

            self.character_five_star_success_prob = tk.StringVar(value=str(self.gacha_system.current_prob['character_five_star_success_prob']))
            ttk.Label(tab, text="5星不歪概率:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.character_five_star_success_prob, width=10).grid(row=1, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(0.5 = 50%)").grid(row=1, column=2, sticky="w", padx=5, pady=5)

            self.character_five_star_pity = tk.StringVar(value=str(self.gacha_system.current_prob['character_five_star_pity']))
            ttk.Label(tab, text="5星保底抽数:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.character_five_star_pity, width=10).grid(row=2, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(默认: 90)").grid(row=2, column=2, sticky="w", padx=5, pady=5)
            
            self.character_four_star_prob = tk.StringVar(value=str(self.gacha_system.current_prob['character_four_star_base']))
            ttk.Label(tab, text="4星基础概率:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.character_four_star_prob, width=10).grid(row=3, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(0.051 = 5.1%)").grid(row=3, column=2, sticky="w", padx=5, pady=5)
            
            self.character_four_star_success_prob = tk.StringVar(value=str(self.gacha_system.current_prob['character_four_star_success_prob']))
            ttk.Label(tab, text="4星不歪概率:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.character_four_star_success_prob, width=10).grid(row=4, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(0.5 = 50%)").grid(row=4, column=2, sticky="w", padx=5, pady=5)

            self.character_four_star_pity = tk.StringVar(value=str(self.gacha_system.current_prob['character_four_star_pity']))
            ttk.Label(tab, text="4星保底抽数:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.character_four_star_pity, width=10).grid(row=5, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(默认: 10)").grid(row=5, column=2, sticky="w", padx=5, pady=5)  

            # 角色池五星小保底
            self.setup_character_5_star_small_pity(tab_character)

            # 角色池四星小保底
            self.setup_character_4_star_small_pity(tab_character)
            
            # 角色池五星大保底机制设置
            self.character_five_star_big_pity_enabled = tk.BooleanVar(value=self.gacha_system.current_prob['character_five_star_big_pity_enabled'])
            character_five_star_big_pity_checkbox = ttk.Checkbutton(tab, text="启用5星大保底机制", variable=self.character_five_star_big_pity_enabled)
            character_five_star_big_pity_checkbox.grid(row=8, column=0, columnspan=3, sticky="w", padx=5, pady=5)

            # 角色池四星大保底机制设置
            self.character_four_star_big_pity_enabled = tk.BooleanVar(value=self.gacha_system.current_prob['character_four_star_big_pity_enabled'])
            character_four_star_big_pity_checkbox = ttk.Checkbutton(tab, text="启用4星大保底机制", variable=self.character_four_star_big_pity_enabled)
            # character_four_star_big_pity_checkbox.grid(row=13, column=2, columnspan=3, sticky="w", padx=(20, 0), pady=5)
            character_four_star_big_pity_checkbox.grid(row=8, column=2, columnspan=3,sticky="w" ,padx=5, pady=5)


        setup_character_prob_tab(self, tab_character)

        # 光锥池概率设置
        def setup_weapon_prob_tab(self, tab):
            
            self.weapon_five_star_prob = tk.StringVar(value=str(self.gacha_system.current_prob['weapon_five_star_base']))
            ttk.Label(tab, text="5星基础概率:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.weapon_five_star_prob, width=10).grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(0.008 = 0.8%)").grid(row=0, column=2, sticky="w", padx=5, pady=5)
            
            self.weapon_five_star_success_prob = tk.StringVar(value=str(self.gacha_system.current_prob['weapon_five_star_success_prob']))
            ttk.Label(tab, text="5星不歪概率:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.weapon_five_star_success_prob, width=10).grid(row=1, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(0.75 = 75%)").grid(row=1, column=2, sticky="w", padx=5, pady=5)

            self.weapon_five_star_pity = tk.StringVar(value=str(self.gacha_system.current_prob['weapon_five_star_pity']))
            ttk.Label(tab, text="5星保底抽数:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.weapon_five_star_pity, width=10).grid(row=2, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(默认: 80)").grid(row=2, column=2, sticky="w", padx=5, pady=5)
            
            self.weapon_four_star_prob = tk.StringVar(value=str(self.gacha_system.current_prob['weapon_four_star_base']))
            ttk.Label(tab, text="4星基础概率:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.weapon_four_star_prob, width=10).grid(row=3, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(0.066 = 6.6%)").grid(row=3, column=2, sticky="w", padx=5, pady=5)

            self.weapon_four_star_success_prob = tk.StringVar(value=str(self.gacha_system.current_prob['weapon_four_star_success_prob']))
            ttk.Label(tab, text="4星不歪概率:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.weapon_four_star_success_prob, width=10).grid(row=4, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(0.75 = 75%)").grid(row=4, column=2, sticky="w", padx=5, pady=5)
            
            self.weapon_four_star_pity = tk.StringVar(value=str(self.gacha_system.current_prob['weapon_four_star_pity']))
            ttk.Label(tab, text="4星保底抽数:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.weapon_four_star_pity, width=10).grid(row=5, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(默认: 10)").grid(row=5, column=2, sticky="w", padx=5, pady=5)

            # 光锥池五星小保底
            self.setup_weapon_5_star_small_pity(tab_weapon)

            # 光锥池四星小保底
            self.setup_weapon_4_star_small_pity(tab_weapon)

            # 光锥池五星大保底机制设置
            self.weapon_five_star_big_pity_enabled = tk.BooleanVar(value=self.gacha_system.current_prob['weapon_five_star_big_pity_enabled'])
            weapon_five_star_big_pity_checkbox = ttk.Checkbutton(tab, text="启用5星大保底机制", variable=self.weapon_five_star_big_pity_enabled)
            weapon_five_star_big_pity_checkbox.grid(row=8, column=0, columnspan=3, sticky="w", padx=5,pady=5)

            # 光锥池四星大保底机制设置
            self.weapon_four_star_big_pity_enabled = tk.BooleanVar(value=self.gacha_system.current_prob['weapon_four_star_big_pity_enabled'])
            weapon_four_star_big_pity_checkbox = ttk.Checkbutton(tab, text="启用4星大保底机制", variable=self.weapon_four_star_big_pity_enabled)
            # character_four_star_big_pity_checkbox.grid(row=13, column=2, columnspan=3, sticky="w", padx=(20, 0), pady=5)
            weapon_four_star_big_pity_checkbox.grid(row=8, column=2, columnspan=3,sticky="w", padx=5,pady=5)
            # 其他设置项按照类似方式添加...

        setup_weapon_prob_tab(self, tab_weapon)

        # 常驻池概率设置
        def setup_standard_prob_tab(self, tab):
            self.standard_five_star_prob = tk.StringVar(value=str(self.gacha_system.current_prob['standard_five_star_base']))
            ttk.Label(tab, text="5星基础概率:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.standard_five_star_prob, width=10).grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(0.006 = 0.6%)").grid(row=0, column=2, sticky="w", padx=5, pady=5)
            
            self.standard_five_star_pity = tk.StringVar(value=str(self.gacha_system.current_prob['standard_five_star_pity']))
            ttk.Label(tab, text="5星保底抽数:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.standard_five_star_pity, width=10).grid(row=1, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(默认: 90)").grid(row=1, column=2, sticky="w", padx=5, pady=5)
            
            self.standard_four_star_prob = tk.StringVar(value=str(self.gacha_system.current_prob['standard_four_star_base']))
            ttk.Label(tab, text="常驻池4星基础概率:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.standard_four_star_prob, width=10).grid(row=2, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(0.051 = 5.1%)").grid(row=2, column=2, sticky="w", padx=5, pady=5)

            
            self.standard_four_star_pity = tk.StringVar(value=str(self.gacha_system.current_prob['standard_four_star_pity']))
            ttk.Label(tab, text="常驻池4星保底抽数:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
            ttk.Entry(tab, textvariable=self.standard_four_star_pity, width=10).grid(row=3, column=1, padx=5, pady=5)
            ttk.Label(tab, text="(默认: 10)").grid(row=3, column=2, sticky="w", padx=5, pady=5)

        setup_standard_prob_tab(self, tab_standard)

        # 保存设置和恢复默认设置按钮
        button_frame = ttk.Frame(settings_window)  # 创建一个水平的按钮容器
        button_frame.pack(side="bottom", fill="x", expand=True, padx=5, pady=5)

        save_button = ttk.Button(button_frame, text="保存设置", command=lambda: self.save_probability_settings(settings_window))
        default_button = ttk.Button(button_frame, text="恢复默认设置", command=lambda: self.restore_default_settings(settings_window))

        # 将按钮加入到button_frame中，并设置它们填充整个button_frame
        save_button.pack(side="left", expand=True)
        default_button.pack(side="left",expand=True)


    def save_probability_settings(self, window):
        try:
            # 更新角色池5星小保底机制
            if self.character_five_star_small_pity_var_random.get():
                self.gacha_system.update_probability('character_five_star_small_pity_mechanism', 'random')
            elif self.character_five_star_small_pity_var_must_waste.get():
                self.gacha_system.update_probability('character_five_star_small_pity_mechanism', 'must_waste')
            elif self.character_five_star_small_pity_var_must_not_waste.get():
                self.gacha_system.update_probability('character_five_star_small_pity_mechanism', 'must_not_waste')
            # 更新角色池4星小保底机制
            if self.character_four_star_small_pity_var_random.get():
                self.gacha_system.update_probability('character_four_star_small_pity_mechanism', 'random')
            elif self.character_four_star_small_pity_var_must_waste.get():
                self.gacha_system.update_probability('character_four_star_small_pity_mechanism', 'must_waste')
            elif self.character_four_star_small_pity_var_must_not_waste.get():
                self.gacha_system.update_probability('character_four_star_small_pity_mechanism', 'must_not_waste')

            # 更新光锥池5星小保底机制
            if self.weapon_five_star_small_pity_var_random.get():
                self.gacha_system.update_probability('weapon_five_star_small_pity_mechanism', 'random')
            elif self.weapon_five_star_small_pity_var_must_waste.get():
                self.gacha_system.update_probability('weapon_five_star_small_pity_mechanism', 'must_waste')
            elif self.weapon_five_star_small_pity_var_must_not_waste.get():
                self.gacha_system.update_probability('weapon_five_star_small_pity_mechanism', 'must_not_waste')
            # 更新光锥池4星小保底机制
            if self.weapon_four_star_small_pity_var_random.get():
                self.gacha_system.update_probability('weapon_four_star_small_pity_mechanism', 'random')
            elif self.weapon_four_star_small_pity_var_must_waste.get():
                self.gacha_system.update_probability('weapon_four_star_small_pity_mechanism', 'must_waste')
            elif self.weapon_four_star_small_pity_var_must_not_waste.get():
                self.gacha_system.update_probability('weapon_four_star_small_pity_mechanism', 'must_not_waste')
            self.gacha_system.update_probability('character_five_star_base', float(self.character_five_star_prob.get()))
            self.gacha_system.update_probability('weapon_five_star_base', float(self.weapon_five_star_prob.get()))
            self.gacha_system.update_probability('character_four_star_base', float(self.character_four_star_prob.get()))
            self.gacha_system.update_probability('weapon_four_star_base', float(self.weapon_four_star_prob.get()))
            self.gacha_system.update_probability('character_five_star_pity', int(self.character_five_star_pity.get()))
            self.gacha_system.update_probability('weapon_five_star_pity', int(self.weapon_five_star_pity.get()))
            self.gacha_system.update_probability('character_five_star_success_prob', float(self.character_five_star_success_prob.get()))
            self.gacha_system.update_probability('weapon_five_star_success_prob', float(self.weapon_five_star_success_prob.get()))
            self.gacha_system.update_probability('character_four_star_success_prob', float(self.character_four_star_success_prob.get()))
            self.gacha_system.update_probability('weapon_four_star_success_prob', float(self.weapon_four_star_success_prob.get()))
            self.gacha_system.update_probability('character_four_star_pity', int(self.character_four_star_pity.get()))
            self.gacha_system.update_probability('weapon_four_star_pity', int(self.weapon_four_star_pity.get()))
            self.gacha_system.update_probability('character_five_star_big_pity_enabled', self.character_five_star_big_pity_enabled.get())
            self.gacha_system.update_probability('character_four_star_big_pity_enabled', self.character_four_star_big_pity_enabled.get())
            self.gacha_system.update_probability('weapon_five_star_big_pity_enabled', self.weapon_five_star_big_pity_enabled.get())
            self.gacha_system.update_probability('weapon_four_star_big_pity_enabled', self.weapon_four_star_big_pity_enabled.get())
            self.gacha_system.update_probability('standard_five_star_base', float(self.standard_five_star_prob.get()))
            self.gacha_system.update_probability('standard_five_star_pity', int(self.standard_five_star_pity.get()))
            self.gacha_system.update_probability('standard_four_star_base', float(self.standard_four_star_prob.get()))
            self.gacha_system.update_probability('standard_four_star_pity', int(self.standard_four_star_pity.get()))
            # 更新抽卡统计信息展示
            self.update_stats_display()
            messagebox.showinfo("成功", "概率设置已保存")
            window.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数值")

    def restore_default_settings(self, window):
        # 恢复默认设置
        default_settings = {
            'character_five_star_base': 0.006,
            'weapon_five_star_base': 0.008,
            'character_four_star_base': 0.051,
            'weapon_four_star_base': 0.066,
            'character_five_star_pity': 90,
            'weapon_five_star_pity': 80,
            'character_five_star_success_prob': 0.5,
            'weapon_five_star_success_prob': 0.75,
            'character_four_star_success_prob': 0.5,
            'weapon_four_star_success_prob': 0.75,
            'character_four_star_pity': 10,
            'weapon_four_star_pity': 10,
            'character_five_star_big_pity_enabled': True,
            'character_four_star_big_pity_enabled': True,
            'weapon_five_star_big_pity_enabled': True,
            'weapon_four_star_big_pity_enabled': True,
            'standard_five_star_base': 0.006,
            'standard_five_star_pity': 90,
            'standard_four_star_base': 0.051,
            'standard_four_star_pity': 10,
            'character_five_star_small_pity_mechanism': 'random',
            'character_four_star_small_pity_mechanism': 'random',
            'weapon_five_star_small_pity_mechanism': 'random',
            'weapon_four_star_small_pity_mechanism': 'random'
        }
        
        # 更新界面上的值
        self.character_five_star_prob.set(str(default_settings['character_five_star_base']))
        self.weapon_five_star_prob.set(str(default_settings['weapon_five_star_base']))
        self.character_four_star_prob.set(str(default_settings['character_four_star_base']))
        self.weapon_four_star_prob.set(str(default_settings['weapon_four_star_base']))
        self.character_five_star_pity.set(str(default_settings['character_five_star_pity']))
        self.weapon_five_star_pity.set(str(default_settings['weapon_five_star_pity']))
        self.character_five_star_success_prob.set(str(default_settings['character_five_star_success_prob']))
        self.weapon_five_star_success_prob.set(str(default_settings['weapon_five_star_success_prob']))
        self.character_four_star_success_prob.set(str(default_settings['character_four_star_success_prob']))
        self.weapon_four_star_success_prob.set(str(default_settings['weapon_four_star_success_prob']))
        self.character_four_star_pity.set(str(default_settings['character_four_star_pity']))
        self.weapon_four_star_pity.set(str(default_settings['weapon_four_star_pity']))
        self.character_five_star_big_pity_enabled.set(default_settings['character_five_star_big_pity_enabled'])
        self.character_four_star_big_pity_enabled.set(default_settings['character_four_star_big_pity_enabled'])
        self.weapon_five_star_big_pity_enabled.set(default_settings['weapon_five_star_big_pity_enabled'])
        self.weapon_four_star_big_pity_enabled.set(default_settings['weapon_four_star_big_pity_enabled'])
        self.standard_five_star_prob.set(str(default_settings['standard_five_star_base']))
        self.standard_five_star_pity.set(str(default_settings['standard_five_star_pity']))
        self.standard_four_star_prob.set(str(default_settings['standard_four_star_base']))
        self.standard_four_star_pity.set(str(default_settings['standard_four_star_pity']))
        # 更新角色池5星小保底机制单选框的状态
        self.character_five_star_small_pity_var_random.set(default_settings['character_five_star_small_pity_mechanism'] == 'random')
        self.character_five_star_small_pity_var_must_waste.set(default_settings['character_five_star_small_pity_mechanism'] == 'must_waste')
        self.character_five_star_small_pity_var_must_not_waste.set(default_settings['character_five_star_small_pity_mechanism'] == 'must_not_waste')
        # 更新角色池4星小保底机制单选框的状态
        self.character_four_star_small_pity_var_random.set(default_settings['character_four_star_small_pity_mechanism'] == 'random')
        self.character_four_star_small_pity_var_must_waste.set(default_settings['character_four_star_small_pity_mechanism'] == 'must_waste')
        self.character_four_star_small_pity_var_must_not_waste.set(default_settings['character_four_star_small_pity_mechanism'] == 'must_not_waste')

        # 更新光锥池5星小保底机制单选框的状态
        self.weapon_five_star_small_pity_var_random.set(default_settings['weapon_five_star_small_pity_mechanism'] == 'random')
        self.weapon_five_star_small_pity_var_must_waste.set(default_settings['weapon_five_star_small_pity_mechanism'] == 'must_waste')
        self.weapon_five_star_small_pity_var_must_not_waste.set(default_settings['weapon_five_star_small_pity_mechanism'] == 'must_not_waste')
        # 更新光锥池4星小保底机制单选框的状态
        self.weapon_four_star_small_pity_var_random.set(default_settings['weapon_four_star_small_pity_mechanism'] == 'random')
        self.weapon_four_star_small_pity_var_must_waste.set(default_settings['weapon_four_star_small_pity_mechanism'] == 'must_waste')
        self.weapon_four_star_small_pity_var_must_not_waste.set(default_settings['weapon_four_star_small_pity_mechanism'] == 'must_not_waste')
        
        # 更新系统中的值
        for key, value in default_settings.items():
            self.gacha_system.update_probability(key, value)

        # 更新抽卡统计信息展示
        self.update_stats_display()
        
        messagebox.showinfo("成功", "已恢复默认设置")
        window.destroy()


    def setup_character_5_star_small_pity(self, tab):
        # 角色池5星小保底机制设置 开始
        character_five_star_small_pity_frame = ttk.LabelFrame(tab, text="5星小保底机制")
        character_five_star_small_pity_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=5, padx=5)
        # 使用不同的变量来控制每个RadioButton
        self.character_five_star_small_pity_var_random = BooleanVar(value=False)  
        self.character_five_star_small_pity_var_must_waste = BooleanVar(value=False)
        self.character_five_star_small_pity_var_must_not_waste = BooleanVar(value=False)

        def command_five_star_random():
            self.character_five_star_small_pity_var_must_waste.set(False)
            self.character_five_star_small_pity_var_must_not_waste.set(False)

        def command_five_star_must_waste():
            self.character_five_star_small_pity_var_random.set(False)
            self.character_five_star_small_pity_var_must_not_waste.set(False)

        def command_five_star_must_not_waste():
            self.character_five_star_small_pity_var_random.set(False)
            self.character_five_star_small_pity_var_must_waste.set(False)

        ttk.Radiobutton(character_five_star_small_pity_frame, text="随机", variable=self.character_five_star_small_pity_var_random, command=command_five_star_random).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Radiobutton(character_five_star_small_pity_frame, text="必歪", variable=self.character_five_star_small_pity_var_must_waste, command=command_five_star_must_waste).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(character_five_star_small_pity_frame, text="必不歪", variable=self.character_five_star_small_pity_var_must_not_waste, command=command_five_star_must_not_waste).grid(row=0, column=2, sticky="w", padx=5)

        # 根据当前设置初始化RadioButton状态
        current_mechanism = self.gacha_system.current_prob.get('character_five_star_small_pity_mechanism', 'random')
        if current_mechanism == 'random':
            self.character_five_star_small_pity_var_random.set(True)
        elif current_mechanism == 'must_waste':
            self.character_five_star_small_pity_var_must_waste.set(True)
        else:
            self.character_five_star_small_pity_var_must_not_waste.set(True)

        # 角色池5星小保底机制设置 结束

    def setup_character_4_star_small_pity(self, tab):
        # 角色池4星小保底机制设置 开始
        character_four_star_small_pity_frame = ttk.LabelFrame(tab, text="4星小保底机制")
        character_four_star_small_pity_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=5, padx=5)
        # 使用不同的变量来控制每个RadioButton
        self.character_four_star_small_pity_var_random = BooleanVar(value=False)  
        self.character_four_star_small_pity_var_must_waste = BooleanVar(value=False)
        self.character_four_star_small_pity_var_must_not_waste = BooleanVar(value=False)

        def command_four_star_random():
            self.character_four_star_small_pity_var_must_waste.set(False)
            self.character_four_star_small_pity_var_must_not_waste.set(False)

        def command_four_star_must_waste():
            self.character_four_star_small_pity_var_random.set(False)
            self.character_four_star_small_pity_var_must_not_waste.set(False)

        def command_four_star_must_not_waste():
            self.character_four_star_small_pity_var_random.set(False)
            self.character_four_star_small_pity_var_must_waste.set(False)

        ttk.Radiobutton(character_four_star_small_pity_frame, text="随机", variable=self.character_four_star_small_pity_var_random, command=command_four_star_random).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Radiobutton(character_four_star_small_pity_frame, text="必歪", variable=self.character_four_star_small_pity_var_must_waste, command=command_four_star_must_waste).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(character_four_star_small_pity_frame, text="必不歪", variable=self.character_four_star_small_pity_var_must_not_waste, command=command_four_star_must_not_waste).grid(row=0, column=2, sticky="w", padx=5)

        # 根据当前设置初始化RadioButton状态
        current_mechanism = self.gacha_system.current_prob.get('character_four_star_small_pity_mechanism', 'random')
        if current_mechanism == 'random':
            self.character_four_star_small_pity_var_random.set(True)
        elif current_mechanism == 'must_waste':
            self.character_four_star_small_pity_var_must_waste.set(True)
        else:
            self.character_four_star_small_pity_var_must_not_waste.set(True)

        # 角色池4星小保底机制设置 结束

    def setup_weapon_5_star_small_pity(self, tab):
        # 光锥池5星小保底机制设置 开始
        weapon_five_star_small_pity_frame = ttk.LabelFrame(tab, text="5星小保底机制")
        weapon_five_star_small_pity_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=5, padx=5)
        # 使用不同的变量来控制每个RadioButton
        self.weapon_five_star_small_pity_var_random = BooleanVar(value=False)  
        self.weapon_five_star_small_pity_var_must_waste = BooleanVar(value=False)
        self.weapon_five_star_small_pity_var_must_not_waste = BooleanVar(value=False)

        def command_five_star_random():
            self.weapon_five_star_small_pity_var_must_waste.set(False)
            self.weapon_five_star_small_pity_var_must_not_waste.set(False)

        def command_five_star_must_waste():
            self.weapon_five_star_small_pity_var_random.set(False)
            self.weapon_five_star_small_pity_var_must_not_waste.set(False)

        def command_five_star_must_not_waste():
            self.weapon_five_star_small_pity_var_random.set(False)
            self.weapon_five_star_small_pity_var_must_waste.set(False)

        ttk.Radiobutton(weapon_five_star_small_pity_frame, text="随机", variable=self.weapon_five_star_small_pity_var_random, command=command_five_star_random).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Radiobutton(weapon_five_star_small_pity_frame, text="必歪", variable=self.weapon_five_star_small_pity_var_must_waste, command=command_five_star_must_waste).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(weapon_five_star_small_pity_frame, text="必不歪", variable=self.weapon_five_star_small_pity_var_must_not_waste, command=command_five_star_must_not_waste).grid(row=0, column=2, sticky="w", padx=5)

        # 根据当前设置初始化RadioButton状态
        current_mechanism = self.gacha_system.current_prob.get('weapon_five_star_small_pity_mechanism', 'random')
        if current_mechanism == 'random':
            self.weapon_five_star_small_pity_var_random.set(True)
        elif current_mechanism == 'must_waste':
            self.weapon_five_star_small_pity_var_must_waste.set(True)
        else:
            self.weapon_five_star_small_pity_var_must_not_waste.set(True)

        # 光锥池5星小保底机制设置 结束

    def setup_weapon_4_star_small_pity(self, tab):
        # 光锥池4星小保底机制设置 开始
        weapon_four_star_small_pity_frame = ttk.LabelFrame(tab, text="4星小保底机制")
        weapon_four_star_small_pity_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=5, padx=5)
        # 使用不同的变量来控制每个RadioButton
        self.weapon_four_star_small_pity_var_random = BooleanVar(value=False)  
        self.weapon_four_star_small_pity_var_must_waste = BooleanVar(value=False)
        self.weapon_four_star_small_pity_var_must_not_waste = BooleanVar(value=False)

        def command_four_star_random():
            self.weapon_four_star_small_pity_var_must_waste.set(False)
            self.weapon_four_star_small_pity_var_must_not_waste.set(False)

        def command_four_star_must_waste():
            self.weapon_four_star_small_pity_var_random.set(False)
            self.weapon_four_star_small_pity_var_must_not_waste.set(False)

        def command_four_star_must_not_waste():
            self.weapon_four_star_small_pity_var_random.set(False)
            self.weapon_four_star_small_pity_var_must_waste.set(False)

        ttk.Radiobutton(weapon_four_star_small_pity_frame, text="随机", variable=self.weapon_four_star_small_pity_var_random, command=command_four_star_random).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Radiobutton(weapon_four_star_small_pity_frame, text="必歪", variable=self.weapon_four_star_small_pity_var_must_waste, command=command_four_star_must_waste).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(weapon_four_star_small_pity_frame, text="必不歪", variable=self.weapon_four_star_small_pity_var_must_not_waste, command=command_four_star_must_not_waste).grid(row=0, column=2, sticky="w", padx=5)

        # 根据当前设置初始化RadioButton状态
        current_mechanism = self.gacha_system.current_prob.get('weapon_four_star_small_pity_mechanism', 'random')
        if current_mechanism == 'random':
            self.weapon_four_star_small_pity_var_random.set(True)
        elif current_mechanism == 'must_waste':
            self.weapon_four_star_small_pity_var_must_waste.set(True)
        else:
            self.weapon_four_star_small_pity_var_must_not_waste.set(True)

        # 光锥池4星小保底机制设置 结束

    def get_current_pity(self):
        # 根据当前选择的卡池类型获取对应的保底数值
        if self.gacha_system.current_banner:
            pool_type = self.gacha_system.pools['banners'][self.gacha_system.current_banner].get('pool_type', 'standard')
            if pool_type == 'character':
                return self.gacha_system.current_prob['character_five_star_pity']
            elif pool_type == 'weapon':
                return self.gacha_system.current_prob['weapon_five_star_pity']
            else:
                return self.gacha_system.current_prob['standard_five_star_pity']
        else:
            # 如果没有选择卡池，返回一个默认值或者提示用户选择卡池
            return self.gacha_system.current_prob['standard_five_star_pity']

# GachaSystem部分开始
class GachaSystem:
    def __init__(self, pool_file, prob_file='custom_probabilities.yaml',no_update=False):
        self.pool_file = pool_file
        self.prob_file = prob_file
        self.is_first_download = not os.path.exists(self.pool_file)
        self.ensure_pool_file_exists()
        if not self.is_first_download and not no_update:
            update_result = self.check_and_update_pool_file()
            if update_result == "current":
                self.show_message("卡池文件已是最新版本。", CYAN)
            elif update_result == "updated":
                self.show_message("卡池文件已更新到最新版本。", GREEN)
            else:
                self.show_message(f"检查更新时发生错误: {update_result}。\n将使用当前版本的卡池文件。", YELLOW)
            # print(f"{update_result}")
        elif no_update:
            self.show_message("已跳过更新检查。", GREEN)
        else:
            return
        self.load_pools(pool_file)
        self.load_probabilities(prob_file) # 加载自定义概率文件
        # 使用封装好的函数
        self.inits()

    def load_pools(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            self.pools = yaml.load(f)
        self.banners = list(self.pools['banners'].keys())

    def save_state(self):
        try:
            state = {
                'current_banner': self.current_banner,
                'total_pulls': self.total_pulls,
                'banner_pulls': self.banner_pulls,
                'pull_history': self.pull_history,
                
                # 角色池数据
                'character_pity_5': self.character_pity_5,
                'character_pity_4': self.character_pity_4,
                'character_gold_records': self.character_gold_records,
                'character_purple_records': self.character_purple_records,
                'character_failed_featured_5star': self.character_failed_featured_5star,
                'character_successful_featured_5star': self.character_successful_featured_5star,
                'character_pulls_since_last_5star': self.character_pulls_since_last_5star,
                'character_is_guaranteed': self.character_is_guaranteed,
                'character_pulls': self.character_pulls,
                
                # 光锥池数据
                'weapon_pity_5': self.weapon_pity_5,
                'weapon_pity_4': self.weapon_pity_4,
                'weapon_gold_records': self.weapon_gold_records,
                'weapon_purple_records': self.weapon_purple_records,
                'weapon_failed_featured_5star': self.weapon_failed_featured_5star,
                'weapon_successful_featured_5star': self.weapon_successful_featured_5star,
                'weapon_pulls_since_last_5star': self.weapon_pulls_since_last_5star,
                'weapon_is_guaranteed': self.weapon_is_guaranteed,
                'weapon_pulls': self.weapon_pulls,
                
                # 常驻池数据
                'standard_pity_5': self.pity_5,
                'standard_pity_4': self.pity_4,
                'standard_gold_records': self.gold_records,
                'standard_purple_records': self.purple_records,
                'standard_pulls_since_last_5star': self.pulls_since_last_5star,
                'standard_pulls': self.standard_pulls,

                'character_four_star_guaranteed': self.character_four_star_guaranteed,
                'weapon_four_star_guaranteed': self.weapon_four_star_guaranteed,
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
            
            # 添加注释
            data_str = data_str.replace('current_banner:', '# 当前选择的卡池\ncurrent_banner:')
            data_str = data_str.replace('total_pulls:', '# 总抽卡次数\ntotal_pulls:')
            data_str = data_str.replace('banner_pulls:', '# 每个卡池的抽卡次数\nbanner_pulls:')
            data_str = data_str.replace('pull_history:', '# 抽卡历史记录\npull_history:')
            
            data_str = data_str.replace('character_pity_5:', '# 角色池5星保底计数\ncharacter_pity_5:')
            data_str = data_str.replace('character_pity_4:', '# 角色池4星保底计数\ncharacter_pity_4:')
            data_str = data_str.replace('character_gold_records:', '# 角色池5星记录\ncharacter_gold_records:')
            data_str = data_str.replace('character_purple_records:', '# 角色池4星记录\ncharacter_purple_records:')
            data_str = data_str.replace('character_failed_featured_5star:', '# 角色池歪掉的5星次数\ncharacter_failed_featured_5star:')
            data_str = data_str.replace('character_successful_featured_5star:', '# 角色池抽中UP的5星次数\ncharacter_successful_featured_5star:')
            data_str = data_str.replace('character_pulls_since_last_5star:', '# 角色池距离上次5星的抽数\ncharacter_pulls_since_last_5star:')
            data_str = data_str.replace('character_is_guaranteed:', '# 角色池是否大保底\ncharacter_is_guaranteed:')
            
            data_str = data_str.replace('weapon_pity_5:', '# 光锥池5星保底计数\nweapon_pity_5:')
            data_str = data_str.replace('weapon_pity_4:', '# 光锥池4星保底计数\nweapon_pity_4:')
            data_str = data_str.replace('weapon_gold_records:', '# 光锥池5星记录\nweapon_gold_records:')
            data_str = data_str.replace('weapon_purple_records:', '# 光锥池4星记录\nweapon_purple_records:')
            data_str = data_str.replace('weapon_failed_featured_5star:', '# 光锥池歪掉的5星次数\nweapon_failed_featured_5star:')
            data_str = data_str.replace('weapon_successful_featured_5star:', '# 光锥池抽中UP的5星次数\nweapon_successful_featured_5star:')
            data_str = data_str.replace('weapon_pulls_since_last_5star:', '# 光锥池距离上次5星的抽数\nweapon_pulls_since_last_5star:')
            data_str = data_str.replace('weapon_is_guaranteed:', '# 光锥池是否大保底\nweapon_is_guaranteed:')
            
            data_str = data_str.replace('standard_pity_5:', '# 常驻池5星保底计数\nstandard_pity_5:')
            data_str = data_str.replace('standard_pity_4:', '# 常驻池4星保底计数\nstandard_pity_4:')
            data_str = data_str.replace('standard_gold_records:', '# 常驻池5星记录\nstandard_gold_records:')
            data_str = data_str.replace('standard_purple_records:', '# 常驻池4星记录\nstandard_purple_records:')
            data_str = data_str.replace('standard_pulls_since_last_5star:', '# 常驻池距离上次5星的抽数\nstandard_pulls_since_last_5star:')
            
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
                self.total_pulls = state.get('total_pulls', 0)
                self.banner_pulls = state.get('banner_pulls', {})
                self.pull_history = state.get('pull_history', [])
                
                # 加载角色池数据
                self.character_pity_5 = state.get('character_pity_5', 0)
                self.character_pity_4 = state.get('character_pity_4', 0)
                self.character_gold_records = state.get('character_gold_records', [])
                self.character_purple_records = state.get('character_purple_records', [])
                self.character_failed_featured_5star = state.get('character_failed_featured_5star', 0)
                self.character_successful_featured_5star = state.get('character_successful_featured_5star', 0)
                self.character_pulls_since_last_5star = state.get('character_pulls_since_last_5star', 0)
                self.character_is_guaranteed = state.get('character_is_guaranteed', False)
                self.character_pulls = state.get('character_pulls', 0)
                
                # 加载光锥池数据
                self.weapon_pity_5 = state.get('weapon_pity_5', 0)
                self.weapon_pity_4 = state.get('weapon_pity_4', 0)
                self.weapon_gold_records = state.get('weapon_gold_records', [])
                self.weapon_purple_records = state.get('weapon_purple_records', [])
                self.weapon_failed_featured_5star = state.get('weapon_failed_featured_5star', 0)
                self.weapon_successful_featured_5star = state.get('weapon_successful_featured_5star', 0)
                self.weapon_pulls_since_last_5star = state.get('weapon_pulls_since_last_5star', 0)
                self.weapon_is_guaranteed = state.get('weapon_is_guaranteed', False)
                self.weapon_pulls = state.get('weapon_pulls', 0)
                
                # 加载常驻池数据
                self.pity_5 = state.get('standard_pity_5', 0)
                self.pity_4 = state.get('standard_pity_4', 0)
                self.gold_records = state.get('standard_gold_records', [])
                self.purple_records = state.get('standard_purple_records', [])
                self.pulls_since_last_5star = state.get('standard_pulls_since_last_5star', 0)
                self.standard_pulls = state.get('standard_pulls', 0)

                self.character_four_star_guaranteed = state.get('character_four_star_guaranteed', False)
                self.weapon_four_star_guaranteed = state.get('weapon_four_star_guaranteed', False)
                
                # 处理pull_history中的item_type
                for pull in self.pull_history:
                    if pull['item_type'] == 'character':
                        pull['item_type'] = CHARACTER_DISPLAY_NAME
                    elif pull['item_type'] == 'weapon':
                        pull['item_type'] = WEAPON_DISPLAY_NAME
        except FileNotFoundError:
            self.show_message("未找到保存的数据，使用默认值初始化。", YELLOW)
        except Exception as e:
            self.show_message(f"加载数据时出错: {e}", RED)

    # 自定义概率相关
    def load_probabilities(self, prob_file):
        if not os.path.exists(prob_file):
            self.create_default_probabilities()
        with open(prob_file, 'r', encoding='utf-8') as f:
            self.probabilities = yaml.load(f)
        self.current_prob = self.probabilities['custom']

    def save_probabilities(self, prob_file='custom_probabilities.yaml'):
        with open(prob_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.probabilities, f)

    def update_probability(self, key, value):
        self.current_prob[key] = value
        self.probabilities['custom'][key] = value
        self.save_probabilities()

    def create_default_probabilities(self):
        # 生成的默认配置
        default_probabilities = {
            'custom': {
                'character_five_star_base': 0.006,
                'weapon_five_star_base': 0.008,
                'character_four_star_base': 0.051,
                'weapon_four_star_base': 0.066,
                'character_five_star_pity': 90,
                'weapon_five_star_pity': 80,
                'character_five_star_success_prob': 0.5,
                'weapon_five_star_success_prob': 0.75,
                'character_four_star_success_prob': 0.5,
                'weapon_four_star_success_prob': 0.75,
                'character_four_star_pity': 10,
                'weapon_four_star_pity': 10,
                'character_five_star_big_pity_enabled': True,
                'character_four_star_big_pity_enabled': True,
                'weapon_five_star_big_pity_enabled': True,
                'weapon_four_star_big_pity_enabled': True,
                'standard_five_star_base': 0.006,
                'standard_five_star_pity': 90,
                'standard_four_star_base': 0.051,
                'standard_four_star_pity': 10,
                'character_five_star_small_pity_mechanism': 'random',
                'character_four_star_small_pity_mechanism': 'random',
                'weapon_five_star_small_pity_mechanism': 'random',
                'weapon_four_star_small_pity_mechanism': 'random'
            }
        }

        yaml_str = "# 自定义概率设置文件\n"
        yaml_str += "# 请勿手动修改，除非你知道自己在做什么\n\n"
        
        yaml.default_flow_style = False
        yaml.width = 4096
        yaml.indent(mapping=2, sequence=4, offset=2)
        
        from io import StringIO
        string_stream = StringIO()
        yaml.dump(default_probabilities, string_stream)
        data_str = string_stream.getvalue()
        
        # 添加注释
        data_str = data_str.replace('custom:', '# 自定义概率设置\ncustom:')
        data_str = data_str.replace('character_five_star_base:', '  # 角色池5星基础概率\n  character_five_star_base:')
        data_str = data_str.replace('weapon_five_star_base:', '  # 光锥池5星基础概率\n  weapon_five_star_base:')
        data_str = data_str.replace('character_four_star_base:', '  # 角色池4星基础概率\n  character_four_star_base:')
        data_str = data_str.replace('weapon_four_star_base:', '  # 光锥池4星基础概率\n  weapon_four_star_base:')
        data_str = data_str.replace('character_five_star_pity:', '  # 角色池5星保底抽数\n  character_five_star_pity:')
        data_str = data_str.replace('weapon_five_star_pity:', '  # 光锥池5星保底抽数\n  weapon_five_star_pity:')
        data_str = data_str.replace('character_five_star_success_prob:', '  # 角色池5星不歪概率\n  character_five_star_success_prob:')
        data_str = data_str.replace('weapon_five_star_success_prob:', '  # 光锥池5星不歪概率\n  weapon_five_star_success_prob:')
        data_str = data_str.replace('character_four_star_success_prob:', '  # 角色池4星不歪概率\n  character_four_star_success_prob:')
        data_str = data_str.replace('weapon_four_star_success_prob:', '  # 光锥池4星不歪概率\n  weapon_four_star_success_prob:')
        data_str = data_str.replace('character_four_star_pity:', '  # 角色池4星保底抽数\n  character_four_star_pity:')
        data_str = data_str.replace('weapon_four_star_pity:', '  # 光锥池4星保底抽数\n  weapon_four_star_pity:')
        data_str = data_str.replace('character_five_star_big_pity_enabled:', '  # 是否启用角色池5星大保底\n  character_five_star_big_pity_enabled:')
        data_str = data_str.replace('character_four_star_big_pity_enabled:', '  # 是否启用角色池4星大保底\n  character_four_star_big_pity_enabled:')
        data_str = data_str.replace('weapon_five_star_big_pity_enabled:', '  # 是否启用光锥池5星大保底\n  weapon_five_star_big_pity_enabled:')
        data_str = data_str.replace('weapon_four_star_big_pity_enabled:', '  # 是否启用光锥池4星大保底\n  weapon_four_star_big_pity_enabled:')
        data_str = data_str.replace('standard_five_star_base:', '  # 常驻池5星基础概率\n  standard_five_star_base:')
        data_str = data_str.replace('standard_five_star_pity:', '  # 常驻池5星保底抽数\n  standard_five_star_pity:')
        data_str = data_str.replace('standard_four_star_base:', '  # 常驻池4星基础概率\n  standard_four_star_base:')
        data_str = data_str.replace('standard_four_star_pity:', '  # 常驻池4星保底抽数\n  standard_four_star_pity:')
        data_str = data_str.replace('character_five_star_small_pity_mechanism:', '  # 角色池5星小保底歪的机制\n  character_five_star_small_pity_mechanism:')
        data_str = data_str.replace('character_four_star_small_pity_mechanism:', '  # 角色池4星小保底歪的机制\n  character_four_star_small_pity_mechanism:')
        data_str = data_str.replace('weapon_five_star_small_pity_mechanism:', '  # 光锥池5星小保底歪的机制\n  weapon_five_star_small_pity_mechanism:')
        data_str = data_str.replace('weapon_four_star_small_pity_mechanism:', '  # 光锥池4星小保底歪的机制\n  weapon_four_star_small_pity_mechanism:')
        
        yaml_str += data_str

        with open(self.prob_file, 'w', encoding='utf-8') as f:
            f.write(yaml_str)

        self.probabilities = default_probabilities
        self.current_prob = self.probabilities['custom']

    def update_character_five_star_small_pity_mechanism(self, five_star_mechanism, four_star_mechanism):
        self.character_five_star_small_pity_mechanism = five_star_mechanism
        self.character_four_star_small_pity_mechanism = four_star_mechanism
        self.save_probabilities()
        
    def ensure_pool_file_exists(self):
        if not os.path.exists(self.pool_file):
            download = messagebox.askyesno("错误", f"卡池文件不存在。是否从GitHub下载最新的卡池文件？")
            if download:
                try:
                    proxy_url = f"{GITHUB_PROXY}{BANNER_DOWNLOAD_URL}"
                    response = requests.get(proxy_url)
                    response.raise_for_status()
                    with open(self.pool_file, 'wb') as f:
                        f.write(response.content)
                    self.show_message("卡池文件下载成功！", GREEN)
                    self.is_first_download = True
                    self.load_pools(self.pool_file)  # 立即加载新下载的文件
                    self.load_probabilities(self.prob_file) # 加载自定义概率文件
                    self.inits()
                except requests.RequestException as e:
                    self.show_message(f"下载失败: {e}", RED)
                    sys.exit(1)
            else:
                self.show_message(f"请提供卡池文件。", RED)
                sys.exit(1)
        else:
            self.load_pools(self.pool_file)  # 如果文件已存在，也要加载

    def check_and_update_pool_file(self):
        try:
            proxy_url = f"{GITHUB_PROXY}{BANNER_DOWNLOAD_URL}"
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
            return "error", f"检查更新时发生错误: {e}"

    def switch_banner(self, banner_name):
        # print(f"尝试切换到卡池: {banner_name}")  # 调试信息
        # print(f"可用的卡池: {self.banners}")  # 调试信息
        if banner_name not in self.banners:
            # print(f"卡池 {banner_name} 不在可用卡池列表中")  # 调试信息
            return False
        self.current_banner = banner_name
        # print(f"成功切换到卡池: {self.current_banner}")  # 调试信息
        self.save_state()
        return True

    def perform_pull(self, num_pulls):
        if not self.current_banner:
            self.show_message("请先选择一个卡池。", RED)
            return

        banner = self.pools['banners'][self.current_banner]
        pool_type = banner.get('pool_type', 'standard')

        pulls = []
        summary = {'5星': 0, '5星UP': 0, '4星': 0, '4星UP': 0, '3星': 0}
        # guaranteed_4_star = False

        if pool_type == 'weapon':
            five_star_pity = self.current_prob['weapon_five_star_pity']
            five_star_base = self.current_prob['weapon_five_star_base']
            four_star_base = self.current_prob['weapon_four_star_base']
            four_star_pity = self.current_prob['weapon_four_star_pity']
            five_star_big_pity_enabled = self.current_prob['weapon_five_star_big_pity_enabled']
            four_star_big_pity_enabled = self.current_prob['weapon_four_star_big_pity_enabled']
        elif pool_type == 'character':
            five_star_pity = self.current_prob['character_five_star_pity']
            five_star_base = self.current_prob['character_five_star_base']
            four_star_base = self.current_prob['character_four_star_base']
            four_star_pity = self.current_prob['character_four_star_pity']
            five_star_big_pity_enabled = self.current_prob['character_five_star_big_pity_enabled']
            four_star_big_pity_enabled = self.current_prob['character_four_star_big_pity_enabled']
        else:
            five_star_pity = self.current_prob['standard_five_star_pity']
            five_star_base = self.current_prob['standard_five_star_base']
            four_star_base = self.current_prob['standard_four_star_base']
            four_star_pity = self.current_prob['standard_four_star_pity']
            five_star_big_pity_enabled = False
            four_star_big_pity_enabled = False

        for i in range(num_pulls):
            self.total_pulls += 1
            self.banner_pulls[self.current_banner] = self.banner_pulls.get(self.current_banner, 0) + 1
            
            if pool_type == 'character':
                self.character_pulls += 1
            elif pool_type == 'weapon':
                self.weapon_pulls += 1
            else:
                self.standard_pulls += 1
            
            pity_5, pity_4, gold_records, purple_records, failed_featured_5star, successful_featured_5star, pulls_since_last_5star, is_guaranteed, four_star_guaranteed = self.get_pool_stats(pool_type)

            five_star_rate_up_ratio = float(74 / 90) # 从74抽开始概率随每抽提升
            five_star_rate_up_pulls = int(five_star_rate_up_ratio * five_star_pity) # 去掉小数点
            
            # 确定是否出五星
            if (pity_5 >= five_star_pity - 1 or
                (pity_5 < five_star_rate_up_pulls and # 如果抽数未达到概率随抽数提升条件
                random.random() < five_star_base) or  
                (pity_5 >= five_star_rate_up_pulls and  # 如果抽数达到概率随抽数提升条件
                random.random() < five_star_base + (pity_5 * five_star_base))):
                result = self.pull_5_star(pool_type)
                gold_records.append(pity_5 + 1)
                pulls_for_this_5star = pulls_since_last_5star + 1
                if result['rarity'] == '5_star':
                    pulls_rarity = '五星'
                if self.current_banner != 'standard':
                    if result['is_up']:
                        summary['5星UP'] += 1
                        if is_guaranteed:
                            messagebox.showinfo("出货了!", f"恭喜，你用了{pulls_for_this_5star}抽获得了{pulls_rarity}{result['type']}{result['item']}\n这是大保底!")
                        else:
                            successful_featured_5star += 1 # 只有在小保底时计数器才会增加1
                            messagebox.showinfo("出货了!", f"你用了{pulls_for_this_5star}抽获得了{pulls_rarity}{result['type']}{result['item']}\n是小保底，恭喜没歪!")
                    else:
                        failed_featured_5star += 1
                        if five_star_big_pity_enabled:
                            messagebox.showinfo("出货了!", f"你用了{pulls_for_this_5star}抽获得了{pulls_rarity}{result['type']}{result['item']}\n可惜歪了，下次将是大保底!")
                        else:
                            messagebox.showinfo("出货了!", f"你用了{pulls_for_this_5star}抽获得了{pulls_rarity}{result['type']}{result['item']}\n可惜歪了，下次...下次还是小保底啦哈哈哈！\n如果想启用大保底机制记得去改一下抽卡概率")
                else: # 常驻池逻辑
                    messagebox.showinfo("出货了!", f"恭喜，你用了{pulls_for_this_5star}抽获得了{pulls_rarity}{result['type']}{result['item']}!")
                
                if five_star_big_pity_enabled:
                    self.update_pool_stats(pool_type, pity_5=0, pity_4=0, pulls_since_last_5star=0, 
                                        is_guaranteed=not result['is_up'],  # 如果这次没有抽中UP，下次就是大保底
                                        failed_featured_5star=failed_featured_5star,
                                        successful_featured_5star=successful_featured_5star)
                else:
                    self.update_pool_stats(pool_type, pity_5=0, pity_4=0, pulls_since_last_5star=0, 
                    failed_featured_5star=failed_featured_5star,
                    successful_featured_5star=successful_featured_5star)
                summary['5星'] += 1
                # guaranteed_4_star = False
                # print(f"当前保底抽数为{five_star_pity}\n当前抽卡概率为{five_star_base}") # Debug
            # 确定是否出四星
            elif pity_4 >= four_star_pity - 1 or random.random() < four_star_base:
                result = self.pull_4_star(pool_type)
                purple_records.append(pity_4 + 1)
                if four_star_big_pity_enabled:
                    self.update_pool_stats(pool_type, pity_5=pity_5+1, pity_4=0, 
                                        four_star_guaranteed=not result['is_up'],
                                        pulls_since_last_5star=pulls_since_last_5star+1)
                else:
                    self.update_pool_stats(pool_type, pity_5=pity_5+1, pity_4=0, pulls_since_last_5star=pulls_since_last_5star+1)
                summary['4星'] += 1 # 不知道有什么用的summary

                if pool_type != 'standard':
                    four_star_guaranteed = not result['is_up']
                else:
                    four_star_guaranteed = False


                if self.current_banner != 'standard' and result['is_up']:
                    summary['4星UP'] += 1 # 不知道有什么用的summary

                # guaranteed_4_star = True
                # print(f"当前保底抽数为{four_star_pity}\n当前抽卡概率为{four_star_base}") # Debug
            else:
                result = self.pull_3_star()
                self.update_pool_stats(pool_type, pity_5=pity_5+1, pity_4=pity_4+1, pulls_since_last_5star=pulls_since_last_5star+1)
                summary['3星'] += 1

            pulls.append((result['rarity'], result['type'], result['item']))
            self.pull_history.append({'rarity': result['rarity'], 'item_type': result['type'], 'item': result['item']})


        return pulls
        


    def get_pool_stats(self, pool_type):
        if pool_type == 'character':
            return (self.character_pity_5, self.character_pity_4, self.character_gold_records, 
                    self.character_purple_records, self.character_failed_featured_5star, 
                    self.character_successful_featured_5star, self.character_pulls_since_last_5star, 
                    self.character_is_guaranteed, self.character_four_star_guaranteed)
        elif pool_type == 'weapon':
            return (self.weapon_pity_5, self.weapon_pity_4, self.weapon_gold_records, 
                    self.weapon_purple_records, self.weapon_failed_featured_5star, 
                    self.weapon_successful_featured_5star, self.weapon_pulls_since_last_5star, 
                    self.weapon_is_guaranteed, self.weapon_four_star_guaranteed)
        else:
            return (self.pity_5, self.pity_4, self.gold_records, self.purple_records, 
                    self.failed_featured_5star, self.successful_featured_5star, 
                    self.pulls_since_last_5star, self.is_guaranteed, self.four_star_guaranteed)
        

    def update_pool_stats(self, pool_type, **kwargs):
        if pool_type == 'character':
            for key, value in kwargs.items():
                setattr(self, f"character_{key}", value)
        elif pool_type == 'weapon':
            for key, value in kwargs.items():
                setattr(self, f"weapon_{key}", value)
        else:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def pull_5_star(self, pool_type):


        if pool_type == 'weapon':
            success_prob = self.current_prob['weapon_five_star_success_prob']
            five_star_small_pity_mechanism = self.current_prob['weapon_five_star_small_pity_mechanism']
            five_star_big_pity_enabled = self.current_prob['weapon_five_star_big_pity_enabled']
        elif pool_type == 'character':
            success_prob = self.current_prob['character_five_star_success_prob']
            five_star_small_pity_mechanism = self.current_prob['character_five_star_small_pity_mechanism']
            five_star_big_pity_enabled = self.current_prob['character_five_star_big_pity_enabled']
        else:
            success_prob = 0
            five_star_small_pity_mechanism = random

        is_up = self.is_guaranteed or ( 
            (five_star_small_pity_mechanism == 'random' and random.random() < success_prob) or
            (five_star_small_pity_mechanism == 'must_not_waste'))
        
        if pool_type == 'character':
            if is_up: # 没歪
                item = random.choice(self.pools['banners'][self.current_banner]['character_up_5_star'])
                self.is_guaranteed = False
            else: # 歪了
                item = random.choice(self.pools['common_pools']['character_5_star'])
                if five_star_big_pity_enabled:
                    self.is_guaranteed = True
                else:
                    self.is_guaranteed = False
            # print(f"当前五星不歪概率为{success_prob}") # Debug
            return {'rarity': '5_star', 'type': CHARACTER_DISPLAY_NAME, 'item': item, 'is_up': is_up}
        elif pool_type == 'weapon':
            if is_up: # 没歪
                item = random.choice(self.pools['banners'][self.current_banner]['weapon_up_5_star'])
                self.is_guaranteed = False
            else: # 歪了
                item = random.choice(self.pools['common_pools']['weapon_5_star'])
                if five_star_big_pity_enabled:
                    self.is_guaranteed = True
                else:
                    self.is_guaranteed = False
            # print(f"当前五星不歪概率为{success_prob}") # Debug
            return {'rarity': '5_star', 'type': WEAPON_DISPLAY_NAME, 'item': item, 'is_up': is_up}
        else:  # standard pool
            if random.random() < 0.5:
                item = random.choice(self.pools['common_pools']['character_5_star'])
                return {'rarity': '5_star', 'type': CHARACTER_DISPLAY_NAME, 'item': item, 'is_up': False}
            else:
                item = random.choice(self.pools['common_pools']['weapon_5_star'])
                return {'rarity': '5_star', 'type': CHARACTER_DISPLAY_NAME, 'item': item, 'is_up': False}

    def pull_4_star(self, pool_type):

        if pool_type == 'weapon':
            success_prob = self.current_prob['weapon_four_star_success_prob']
            four_star_small_pity_mechanism = self.current_prob['weapon_four_star_small_pity_mechanism']
            four_star_big_pity_enabled = self.current_prob['weapon_four_star_big_pity_enabled']
        elif pool_type == 'character':
            success_prob = self.current_prob['character_four_star_success_prob']
            four_star_small_pity_mechanism = self.current_prob['character_four_star_small_pity_mechanism']
            four_star_big_pity_enabled = self.current_prob['character_four_star_big_pity_enabled']
        else: # 常驻
            success_prob = 0 # 随便写个值
            four_star_big_pity_enabled = True
            four_star_small_pity_mechanism = 'random'

        is_up = self.four_star_guaranteed or ( 
    (four_star_small_pity_mechanism == 'random' and random.random() < success_prob) or
    (four_star_small_pity_mechanism == 'must_not_waste')) # 四星大保底以及必歪必不歪时的up情况
        if is_up and pool_type != 'standard':
            if pool_type == 'character':
                item = random.choice(self.pools['banners'][self.current_banner].get('character_up_4_star', []))
                self.four_star_guaranteed = False
                return {'rarity': '4_star', 'type': CHARACTER_DISPLAY_NAME, 'item': item, 'is_up': True}
            else:  # weapon pool
                item = random.choice(self.pools['banners'][self.current_banner].get('weapon_up_4_star', []))
                self.four_star_guaranteed = False
                return {'rarity': '4_star', 'type': WEAPON_DISPLAY_NAME, 'item': item, 'is_up': True}
        else: # 非up 或者 为常驻
            # 50%的概率从四星角色中抽取，50%的概率从四星光锥中抽取
            four_star_item_pool = self.pools['common_pools']['character_4_star'] if random.random() < 0.5 else self.pools['common_pools']['weapon_4_star']
            # 获取当前卡池up的四星物品
            up_items = self.pools['banners'][self.current_banner].get(f'{pool_type}_up_4_star', [])
            # 非up的列表
            non_up_items = [item for item in four_star_item_pool if item not in up_items]
            # 随便抽一个
            item = random.choice(non_up_items)
            # 更新四星大保底状态
            if four_star_big_pity_enabled:
                self.four_star_guaranteed = True
            else:
                self.four_star_guaranteed = False
            # 判断物品类型
            if item in self.pools['common_pools']['character_4_star']:
                type = CHARACTER_DISPLAY_NAME
            elif item in self.pools['common_pools']['weapon_4_star']:
                type = WEAPON_DISPLAY_NAME
            else:
                # 如果不确定物品类型，可以选择默认为一种或记录日志等
                type = '未知'
            return {'rarity': '4_star', 'type': type, 'item': item, 'is_up': False}

    def pull_3_star(self):
        item = random.choice(self.pools['common_pools']['weapon_3_star'])
        return {'rarity': '3_star', 'type': WEAPON_DISPLAY_NAME, 'item': item, 'is_up': False}

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
        # print("分类卡池:")  # 调试信息
        for banner_id, banner_info in self.pools['banners'].items():
            if banner_id != standard_banner:
                banner_name = banner_info.get('name', banner_id)
                # print(f"  处理卡池: {banner_id} - {banner_name}")  # 调试信息
                if banner_info.get('pool_type') == 'character':
                    character_banners.append((banner_id, banner_name))
                    # print(f"    添加到角色卡池")  # 调试信息
                elif banner_info.get('pool_type') == 'weapon':
                    weapon_banners.append((banner_id, banner_name))
                    # print(f"    添加到武器卡池")  # 调试信息
        # print(f"角色卡池: {character_banners}")  # 调试信息
        # print(f"武器卡池: {weapon_banners}")  # 调试信息
        return character_banners, weapon_banners
    
    def get_standard_banner(self):
        return next((banner_id for banner_id, banner_info in self.pools['banners'].items() if banner_info.get('name') == '群星跃迁'), None)
    
    def calculate_luck(self, pool_type):
        if pool_type == 'character':
            gold_records = self.character_gold_records
            failed_featured = self.character_failed_featured_5star
            total_featured = self.character_failed_featured_5star + self.character_successful_featured_5star
            five_star_pity = self.current_prob['character_five_star_pity']
        elif pool_type == 'weapon':
            gold_records = self.weapon_gold_records
            failed_featured = self.weapon_failed_featured_5star
            total_featured = self.weapon_failed_featured_5star + self.weapon_successful_featured_5star
            five_star_pity = self.current_prob['weapon_five_star_pity']
        else:  # standard pool
            gold_records = self.gold_records
            failed_featured = 0  # Not applicable for standard pool
            total_featured = 0
            five_star_pity = self.current_prob['standard_five_star_pity']

        if not gold_records:
            return "暂无数据"

        min_pulls = min(gold_records)
        max_pulls = max(gold_records)
        avg_pulls = sum(gold_records) / len(gold_records)
        luck_score = 0

        # 由具体数值更改为一个比例

        # 最少抽数
        min_judged_1 = int(five_star_pity * (15 / 90)) # 15
        min_judged_2 = int(five_star_pity * (25 / 90)) # 25
        min_judged_3 = int(five_star_pity * (35 / 90)) # 35
        min_judged_4 = int(five_star_pity * (45 / 90)) # 45
        # 最多抽数
        max_judged_1 = int(five_star_pity * (55 / 90)) # 55
        max_judged_2 = int(five_star_pity * (65 / 90)) # 65
        max_judged_3 = int(five_star_pity * (80 / 90)) # 80
        # 平均抽数
        avg_judged_1 = int(five_star_pity * (30 / 90)) # 30
        avg_judged_2 = int(five_star_pity * (40 / 90)) # 40
        avg_judged_3 = int(five_star_pity * (50 / 90)) # 50
        avg_judged_4 = int(five_star_pity * (60 / 90)) # 60
        avg_judged_5 = int(five_star_pity * (70 / 90)) # 70

        # 最少抽数评分
        if min_pulls <= min_judged_1:
            luck_score += 5  
        elif min_pulls <= min_judged_2:
            luck_score += 4
        elif min_pulls <= min_judged_3:
            luck_score += 3
        elif min_pulls <= min_judged_4:
            luck_score += 2
        else:
            luck_score += 1  

        # 最多抽数评分
        if max_pulls <= max_judged_1:
            luck_score += 3 
        elif max_pulls <= max_judged_2:
            luck_score += 2
        elif max_pulls <= max_judged_3:
            luck_score += 1
        else:
            luck_score += 0 

        # 平均抽数评分
        if avg_pulls <= avg_judged_1:
            luck_score += 5  
        elif avg_pulls <= avg_judged_2:
            luck_score += 4
        elif avg_pulls <= avg_judged_3:
            luck_score += 3
        elif avg_pulls <= avg_judged_4:
            luck_score += 2
        elif avg_pulls <= avg_judged_5:
            luck_score += 1
        else:
            luck_score += 0  

        # UP角色/武器歪卡率评分 (仅限UP池)
        if pool_type != 'standard' and total_featured > 0:
            fail_rate = failed_featured / total_featured
            if fail_rate == 0:
                luck_score += 5 
            elif fail_rate <= 0.1:
                luck_score += 4
            elif fail_rate <= 0.25:
                luck_score += 3
            elif fail_rate <= 0.4:
                luck_score += 2
            elif fail_rate <= 0.75:
                luck_score += 1
            else:
                luck_score += 0  

        # 根据分数判断运势
        if luck_score >= 20:
            return "极佳"
        elif luck_score >= 18:
            return "大吉"
        elif luck_score >= 15:
            return "上吉"
        elif luck_score >= 12:
            return "中吉"
        elif luck_score >= 9:
            return "小吉"
        elif luck_score >= 6:
            return "平"
        elif luck_score >= 3:
            return "小凶"
        elif luck_score >= 1:
            return "中凶"
        else:
            return "大凶"

    def reset_statistics(self):
        self.character_pity_5 = 0
        self.character_pity_4 = 0
        self.weapon_pity_5 = 0
        self.weapon_pity_4 = 0
        self.character_gold_records = []
        self.character_purple_records = []
        self.weapon_gold_records = []
        self.weapon_purple_records = []
        self.character_failed_featured_5star = 0
        self.character_successful_featured_5star = 0
        self.weapon_failed_featured_5star = 0
        self.weapon_successful_featured_5star = 0
        self.character_pulls_since_last_5star = 0
        self.weapon_pulls_since_last_5star = 0
        self.character_is_guaranteed = False
        self.weapon_is_guaranteed = False
        self.total_pulls = 0
        self.banner_pulls = {}
        self.pull_history = []
        self.pity_5 = 0
        self.pity_4 = 0
        self.gold_records = []
        self.purple_records = []
        self.pulls_since_last_5star = 0
        self.is_guaranteed = False
        self.failed_featured_5star = 0
        self.successful_featured_5star = 0
        self.character_pulls = 0
        self.weapon_pulls = 0
        self.standard_pulls = 0
        self.four_star_guaranteed = False
        self.character_four_star_guaranteed = False
        self.weapon_four_star_guaranteed = False
        self.save_state()

    def inits(self):
        self.current_banner = None
        # 为角色池和光锥池分别初始化保底计数器和统计信息
        self.character_pity_5 = 0
        self.character_pity_4 = 0
        self.weapon_pity_5 = 0
        self.weapon_pity_4 = 0
        self.character_gold_records = []
        self.character_purple_records = []
        self.weapon_gold_records = []
        self.weapon_purple_records = []
        self.character_failed_featured_5star = 0
        self.character_successful_featured_5star = 0
        self.weapon_failed_featured_5star = 0
        self.weapon_successful_featured_5star = 0
        self.character_pulls_since_last_5star = 0
        self.weapon_pulls_since_last_5star = 0
        self.character_is_guaranteed = False
        self.weapon_is_guaranteed = False
        self.total_pulls = 0
        self.banner_pulls = {}
        self.pull_history = []
        self.pity_5 = 0
        self.pity_4 = 0
        self.gold_records = []
        self.purple_records = []
        self.pulls_since_last_5star = 0
        self.is_guaranteed = False
        self.failed_featured_5star = 0
        self.successful_featured_5star = 0
        self.character_pulls = 0
        self.weapon_pulls = 0
        self.standard_pulls = 0
        self.four_star_guaranteed = False
        self.character_four_star_guaranteed = False
        self.weapon_four_star_guaranteed = False
        self.TIPS = TIPS
        self.load_state()

# GachaSystem 部分结束


# 主程序
if __name__ == "__main__":
    # root = ThemedTk(theme="adapta")  # 不使用主题
    root = tk.Tk()
    icon_data = """
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAMAAABHPGVmAAABBVBMVEVHcEwAAAAAAAAAAAACAAYCAQIxIxsLBAYLHh4AAAAnQ008O0V8cW/////54uH/7dzw19f+z5r88e79vpf79P3/3q8XqM8Zi+YVw+GV0tP57Pv/+uz4u7n7xsU+v+wTqe3+rZv916nb0N+64enl3vVq2/IOk8djqt75r7ad3eyir9QldtnP6tnoy8f/5Mf++/5nxteq+fhCXb8SSOH8tV4u6d7e7PgTaOv9oZ43re5qk9v4xrF+uuHs4Nc5l9bCx+M7q8yUmtpWt9GulaVK0vBDWlXl+vvHtcJEhNWlmHNXf9Tc1P0d0+Bq9e6tvvH+y3gXGbH9hoddi4oDHvHMp6eYVZ6xam16XeqSAAAADXRSTlMAaQw+sI7j3fUj/t/+ZwJtfwAACDlJREFUeJztmdl2okobhttZky5BHBBxVkRBUcBIVBQ1DkQTtTPs+7+U/6sC+08Pe60YzNHOm8S1ciAP7zdVFXz79qUvfelL/yH5faGA/9unyu8L31f+iYQC3z5NGMEjhJqv4eAnYU4IUG53F/Z9LgKhVA51wxfPzC8IhOpWFb2ELo+g0BvVq1UaXV0yLb+5cCHVbjtysYD9BeE4odH3SwXsbwgCmdAME41dhBH6G8J1QqP74CUYsau/IVB3h51MqMvk3nePEok/IakddjKZoGrkApBgB/X7hz8itt7VMSQeRyvvVmJhhBKVfl/5w4kL6U68l7HvO+IPaSrRP/wKye3qdZqOgy5QxsENovrpNJX+zQyG1IkVho96DJg/whNIWgEzb/Nfh3DViZM42njMfWCFkNJPVwBDKYcD9RZyiheUsbeZH7pHKN2vYAiYqRzSpzaJ17GIk3iX9pR7fyQOxQUQQkkr6UQCm+HppIJSIMYRuvdiJQAFjJL9ROJEURIHhaebzSSFeN7B8DyD7rxAcLQI5EQBJRK3zXyFZ3iGyTleeHTtZUxGqgAp9xNJTDlhEsnCWEE8hSHwA9GKe5mSsSgiEGAQSsW1Mh5TPIEQhsdoQbtjSDmZTCYqDgZACTDmQFI5UCrlbXxBu0O1Eggx43ASh0MFGMQJhqCUl10LbneEGAcCGGIH/g59BTMohvhIoY2X4RUg6xV1Wy43HcoYGIdEot+nAEL9hHz3VMB3GKL8aJbLJzfYDkxkzGCoOGF0kbdoTTCk4kBOlGS/n6jwlEJRpBnBSNVLAZN2R2hMIEn4zSfHGMIrCRwsiu/issh5bHdSwCiJIZCXMjDGY2h/lKwoClhhut0uTDBvWwnS7tAmP5q3t0Bp5vMAGfeVSp+CiYzbpIu6KVT3spoEosiFlG9BBFIACJUvU4RBIDkkeSlgp90x5NaFFIAxLldexkqctCJAUnX03XO7g24dCBgpFDCm86IosBzGMaSby3k6pMQi7l7rx49mvlm+bRJGIZ/YvFAYQpGBUkfWhwo45qwNvpXD4O9u8yCXUSiPpTyFF3bo9i7K1T/W7r7ra3LiDL04kMFdE0NcRqG5kRRnZY/nEKrWu+HzUxIIwih5WUV8AbeAUfzOYdBOtPKSxDsMGqIl7arn7yH817BxgFx0vkeilgOh7woYQtMFbKaZn1vUTyPxee7u/AIO4JHYpYHUOUoOpONC3HBZc+oUrVSq2sx9YL3ykbKdwJ6Nl0YOJL9h8s1mvgOCQ48ynzvRqm6aoKr1gR1XiMbXZeByCj0aEMhmg2AL5DLo+HzjOLFq1qa5UZ8+UMAhdILAPZsORFoP4KDrQAqdubP/tQYM05Y4tPpAAV87e1B8z3RntMb/3EntGqhabbcnNC05KanWqHiK6g0+sqH3OxA0gbvupB0rls21WhhTa7dpei5Rk0mcthgAcdzaTYn/nMTE3JnI4OBQVY1kRTIHa7TGoHanM6rGJxPayjFtDpTWjsFQKBi8vj4jaqSCHUi8y3e0EapLTvolswaUiTRi4pO4Vedri0Xv/p/Xo67dza25tr9+vxefC0ETBnYp+ak9mupaCp9GjiO1Vmu1oYDbTLXKt3qirb3OpZ1zVjnO5++3EnK7HMcHTSqSIfdE7RWWcu04AiOt2laExFhMa2Fr+mv1dEbdYivvhzDkW21usObXk4oizRaiqc1RXZO3JlixtFGb2QxagNDkk2u0PZqS9PRuK8HaYFDb7yGlrQEzmUwoqSeI4rYmyrbYa7XUvbxtbyx1qmnbre2OHbQ/yiNpb73bSiBq6Jqub7lej2tjmaP1oGaKoJ4gcCq3lUdcW9O4rS1yAze0R93ejqTB+62ErgzdMHSR6y3MNjTGSM/hoK8HA1VoiWZL3G5borbvmdb6FCztKGOIVXv/MhyRQYbR6y1mZrtdm+qD00lUFQTZ5DRN3MPd//+oPTpqGCKeYyUQZW3blm2ATM12a2pYp6sZw0ddFka1Xx9M7I+6LNs2QPat6Lut+K5KNmuz095s1jBbM0N0rzZ/tkXdUNFvDz90zJhiiKQ+vX/9Cmolezq1M7NMpjGbse6qstMNmx2yuzeA7qDGmSPwPRWnU9Hk1tz7x34swk6xMqBGZsoOdvv5aGTLpWF2yW7dioLrc+Zi1mgIexEjRK62PutQBwFrEMQMIEXj2RgOi8tlcVgqFkvGblBrcaY4HA5FcbEATA+KzuSgEBF31voFAWtgSEaWGxnjWS8+Pj4uiyVA4Q+4/rBYzPawMGWBxzFM6DM397FIo4EpDZ1l5Yah6+wSX34Jn9lsdlkElYTWCTLjiNbSmQsx1DELFAiFIA4BZBhsqVQUBGEJkAeMEtbrXnFRnEFEF1wPQ9Szn92GrjAks4RxpZrPRollIU7C483NA6aAG1VVBVIZjYZIjJxTv678ERmnpdgSAKPLOOul7M2N4FCyDwJk6TEjQ1CBYk9NrqVGz98aBaIluE+IEEDEIU5DFiA3D6zBAuMhC95AUAC4mxpsUX36yLY7dPWQHQ57hPIoLHE2Hm5uSrohl7JQCs/PulzCFQBpgVtZrIIfOqQEVxlhCd9X1dqTJqiPEKiHm2wWwsYCQZdZwphBqoSn64++3/L7glerhrB4WkWCwZVKKFmSEVgMAAG0YnG4FHpPYZ+Xh10xXzAcDAVi2Jaq3mAf8JPBBU16FXI2W4V9nh89+38GD1uB2y+x2RuWhWyzpWy2cXXZF3SEkiUMyD/0TSmjXV38HWBohSGEAYErNa7Cn/E2MxSOvlHE9znvZf0xV4FY4LNf/X7pS1/60r/qf/Qii9lWlXs9AAAAAElFTkSuQmCC"""
    icon_image_bytes = base64.b64decode(icon_data.split(',')[1])
    icon_image = Image.open(io.BytesIO(icon_image_bytes))
    photo = ImageTk.PhotoImage(icon_image)
    root.iconphoto(True, photo)
    gui = GachaSimulatorGUI(root)
    root.mainloop()
