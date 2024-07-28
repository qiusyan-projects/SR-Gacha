<div align=center>

![SR-Gacha](https://socialify.git.ci/qiusyan-projects/SR-Gacha/image?description=1&font=Jost&forks=1&issues=1&language=1&logo=https%3A%2F%2Favatars.githubusercontent.com%2Fu%2F175322378%3Fv%3D4&name=1&owner=1&pattern=Circuit%20Board&pulls=1&stargazers=1&theme=Auto)

_✨ 星穹铁道抽卡模拟器，使用Python编写 ✨_

![Language](https://img.shields.io/badge/language-python-blue?style=flat-square)
![github license](https://img.shields.io/github/license/qiusyan-projects/SR-Gacha?style=flat-square)

![GitHub contributors](https://img.shields.io/github/contributors/qiusyan-projects/SR-Gacha?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/qiusyan-projects/SR-Gacha/shell?style=flat-square)
<!-- ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/qiusyan-projects/SR-Gacha/main.yml?style=for-the-badge) -->
![GitHub Release](https://img.shields.io/github/v/release/qiusyan-projects/SR-Gacha?filter=v1.1.1&style=flat-square)
![GitHub Repo stars](https://img.shields.io/github/stars/qiusyan-projects/SR-Gacha?style=flat-square)


</div>


*此 **命令行版本** 分支将不再维护，请使用 main 分支的 **GUI版本***


***

# Usage

## 一键启动

**如果你是 `Windows` 用户，那么可以使用我打包好的exe文件一键启动**

<!-- Actions:  [![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/qiusyan-projects/SR-Gacha/main.yml?style=for-the-badge)](https://nightly.link/qiusyan-projects/SR-Gacha/workflows/main/main/gacha.zip) **（推荐使用）** -->

Release:  [![GitHub Release](https://img.shields.io/github/v/release/qiusyan-projects/SR-Gacha?filter=v1.1.1&style=flat-square)](https://github.com/qiusyan-projects/SR-Gacha/releases/tag/v1.1.1)  

## 通过Python启动

适用于 `Windows/MacOS/Linux` 

1. 使用 `pip install -r requirements.txt` 安装依赖
    - （可选）从 **main分支** 中下载 `banners.yml` 并与脚本放置于同一文件夹
2. 使用 `python gacha.py` 运行脚本
3. Have Fun!

<!-- ## 当前卡池版本 (banners.yml)

`2.4` -->

## 其他

功能有

```
show - 查看所有可用卡池
set <卡池ID> - 选择卡池
banner - 查看当前选择的卡池
pull <次数> - 进行抽卡
info - 查看抽卡统计信息
history - 查看抽卡历史
version - 查看版本信息和指令列表
reload - 重新加载卡池配置文件
clear - 清除所有抽卡数据
tips - 查看Tips
update - 检查并更新卡池文件
```

> 这个程序理论上适用于所有米家游戏（只要使用了此概率的）
>
> 可以通过修改卡池文件 (banners.yml) 来实现 **原神 / 绝区零** 抽卡的效果

## 如何禁用自动更新？
由于我启用了 **自动检查更新卡池文件** ，本地 `banners.yml` 版本如果跟仓库中的不一样就会自动下载并替换，所以如果你想修改卡池文件以实现其他游戏的抽卡效果，请使用
```sh
python gacha.py --no-update
```
或者
```sh
./gacha.exe --no-update
```
来禁用自动检查更新

# 已知问题

- 已知在双栏输出抽卡结果时，当左侧结果末尾有`(UP)` / `(Non-UP)` 标记时会错位



# 友情链接
全新异世探险百合类GalGame正在制作中！本体完全免费，点击链接快速前往仓库：https://github.com/MewBaka/OtherSideProject

***

**点个Star叭 💕**

**欢迎PR！**
