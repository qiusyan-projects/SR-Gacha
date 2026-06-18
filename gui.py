"""
SR-Gacha GUI 模块
包含 GachaSimulatorGUI 类：基于 Tkinter 的图形用户界面
"""

import os
import random
import re
from datetime import datetime
import tkinter as tk
from tkinter import (
    BooleanVar,
    messagebox,
    StringVar,
    ttk,
)

import requests

from constants import (
    AUTHOR,
    BANNER_FILE,
    CHARACTER_DISPLAY_NAME,
    DEFAULT_PROBABILITIES,
    GITHUB_REPO,
    VERSION,
    WEAPON_DISPLAY_NAME,
)
from gacha_system import GachaSystem


class GachaSimulatorGUI:
    """崩坏：星穹铁道抽卡模拟器 GUI"""

    def __init__(self, root):
        self.root = root
        self.root.withdraw()

        self.root.title("崩坏：星穹铁道抽卡模拟器")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        # 默认字体
        self.default_font_name = 'Microsoft YaHei'
        self.default_font = (self.default_font_name, 10)
        self.large_font = (self.default_font_name, 14)

        # 初始化 BooleanVar
        self._init_boolean_vars()

        # 检查更新（会创建 self.gacha_system）
        self.check_for_updates()

        # 确保 GachaSystem 已正确初始化
        if not hasattr(self.gacha_system, 'pools'):
            messagebox.showerror("错误", "无法加载卡池数据。请重新启动程序。")
            import sys
            sys.exit(1)

        # 初始化 GUI 组件
        self.initialize_gui_components()

        # 显示主窗口
        self.root.deiconify()

    def _init_boolean_vars(self):
        """初始化小保底机制相关的 BooleanVar"""
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

    # ── 更新检查 ──────────────────────────────────────────

    def check_for_updates(self):
        if os.path.exists(BANNER_FILE):
            check_update = messagebox.askyesno(
                "更新确认", "是否检查卡池文件更新？（修改卡池了的不要选更新）"
            )
            no_update = not check_update
        else:
            no_update = False
        self.gacha_system = GachaSystem(BANNER_FILE, no_update=no_update)

    # ── GUI 初始化 ────────────────────────────────────────

    def initialize_gui_components(self):
        self.banner_id_map = {}
        self.banner_name_map = {}
        self.initialize_banner_maps()
        self.setup_gui()

    def initialize_banner_maps(self):
        character_banners, weapon_banners = self.gacha_system.categorize_banners()
        all_banners = character_banners + weapon_banners
        for banner_id, banner_name in all_banners:
            self.banner_id_map[banner_name] = banner_id
            self.banner_name_map[banner_id] = banner_name

    def setup_gui(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.left_frame = ttk.Frame(self.main_frame, width=250)
        self.right_frame = ttk.Frame(self.main_frame)

        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.left_frame.pack_propagate(False)

        self.setup_left_frame()
        self.setup_right_frame()

    # ── 左侧面板 ──────────────────────────────────────────

    def setup_left_frame(self):
        # 卡池切换
        banner_frame = ttk.LabelFrame(self.left_frame, text="卡池切换")
        banner_frame.pack(pady=2, padx=5, fill=tk.X)

        self.toggle_button = ttk.Button(
            banner_frame,
            text=f"切换到{WEAPON_DISPLAY_NAME}池列表",
            command=self.toggle_banner_type,
        )
        self.toggle_button.grid(row=0, column=0, pady=2, padx=2, sticky="ew")

        self.standard_banner_button = ttk.Button(
            banner_frame,
            text="切换到常驻池",
            command=self.select_standard_banner,
        )
        self.standard_banner_button.grid(row=0, column=1, pady=2, padx=2, sticky="ew")

        self.banner_listbox = tk.Listbox(banner_frame, height=8, font=self.default_font)
        self.banner_listbox.grid(
            row=1, column=0, columnspan=2, pady=2, padx=2, sticky="nsew"
        )

        self.switch_banner_button = ttk.Button(
            banner_frame, text="切换到选择的卡池", command=self.on_switch_banner
        )
        self.switch_banner_button.grid(
            row=2, column=0, columnspan=2, pady=2, padx=2, sticky="ew"
        )

        banner_frame.columnconfigure(0, weight=1)
        banner_frame.columnconfigure(1, weight=1)

        # 抽卡
        gacha_frame = ttk.LabelFrame(self.left_frame, text="抽卡")
        gacha_frame.pack(pady=2, padx=5, fill=tk.X)

        self.pull_1_button = ttk.Button(
            gacha_frame, text="抽一次", command=lambda: self.on_pull(1)
        )
        self.pull_1_button.grid(row=0, column=0, pady=2, padx=2, sticky="ew")

        self.pull_10_button = ttk.Button(
            gacha_frame, text="十连抽！", command=lambda: self.on_pull(10)
        )
        self.pull_10_button.grid(row=0, column=1, pady=2, padx=2, sticky="ew")

        self.pull_pity_button = ttk.Button(
            gacha_frame,
            text="抽一个小保底",
            command=lambda: self.on_pull(self.get_current_pity()),
        )
        self.pull_pity_button.grid(
            row=1, column=0, columnspan=2, pady=2, padx=2, sticky="ew"
        )

        gacha_frame.columnconfigure(0, weight=1)
        gacha_frame.columnconfigure(1, weight=1)

        # 工具箱
        util_frame = ttk.LabelFrame(self.left_frame, text="工具箱")
        util_frame.pack(pady=2, padx=5, fill=tk.X)

        self.random_tip_button = ttk.Button(
            util_frame, text="随机Tips", command=self.show_random_tip
        )
        self.random_tip_button.grid(row=0, column=0, pady=2, padx=2, sticky="ew")

        self.prob_settings_button = ttk.Button(
            util_frame, text="修改当前卡池概率", command=self.open_probability_settings
        )
        self.prob_settings_button.grid(row=0, column=1, pady=2, padx=2, sticky="ew")

        self.version_button = ttk.Button(
            util_frame, text="查看当前版本", command=self.show_version
        )
        self.version_button.grid(row=1, column=0, pady=2, padx=2, sticky="ew")

        self.update_button = ttk.Button(
            util_frame, text="检查卡池更新", command=self.check_pool_update
        )
        self.update_button.grid(row=1, column=1, pady=2, padx=2, sticky="ew")

        self.clear_data_button = ttk.Button(
            util_frame, text="重置抽卡统计数据", command=self.clear_gacha_data
        )
        self.clear_data_button.grid(
            row=2, column=0, columnspan=2, pady=2, padx=2, sticky="ew"
        )

        util_frame.columnconfigure(0, weight=1)
        util_frame.columnconfigure(1, weight=1)

        # 统计信息
        self.stats_frame = ttk.LabelFrame(self.left_frame, text="统计信息")
        self.stats_frame.pack(pady=2, padx=5, fill=tk.X)

        self.current_stats_label = ttk.Label(
            self.stats_frame, text="当前显示的是角色池的数据", font=self.default_font
        )
        self.current_stats_label.pack(pady=2)
        self.current_banner_type = StringVar(value="character")

        self.stats_text = tk.Text(
            self.stats_frame, width=25, font=self.default_font, wrap=tk.WORD
        )
        self.stats_text.pack(fill=tk.X, expand=True)
        self.stats_text.config(state=tk.DISABLED)

        self.banner_listbox.bind("<Double-1>", self.show_banner_details)

        self.update_banner_list()
        self.update_stats_display()

    # ── 右侧面板 ──────────────────────────────────────────

    def setup_right_frame(self):
        # 卡池信息
        banner_info_frame = ttk.Frame(self.right_frame)
        banner_info_frame.pack(fill=tk.X, pady=10, padx=10)

        self.banner_label_var = StringVar()
        self.banner_label = ttk.Label(
            banner_info_frame,
            textvariable=self.banner_label_var,
            font=self.large_font,
        )
        self.banner_label.pack(side=tk.LEFT)

        self.clear_history_button = ttk.Button(
            banner_info_frame, text="清空抽卡记录", command=self.clear_pull_history
        )
        self.clear_history_button.pack(side=tk.RIGHT)

        # 抽卡历史
        history_frame = ttk.LabelFrame(self.right_frame, text="抽卡历史")
        history_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        columns = ('时间', '星级', '类型', '名称', '卡池', '是否UP')
        self.pull_history_tree = ttk.Treeview(
            history_frame, columns=columns, show='headings'
        )

        column_widths = {
            '时间': 150, '星级': 50, '类型': 50,
            '名称': 150, '卡池': 150, '是否UP': 50,
        }
        for col in columns:
            self.pull_history_tree.heading(col, text=col, anchor='center')
            self.pull_history_tree.column(
                col, width=column_widths[col], anchor='center'
            )

        vsb = ttk.Scrollbar(
            history_frame, orient="vertical",
            command=self.pull_history_tree.yview,
        )
        self.pull_history_tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(
            history_frame, orient="horizontal",
            command=self.pull_history_tree.xview,
        )
        self.pull_history_tree.configure(xscrollcommand=hsb.set)

        self.pull_history_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)

        # Tips
        tips_frame = ttk.LabelFrame(self.right_frame, text="Tips")
        tips_frame.pack(pady=10, padx=10, fill=tk.X)

        self.tip_label = ttk.Label(
            tips_frame, text="", font=self.default_font,
            foreground="blue", wraplength=500,
        )
        self.tip_label.pack(pady=5, padx=5)

        self.update_gui_banner_name()
        self.show_random_tip()

        self.pull_history_tree.bind("<Double-1>", self.show_item_details)

    # ── 卡池切换 ──────────────────────────────────────────

    def toggle_banner_type(self):
        if self.current_banner_type.get() == "character":
            self.current_banner_type.set("weapon")
            self.toggle_button.config(
                text=f"切换到{CHARACTER_DISPLAY_NAME}池列表"
            )
        else:
            self.current_banner_type.set("character")
            self.toggle_button.config(
                text=f"切换到{WEAPON_DISPLAY_NAME}池列表"
            )
        self.update_banner_list()

    def select_standard_banner(self):
        standard_banner = self.gacha_system.get_standard_banner()
        if standard_banner:
            if self.gacha_system.switch_banner(standard_banner):
                banner_info = self.gacha_system.pools['banners'].get(
                    standard_banner, {}
                )
                banner_name = banner_info.get('name', standard_banner)
                self.update_gui_banner_name()
                self.update_banner_list()
                self.update_stats_display('standard')
                messagebox.showinfo("提示", f"已切换到常驻池：{banner_name}")
            else:
                messagebox.showerror("错误", "切换到常驻池失败")
        else:
            messagebox.showinfo("提示", "未找到常驻池")

    def update_banner_list(self):
        self.banner_listbox.delete(0, tk.END)
        character_banners, weapon_banners = self.gacha_system.categorize_banners()
        banners_to_show = (
            character_banners
            if self.current_banner_type.get() == "character"
            else weapon_banners
        )

        for banner_id, banner_name in banners_to_show:
            banner_info = self.gacha_system.pools['banners'][banner_id]
            if 'character_up_5_star' in banner_info:
                up = banner_info['character_up_5_star'][0]
                display_name = f"{banner_name} - UP: {up}"
            elif 'weapon_up_5_star' in banner_info:
                up = banner_info['weapon_up_5_star'][0]
                display_name = f"{banner_name} - UP: {up}"
            else:
                display_name = banner_name
            self.banner_listbox.insert(tk.END, display_name)
            if (
                self.gacha_system.current_banner is not None
                and banner_id == self.gacha_system.current_banner
            ):
                self.banner_listbox.selection_set(tk.END)

    def on_switch_banner(self):
        selected_indices = self.banner_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("提示", "你还没有选择一个卡池")
            return

        selected_banner_display_name = self.banner_listbox.get(selected_indices[0])
        selected_banner_name = selected_banner_display_name.split(" - UP:")[0]
        selected_banner_id = self.banner_id_map.get(selected_banner_name)

        if selected_banner_id:
            if self.gacha_system.switch_banner(selected_banner_id):
                self.update_banner_list()
                self.update_gui_banner_name()

                new_pool_type = self.gacha_system.pools['banners'][
                    selected_banner_id
                ].get('pool_type', 'standard')
                self.update_stats_display(new_pool_type)

                banner_info = self.gacha_system.pools['banners'].get(
                    selected_banner_id, {}
                )
                banner_name = banner_info.get('name', selected_banner_name)
                messagebox.showinfo("提示", f"已切换到卡池：{banner_name}")
            else:
                messagebox.showerror(
                    "错误", f"切换到卡池 {selected_banner_name} 失败"
                )
        else:
            messagebox.showerror("错误", f"未找到卡池 {selected_banner_name} 的ID")

        self.update_stats_display()

    def show_banner_details(self, event):
        selected_index = event.widget.nearest(event.y)
        selected_banner_display_name = self.banner_listbox.get(selected_index)
        selected_banner_name = selected_banner_display_name.split(" - UP:")[0]
        selected_banner_id = self.banner_id_map.get(selected_banner_name)

        if selected_banner_id:
            banner_info = self.gacha_system.pools['banners'].get(
                selected_banner_id, {}
            )
        else:
            banner_info = {}

        pool_type = banner_info.get('pool_type', 'standard')
        pool_type_display = (
            WEAPON_DISPLAY_NAME if pool_type == 'weapon' else CHARACTER_DISPLAY_NAME
        )

        up_5_key = f'{pool_type}_up_5_star'
        up_4_key = f'{pool_type}_up_4_star'
        up_5_info = banner_info.get(up_5_key, [])
        up_4_info = banner_info.get(up_4_key, [])

        details = (
            f"卡池名称: {banner_info.get('name', '未知')}\n"
            f"卡池类型: {pool_type_display}\n"
            f"UP的五星{pool_type_display}: "
            f"{' | '.join(up_5_info) if up_5_info else '无'}\n"
            f"UP的四星{pool_type_display}: "
            f"{' | '.join(up_4_info) if up_4_info else '无'}"
        )
        messagebox.showinfo("卡池详情", details)

    # ── 抽卡操作 ──────────────────────────────────────────

    def on_pull(self, num_pulls):
        pulls = self.gacha_system.perform_pull(num_pulls)
        if pulls:
            self.update_gui_pull_history(pulls)
            self.gacha_system.save_state()

            current_pool_type = self.gacha_system.pools['banners'][
                self.gacha_system.current_banner
            ].get('pool_type', 'standard')
            self.update_stats_display(current_pool_type)

    def get_current_pity(self):
        if self.gacha_system.current_banner:
            pool_type = self.gacha_system.pools['banners'][
                self.gacha_system.current_banner
            ].get('pool_type', 'standard')
            if pool_type == 'character':
                return self.gacha_system.current_prob['character_five_star_pity']
            elif pool_type == 'weapon':
                return self.gacha_system.current_prob['weapon_five_star_pity']
            else:
                return self.gacha_system.current_prob['standard_five_star_pity']
        else:
            return self.gacha_system.current_prob['standard_five_star_pity']

    def update_gui_banner_name(self):
        if self.gacha_system.current_banner:
            banner_info = self.gacha_system.pools['banners'].get(
                self.gacha_system.current_banner, {}
            )
            banner_name = banner_info.get('name', self.gacha_system.current_banner)
            self.banner_label_var.set(f"当前卡池: {banner_name}")
        else:
            self.banner_label_var.set("当前卡池: 未选择")

    def update_gui_pull_history(self, pulls):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_banner_info = self.gacha_system.pools['banners'].get(
            self.gacha_system.current_banner, {}
        )
        current_banner_name = current_banner_info.get(
            'name', self.gacha_system.current_banner
        )
        is_standard_banner = current_banner_info.get('pool_type') == 'standard'

        for rarity, item_type, item in pulls:
            display_rarity = rarity.replace('_star', '星')
            tag = display_rarity.split('星')[0]

            is_up = ""
            if not is_standard_banner and rarity in ['4_star', '5_star']:
                up_items = current_banner_info.get(f"{item_type}_up_{rarity}", [])
                if not up_items and item_type == CHARACTER_DISPLAY_NAME:
                    up_items = current_banner_info.get(f"character_up_{rarity}", [])
                elif not up_items and item_type == WEAPON_DISPLAY_NAME:
                    up_items = current_banner_info.get(f"weapon_up_{rarity}", [])
                is_up = "是" if item in up_items else "否"

            if rarity == '3_star' or is_standard_banner:
                is_up = ""

            self.pull_history_tree.insert(
                '', 0,
                values=(
                    current_time, display_rarity, item_type, item,
                    current_banner_name, is_up,
                ),
                tags=(tag,),
            )

        self.pull_history_tree.tag_configure('5', foreground='gold')
        self.pull_history_tree.tag_configure('4', foreground='purple')

    def show_random_tip(self):
        self.tip_label.config(text=random.choice(self.gacha_system.TIPS))

    # ── 统计数据显示 ──────────────────────────────────────

    def update_stats_display(self, pool_type=None):
        if pool_type is None:
            if self.gacha_system.current_banner:
                banner_info = self.gacha_system.pools['banners'].get(
                    self.gacha_system.current_banner, {}
                )
                pool_type = banner_info.get('pool_type', 'standard')
            else:
                pool_type = 'standard'

        stats_data = self._get_stats_data(pool_type)

        gold_records = stats_data['gold_records']
        if gold_records:
            avg_gold = f"{sum(gold_records) / len(gold_records):.2f}"
            min_gold = min(gold_records)
            max_gold = max(gold_records)
        else:
            avg_gold = "暂无数据"
            min_gold = "暂无数据"
            max_gold = "暂无数据"

        total_featured = (
            stats_data['successful_featured'] + stats_data['failed_featured']
        )
        if total_featured > 0:
            success_rate = (
                f"{stats_data['successful_featured'] / total_featured * 100:.2f}%"
            )
        else:
            success_rate = "暂无数据"

        lines = [
            f"{stats_data['stats_type']}的抽取次数: {stats_data['pool_pulls']}",
            f"距离下一个5星保底的抽数: "
            f"{stats_data['five_star_pity'] - stats_data['pity_5']}",
            f"距离下一个4星保底: "
            f"{stats_data['four_star_pity'] - stats_data['pity_4']}",
            f"获得5星次数: {len(gold_records)}",
            f"获得4星次数: {len(stats_data['purple_records'])}",
            f"最少抽数出金: {min_gold}",
            f"最多抽数出金: {max_gold}",
            f"平均出金抽数: {avg_gold}",
        ]

        if pool_type != 'standard':
            lines.append(f"歪掉5星次数: {stats_data['failed_featured']}")
            lines.append(f"小保底不歪概率: {success_rate}")
        else:
            lines.append("歪掉5星次数: 无")
            lines.append("小保底不歪概率: 无")

        lines.append(f"距离上次5星: {stats_data['pulls_since_last_5star']}")

        # 大保底状态
        if stats_data['big_pity_enabled']:
            if pool_type != 'standard':
                lines.append(
                    f"5星大保底状态: "
                    f"{'是' if stats_data['is_guaranteed'] else '否'}"
                )
            else:
                lines.append("5星大保底状态: 无")
        else:
            lines.append("5星大保底状态: 你没有启用大保底机制")

        if stats_data['big_pity_4_enabled']:
            if pool_type != 'standard':
                lines.append(
                    f"4星大保底状态: "
                    f"{'是' if stats_data['four_star_guaranteed'] else '否'}"
                )
            else:
                lines.append("4星大保底状态: 无")
        else:
            lines.append("4星大保底状态: 你没有启用大保底机制")

        # 小保底机制
        mechanism_names = {
            'random': '默认', 'must_not_waste': '必不歪', 'must_waste': '必歪',
        }
        if pool_type != 'standard':
            lines.append(
                f"5星小保底机制: "
                f"{mechanism_names.get(stats_data['five_star_small_pity'], '无效')}"
            )
            lines.append(
                f"4星小保底机制: "
                f"{mechanism_names.get(stats_data['four_star_small_pity'], '无效')}"
            )
        else:
            lines.append("5星小保底机制: 无")
            lines.append("4星小保底机制: 无")

        luck_rating = self.gacha_system.calculate_luck(pool_type)
        lines.append(f"抽卡运势: {luck_rating}")

        self.current_stats_label.config(
            text=f"当前显示的是{stats_data['stats_type']}的数据"
        )
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, '\n'.join(lines))
        self.stats_text.config(state=tk.DISABLED)

        self.stats_text.update_idletasks()
        height = self.stats_text.count('1.0', 'end', 'displaylines')
        self.stats_text.config(height=height)

    def _get_stats_data(self, pool_type):
        """获取指定池类型的所有统计数据"""
        gs = self.gacha_system
        if pool_type == 'character':
            return {
                'stats_type': f"{CHARACTER_DISPLAY_NAME}池",
                'pity_5': gs.character_pity_5,
                'pity_4': gs.character_pity_4,
                'gold_records': gs.character_gold_records,
                'purple_records': gs.character_purple_records,
                'failed_featured': gs.character_failed_featured_5star,
                'successful_featured': gs.character_successful_featured_5star,
                'pulls_since_last_5star': gs.character_pulls_since_last_5star,
                'is_guaranteed': gs.character_is_guaranteed,
                'pool_pulls': gs.character_pulls,
                'five_star_pity': gs.current_prob['character_five_star_pity'],
                'four_star_pity': gs.current_prob['character_four_star_pity'],
                'five_star_small_pity': gs.current_prob[
                    'character_five_star_small_pity_mechanism'
                ],
                'four_star_small_pity': gs.current_prob[
                    'character_four_star_small_pity_mechanism'
                ],
                'big_pity_enabled': gs.current_prob[
                    'character_five_star_big_pity_enabled'
                ],
                'big_pity_4_enabled': gs.current_prob[
                    'character_four_star_big_pity_enabled'
                ],
                'four_star_guaranteed': gs.character_four_star_guaranteed,
            }
        elif pool_type == 'weapon':
            return {
                'stats_type': f"{WEAPON_DISPLAY_NAME}池",
                'pity_5': gs.weapon_pity_5,
                'pity_4': gs.weapon_pity_4,
                'gold_records': gs.weapon_gold_records,
                'purple_records': gs.weapon_purple_records,
                'failed_featured': gs.weapon_failed_featured_5star,
                'successful_featured': gs.weapon_successful_featured_5star,
                'pulls_since_last_5star': gs.weapon_pulls_since_last_5star,
                'is_guaranteed': gs.weapon_is_guaranteed,
                'pool_pulls': gs.weapon_pulls,
                'five_star_pity': gs.current_prob['weapon_five_star_pity'],
                'four_star_pity': gs.current_prob['weapon_four_star_pity'],
                'five_star_small_pity': gs.current_prob[
                    'weapon_five_star_small_pity_mechanism'
                ],
                'four_star_small_pity': gs.current_prob[
                    'weapon_four_star_small_pity_mechanism'
                ],
                'big_pity_enabled': gs.current_prob[
                    'weapon_five_star_big_pity_enabled'
                ],
                'big_pity_4_enabled': gs.current_prob[
                    'weapon_four_star_big_pity_enabled'
                ],
                'four_star_guaranteed': gs.weapon_four_star_guaranteed,
            }
        else:
            return {
                'stats_type': "常驻池",
                'pity_5': gs.pity_5,
                'pity_4': gs.pity_4,
                'gold_records': gs.gold_records,
                'purple_records': gs.purple_records,
                'failed_featured': gs.failed_featured_5star,
                'successful_featured': gs.successful_featured_5star,
                'pulls_since_last_5star': gs.pulls_since_last_5star,
                'is_guaranteed': gs.is_guaranteed,
                'pool_pulls': gs.standard_pulls,
                'five_star_pity': gs.current_prob['standard_five_star_pity'],
                'four_star_pity': gs.current_prob['standard_four_star_pity'],
                'five_star_small_pity': 'random',
                'four_star_small_pity': 'random',
                'big_pity_enabled': True,
                'big_pity_4_enabled': True,
                'four_star_guaranteed': gs.four_star_guaranteed,
            }

    # ── 版本与更新 ────────────────────────────────────────

    def show_version(self):
        messagebox.showinfo(
            "版本信息",
            f"当前版本: {VERSION}\n作者：{AUTHOR}\n"
            f"Github：{GITHUB_REPO}\n来点Star叭~💖",
        )
        try:
            response = requests.get(
                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            )
            response.raise_for_status()
        except requests.exceptions.SSLError:
            response = requests.get(
                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                verify=False,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            messagebox.showerror("错误", f"检查更新时发生错误: {e}")
            return

        latest_release = response.json()
        latest_version = latest_release['tag_name']

        if self.compare_versions(latest_version, VERSION):
            messagebox.showinfo(
                "更新提示", f"检测到新版本 {latest_version}，请及时更新！"
            )
        else:
            messagebox.showinfo("已是最新版本", "你的程序已是最新版本。")

    @staticmethod
    def compare_versions(version1, version2):
        v1 = tuple(map(int, re.sub(r'^[^0-9]+', '', version1).split('.')))
        v2 = tuple(map(int, re.sub(r'^[^0-9]+', '', version2).split('.')))
        return v1 > v2

    def check_pool_update(self):
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

    # ── 物品详情 ──────────────────────────────────────────

    def show_item_details(self, event):
        selected_items = self.pull_history_tree.selection()
        if not selected_items:
            return
        item = selected_items[0]
        item_details = self.pull_history_tree.item(item, "values")
        messagebox.showinfo(
            "物品详情",
            f"名称: {item_details[3]}\n类型: {item_details[2]}\n"
            f"星级: {item_details[1]}\n是否UP: {item_details[5]}",
        )

    # ── 数据清理 ──────────────────────────────────────────

    def clear_gacha_data(self):
        confirm = messagebox.askyesno(
            "确认", "您确定要清除所有抽卡统计数据吗？此操作不可逆。"
        )
        if confirm:
            second_confirm = messagebox.askyesno(
                "二次确认", "真的要清除所有数据吗？这将重置所有统计信息。"
            )
            if second_confirm:
                self.gacha_system.reset_statistics()
                self.update_stats_display()
                messagebox.showinfo("成功", "所有抽卡统计数据已被清除。")

    def clear_pull_history(self):
        confirm = messagebox.askyesno(
            "确认", "您确定要清空抽卡记录吗？此操作不可逆。"
        )
        if confirm:
            self.pull_history_tree.delete(*self.pull_history_tree.get_children())
            self.gacha_system.pull_history = []
            self.gacha_system.save_state()
            messagebox.showinfo("成功", "抽卡记录已清空。")

    # ── 概率设置窗口 ──────────────────────────────────────

    def open_probability_settings(self, pool_type=None):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("概率设置")
        settings_window.geometry("450x500")

        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill="both", expand=True)

        tab_character = ttk.Frame(notebook, padding="30")
        tab_weapon = ttk.Frame(notebook, padding="30")
        tab_standard = ttk.Frame(notebook, padding="30")

        notebook.add(tab_character, text=f"{CHARACTER_DISPLAY_NAME}池")
        notebook.add(tab_weapon, text=f"{WEAPON_DISPLAY_NAME}池")
        notebook.add(tab_standard, text="常驻池")

        if pool_type is None:
            if self.gacha_system.current_banner:
                banner_info = self.gacha_system.pools['banners'].get(
                    self.gacha_system.current_banner, {}
                )
                pool_type = banner_info.get('pool_type', 'standard')
            else:
                pool_type = 'standard'

        if pool_type == 'character':
            notebook.select(tab_character)
        elif pool_type == 'weapon':
            notebook.select(tab_weapon)
        else:
            notebook.select(tab_standard)

        self._setup_character_prob_tab(tab_character)
        self._setup_weapon_prob_tab(tab_weapon)
        self._setup_standard_prob_tab(tab_standard)

        # 保存 / 恢复按钮
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(side="bottom", fill="x", expand=True, padx=5, pady=5)

        save_button = ttk.Button(
            button_frame, text="保存设置",
            command=lambda: self.save_probability_settings(settings_window),
        )
        default_button = ttk.Button(
            button_frame, text="恢复默认设置",
            command=lambda: self.restore_default_settings(settings_window),
        )
        save_button.pack(side="left", expand=True)
        default_button.pack(side="left", expand=True)

    def _setup_character_prob_tab(self, tab):
        gs = self.gacha_system
        self.character_five_star_prob = StringVar(
            value=str(gs.current_prob['character_five_star_base'])
        )
        ttk.Label(tab, text="5星基础概率:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.character_five_star_prob, width=10).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(0.006 = 0.6%)").grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )

        self.character_five_star_success_prob = StringVar(
            value=str(gs.current_prob['character_five_star_success_prob'])
        )
        ttk.Label(tab, text="5星不歪概率:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            tab, textvariable=self.character_five_star_success_prob, width=10
        ).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(tab, text="(0.5 = 50%)").grid(
            row=1, column=2, sticky="w", padx=5, pady=5
        )

        self.character_five_star_pity = StringVar(
            value=str(gs.current_prob['character_five_star_pity'])
        )
        ttk.Label(tab, text="5星保底抽数:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.character_five_star_pity, width=10).grid(
            row=2, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(默认: 90)").grid(
            row=2, column=2, sticky="w", padx=5, pady=5
        )

        self.character_four_star_prob = StringVar(
            value=str(gs.current_prob['character_four_star_base'])
        )
        ttk.Label(tab, text="4星基础概率:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.character_four_star_prob, width=10).grid(
            row=3, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(0.051 = 5.1%)").grid(
            row=3, column=2, sticky="w", padx=5, pady=5
        )

        self.character_four_star_success_prob = StringVar(
            value=str(gs.current_prob['character_four_star_success_prob'])
        )
        ttk.Label(tab, text="4星不歪概率:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            tab, textvariable=self.character_four_star_success_prob, width=10
        ).grid(row=4, column=1, padx=5, pady=5)
        ttk.Label(tab, text="(0.5 = 50%)").grid(
            row=4, column=2, sticky="w", padx=5, pady=5
        )

        self.character_four_star_pity = StringVar(
            value=str(gs.current_prob['character_four_star_pity'])
        )
        ttk.Label(tab, text="4星保底抽数:").grid(
            row=5, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.character_four_star_pity, width=10).grid(
            row=5, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(默认: 10)").grid(
            row=5, column=2, sticky="w", padx=5, pady=5
        )

        self._setup_small_pity_radiobuttons(
            tab, row=6,
            var_random=self.character_five_star_small_pity_var_random,
            var_waste=self.character_five_star_small_pity_var_must_waste,
            var_not_waste=self.character_five_star_small_pity_var_must_not_waste,
            current_key='character_five_star_small_pity_mechanism',
            label="5星小保底机制",
        )
        self._setup_small_pity_radiobuttons(
            tab, row=7,
            var_random=self.character_four_star_small_pity_var_random,
            var_waste=self.character_four_star_small_pity_var_must_waste,
            var_not_waste=self.character_four_star_small_pity_var_must_not_waste,
            current_key='character_four_star_small_pity_mechanism',
            label="4星小保底机制",
        )

        self.character_five_star_big_pity_enabled = BooleanVar(
            value=gs.current_prob['character_five_star_big_pity_enabled']
        )
        ttk.Checkbutton(
            tab, text="启用5星大保底机制",
            variable=self.character_five_star_big_pity_enabled,
        ).grid(row=8, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        self.character_four_star_big_pity_enabled = BooleanVar(
            value=gs.current_prob['character_four_star_big_pity_enabled']
        )
        ttk.Checkbutton(
            tab, text="启用4星大保底机制",
            variable=self.character_four_star_big_pity_enabled,
        ).grid(row=8, column=2, columnspan=3, sticky="w", padx=5, pady=5)

    def _setup_weapon_prob_tab(self, tab):
        gs = self.gacha_system
        self.weapon_five_star_prob = StringVar(
            value=str(gs.current_prob['weapon_five_star_base'])
        )
        ttk.Label(tab, text="5星基础概率:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.weapon_five_star_prob, width=10).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(0.008 = 0.8%)").grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )

        self.weapon_five_star_success_prob = StringVar(
            value=str(gs.current_prob['weapon_five_star_success_prob'])
        )
        ttk.Label(tab, text="5星不歪概率:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            tab, textvariable=self.weapon_five_star_success_prob, width=10
        ).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(tab, text="(0.75 = 75%)").grid(
            row=1, column=2, sticky="w", padx=5, pady=5
        )

        self.weapon_five_star_pity = StringVar(
            value=str(gs.current_prob['weapon_five_star_pity'])
        )
        ttk.Label(tab, text="5星保底抽数:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.weapon_five_star_pity, width=10).grid(
            row=2, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(默认: 80)").grid(
            row=2, column=2, sticky="w", padx=5, pady=5
        )

        self.weapon_four_star_prob = StringVar(
            value=str(gs.current_prob['weapon_four_star_base'])
        )
        ttk.Label(tab, text="4星基础概率:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.weapon_four_star_prob, width=10).grid(
            row=3, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(0.066 = 6.6%)").grid(
            row=3, column=2, sticky="w", padx=5, pady=5
        )

        self.weapon_four_star_success_prob = StringVar(
            value=str(gs.current_prob['weapon_four_star_success_prob'])
        )
        ttk.Label(tab, text="4星不歪概率:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            tab, textvariable=self.weapon_four_star_success_prob, width=10
        ).grid(row=4, column=1, padx=5, pady=5)
        ttk.Label(tab, text="(0.75 = 75%)").grid(
            row=4, column=2, sticky="w", padx=5, pady=5
        )

        self.weapon_four_star_pity = StringVar(
            value=str(gs.current_prob['weapon_four_star_pity'])
        )
        ttk.Label(tab, text="4星保底抽数:").grid(
            row=5, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.weapon_four_star_pity, width=10).grid(
            row=5, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(默认: 10)").grid(
            row=5, column=2, sticky="w", padx=5, pady=5
        )

        self._setup_small_pity_radiobuttons(
            tab, row=6,
            var_random=self.weapon_five_star_small_pity_var_random,
            var_waste=self.weapon_five_star_small_pity_var_must_waste,
            var_not_waste=self.weapon_five_star_small_pity_var_must_not_waste,
            current_key='weapon_five_star_small_pity_mechanism',
            label="5星小保底机制",
        )
        self._setup_small_pity_radiobuttons(
            tab, row=7,
            var_random=self.weapon_four_star_small_pity_var_random,
            var_waste=self.weapon_four_star_small_pity_var_must_waste,
            var_not_waste=self.weapon_four_star_small_pity_var_must_not_waste,
            current_key='weapon_four_star_small_pity_mechanism',
            label="4星小保底机制",
        )

        self.weapon_five_star_big_pity_enabled = BooleanVar(
            value=gs.current_prob['weapon_five_star_big_pity_enabled']
        )
        ttk.Checkbutton(
            tab, text="启用5星大保底机制",
            variable=self.weapon_five_star_big_pity_enabled,
        ).grid(row=8, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        self.weapon_four_star_big_pity_enabled = BooleanVar(
            value=gs.current_prob['weapon_four_star_big_pity_enabled']
        )
        ttk.Checkbutton(
            tab, text="启用4星大保底机制",
            variable=self.weapon_four_star_big_pity_enabled,
        ).grid(row=8, column=2, columnspan=3, sticky="w", padx=5, pady=5)

    def _setup_standard_prob_tab(self, tab):
        gs = self.gacha_system
        self.standard_five_star_prob = StringVar(
            value=str(gs.current_prob['standard_five_star_base'])
        )
        ttk.Label(tab, text="5星基础概率:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.standard_five_star_prob, width=10).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(0.006 = 0.6%)").grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )

        self.standard_five_star_pity = StringVar(
            value=str(gs.current_prob['standard_five_star_pity'])
        )
        ttk.Label(tab, text="5星保底抽数:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.standard_five_star_pity, width=10).grid(
            row=1, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(默认: 90)").grid(
            row=1, column=2, sticky="w", padx=5, pady=5
        )

        self.standard_four_star_prob = StringVar(
            value=str(gs.current_prob['standard_four_star_base'])
        )
        ttk.Label(tab, text="常驻池4星基础概率:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.standard_four_star_prob, width=10).grid(
            row=2, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(0.051 = 5.1%)").grid(
            row=2, column=2, sticky="w", padx=5, pady=5
        )

        self.standard_four_star_pity = StringVar(
            value=str(gs.current_prob['standard_four_star_pity'])
        )
        ttk.Label(tab, text="常驻池4星保底抽数:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(tab, textvariable=self.standard_four_star_pity, width=10).grid(
            row=3, column=1, padx=5, pady=5
        )
        ttk.Label(tab, text="(默认: 10)").grid(
            row=3, column=2, sticky="w", padx=5, pady=5
        )

    def _setup_small_pity_radiobuttons(
        self, tab, row, var_random, var_waste, var_not_waste,
        current_key, label,
    ):
        """创建小保底机制的三个单选按钮"""
        frame = ttk.LabelFrame(tab, text=label)
        frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=5, padx=5)

        def select_random():
            var_waste.set(False)
            var_not_waste.set(False)

        def select_waste():
            var_random.set(False)
            var_not_waste.set(False)

        def select_not_waste():
            var_random.set(False)
            var_waste.set(False)

        ttk.Radiobutton(
            frame, text="随机", variable=var_random, command=select_random
        ).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Radiobutton(
            frame, text="必歪", variable=var_waste, command=select_waste
        ).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(
            frame, text="必不歪", variable=var_not_waste, command=select_not_waste
        ).grid(row=0, column=2, sticky="w", padx=5)

        # 根据当前设置初始化
        current = self.gacha_system.current_prob.get(current_key, 'random')
        if current == 'random':
            var_random.set(True)
        elif current == 'must_waste':
            var_waste.set(True)
        else:
            var_not_waste.set(True)

    # ── 概率保存 / 恢复 ──────────────────────────────────

    def save_probability_settings(self, window):
        try:
            gs = self.gacha_system
            # 小保底机制
            self._save_small_pity(
                gs, 'character_five_star_small_pity_mechanism',
                self.character_five_star_small_pity_var_random,
                self.character_five_star_small_pity_var_must_waste,
                self.character_five_star_small_pity_var_must_not_waste,
            )
            self._save_small_pity(
                gs, 'character_four_star_small_pity_mechanism',
                self.character_four_star_small_pity_var_random,
                self.character_four_star_small_pity_var_must_waste,
                self.character_four_star_small_pity_var_must_not_waste,
            )
            self._save_small_pity(
                gs, 'weapon_five_star_small_pity_mechanism',
                self.weapon_five_star_small_pity_var_random,
                self.weapon_five_star_small_pity_var_must_waste,
                self.weapon_five_star_small_pity_var_must_not_waste,
            )
            self._save_small_pity(
                gs, 'weapon_four_star_small_pity_mechanism',
                self.weapon_four_star_small_pity_var_random,
                self.weapon_four_star_small_pity_var_must_waste,
                self.weapon_four_star_small_pity_var_must_not_waste,
            )

            # 数值类
            gs.update_probability(
                'character_five_star_base',
                float(self.character_five_star_prob.get()),
            )
            gs.update_probability(
                'weapon_five_star_base', float(self.weapon_five_star_prob.get())
            )
            gs.update_probability(
                'character_four_star_base',
                float(self.character_four_star_prob.get()),
            )
            gs.update_probability(
                'weapon_four_star_base', float(self.weapon_four_star_prob.get())
            )
            gs.update_probability(
                'character_five_star_pity',
                int(self.character_five_star_pity.get()),
            )
            gs.update_probability(
                'weapon_five_star_pity', int(self.weapon_five_star_pity.get())
            )
            gs.update_probability(
                'character_five_star_success_prob',
                float(self.character_five_star_success_prob.get()),
            )
            gs.update_probability(
                'weapon_five_star_success_prob',
                float(self.weapon_five_star_success_prob.get()),
            )
            gs.update_probability(
                'character_four_star_success_prob',
                float(self.character_four_star_success_prob.get()),
            )
            gs.update_probability(
                'weapon_four_star_success_prob',
                float(self.weapon_four_star_success_prob.get()),
            )
            gs.update_probability(
                'character_four_star_pity',
                int(self.character_four_star_pity.get()),
            )
            gs.update_probability(
                'weapon_four_star_pity', int(self.weapon_four_star_pity.get())
            )
            gs.update_probability(
                'character_five_star_big_pity_enabled',
                self.character_five_star_big_pity_enabled.get(),
            )
            gs.update_probability(
                'character_four_star_big_pity_enabled',
                self.character_four_star_big_pity_enabled.get(),
            )
            gs.update_probability(
                'weapon_five_star_big_pity_enabled',
                self.weapon_five_star_big_pity_enabled.get(),
            )
            gs.update_probability(
                'weapon_four_star_big_pity_enabled',
                self.weapon_four_star_big_pity_enabled.get(),
            )
            gs.update_probability(
                'standard_five_star_base',
                float(self.standard_five_star_prob.get()),
            )
            gs.update_probability(
                'standard_five_star_pity', int(self.standard_five_star_pity.get())
            )
            gs.update_probability(
                'standard_four_star_base',
                float(self.standard_four_star_prob.get()),
            )
            gs.update_probability(
                'standard_four_star_pity', int(self.standard_four_star_pity.get())
            )

            self.update_stats_display()
            messagebox.showinfo("成功", "概率设置已保存")
            window.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数值")

    @staticmethod
    def _save_small_pity(gs, key, var_random, var_waste, var_not_waste):
        if var_random.get():
            gs.update_probability(key, 'random')
        elif var_waste.get():
            gs.update_probability(key, 'must_waste')
        elif var_not_waste.get():
            gs.update_probability(key, 'must_not_waste')

    def restore_default_settings(self, window):
        defaults = DEFAULT_PROBABILITIES

        # 更新界面值
        self.character_five_star_prob.set(str(defaults['character_five_star_base']))
        self.weapon_five_star_prob.set(str(defaults['weapon_five_star_base']))
        self.character_four_star_prob.set(str(defaults['character_four_star_base']))
        self.weapon_four_star_prob.set(str(defaults['weapon_four_star_base']))
        self.character_five_star_pity.set(str(defaults['character_five_star_pity']))
        self.weapon_five_star_pity.set(str(defaults['weapon_five_star_pity']))
        self.character_five_star_success_prob.set(
            str(defaults['character_five_star_success_prob'])
        )
        self.weapon_five_star_success_prob.set(
            str(defaults['weapon_five_star_success_prob'])
        )
        self.character_four_star_success_prob.set(
            str(defaults['character_four_star_success_prob'])
        )
        self.weapon_four_star_success_prob.set(
            str(defaults['weapon_four_star_success_prob'])
        )
        self.character_four_star_pity.set(str(defaults['character_four_star_pity']))
        self.weapon_four_star_pity.set(str(defaults['weapon_four_star_pity']))
        self.character_five_star_big_pity_enabled.set(
            defaults['character_five_star_big_pity_enabled']
        )
        self.character_four_star_big_pity_enabled.set(
            defaults['character_four_star_big_pity_enabled']
        )
        self.weapon_five_star_big_pity_enabled.set(
            defaults['weapon_five_star_big_pity_enabled']
        )
        self.weapon_four_star_big_pity_enabled.set(
            defaults['weapon_four_star_big_pity_enabled']
        )
        self.standard_five_star_prob.set(str(defaults['standard_five_star_base']))
        self.standard_five_star_pity.set(str(defaults['standard_five_star_pity']))
        self.standard_four_star_prob.set(str(defaults['standard_four_star_base']))
        self.standard_four_star_pity.set(str(defaults['standard_four_star_pity']))

        # 小保底机制复位
        self.character_five_star_small_pity_var_random.set(True)
        self.character_four_star_small_pity_var_random.set(True)
        self.weapon_five_star_small_pity_var_random.set(True)
        self.weapon_four_star_small_pity_var_random.set(True)

        # 写入系统
        for key, value in defaults.items():
            self.gacha_system.update_probability(key, value)

        self.update_stats_display()
        messagebox.showinfo("成功", "已恢复默认设置")
        window.destroy()
