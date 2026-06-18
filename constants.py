"""
SR-Gacha 常量定义模块
崩坏：星穹铁道抽卡模拟器
"""

# ── 颜色常量 ─────────────────────────────────────────────
PURPLE = '#BA55D3'
GOLD = '#FFD700'
GREEN = '#32CD32'
RED = '#FF4500'
RESET = '#FFFFFF'
CYAN = '#00CED1'
YELLOW = '#FFFF00'
BLUE = '#1E90FF'

# ── 显示名称 ─────────────────────────────────────────────
CHARACTER_DISPLAY_NAME = '角色'
WEAPON_DISPLAY_NAME = '光锥'

# ── 文件路径与 URL ──────────────────────────────────────
BANNER_FILE = 'banners.yml'
GITHUB_PROXY = ''
BANNER_DOWNLOAD_URL = "https://raw.gh.qiusyan.top/qiusyan-projects/SR-Gacha/main/banners.yml"

# ── 版本信息 ─────────────────────────────────────────────
VERSION = "2.2.11"
AUTHOR = "QiuSYan & Claude"
GITHUB_REPO = "qiusyan-projects/SR-Gacha"

# ── 小贴士 ───────────────────────────────────────────────
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
    "可以通过修改抽卡概率来达成任意抽卡效果",
]

# ── 默认概率设置 ─────────────────────────────────────────
DEFAULT_PROBABILITIES = {
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
    'weapon_four_star_small_pity_mechanism': 'random',
}
