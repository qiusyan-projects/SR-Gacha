import random
import json
import argparse
from collections import Counter
import os
import pickle
import signal
import sys
import requests
import yaml

os.system("title 抽卡模拟器")

# 颜色定义
PURPLE = '\033[95m'
GOLD = '\033[93m'
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
CYAN = '\033[36m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
# 变量
BANNER_FILE = 'banners.json'
GITHUB_PROXY = 'https://mirror.ghproxy.com'
BANNER_DOWNLOAD_URL = "https://raw.githubusercontent.com/qiusyan-projects/SR-Gacha/main/banners.json"


class GachaSystem:
    def __init__(self, pool_file):
        self.pool_file = pool_file
        self.ensure_pool_file_exists()
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
        self.load_state()

    def load_pools(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            self.pools = json.load(f)
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
                'pulls_since_last_5star': self.pulls_since_last_5star
            }
            
            # 创建包含注释的YAML字符串
            yaml_str = "# 抽卡模拟器数据文件\n"
            yaml_str += "# 请勿手动修改，除非你知道自己在做什么\n\n"
            
            yaml_str += yaml.dump(state, allow_unicode=True, sort_keys=False)
            
            # 为每个键添加注释
            yaml_str = yaml_str.replace('current_banner:', '# 当前选择的卡池\ncurrent_banner:')
            yaml_str = yaml_str.replace('pity_5:', '# 距离保底5星的抽数\npity_5:')
            yaml_str = yaml_str.replace('pity_4:', '# 距离保底4星的抽数\npity_4:')
            yaml_str = yaml_str.replace('failed_featured_pulls:', '# 未抽中UP角色/光锥的次数\nfailed_featured_pulls:')
            yaml_str = yaml_str.replace('total_pulls:', '# 总抽卡次数\ntotal_pulls:')
            yaml_str = yaml_str.replace('banner_pulls:', '# 每个卡池的抽卡次数\nbanner_pulls:')
            yaml_str = yaml_str.replace('gold_records:', '# 获得5星的抽数记录\ngold_records:')
            yaml_str = yaml_str.replace('purple_records:', '# 获得4星的抽数记录\npurple_records:')
            yaml_str = yaml_str.replace('failed_featured_5star:', '# 歪掉的5星次数\nfailed_featured_5star:')
            yaml_str = yaml_str.replace('successful_featured_5star:', '# 抽中UP的5星次数\nsuccessful_featured_5star:')
            yaml_str = yaml_str.replace('pulls_since_last_5star:', '# 距离上次5星的抽数\npulls_since_last_5star:')
            
            with open('gacha_data.yaml', 'w', encoding='utf-8') as f:
                f.write(yaml_str)
            print("数据已保存到 'gacha_data.yaml'")
        except Exception as e:
            print(f"无法保存数据: {e}")

    def load_state(self):
        try:
            with open('gacha_data.yaml', 'r', encoding='utf-8') as f:
                state = yaml.safe_load(f)
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
            print("数据已从 'gacha_data.yaml' 加载.")
        except FileNotFoundError:
            print("没有找到 'gacha_data.yaml' 文件，使用初始数据.")
        except Exception as e:
            print(f"无法加载数据: {e}")

    def ensure_pool_file_exists(self):
        if not os.path.exists(self.pool_file):
            print(f"错误: '{self.pool_file}' 文件不存在。")
            download = input("是否从GitHub下载最新的banners.json? (y/n): ").lower().strip()
            if download == 'y':
                try:
                    proxy_url = f"{GITHUB_PROXY}/{BANNER_DOWNLOAD_URL}"
                    response = requests.get(proxy_url)
                    response.raise_for_status()
                    with open(self.pool_file, 'wb') as f:
                        f.write(response.content)
                    print(f"{GREEN}成功下载 '{self.pool_file}'！{RESET}")
                except requests.RequestException as e:
                    print(f"{RED}下载失败: {e}{RESET}")
                    sys.exit(1)
            else:
                print("你选择了不从Github下载数据文件，请手动将banners.json文件放置于程序目录")
                sys.exit(1)

    def set_banner(self, banner_name):
        if banner_name in self.pools['banners']:
            self.current_banner = banner_name
            if banner_name not in self.banner_pulls:
                self.banner_pulls[banner_name] = 0
            print(f"切换到卡池: {self.pools['banners'][banner_name]['name']}")
            self.save_state()
        else:
            print(f"错误: 卡池 '{banner_name}' 不存在")

    def show_banners(self):
        print("\n可用卡池列表:")
        
        character_banners = []
        weapon_banners = []
        
        for banner_name, banner in self.pools['banners'].items():
            if banner_name == 'standard':
                continue  # 跳过常驻卡池
            
            pool_type = banner.get('pool_type', 'character')
            name = banner['name']
            
            if pool_type == 'character':
                up_5_star = banner.get('character_up_5_star', [''])[0]
                character_banners.append((name, banner_name, up_5_star))
            elif pool_type == 'weapon':
                up_5_star = banner.get('weapon_up_5_star', [''])[0]
                weapon_banners.append((name, banner_name, up_5_star))
        
        max_name_length = max(len(banner[0]) for banner in character_banners + weapon_banners)
        max_id_length = max(len(banner[1]) for banner in character_banners + weapon_banners)
        max_up_length = max(len(banner[2]) for banner in character_banners + weapon_banners)
        
        col_width = max_name_length + max_id_length + max_up_length + 15
        
        print(f"{'角色卡池':<{col_width}}  {'光锥卡池':<{col_width}}")
        print("-" * col_width + "  " + "-" * col_width)
        
        for i in range(max(len(character_banners), len(weapon_banners))):
            char_banner = character_banners[i] if i < len(character_banners) else ("", "", "")
            weap_banner = weapon_banners[i] if i < len(weapon_banners) else ("", "", "")
            
            char_str = f"{char_banner[0]:<{max_name_length}} {GREEN}(ID: {char_banner[1]:<{max_id_length}}){RESET} {GOLD}{char_banner[2]:<{max_up_length}}{RESET}"
            weap_str = f"{weap_banner[0]:<{max_name_length}} {GREEN}(ID: {weap_banner[1]:<{max_id_length}}){RESET} {GOLD}{weap_banner[2]:<{max_up_length}}{RESET}"
            
            print(f"{char_str:<{col_width}}  {weap_str:<{col_width}}")
        
        print(f"\n{CYAN}常驻卡池:{RESET} 群星跃迁 {GREEN}(ID: standard){RESET}")
        print(f"\n使用 set <卡池ID> 来切换卡池{RESET}")

    def do_pull(self, times):
        if not self.current_banner:
            print("错误: 未选择卡池")
            return

        print(f"开始抽卡，当前卡池: {CYAN}{self.pools['banners'][self.current_banner]['name']}{RESET}")

        results = []
        summary = Counter()
        guaranteed_4_star = False
        five_star_results = []  # 用于存储本次抽卡中的五星结果

        for i in range(times):
            self.total_pulls += 1
            self.banner_pulls[self.current_banner] += 1
            self.pulls_since_last_5star += 1

            pool_type = "character" if "character_up_5_star" in self.pools['banners'][self.current_banner] else "weapon"

            # 确定是否出五星
            if self.pity_5 >= 89 or random.randint(1, 10000) <= 60 + min(self.pity_5 * 600 // 73, 7300):
                result = self.pull_5_star(pool_type)
                self.gold_records.append(self.pity_5 + 1)  # 记录出金抽数
                self.pity_5 = 0
                self.pity_4 = 0  # 重置4星保底
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
                summary['4星'] += 1
                if self.current_banner != 'standard' and result['is_up']:
                    summary['4星UP'] += 1
                guaranteed_4_star = True
            else:
                result = self.pull_3_star()
                self.pity_5 += 1
                self.pity_4 += 1
                summary['3星'] += 1
            
            if result['rarity'] == '5星':
                five_star_results.append((self.pulls_since_last_5star, result['name'], result['is_up']))
                self.pulls_since_last_5star = 0

            results.append(result)

        self.print_results(results)
        self.print_summary(summary)

        for pulls, name, is_up in five_star_results:
            if self.current_banner != 'standard':
                if is_up:
                    print(f"{GREEN}恭喜，你花费了{pulls}抽获得了五星角色/光锥{name}！恭喜没歪！{RESET}")
                else:
                    print(f"{RED}恭喜，你花费了{pulls}抽获得了五星角色/光锥{name}！可惜歪了！{RESET}")
            else:
                print(f"{GOLD}恭喜，你花费了{pulls}抽获得了五星角色/光锥{name}！{RESET}")

        print(f"结束抽卡，当前卡池: {CYAN}{self.pools['banners'][self.current_banner]['name']}{RESET}")
        self.print_pity_info()
        self.save_state()

    def pull_3_star(self):
        common_items = self.pools['common_pools']['weapon_3_star']
        result = random.choice(common_items)
        return {"name": result, "is_up": False, "rarity": "3星"}

    def pull_4_star(self, pool_type):
        banner = self.pools['banners'][self.current_banner]
        if self.current_banner == 'standard':
            all_4_star = (self.pools['common_pools']['character_4_star'] + 
                        self.pools['common_pools']['weapon_4_star'])
            result = random.choice(all_4_star)
            return {"name": result, "is_up": False, "rarity": "4星"}
        else:
            up_key = f"{pool_type}_up_4_star"
            common_key = f"{pool_type}_4_star"
            
            if pool_type == "weapon" and up_key not in banner:
                up_key = "weapon_up_4_star"
                common_key = "weapon_4_star"
            
            all_items = self.pools['common_pools'].get('character_4_star', []) + self.pools['common_pools'].get('weapon_4_star', [])
            up_names = banner.get(up_key, [])

            if up_names and random.randint(1, 100) <= 50:
                result = random.choice(up_names)
                return {"name": result, "is_up": True, "rarity": "4星"}
            else:
                result = random.choice(all_items)
                return {"name": result, "is_up": False, "rarity": "4星"}


    def pull_5_star(self, pool_type):
        banner = self.pools['banners'][self.current_banner]
        if self.current_banner == 'standard':
            all_5_star = (self.pools['common_pools']['character_5_star'] + 
                        self.pools['common_pools']['weapon_5_star'])
            result = random.choice(all_5_star)
            return {"name": result, "is_up": False, "rarity": "5星"}
        else:
            up_key = f"{pool_type}_up_5_star"
            common_key = f"{pool_type}_5_star"
            
            if pool_type == "weapon" and up_key not in banner:
                up_key = "weapon_up_5_star"
                common_key = "weapon_5_star"
            
            up_items = banner.get(up_key, [])
            if pool_type == "character":
                common_items = self.pools['common_pools'].get('character_5_star', [])
            else:
                common_items = self.pools['common_pools'].get('weapon_5_star', [])

            if random.randint(1, 100) <= 50 or self.failed_featured_pulls >= 1:
                if up_items:
                    self.failed_featured_pulls = 0
                    result = random.choice(up_items)
                    return {"name": result, "is_up": True, "rarity": "5星"}

            self.failed_featured_pulls += 1
            result = random.choice(common_items)
            return {"name": result, "is_up": False, "rarity": "5星"}




    def print_results(self, results):
        print("\n抽卡结果:")
        half = len(results) // 2
        for i in range(max(half, len(results) - half)):
            left = self.format_result(results[i], i + 1) if i < len(results) else ""
            right = self.format_result(results[i + half], i + half + 1) if i + half < len(results) else ""
            print(f"{left:<50} {right}")

    def format_result(self, result, index):
        if not result:
            return ""
        name = result['name']
        is_up = result['is_up']
        rarity = result['rarity']
        
        if rarity == '5星':
            color = GOLD
        elif rarity == '4星':
            color = PURPLE
        else:
            color = RESET
        
        if rarity == '3星':
            result_text = f"{color}{name}{RESET}"
        else:
            if self.current_banner == 'standard':
                result_text = f"{color}{name}{RESET}"
            elif is_up:
                result_text = f"{color}{name} {GREEN}(UP){RESET}"
            else:
                result_text = f"{color}{name} {RED}(Non-UP){RESET}"
        
        return f"第{index:2d}抽: {result_text}"


    def print_summary(self, summary):
        print("\n抽卡总结:")
        if self.current_banner == 'standard':
            print(f"{GOLD}5星: {summary['5星']}{RESET}")
            print(f"{PURPLE}4星: {summary['4星']}{RESET}")
            print(f"3星: {summary['3星']}")
        else:
            print(f"{GOLD}5星: {summary['5星']} {GREEN}(UP: {summary['5星UP']}){RESET}")
            print(f"{PURPLE}4星: {summary['4星']} {GREEN}(UP: {summary['4星UP']}){RESET}")
            print(f"3星: {summary['3星']}")

    def print_pity_info(self):
        print(f"\n距离下一个5星保底还需: {90 - self.pity_5} 抽")
        print(f"距离下一个4星保底还需: {10 - self.pity_4} 抽")
        print(f"当前卡池总抽数: {self.banner_pulls[self.current_banner]}")
        print(f"总抽卡次数: {self.total_pulls}")


    def show_info(self):
        print(f"\n{GOLD}抽卡统计信息:{RESET}")
        print(f"总抽卡次数: {self.total_pulls}")
        print(f"5星角色/光锥数量: {GOLD}{len(self.gold_records)}{RESET}")
        print(f"4星角色/光锥数量: {PURPLE}{len(self.purple_records)}{RESET}")
        
        if self.gold_records:
            avg_gold_pulls = sum(self.gold_records) / len(self.gold_records)
            print(f"最少抽数出金: {GREEN}{min(self.gold_records)}{RESET}")
            print(f"最多抽数出金: {RED}{max(self.gold_records)}{RESET}")
            print(f"平均抽数出金: {CYAN}{avg_gold_pulls:.2f}{RESET}")
        
        total_featured_5star = self.successful_featured_5star + self.failed_featured_5star
        if total_featured_5star > 0:
            success_rate = self.successful_featured_5star / total_featured_5star * 100
            print(f"歪UP池总次数: {RED}{self.failed_featured_5star}{RESET}")
            print(f"小保底不歪概率: {CYAN}{success_rate:.2f}%{RESET}")
            
            # 新增：判断抽卡顺利程度
            luck_level = self.evaluate_luck(avg_gold_pulls, success_rate)
            print(f"\n{CYAN}抽卡顺利程度: {luck_level}{RESET}")
        
        if self.current_banner:
            print(f"\n{CYAN}当前卡池: {self.pools['banners'][self.current_banner]['name']}{RESET}")
            print(f"距离下一个5星保底还需: {90 - self.pity_5} 抽")
            print(f"距离下一个4星保底还需: {10 - self.pity_4} 抽")
        else:
            print("\n当前未选择卡池")
            print("请使用 'set <卡池ID>' 命令选择一个卡池")

    def evaluate_luck(self, avg_gold_pulls, success_rate):
        # 设定评判标准
        avg_pulls_threshold = 65  # 平均65抽以下为好
        success_rate_threshold = 70  # 70%以上不歪率为好

        # 计算得分
        pull_score = 2 if avg_gold_pulls <= avg_pulls_threshold else 0
        rate_score = 2 if success_rate >= success_rate_threshold else 0
        total_score = pull_score + rate_score

        # 根据得分判断运气等级
        if total_score == 4:
            return f"{RED}大吉{RESET}"
        elif total_score == 3:
            return f"{GOLD}中吉{RESET}"
        elif total_score == 2:
            return f"{YELLOW}小吉{RESET}"
        elif total_score == 1:
            return f"{GREEN}小凶{RESET}"
        elif total_score == 0:
            if avg_gold_pulls > 80 or success_rate < 30:
                return f"{PURPLE}大凶{RESET}"
            else:
                return f"{BLUE}中凶{RESET}"


    def show_version_info(self):
        version = "1.0.0"  
        author = "QiuSYan & Claude" 
        github = "qiusyan-projects/SR-Gacha"
        print(f"\n{GOLD}抽卡模拟器{RESET}")
        print(f"版本: {version}")
        print(f"作者: {author}")
        print(f"Github: {CYAN}{github}{RESET}")
        print("\n指令列表:")
        print("show - 查看所有可用卡池")
        print("set <卡池ID> - 选择卡池")
        print("banner - 查看当前选择的卡池")
        print("pull <次数> - 进行抽卡")
        print("info - 查看抽卡统计信息")
        print("version - 查看版本信息和指令列表")
        print("exit - 退出程序")

    def show_current_banner(self):
        if not self.current_banner:
            print("错误：当前未选择任何卡池")
            return

        banner = self.pools['banners'][self.current_banner]
        print(f"\n{GOLD}当前选择的卡池:{RESET}")
        print(f"\n{CYAN}名称: {banner['name']}{RESET}")
        print(f"{GREEN}ID: {self.current_banner}{RESET}")

        if self.current_banner == 'standard':
            print("类型: 常驻池")
        else:
            pool_type = banner.get('pool_type', 'character')
            print(f"类型: {'角色池' if pool_type == 'character' else '光锥池'}")

            if pool_type == 'character':
                if 'character_up_5_star' in banner:
                    print(f"\n{GOLD}UP 五星角色:{RESET}")
                    for char in banner['character_up_5_star']:
                        print(f"  - {GOLD}{char}{RESET}")
                
                if 'character_up_4_star' in banner:
                    print(f"\n{PURPLE}UP 四星角色:{RESET}")
                    for char in banner['character_up_4_star']:
                        print(f"  - {PURPLE}{char}{RESET}")

            if pool_type == 'weapon':
                if 'weapon_up_5_star' in banner:
                    print(f"\n{GOLD}UP 五星光锥:{RESET}")
                    for weapon in banner['weapon_up_5_star']:
                        print(f"  - {GOLD}{weapon}{RESET}")
                
                if 'weapon_up_4_star' in banner:
                    print(f"\n{PURPLE}UP 四星光锥:{RESET}")
                    for weapon in banner['weapon_up_4_star']:
                        print(f"  - {PURPLE}{weapon}{RESET}")

        print(f"\n当前卡池抽取次数: {self.banner_pulls.get(self.current_banner, 0)}")
        print(f"距离下一个5星保底还需: {90 - self.pity_5} 抽")
        print(f"距离下一个4星保底还需: {10 - self.pity_4} 抽")

    def reload_pools(self):
        print(f"正在重新加载 '{self.pool_file}'...")
        self.load_pools(self.pool_file)
        print("重新加载完成。")

def signal_handler(sig, frame):
    print("\n\n感谢使用抽卡模拟器！祝抽卡愉快！")
    exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="抽卡模拟器")
    args = parser.parse_args()

    print("欢迎使用抽卡模拟器！")
    print("可用命令：")
    print("show - 查看所有可用卡池")
    print("set <卡池ID> - 选择卡池")
    print("banner - 查看当前选择的卡池")
    print("pull <次数> - 进行抽卡")
    print("info - 查看抽卡统计信息")
    print("version - 查看版本信息和指令列表")
    print("reload - 重新加载卡池配置文件")
    print("exit - 退出程序")
    print()

    try:
        gacha = GachaSystem(BANNER_FILE)
    except SystemExit:
        input("按任意键退出...")
        return

    try:
        while True:
            command = input(f"{CYAN}请输入命令: {RESET}").strip().split()
            
            if not command:
                continue

            if command[0] in ["stop", "exit"]:
                break
            elif command[0] == "show":
                gacha.show_banners()
            elif command[0] == "set":
                if len(command) < 2:
                    print("错误：请指定卡池ID")
                else:
                    gacha.set_banner(command[1])
            elif command[0] == "banner":
                gacha.show_current_banner()
            elif command[0] == "pull":
                if len(command) < 2:
                    print("错误：请指定抽卡次数")
                elif not gacha.current_banner:
                    print("错误：请先使用 set 命令选择一个卡池")
                else:
                    try:
                        times = int(command[1])
                        gacha.do_pull(times)
                    except ValueError:
                        print("错误：抽卡次数必须是一个整数")
            elif command[0] == "info":
                gacha.show_info()
            elif command[0] in ["ver", "version"]:
                gacha.show_version_info()
            elif command[0] == "reload":
                gacha.reload_pools()
            else:
                print("未知命令。可用命令：show, set, banner, pull, info, version, exit")
    except KeyboardInterrupt:
        pass
    
    print("\n感谢使用抽卡模拟器！祝抽卡愉快！")
    print(f"\n跟程序同一目录的{CYAN}`gacha_data.yaml`{RESET}是数据文件，保存了你的抽卡记录，删不删由你")
    input("按任意键退出...")  

if __name__ == "__main__":
    main()