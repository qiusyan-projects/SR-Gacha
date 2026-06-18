"""
SR-Gacha 抽卡核心引擎模块
包含 GachaSystem 类：概率计算、保底机制、状态持久化
"""

import random
import os
import sys
from io import StringIO
from tkinter import messagebox

import requests
from ruamel.yaml import YAML

from constants import (
    BANNER_FILE,
    BANNER_DOWNLOAD_URL,
    CHARACTER_DISPLAY_NAME,
    WEAPON_DISPLAY_NAME,
    CYAN,
    DEFAULT_PROBABILITIES,
    GITHUB_PROXY,
    GREEN,
    RED,
    RESET,
    TIPS,
    YELLOW,
)

# 模块级 YAML 实例，全局共享
yaml = YAML()


class GachaSystem:
    """崩坏：星穹铁道抽卡模拟核心引擎"""

    def __init__(self, pool_file, prob_file='custom_probabilities.yaml', no_update=False):
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
                self.show_message(
                    f"检查更新时发生错误: {update_result}。\n将使用当前版本的卡池文件。",
                    YELLOW,
                )
        elif no_update:
            self.show_message("已跳过更新检查。", GREEN)
        else:
            return
        self.load_pools(pool_file)
        self.load_probabilities(prob_file)
        self.inits()

    # ── 卡池加载 ──────────────────────────────────────────

    def load_pools(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            self.pools = yaml.load(f)
        self.banners = list(self.pools['banners'].keys())

    def switch_banner(self, banner_name):
        if banner_name not in self.banners:
            return False
        self.current_banner = banner_name
        self.save_state()
        return True

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
        return next(
            (
                banner_id
                for banner_id, banner_info in self.pools['banners'].items()
                if banner_info.get('name') == '群星跃迁'
            ),
            None,
        )

    # ── 概率管理 ──────────────────────────────────────────

    def load_probabilities(self, prob_file):
        if not os.path.exists(prob_file):
            self.create_default_probabilities()
        with open(prob_file, 'r', encoding='utf-8') as f:
            self.probabilities = yaml.load(f)
        self.current_prob = self.probabilities['custom']

    def save_probabilities(self):
        with open(self.prob_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.probabilities, f)

    def update_probability(self, key, value):
        self.current_prob[key] = value
        self.probabilities['custom'][key] = value
        self.save_probabilities()

    def create_default_probabilities(self):
        default_probabilities = {'custom': dict(DEFAULT_PROBABILITIES)}

        yaml_str = "# 自定义概率设置文件\n"
        yaml_str += "# 请勿手动修改，除非你知道自己在做什么\n\n"

        yaml.default_flow_style = False
        yaml.width = 4096
        yaml.indent(mapping=2, sequence=4, offset=2)

        string_stream = StringIO()
        yaml.dump(default_probabilities, string_stream)
        data_str = string_stream.getvalue()

        # 添加注释
        comment_map = {
            'custom:': '# 自定义概率设置\ncustom:',
            'character_five_star_base:': '  # 角色池5星基础概率\n  character_five_star_base:',
            'weapon_five_star_base:': '  # 光锥池5星基础概率\n  weapon_five_star_base:',
            'character_four_star_base:': '  # 角色池4星基础概率\n  character_four_star_base:',
            'weapon_four_star_base:': '  # 光锥池4星基础概率\n  weapon_four_star_base:',
            'character_five_star_pity:': '  # 角色池5星保底抽数\n  character_five_star_pity:',
            'weapon_five_star_pity:': '  # 光锥池5星保底抽数\n  weapon_five_star_pity:',
            'character_five_star_success_prob:': '  # 角色池5星不歪概率\n  character_five_star_success_prob:',
            'weapon_five_star_success_prob:': '  # 光锥池5星不歪概率\n  weapon_five_star_success_prob:',
            'character_four_star_success_prob:': '  # 角色池4星不歪概率\n  character_four_star_success_prob:',
            'weapon_four_star_success_prob:': '  # 光锥池4星不歪概率\n  weapon_four_star_success_prob:',
            'character_four_star_pity:': '  # 角色池4星保底抽数\n  character_four_star_pity:',
            'weapon_four_star_pity:': '  # 光锥池4星保底抽数\n  weapon_four_star_pity:',
            'character_five_star_big_pity_enabled:': '  # 是否启用角色池5星大保底\n  character_five_star_big_pity_enabled:',
            'character_four_star_big_pity_enabled:': '  # 是否启用角色池4星大保底\n  character_four_star_big_pity_enabled:',
            'weapon_five_star_big_pity_enabled:': '  # 是否启用光锥池5星大保底\n  weapon_five_star_big_pity_enabled:',
            'weapon_four_star_big_pity_enabled:': '  # 是否启用光锥池4星大保底\n  weapon_four_star_big_pity_enabled:',
            'standard_five_star_base:': '  # 常驻池5星基础概率\n  standard_five_star_base:',
            'standard_five_star_pity:': '  # 常驻池5星保底抽数\n  standard_five_star_pity:',
            'standard_four_star_base:': '  # 常驻池4星基础概率\n  standard_four_star_base:',
            'standard_four_star_pity:': '  # 常驻池4星保底抽数\n  standard_four_star_pity:',
            'character_five_star_small_pity_mechanism:': '  # 角色池5星小保底歪的机制\n  character_five_star_small_pity_mechanism:',
            'character_four_star_small_pity_mechanism:': '  # 角色池4星小保底歪的机制\n  character_four_star_small_pity_mechanism:',
            'weapon_five_star_small_pity_mechanism:': '  # 光锥池5星小保底歪的机制\n  weapon_five_star_small_pity_mechanism:',
            'weapon_four_star_small_pity_mechanism:': '  # 光锥池4星小保底歪的机制\n  weapon_four_star_small_pity_mechanism:',
        }
        for old, new in comment_map.items():
            data_str = data_str.replace(old, new)

        yaml_str += data_str

        with open(self.prob_file, 'w', encoding='utf-8') as f:
            f.write(yaml_str)

        self.probabilities = default_probabilities
        self.current_prob = self.probabilities['custom']

    # ── 文件更新 ──────────────────────────────────────────

    def ensure_pool_file_exists(self):
        if not os.path.exists(self.pool_file):
            download = messagebox.askyesno(
                "错误", "卡池文件不存在。是否从GitHub下载最新的卡池文件？"
            )
            if download:
                try:
                    proxy_url = f"{GITHUB_PROXY}{BANNER_DOWNLOAD_URL}"
                    response = requests.get(proxy_url)
                    response.raise_for_status()
                    with open(self.pool_file, 'wb') as f:
                        f.write(response.content)
                    self.show_message("卡池文件下载成功！", GREEN)
                    self.is_first_download = True
                    self.load_pools(self.pool_file)
                    self.load_probabilities(self.prob_file)
                    self.inits()
                except requests.RequestException as e:
                    self.show_message(f"下载失败: {e}", RED)
                    sys.exit(1)
            else:
                self.show_message("请提供卡池文件。", RED)
                sys.exit(1)
        else:
            self.load_pools(self.pool_file)

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

    # ── 核心抽卡逻辑 ──────────────────────────────────────

    def perform_pull(self, num_pulls):
        if not self.current_banner:
            self.show_message("请先选择一个卡池。", RED)
            return

        banner = self.pools['banners'][self.current_banner]
        pool_type = banner.get('pool_type', 'standard')

        pulls = []

        # 确定当前池的概率参数
        prob = self._get_pool_prob_params(pool_type)

        for _ in range(num_pulls):
            self.total_pulls += 1
            self.banner_pulls[self.current_banner] = (
                self.banner_pulls.get(self.current_banner, 0) + 1
            )

            if pool_type == 'character':
                self.character_pulls += 1
            elif pool_type == 'weapon':
                self.weapon_pulls += 1
            else:
                self.standard_pulls += 1

            stats = self.get_pool_stats(pool_type)
            (
                pity_5, pity_4, gold_records, purple_records,
                failed_featured_5star, successful_featured_5star,
                pulls_since_last_5star, is_guaranteed, four_star_guaranteed,
            ) = stats

            # 软保底：从总保底的 74/90 比例位置开始概率递增
            five_star_rate_up_ratio = float(74 / 90)
            five_star_rate_up_pulls = int(five_star_rate_up_ratio * prob['pity'])

            # 判定五星
            is_5_star = (
                pity_5 >= prob['pity'] - 1
                or (
                    pity_5 < five_star_rate_up_pulls
                    and random.random() < prob['base_5']
                )
                or (
                    pity_5 >= five_star_rate_up_pulls
                    and random.random() < prob['base_5'] + (pity_5 * prob['base_5'])
                )
            )

            if is_5_star:
                result = self._pull_5_star(pool_type)
                gold_records.append(pity_5 + 1)
                pulls_for_this_5star = pulls_since_last_5star + 1

                # 弹窗提示
                self._show_5star_popup(
                    result, pulls_for_this_5star, pool_type,
                    is_guaranteed, prob['big_pity_enabled'],
                )

                if pool_type != 'standard':
                    if result['is_up']:
                        if not is_guaranteed:
                            successful_featured_5star += 1
                    else:
                        failed_featured_5star += 1

                if prob['big_pity_enabled']:
                    self.update_pool_stats(
                        pool_type,
                        pity_5=0, pity_4=0, pulls_since_last_5star=0,
                        is_guaranteed=not result['is_up'],
                        failed_featured_5star=failed_featured_5star,
                        successful_featured_5star=successful_featured_5star,
                    )
                else:
                    self.update_pool_stats(
                        pool_type,
                        pity_5=0, pity_4=0, pulls_since_last_5star=0,
                        failed_featured_5star=failed_featured_5star,
                        successful_featured_5star=successful_featured_5star,
                    )

            # 判定四星
            elif pity_4 >= prob['pity_4'] - 1 or random.random() < prob['base_4']:
                result = self._pull_4_star(pool_type)
                purple_records.append(pity_4 + 1)
                if prob['big_pity_4_enabled']:
                    self.update_pool_stats(
                        pool_type,
                        pity_5=pity_5 + 1, pity_4=0,
                        four_star_guaranteed=not result['is_up'],
                        pulls_since_last_5star=pulls_since_last_5star + 1,
                    )
                else:
                    self.update_pool_stats(
                        pool_type,
                        pity_5=pity_5 + 1, pity_4=0,
                        pulls_since_last_5star=pulls_since_last_5star + 1,
                    )
            else:
                result = self._pull_3_star()
                self.update_pool_stats(
                    pool_type,
                    pity_5=pity_5 + 1, pity_4=pity_4 + 1,
                    pulls_since_last_5star=pulls_since_last_5star + 1,
                )

            pulls.append((result['rarity'], result['type'], result['item']))
            self.pull_history.append({
                'rarity': result['rarity'],
                'item_type': result['type'],
                'item': result['item'],
            })

        return pulls

    def _get_pool_prob_params(self, pool_type):
        """获取当前池的概率参数"""
        if pool_type == 'weapon':
            return {
                'pity': self.current_prob['weapon_five_star_pity'],
                'base_5': self.current_prob['weapon_five_star_base'],
                'base_4': self.current_prob['weapon_four_star_base'],
                'pity_4': self.current_prob['weapon_four_star_pity'],
                'big_pity_enabled': self.current_prob['weapon_five_star_big_pity_enabled'],
                'big_pity_4_enabled': self.current_prob['weapon_four_star_big_pity_enabled'],
            }
        elif pool_type == 'character':
            return {
                'pity': self.current_prob['character_five_star_pity'],
                'base_5': self.current_prob['character_five_star_base'],
                'base_4': self.current_prob['character_four_star_base'],
                'pity_4': self.current_prob['character_four_star_pity'],
                'big_pity_enabled': self.current_prob['character_five_star_big_pity_enabled'],
                'big_pity_4_enabled': self.current_prob['character_four_star_big_pity_enabled'],
            }
        else:
            return {
                'pity': self.current_prob['standard_five_star_pity'],
                'base_5': self.current_prob['standard_five_star_base'],
                'base_4': self.current_prob['standard_four_star_base'],
                'pity_4': self.current_prob['standard_four_star_pity'],
                'big_pity_enabled': False,
                'big_pity_4_enabled': False,
            }

    def _show_5star_popup(self, result, pulls_count, pool_type, is_guaranteed, big_pity_enabled):
        """显示五星出货弹窗"""
        rarity_text = '五星'
        if result['is_up']:
            if is_guaranteed:
                messagebox.showinfo(
                    "出货了!",
                    f"恭喜，你用了{pulls_count}抽获得了{rarity_text}{result['type']}{result['item']}\n这是大保底!",
                )
            else:
                messagebox.showinfo(
                    "出货了!",
                    f"你用了{pulls_count}抽获得了{rarity_text}{result['type']}{result['item']}\n是小保底，恭喜没歪!",
                )
        else:
            if pool_type != 'standard':
                if big_pity_enabled:
                    messagebox.showinfo(
                        "出货了!",
                        f"你用了{pulls_count}抽获得了{rarity_text}{result['type']}{result['item']}\n可惜歪了，下次将是大保底!",
                    )
                else:
                    messagebox.showinfo(
                        "出货了!",
                        f"你用了{pulls_count}抽获得了{rarity_text}{result['type']}{result['item']}\n可惜歪了，下次...下次还是小保底啦哈哈哈！\n如果想启用大保底机制记得去改一下抽卡概率",
                    )
            else:
                messagebox.showinfo(
                    "出货了!",
                    f"恭喜，你用了{pulls_count}抽获得了{rarity_text}{result['type']}{result['item']}!",
                )

    def _pull_5_star(self, pool_type):
        if pool_type == 'weapon':
            success_prob = self.current_prob['weapon_five_star_success_prob']
            small_pity = self.current_prob['weapon_five_star_small_pity_mechanism']
            big_pity_enabled = self.current_prob['weapon_five_star_big_pity_enabled']
        elif pool_type == 'character':
            success_prob = self.current_prob['character_five_star_success_prob']
            small_pity = self.current_prob['character_five_star_small_pity_mechanism']
            big_pity_enabled = self.current_prob['character_five_star_big_pity_enabled']
        else:  # 常驻池
            success_prob = 0
            small_pity = 'random'

        is_up = self.is_guaranteed or (
            (small_pity == 'random' and random.random() < success_prob)
            or (small_pity == 'must_not_waste')
        )

        if pool_type == 'character':
            if is_up:
                item = random.choice(
                    self.pools['banners'][self.current_banner]['character_up_5_star']
                )
                self.is_guaranteed = False
            else:
                item = random.choice(self.pools['common_pools']['character_5_star'])
                self.is_guaranteed = True if big_pity_enabled else False
            return {
                'rarity': '5_star',
                'type': CHARACTER_DISPLAY_NAME,
                'item': item,
                'is_up': is_up,
            }

        elif pool_type == 'weapon':
            if is_up:
                item = random.choice(
                    self.pools['banners'][self.current_banner]['weapon_up_5_star']
                )
                self.is_guaranteed = False
            else:
                item = random.choice(self.pools['common_pools']['weapon_5_star'])
                self.is_guaranteed = True if big_pity_enabled else False
            return {
                'rarity': '5_star',
                'type': WEAPON_DISPLAY_NAME,
                'item': item,
                'is_up': is_up,
            }

        else:  # 常驻池：50% 角色 / 50% 光锥
            if random.random() < 0.5:
                item = random.choice(self.pools['common_pools']['character_5_star'])
                return {
                    'rarity': '5_star',
                    'type': CHARACTER_DISPLAY_NAME,
                    'item': item,
                    'is_up': False,
                }
            else:
                item = random.choice(self.pools['common_pools']['weapon_5_star'])
                return {
                    'rarity': '5_star',
                    'type': WEAPON_DISPLAY_NAME,
                    'item': item,
                    'is_up': False,
                }

    def _pull_4_star(self, pool_type):
        if pool_type == 'weapon':
            success_prob = self.current_prob['weapon_four_star_success_prob']
            small_pity = self.current_prob['weapon_four_star_small_pity_mechanism']
            big_pity_enabled = self.current_prob['weapon_four_star_big_pity_enabled']
        elif pool_type == 'character':
            success_prob = self.current_prob['character_four_star_success_prob']
            small_pity = self.current_prob['character_four_star_small_pity_mechanism']
            big_pity_enabled = self.current_prob['character_four_star_big_pity_enabled']
        else:  # 常驻池
            success_prob = 0
            big_pity_enabled = True
            small_pity = 'random'

        is_up = self.four_star_guaranteed or (
            (small_pity == 'random' and random.random() < success_prob)
            or (small_pity == 'must_not_waste')
        )

        if is_up and pool_type != 'standard':
            if pool_type == 'character':
                item = random.choice(
                    self.pools['banners'][self.current_banner].get(
                        'character_up_4_star', []
                    )
                )
                self.four_star_guaranteed = False
                return {
                    'rarity': '4_star',
                    'type': CHARACTER_DISPLAY_NAME,
                    'item': item,
                    'is_up': True,
                }
            else:  # weapon pool
                item = random.choice(
                    self.pools['banners'][self.current_banner].get(
                        'weapon_up_4_star', []
                    )
                )
                self.four_star_guaranteed = False
                return {
                    'rarity': '4_star',
                    'type': WEAPON_DISPLAY_NAME,
                    'item': item,
                    'is_up': True,
                }
        else:
            # 非 UP：50% 角色 / 50% 光锥
            four_star_item_pool = (
                self.pools['common_pools']['character_4_star']
                if random.random() < 0.5
                else self.pools['common_pools']['weapon_4_star']
            )
            up_items = self.pools['banners'][self.current_banner].get(
                f'{pool_type}_up_4_star', []
            )
            non_up_items = [
                item for item in four_star_item_pool if item not in up_items
            ]
            item = random.choice(non_up_items)

            self.four_star_guaranteed = True if big_pity_enabled else False

            if item in self.pools['common_pools']['character_4_star']:
                item_type = CHARACTER_DISPLAY_NAME
            elif item in self.pools['common_pools']['weapon_4_star']:
                item_type = WEAPON_DISPLAY_NAME
            else:
                item_type = '未知'

            return {
                'rarity': '4_star',
                'type': item_type,
                'item': item,
                'is_up': False,
            }

    def _pull_3_star(self):
        item = random.choice(self.pools['common_pools']['weapon_3_star'])
        return {
            'rarity': '3_star',
            'type': WEAPON_DISPLAY_NAME,
            'item': item,
            'is_up': False,
        }

    # ── 统计数据管理 ──────────────────────────────────────

    def get_pool_stats(self, pool_type):
        if pool_type == 'character':
            return (
                self.character_pity_5, self.character_pity_4,
                self.character_gold_records, self.character_purple_records,
                self.character_failed_featured_5star,
                self.character_successful_featured_5star,
                self.character_pulls_since_last_5star,
                self.character_is_guaranteed,
                self.character_four_star_guaranteed,
            )
        elif pool_type == 'weapon':
            return (
                self.weapon_pity_5, self.weapon_pity_4,
                self.weapon_gold_records, self.weapon_purple_records,
                self.weapon_failed_featured_5star,
                self.weapon_successful_featured_5star,
                self.weapon_pulls_since_last_5star,
                self.weapon_is_guaranteed,
                self.weapon_four_star_guaranteed,
            )
        else:
            return (
                self.pity_5, self.pity_4,
                self.gold_records, self.purple_records,
                self.failed_featured_5star, self.successful_featured_5star,
                self.pulls_since_last_5star, self.is_guaranteed,
                self.four_star_guaranteed,
            )

    def update_pool_stats(self, pool_type, **kwargs):
        prefix = ''
        if pool_type == 'character':
            prefix = 'character_'
        elif pool_type == 'weapon':
            prefix = 'weapon_'
        for key, value in kwargs.items():
            setattr(self, f"{prefix}{key}", value)

    def calculate_luck(self, pool_type):
        if pool_type == 'character':
            gold_records = self.character_gold_records
            failed_featured = self.character_failed_featured_5star
            total_featured = (
                self.character_failed_featured_5star
                + self.character_successful_featured_5star
            )
            five_star_pity = self.current_prob['character_five_star_pity']
        elif pool_type == 'weapon':
            gold_records = self.weapon_gold_records
            failed_featured = self.weapon_failed_featured_5star
            total_featured = (
                self.weapon_failed_featured_5star
                + self.weapon_successful_featured_5star
            )
            five_star_pity = self.current_prob['weapon_five_star_pity']
        else:
            gold_records = self.gold_records
            failed_featured = 0
            total_featured = 0
            five_star_pity = self.current_prob['standard_five_star_pity']

        if not gold_records:
            return "暂无数据"

        min_pulls = min(gold_records)
        max_pulls = max(gold_records)
        avg_pulls = sum(gold_records) / len(gold_records)
        luck_score = 0

        # 最少抽数评分
        thresholds_min = [
            (int(five_star_pity * (15 / 90)), 5),
            (int(five_star_pity * (25 / 90)), 4),
            (int(five_star_pity * (35 / 90)), 3),
            (int(five_star_pity * (45 / 90)), 2),
        ]
        for threshold, score in thresholds_min:
            if min_pulls <= threshold:
                luck_score += score
                break
        else:
            luck_score += 1

        # 最多抽数评分
        thresholds_max = [
            (int(five_star_pity * (55 / 90)), 3),
            (int(five_star_pity * (65 / 90)), 2),
            (int(five_star_pity * (80 / 90)), 1),
        ]
        for threshold, score in thresholds_max:
            if max_pulls <= threshold:
                luck_score += score
                break
        # else: luck_score += 0

        # 平均抽数评分
        thresholds_avg = [
            (int(five_star_pity * (30 / 90)), 5),
            (int(five_star_pity * (40 / 90)), 4),
            (int(five_star_pity * (50 / 90)), 3),
            (int(five_star_pity * (60 / 90)), 2),
            (int(five_star_pity * (70 / 90)), 1),
        ]
        for threshold, score in thresholds_avg:
            if avg_pulls <= threshold:
                luck_score += score
                break
        # else: luck_score += 0

        # UP 歪卡率评分（仅限 UP 池）
        if pool_type != 'standard' and total_featured > 0:
            fail_rate = failed_featured / total_featured
            thresholds_fail = [
                (0, 5), (0.1, 4), (0.25, 3), (0.4, 2), (0.75, 1),
            ]
            for threshold, score in thresholds_fail:
                if fail_rate <= threshold:
                    luck_score += score
                    break
            # else: luck_score += 0

        # 运势评级
        ratings = [
            (20, "极佳"), (18, "大吉"), (15, "上吉"), (12, "中吉"),
            (9, "小吉"), (6, "平"), (3, "小凶"), (1, "中凶"),
        ]
        for threshold, rating in ratings:
            if luck_score >= threshold:
                return rating
        return "大凶"

    def reset_statistics(self):
        """重置所有卡池统计数据"""
        fields = [
            'character_pity_5', 'character_pity_4',
            'weapon_pity_5', 'weapon_pity_4',
            'character_gold_records', 'character_purple_records',
            'weapon_gold_records', 'weapon_purple_records',
            'character_failed_featured_5star', 'character_successful_featured_5star',
            'weapon_failed_featured_5star', 'weapon_successful_featured_5star',
            'character_pulls_since_last_5star', 'weapon_pulls_since_last_5star',
            'character_is_guaranteed', 'weapon_is_guaranteed',
            'pity_5', 'pity_4',
            'gold_records', 'purple_records',
            'pulls_since_last_5star', 'is_guaranteed',
            'failed_featured_5star', 'successful_featured_5star',
            'character_pulls', 'weapon_pulls', 'standard_pulls',
            'four_star_guaranteed',
            'character_four_star_guaranteed', 'weapon_four_star_guaranteed',
        ]
        for field in fields:
            if field.endswith('_records') or field.endswith('_pulls'):
                setattr(self, field, [])
            elif field.endswith('_guaranteed'):
                setattr(self, field, False)
            else:
                setattr(self, field, 0)
        self.total_pulls = 0
        self.banner_pulls = {}
        self.pull_history = []
        self.save_state()

    # ── 状态持久化 ────────────────────────────────────────

    def save_state(self):
        try:
            state = {
                'current_banner': self.current_banner,
                'total_pulls': self.total_pulls,
                'banner_pulls': self.banner_pulls,
                'pull_history': self.pull_history,
                # 角色池
                'character_pity_5': self.character_pity_5,
                'character_pity_4': self.character_pity_4,
                'character_gold_records': self.character_gold_records,
                'character_purple_records': self.character_purple_records,
                'character_failed_featured_5star': self.character_failed_featured_5star,
                'character_successful_featured_5star': self.character_successful_featured_5star,
                'character_pulls_since_last_5star': self.character_pulls_since_last_5star,
                'character_is_guaranteed': self.character_is_guaranteed,
                'character_pulls': self.character_pulls,
                # 光锥池
                'weapon_pity_5': self.weapon_pity_5,
                'weapon_pity_4': self.weapon_pity_4,
                'weapon_gold_records': self.weapon_gold_records,
                'weapon_purple_records': self.weapon_purple_records,
                'weapon_failed_featured_5star': self.weapon_failed_featured_5star,
                'weapon_successful_featured_5star': self.weapon_successful_featured_5star,
                'weapon_pulls_since_last_5star': self.weapon_pulls_since_last_5star,
                'weapon_is_guaranteed': self.weapon_is_guaranteed,
                'weapon_pulls': self.weapon_pulls,
                # 常驻池
                'standard_pity_5': self.pity_5,
                'standard_pity_4': self.pity_4,
                'standard_gold_records': self.gold_records,
                'standard_purple_records': self.purple_records,
                'standard_pulls_since_last_5star': self.pulls_since_last_5star,
                'standard_pulls': self.standard_pulls,
                # 四星保底
                'character_four_star_guaranteed': self.character_four_star_guaranteed,
                'weapon_four_star_guaranteed': self.weapon_four_star_guaranteed,
            }

            yaml.default_flow_style = False
            yaml.width = 4096
            yaml.indent(mapping=2, sequence=4, offset=2)

            yaml_str = "# 抽卡模拟器数据文件\n"
            yaml_str += "# 请勿手动修改，除非你知道自己在做什么\n"

            string_stream = StringIO()
            yaml.dump(state, string_stream)
            data_str = string_stream.getvalue()

            # 添加注释
            comment_map = {
                'current_banner:': '# 当前选择的卡池\ncurrent_banner:',
                'total_pulls:': '# 总抽卡次数\ntotal_pulls:',
                'banner_pulls:': '# 每个卡池的抽卡次数\nbanner_pulls:',
                'pull_history:': '# 抽卡历史记录\npull_history:',
                'character_pity_5:': '# 角色池5星保底计数\ncharacter_pity_5:',
                'character_pity_4:': '# 角色池4星保底计数\ncharacter_pity_4:',
                'character_gold_records:': '# 角色池5星记录\ncharacter_gold_records:',
                'character_purple_records:': '# 角色池4星记录\ncharacter_purple_records:',
                'character_failed_featured_5star:': '# 角色池歪掉的5星次数\ncharacter_failed_featured_5star:',
                'character_successful_featured_5star:': '# 角色池抽中UP的5星次数\ncharacter_successful_featured_5star:',
                'character_pulls_since_last_5star:': '# 角色池距离上次5星的抽数\ncharacter_pulls_since_last_5star:',
                'character_is_guaranteed:': '# 角色池是否大保底\ncharacter_is_guaranteed:',
                'weapon_pity_5:': '# 光锥池5星保底计数\nweapon_pity_5:',
                'weapon_pity_4:': '# 光锥池4星保底计数\nweapon_pity_4:',
                'weapon_gold_records:': '# 光锥池5星记录\nweapon_gold_records:',
                'weapon_purple_records:': '# 光锥池4星记录\nweapon_purple_records:',
                'weapon_failed_featured_5star:': '# 光锥池歪掉的5星次数\nweapon_failed_featured_5star:',
                'weapon_successful_featured_5star:': '# 光锥池抽中UP的5星次数\nweapon_successful_featured_5star:',
                'weapon_pulls_since_last_5star:': '# 光锥池距离上次5星的抽数\nweapon_pulls_since_last_5star:',
                'weapon_is_guaranteed:': '# 光锥池是否大保底\nweapon_is_guaranteed:',
                'standard_pity_5:': '# 常驻池5星保底计数\nstandard_pity_5:',
                'standard_pity_4:': '# 常驻池4星保底计数\nstandard_pity_4:',
                'standard_gold_records:': '# 常驻池5星记录\nstandard_gold_records:',
                'standard_purple_records:': '# 常驻池4星记录\nstandard_purple_records:',
                'standard_pulls_since_last_5star:': '# 常驻池距离上次5星的抽数\nstandard_pulls_since_last_5star:',
            }
            for old, new in comment_map.items():
                data_str = data_str.replace(old, new)

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

                # 角色池
                self.character_pity_5 = state.get('character_pity_5', 0)
                self.character_pity_4 = state.get('character_pity_4', 0)
                self.character_gold_records = state.get('character_gold_records', [])
                self.character_purple_records = state.get('character_purple_records', [])
                self.character_failed_featured_5star = state.get(
                    'character_failed_featured_5star', 0
                )
                self.character_successful_featured_5star = state.get(
                    'character_successful_featured_5star', 0
                )
                self.character_pulls_since_last_5star = state.get(
                    'character_pulls_since_last_5star', 0
                )
                self.character_is_guaranteed = state.get(
                    'character_is_guaranteed', False
                )
                self.character_pulls = state.get('character_pulls', 0)

                # 光锥池
                self.weapon_pity_5 = state.get('weapon_pity_5', 0)
                self.weapon_pity_4 = state.get('weapon_pity_4', 0)
                self.weapon_gold_records = state.get('weapon_gold_records', [])
                self.weapon_purple_records = state.get('weapon_purple_records', [])
                self.weapon_failed_featured_5star = state.get(
                    'weapon_failed_featured_5star', 0
                )
                self.weapon_successful_featured_5star = state.get(
                    'weapon_successful_featured_5star', 0
                )
                self.weapon_pulls_since_last_5star = state.get(
                    'weapon_pulls_since_last_5star', 0
                )
                self.weapon_is_guaranteed = state.get('weapon_is_guaranteed', False)
                self.weapon_pulls = state.get('weapon_pulls', 0)

                # 常驻池
                self.pity_5 = state.get('standard_pity_5', 0)
                self.pity_4 = state.get('standard_pity_4', 0)
                self.gold_records = state.get('standard_gold_records', [])
                self.purple_records = state.get('standard_purple_records', [])
                self.pulls_since_last_5star = state.get(
                    'standard_pulls_since_last_5star', 0
                )
                self.standard_pulls = state.get('standard_pulls', 0)

                self.character_four_star_guaranteed = state.get(
                    'character_four_star_guaranteed', False
                )
                self.weapon_four_star_guaranteed = state.get(
                    'weapon_four_star_guaranteed', False
                )

                # 处理 pull_history 中的 item_type（兼容旧数据）
                for pull in self.pull_history:
                    if pull['item_type'] == 'character':
                        pull['item_type'] = CHARACTER_DISPLAY_NAME
                    elif pull['item_type'] == 'weapon':
                        pull['item_type'] = WEAPON_DISPLAY_NAME
        except FileNotFoundError:
            self.show_message("未找到保存的数据，使用默认值初始化。", YELLOW)
        except Exception as e:
            self.show_message(f"加载数据时出错: {e}", RED)

    # ── 初始化 ────────────────────────────────────────────

    def inits(self):
        """初始化所有统计变量"""
        self.current_banner = None
        self.total_pulls = 0
        self.banner_pulls = {}
        self.pull_history = []

        # 角色池
        self.character_pity_5 = 0
        self.character_pity_4 = 0
        self.character_gold_records = []
        self.character_purple_records = []
        self.character_failed_featured_5star = 0
        self.character_successful_featured_5star = 0
        self.character_pulls_since_last_5star = 0
        self.character_is_guaranteed = False
        self.character_pulls = 0
        self.character_four_star_guaranteed = False

        # 光锥池
        self.weapon_pity_5 = 0
        self.weapon_pity_4 = 0
        self.weapon_gold_records = []
        self.weapon_purple_records = []
        self.weapon_failed_featured_5star = 0
        self.weapon_successful_featured_5star = 0
        self.weapon_pulls_since_last_5star = 0
        self.weapon_is_guaranteed = False
        self.weapon_pulls = 0
        self.weapon_four_star_guaranteed = False

        # 常驻池
        self.pity_5 = 0
        self.pity_4 = 0
        self.gold_records = []
        self.purple_records = []
        self.pulls_since_last_5star = 0
        self.is_guaranteed = False
        self.failed_featured_5star = 0
        self.successful_featured_5star = 0
        self.standard_pulls = 0
        self.four_star_guaranteed = False

        self.TIPS = TIPS
        self.load_state()

    # ── 工具方法 ──────────────────────────────────────────

    def show_message(self, message, color=RESET):
        if color == RED:
            messagebox.showerror("错误", message)
        elif color == GREEN:
            messagebox.showinfo("成功", message)
        elif color == YELLOW:
            messagebox.showwarning("警告", message)
        else:
            messagebox.showinfo("提示", message)
