import random
from ruamel.yaml import YAML
import os
import requests
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, StringVar, Toplevel, Label, Button, Entry, Listbox, END, BooleanVar, font, ttk
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
    "可以修改卡池文件来实现其他游戏的抽卡效果",
    "本来我是想整个主题的，但是好像加上之后会变得很卡我就删了",
    "你看什么看！",
    "双击抽卡记录可以查看物品的详细信息"
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

        # 初始化主题选择        
        # self.setup_theme_selection()

        # 确保 GachaSystem 已正确初始化
        if not hasattr(self.gacha_system, 'pools'):
            messagebox.showerror("错误", "无法加载卡池数据。请重新启动程序。")
            exit(1)

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

        self.toggle_button = ttk.Button(banner_frame, text="切换到光锥池列表", command=self.toggle_banner_type)
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

        gacha_frame.columnconfigure(0, weight=1)
        gacha_frame.columnconfigure(1, weight=1)

        # Utility controls
        util_frame = ttk.LabelFrame(self.left_frame, text="工具箱")
        util_frame.pack(pady=2, padx=5, fill=tk.X)

        self.random_tip_button = ttk.Button(util_frame, text="随机Tips", command=self.show_random_tip)
        self.random_tip_button.grid(row=0, column=0, pady=2, padx=2, sticky="ew")

        self.clear_data_button = ttk.Button(util_frame, text="抽卡概率修改", command=self.open_probability_settings)
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
            self.toggle_button.config(text="切换到角色池列表")
        else:
            self.current_banner_type.set("character")
            self.toggle_button.config(text="切换到光锥池列表")
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
        pool_type_display = '光锥' if pool_type == 'weapon' else '角色'
        
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
                if not up_items and item_type == '角色':
                    up_items = current_banner_info.get(f"character_up_{rarity}", [])
                elif not up_items and item_type == '光锥':
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
            stats_type = "角色池"
            pool_pulls = self.gacha_system.character_pulls
        elif pool_type == 'weapon':
            pity_5 = self.gacha_system.weapon_pity_5
            pity_4 = self.gacha_system.weapon_pity_4
            gold_records = self.gacha_system.weapon_gold_records
            purple_records = self.gacha_system.weapon_purple_records
            failed_featured_5star = self.gacha_system.weapon_failed_featured_5star
            successful_featured_5star = self.gacha_system.weapon_successful_featured_5star
            pulls_since_last_5star = self.gacha_system.weapon_pulls_since_last_5star
            is_guaranteed = self.gacha_system.weapon_is_guaranteed
            stats_type = "光锥池"
            pool_pulls = self.gacha_system.weapon_pulls
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
        next_pity_5_str = f"距离下一个五星保底的抽数: {self.gacha_system.current_prob['five_star_pity'] - pity_5}" 
        next_pity_4_str = f"距离下一个四星保底: {self.gacha_system.current_prob['four_star_pity'] - pity_4}" 
        get_gold_records_str = f"获得五星次数: {len(gold_records)}"
        get_purple_records_str = f"获得四星次数: {len(purple_records)}"
        min_gold_records_str = f"最少抽数出金: {min_gold_records}"
        max_gold_records_str = f"最多抽数出金: {max_gold_records}"

        if isinstance(avg_gold_pulls, (int, float)):  # 检查 avg_gold_pulls 是否是数字类型
            avg_gold_pulls_str = f"平均出金抽数: {avg_gold_pulls:.2f}"
        else:
            avg_gold_pulls_str = f"平均出金抽数: {avg_gold_pulls}" 

        if pool_type != 'standard':
            failed_featured_5star_str = f"歪掉五星次数: {failed_featured_5star}"
        else:
            failed_featured_5star_str = f"歪掉五星次数: 无"

        if pool_type != 'standard':
            if isinstance(success_rate, (int, float)):  # 检查 success_rate 是否是数字类型
                success_rate_str = f"小保底不歪概率: {success_rate:.2f}%"
            else:
                success_rate_str = f"小保底不歪概率: {success_rate}"
        else:
            success_rate_str = f"小保底不歪概率: 无"

        pulls_since_last_5star_str = f"距离上次五星: {pulls_since_last_5star}"

        if self.gacha_system.current_prob['big_pity_enabled']:
            if pool_type != 'standard': 
                is_guaranteed_str = f"大保底状态: {'是' if is_guaranteed else '否'}"
            else:
                is_guaranteed_str = f"大保底状态: 无"
        else:
            is_guaranteed_str = f"大保底状态: 你没有启用大保底机制"

        luck_rating_str = f"抽卡运势: {luck_rating}"

        # 使用变量控制输出
        stats = f"""{pool_pulls_str}
    {next_pity_5_str}
    {next_pity_4_str}
    {get_gold_records_str}
    {get_purple_records_str}
    {min_gold_records_str}
    {max_gold_records_str}
    {avg_gold_pulls_str}
    {failed_featured_5star_str}
    {success_rate_str}
    {pulls_since_last_5star_str}
    {is_guaranteed_str}
    {luck_rating_str}""" 


        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)
        self.stats_text.config(state=tk.DISABLED)

        # 动态调整高度
        self.stats_text.update_idletasks()
        height = self.stats_text.count('1.0', 'end', 'displaylines')
        self.stats_text.config(height=height)

    def show_version(self):
        version = "2.2.1" 
        author = "QiuSYan & Claude"
        github = "qiusyan-projects/SR-Gacha"
        other = "来点Star叭~💖"
        messagebox.showinfo("版本信息", f"当前版本: {version}\n作者：{author}\nGithub：{github}\n{other}")    

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


    def open_probability_settings(self):
        # 创建一个新的顶级窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("概率设置")
        settings_window.geometry("350x250")  # 增加窗口宽度以容纳提示语

        ttk.Label(settings_window, text="5星基础概率:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.five_star_prob = tk.StringVar(value=str(self.gacha_system.current_prob['five_star_base']))
        ttk.Entry(settings_window, textvariable=self.five_star_prob, width=10).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(settings_window, text="(0.006 = 0.6%)").grid(row=0, column=2, sticky="w", padx=5, pady=5)

        ttk.Label(settings_window, text="4星基础概率:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.four_star_prob = tk.StringVar(value=str(self.gacha_system.current_prob['four_star_base']))
        ttk.Entry(settings_window, textvariable=self.four_star_prob, width=10).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(settings_window, text="(0.051 = 5.1%)").grid(row=1, column=2, sticky="w", padx=5, pady=5)

        ttk.Label(settings_window, text="5星保底抽数:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.five_star_pity = tk.StringVar(value=str(self.gacha_system.current_prob['five_star_pity']))
        ttk.Entry(settings_window, textvariable=self.five_star_pity, width=10).grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(settings_window, text="(默认: 90)").grid(row=2, column=2, sticky="w", padx=5, pady=5)

        ttk.Label(settings_window, text="4星保底抽数:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.four_star_pity = tk.StringVar(value=str(self.gacha_system.current_prob['four_star_pity']))
        ttk.Entry(settings_window, textvariable=self.four_star_pity, width=10).grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(settings_window, text="(默认: 10)").grid(row=3, column=2, sticky="w", padx=5, pady=5)

        self.big_pity_enabled = tk.BooleanVar(value=self.gacha_system.current_prob['big_pity_enabled'])
        ttk.Checkbutton(settings_window, text="启用大保底机制", variable=self.big_pity_enabled).grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        ttk.Button(settings_window, text="保存设置", command=lambda: self.save_probability_settings(settings_window)).grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        
        # 添加恢复默认设置按钮
        ttk.Button(settings_window, text="恢复默认设置", command=lambda: self.restore_default_settings(settings_window)).grid(row=5, column=2, padx=5, pady=5)

    def save_probability_settings(self, window):
        try:
            self.gacha_system.update_probability('five_star_base', float(self.five_star_prob.get()))
            self.gacha_system.update_probability('four_star_base', float(self.four_star_prob.get()))
            self.gacha_system.update_probability('five_star_pity', int(self.five_star_pity.get()))
            self.gacha_system.update_probability('four_star_pity', int(self.four_star_pity.get()))
            self.gacha_system.update_probability('big_pity_enabled', self.big_pity_enabled.get())
            # 更新抽卡统计信息展示
            self.update_stats_display()
            messagebox.showinfo("成功", "概率设置已保存")
            window.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数值")

    def restore_default_settings(self, window):
        # 恢复默认设置
        default_settings = {
            'five_star_base': 0.006,
            'four_star_base': 0.051,
            'five_star_pity': 90,
            'four_star_pity': 10,
            'big_pity_enabled': True
        }
        
        # 更新界面上的值
        self.five_star_prob.set(str(default_settings['five_star_base']))
        self.four_star_prob.set(str(default_settings['four_star_base']))
        self.five_star_pity.set(str(default_settings['five_star_pity']))
        self.four_star_pity.set(str(default_settings['four_star_pity']))
        self.big_pity_enabled.set(default_settings['big_pity_enabled'])
        
        # 更新系统中的值
        for key, value in default_settings.items():
            self.gacha_system.update_probability(key, value)

        # 更新抽卡统计信息展示
        self.update_stats_display()
        
        messagebox.showinfo("成功", "已恢复默认设置")



# def setup_theme_selection(self):
#     # 创建一个框架来容纳标签和下拉菜单
#     theme_frame = ttk.Frame(self.root)
#     theme_frame.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=10)

#     # 添加提示标签
#     theme_label = ttk.Label(theme_frame, text="选择主题：", font=self.default_font)
#     theme_label.pack(side=tk.LEFT, padx=(0, 5))

#     # 获取可用主题
#     self.themes = self.root.get_themes()
#     self.current_theme = tk.StringVar(value="arc")  # 设置默认主题

#     # 创建主题选择下拉菜单
#     self.theme_menu = ttk.OptionMenu(
#         theme_frame,
#         self.current_theme,
#         "arc",
#         *self.themes,
#         command=self.change_theme
#     )
#     self.theme_menu.pack(side=tk.LEFT)

# def change_theme(self, theme_name):
#     self.root.set_theme(theme_name)



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
                
                # 处理pull_history中的item_type
                for pull in self.pull_history:
                    if pull['item_type'] == 'character':
                        pull['item_type'] = '角色'
                    elif pull['item_type'] == 'weapon':
                        pull['item_type'] = '光锥'
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
                'five_star_base': 0.006,
                'four_star_base': 0.051,
                'five_star_pity': 90,
                'four_star_pity': 10,
                'big_pity_enabled': True
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
        data_str = data_str.replace('five_star_base:', '  # 5星基础概率\n  five_star_base:')
        data_str = data_str.replace('four_star_base:', '  # 4星基础概率\n  four_star_base:')
        data_str = data_str.replace('five_star_pity:', '  # 5星保底抽数\n  five_star_pity:')
        data_str = data_str.replace('four_star_pity:', '  # 4星保底抽数\n  four_star_pity:')
        data_str = data_str.replace('big_pity_enabled:', '  # 是否启用大保底\n  big_pity_enabled:')
        
        yaml_str += data_str

        with open(self.prob_file, 'w', encoding='utf-8') as f:
            f.write(yaml_str)

        self.probabilities = default_probabilities
        self.current_prob = self.probabilities['custom']
        
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
                    self.load_pools(self.pool_file)  # 立即加载新下载的文件
                    self.load_probabilities(self.prob_file) # 加载自定义概率文件
                    self.inits()
                except requests.RequestException as e:
                    self.show_message(f"下载失败: {e}", RED)
                    exit(1)
            else:
                self.show_message(f"请提供 '{self.pool_file}' 文件。", RED)
                exit(1)
        else:
            self.load_pools(self.pool_file)  # 如果文件已存在，也要加载

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
        guaranteed_4_star = False

        for i in range(num_pulls):
            self.total_pulls += 1
            self.banner_pulls[self.current_banner] = self.banner_pulls.get(self.current_banner, 0) + 1
            
            if pool_type == 'character':
                self.character_pulls += 1
            elif pool_type == 'weapon':
                self.weapon_pulls += 1
            else:
                self.standard_pulls += 1
            
            pity_5, pity_4, gold_records, purple_records, failed_featured_5star, successful_featured_5star, pulls_since_last_5star, is_guaranteed = self.get_pool_stats(pool_type)

            five_star_rate_up_ratio = float(74 / 90) # 从74抽开始概率随每抽提升
            five_star_rate_up_pulls = int(five_star_rate_up_ratio * self.current_prob['five_star_pity']) # 去掉小数点
            
            # 确定是否出五星
            if (pity_5 >= self.current_prob['five_star_pity'] - 1 or
                (pity_5 < five_star_rate_up_pulls and # 如果抽数未达到概率随抽数提升条件
                random.random() < self.current_prob['five_star_base']) or  
                (pity_5 >= five_star_rate_up_pulls and  # 如果抽数达到概率随抽数提升条件
                random.random() < self.current_prob['five_star_base'] + (pity_5 * self.current_prob['five_star_base']))):
                result = self.pull_5_star(pool_type)
                gold_records.append(pity_5 + 1)
                pulls_for_this_5star = pulls_since_last_5star + 1
                if self.current_banner != 'standard':
                    if result['is_up']:
                        summary['5星UP'] += 1
                        if is_guaranteed:
                            messagebox.showinfo("出货了!", f"恭喜，你用了{pulls_for_this_5star}抽获得了{result['item']}\n这是大保底!")
                        else:
                            successful_featured_5star += 1 # 只有在小保底时计数器才会增加1
                            messagebox.showinfo("出货了!", f"你用了{pulls_for_this_5star}抽获得了{result['item']}\n是小保底，恭喜没歪!")
                    else:
                        failed_featured_5star += 1
                        if self.current_prob['big_pity_enabled']:
                            messagebox.showinfo("出货了!", f"你用了{pulls_for_this_5star}抽获得了{result['item']}\n可惜歪了，下次将是大保底!")
                        else:
                            messagebox.showinfo("出货了!", f"你用了{pulls_for_this_5star}抽获得了{result['item']}\n可惜歪了，下次...下次还是小保底啦哈哈哈！\n如果想启用大保底机制记得去改一下抽卡概率")
                else: # 常驻池逻辑
                    messagebox.showinfo("出货了!", f"恭喜，你用了{pulls_for_this_5star}抽获得了{result['item']}!")
                
                if self.current_prob['big_pity_enabled']:
                    self.update_pool_stats(pool_type, pity_5=0, pity_4=0, pulls_since_last_5star=0, 
                                        is_guaranteed=not result['is_up'],  # 如果这次没有抽中UP，下次就是大保底
                                        failed_featured_5star=failed_featured_5star,
                                        successful_featured_5star=successful_featured_5star)
                else:
                    self.update_pool_stats(pool_type, pity_5=0, pity_4=0, pulls_since_last_5star=0, 
                    failed_featured_5star=failed_featured_5star,
                    successful_featured_5star=successful_featured_5star)
                summary['5星'] += 1
                guaranteed_4_star = False
            # 确定是否出四星
            elif pity_4 >= self.current_prob['four_star_pity'] - 1 or random.random() < self.current_prob['four_star_base']:
                result = self.pull_4_star(pool_type)
                purple_records.append(pity_4 + 1)
                self.update_pool_stats(pool_type, pity_5=pity_5+1, pity_4=0, pulls_since_last_5star=pulls_since_last_5star+1)
                summary['4星'] += 1
                if self.current_banner != 'standard' and result['is_up']:
                    summary['4星UP'] += 1
                guaranteed_4_star = True
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
                    self.character_is_guaranteed)
        elif pool_type == 'weapon':
            return (self.weapon_pity_5, self.weapon_pity_4, self.weapon_gold_records, 
                    self.weapon_purple_records, self.weapon_failed_featured_5star, 
                    self.weapon_successful_featured_5star, self.weapon_pulls_since_last_5star, 
                    self.weapon_is_guaranteed)
        else:
            return (self.pity_5, self.pity_4, self.gold_records, self.purple_records, 
                    self.failed_featured_5star, self.successful_featured_5star, 
                    self.pulls_since_last_5star, self.is_guaranteed)
        

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
        is_up = random.random() < 0.5 or (self.current_prob['big_pity_enabled'] and self.is_guaranteed)
        if pool_type == 'character':
            if is_up: # 没歪
                item = random.choice(self.pools['banners'][self.current_banner]['character_up_5_star'])
                self.is_guaranteed = False
            else: # 歪了
                item = random.choice(self.pools['common_pools']['character_5_star'])
                if self.current_prob['big_pity_enabled']:
                    self.is_guaranteed = True
                else:
                    self.is_guaranteed = False
            return {'rarity': '5_star', 'type': '角色', 'item': item, 'is_up': is_up}
        elif pool_type == 'weapon':
            if is_up: # 没歪
                item = random.choice(self.pools['banners'][self.current_banner]['weapon_up_5_star'])
                self.is_guaranteed = False
            else: # 歪了
                item = random.choice(self.pools['common_pools']['weapon_5_star'])
                if self.current_prob['big_pity_enabled']:
                    self.is_guaranteed = True
                else:
                    self.is_guaranteed = False
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
        elif pool_type == 'weapon':
            gold_records = self.weapon_gold_records
            failed_featured = self.weapon_failed_featured_5star
            total_featured = self.weapon_failed_featured_5star + self.weapon_successful_featured_5star
        else:  # standard pool
            gold_records = self.gold_records
            failed_featured = 0  # Not applicable for standard pool
            total_featured = 0

        if not gold_records:
            return "暂无数据"

        min_pulls = min(gold_records)
        max_pulls = max(gold_records)
        avg_pulls = sum(gold_records) / len(gold_records)

        luck_score = 0

        # 最少抽数评分
        if min_pulls <= 20:
            luck_score += 3
        elif min_pulls <= 40:
            luck_score += 2
        elif min_pulls <= 60:
            luck_score += 1

        # 最多抽数评分
        if max_pulls <= 60:
            luck_score += 3
        elif max_pulls <= 75:
            luck_score += 2
        elif max_pulls <= 85:
            luck_score += 1

        # 平均抽数评分
        if pool_type == 'standard':
            if avg_pulls <= 45:
                luck_score += 4
            elif avg_pulls <= 60:
                luck_score += 3
            elif avg_pulls <= 75:
                luck_score += 2
            elif avg_pulls <= 85:
                luck_score += 1
        else:
            if avg_pulls <= 50:
                luck_score += 3
            elif avg_pulls <= 65:
                luck_score += 2
            elif avg_pulls <= 75:
                luck_score += 1

        # UP角色/武器歪卡率评分 (仅限UP池)
        if pool_type != 'standard' and total_featured > 0:
            fail_rate = failed_featured / total_featured
            if fail_rate == 0:
                luck_score += 3
            elif fail_rate <= 0.25:
                luck_score += 2
            elif fail_rate <= 0.5:
                luck_score += 1

        # 根据分数判断运势
        if luck_score >= 10:
            return "大吉"
        elif luck_score >= 8:
            return "中吉"
        elif luck_score >= 6:
            return "小吉"
        elif luck_score >= 4:
            return "平"
        elif luck_score >= 2:
            return "小凶"
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
        
        self.TIPS = TIPS
        self.load_state()

# GachaSystem 部分结束

# 主程序
if __name__ == "__main__":
    # root = ThemedTk(theme="adapta")  # 不使用主题
    root = tk.Tk()
    gui = GachaSimulatorGUI(root)
    root.mainloop()