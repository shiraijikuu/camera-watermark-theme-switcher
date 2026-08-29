# theme-switcher —— 主题切换插件

给 camera-watermark 切换界面主题：
- **跟随主题**：自动跟随 Windows 深/浅色设置（每 5 秒检测，系统切换后自动跟随）
- **黑夜模式**：深色界面
- **白天模式**：浅色界面

主窗口顶部有主题下拉，切换实时生效并记住选择（存于本插件目录 `theme.json`）。

> 注意：主题通过 `ttk.Style().theme_use('clam')` **全局生效**，会改变整个应用（含其它窗口）的外观。

**要求：主程序 >= 1.6.0**（含 `on_ui_ready` + `on_window_created` 扩展点；动态窗口：插件设置 / 插件管理 / 插件商店也随主题变色）。

## 安装
- 通过主程序「插件商店」一键安装；或下载本仓库 Release 的 zip，解压到 `plugins/theme-switcher/` 后重启。

## 发布
打包本文件夹（内含 plugin.py）为 zip，上传到 Release，并在主仓库 `plugins.json` 登记
（id/version/checksum/install_url/updated_at）。
