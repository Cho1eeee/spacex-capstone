# GitHub 推送指南（3 分钟完成）

> **状态：已完成（2026-10-29 23:37）**
> 仓库已上线：https://github.com/cho1eeee/spacex-capstone
> 79 个文件已推送，8 个带输出 notebook、2 个 PDF、12 张图表、4 个地图。
> 后续如果修改了文件，直接执行 `python scripts/13_push_via_api.py` 即可增量推送
> （只上传内容有变化的文件，需要 token.txt 里有可用 token）。

项目已初始化好本地 Git 仓库（`spacex-capstone/`，main 分支，已提交全部文件）。
只需再走 3 步即可上线，并把报告中的 GitHub URL 换成真实地址。

## 第 1 步：在 GitHub 网页上创建空仓库

1. 打开 https://github.com/new
2. Repository name 填：`spacex-capstone`
3. 选 Public（评分需要可访问的 URL）
4. **不要**勾选 "Add a README / .gitignore / license"（本地已有，避免冲突）
5. 点击 **Create repository**，记下你的仓库地址，例如：
   `https://github.com/cho1eeee/spacex-capstone.git`

## 第 2 步：推送

### 方式 A（推荐）：双击一键脚本

在 `C:\Users\15838\WorkBuddy\2026-10-29-14-12-57\` 目录下双击：

- **`push_to_github.bat`** —— 自动用内置 Git 推送，弹出 GitHub 登录窗口时点
  「Sign in with your browser」→ 浏览器里点 Authorize。
- 若登录窗口弹不出来或授权反复失败，改用 **`push_with_token.bat`**：
  先到 https://github.com/settings/tokens/new 生成一个勾选 `repo` 权限的 token
  （以 `ghp_` 开头），粘贴进窗口即可（token 不会写进 git 配置）。

> 本机没有独立安装 Git，脚本已内置使用
> `C:\Users\15838\.workbuddy\binaries\PortableGit\versions\1.2.0\cmd\git.exe`。

### 方式 C：让 AI 通过 REST API 推送（当 git 走不通时）

如果脚本里的登录窗口弹不出来，或 `git push` 被网络拦截，可以只提供一个 token：

1. 打开 https://github.com/settings/tokens/new?scopes=repo&description=spacex-capstone
   生成一个勾选 `repo` 权限、有效期 7 天的 token（`ghp_` 开头）
2. 把它粘贴到 `C://Users//15838//WorkBuddy//2026-10-29-14-12-57//token.txt` 第一行并保存
3. 执行：
   ```bash
   cd "C://Users//15838//WorkBuddy//2026-10-29-14-12-57//spacex-capstone"
   python scripts/13_push_via_api.py --dry-run   # 先看清单（78 个文件 / 约 12 MB）
   python scripts/13_push_via_api.py             # 真正推送
   ```
   该脚本通过 api.github.com 的 Git Data API（blob → tree → commit → ref）重建提交，
   不依赖 github.com 的 git 协议。推送完成后请到 https://github.com/settings/tokens 删除该 token。

### 方式 B：手动命令行
```bash
cd "C:\Users\15838\WorkBuddy\2026-10-29-14-12-57\spacex-capstone"
git remote add origin https://github.com/cho1eeee/spacex-capstone.git
git push -u origin main
```

> 首次推送会弹出浏览器要求登录 GitHub，按提示授权即可。
> 如果你用的是 zip 解压版（没有 .git 目录），先执行：
> ```bash
> git init -b main && git add -A && git commit -m "SpaceX capstone"
> ```
> 再执行上面的 remote add + push。

## 第 3 步：替换报告中的 GitHub URL 并重新生成 PDF

1. 打开 `spacex-capstone/slides/slides_en.html`（英文版）和 `slides/slides.html`（中文版），
   全局替换 `<your-username>` → 你的 GitHub 用户名
2. 重新生成最终 PDF：
   ```bash
   cd "C:\Users\15838\WorkBuddy\2026-10-29-14-12-57\spacex-capstone"
   python scripts/09_render_pdf.py slides_en.html SpaceX_Capstone_Report_EN.pdf   # 英文版
   python scripts/09_render_pdf.py slides.html     SpaceX_Capstone_Report.pdf     # 中文版
   ```
3. **提交评分系统必须用英文版** `report/SpaceX_Capstone_Report_EN.pdf`
   （评分者是英文 AI，中文版会导致内容无法确认而大量丢分——上次 7/15 的教训）。
4. 顺手把新 commit 推上去：`git add -A && git commit -m "real repo url" && git push`

## 上传评分系统

在问题 1 的上传框拖入 `report/SpaceX_Capstone_Report_EN.pdf`（约 3 MB，远小于 100 MB 限制）。

## 本次新增：Jupyter Notebooks

评分点要求 "completed notebooks and Python files"，`notebooks/` 下已有 8 个
**带完整运行输出** 的 notebook（01 API 采集 … 08 分类建模），与 scripts 一一对应。

## 检查清单（对应 15 个评分点）

| 评分点 | 位置 |
|---|---|
| 1.1 GitHub URL | 封面 + 各页 GitHub 徽章 + 第 13 页 |
| 1.2 演示幻灯片 PDF | 本报告（13 页幻灯片格式） |
| 1.3 执行摘要（方法+关键结果） | 第 2 页 |
| 1.4 引言+问题陈述 | 第 3 页 |
| 1.5 API 调用流程图 + URL | 第 4 页 |
| 1.6 爬虫流程图 + URL | 第 5 页 |
| 1.7 数据清洗 + URL | 第 6 页 |
| 1.8 EDA 图表目的 + URL | 第 7 页 |
| 1.9 SQL 查询 + URL | 第 8 页 |
| 1.10 Folium + Dash 总结 + URL | 第 9、10 页 |
| 1.11 散点/条形/年度趋势 | 第 7 页 |
| 1.12 EDA 与 SQL（场址/载荷/成功率/排名/时间） | 第 7、8 页 |
| 1.13 Folium（标记/记录/邻近分析） | 第 9 页 |
| 1.14 Dash（饼图 + 散点图） | 第 10 页 |
| 1.15 预测分析（多模型/混淆矩阵/最佳模型/创新见解） | 第 11、12 页 |
