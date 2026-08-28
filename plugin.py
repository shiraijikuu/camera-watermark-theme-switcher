# -*- coding: utf-8 -*-
"""theme-switcher v2.0.0 —— 多主题 + 菜单栏深色化 + 一次性轻动效

- 8 套精选配色 + 跟随系统（auto 深→tokyo / 浅→paper）
- 修复黑夜模式顶部菜单栏白底：递归给 tk.Menu 及其级联子菜单上色
- 三栏布局所需 panel/card/sub_fg 语义色 + 竖排 Notebook + hover 色阶
- 轻动效（默认开，仅开窗/切主题瞬间，不碰渲染高频路径；
  想关闭就在本目录 theme.json 里写 {"animate": false}）
主程序需 >= 2.0.0（提供 self.menubar、self.theme_slot；缺失时自动降级，不报错）。
"""
import os
import json

PLUGIN_VERSION = '2.0.0'

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'theme.json')

# ==================== 配色库（语义键统一）====================
# bg 窗口底 / panel 栏·工具栏 / card 卡片 / field 输入框·滑块槽
# fg 主文字 / sub_fg 次文字 / border 边框 / select 强调色
# select_hover 强调悬停 / select_fg 强调色上的文字 / canvas_bg 预览底
# tree_bg 列表底 / tree_heading_bg 列表表头 / tab_bg 选中标签 / notebook_bg 标签栏底
THEMES = {
    'tokyo': {  # 深夜蓝（默认深色）
        'bg': '#16171f', 'panel': '#1e2030', 'card': '#252839', 'field': '#191b26',
        'fg': '#d7dcec', 'sub_fg': '#8a91ad', 'border': '#33384d',
        'select': '#5b8cff', 'select_hover': '#7aa2ff', 'select_fg': '#ffffff',
        'canvas_bg': '#12131b', 'tree_bg': '#1b1d29', 'tree_heading_bg': '#2a2e42',
        'tab_bg': '#252839', 'notebook_bg': '#1e2030'},
    'oled': {  # 纯黑 OLED（省电、高对比）
        'bg': '#000000', 'panel': '#0d0d10', 'card': '#18181c', 'field': '#141417',
        'fg': '#e8e8ea', 'sub_fg': '#8b8b94', 'border': '#2c2c33',
        'select': '#6ea8fe', 'select_hover': '#8fbcff', 'select_fg': '#06101f',
        'canvas_bg': '#000000', 'tree_bg': '#0d0d10', 'tree_heading_bg': '#1c1c22',
        'tab_bg': '#18181c', 'notebook_bg': '#0d0d10'},
    'graphite': {  # 石墨中性灰
        'bg': '#202124', 'panel': '#292a2d', 'card': '#303134', 'field': '#202124',
        'fg': '#e8eaed', 'sub_fg': '#9aa0a6', 'border': '#3c4043',
        'select': '#8ab4f8', 'select_hover': '#aecbfa', 'select_fg': '#101418',
        'canvas_bg': '#1a1b1e', 'tree_bg': '#292a2d', 'tree_heading_bg': '#35363a',
        'tab_bg': '#303134', 'notebook_bg': '#292a2d'},
    'forest': {  # 深林墨绿
        'bg': '#121a17', 'panel': '#18221d', 'card': '#1f2b25', 'field': '#141d19',
        'fg': '#d6e4dc', 'sub_fg': '#88a295', 'border': '#2f3d36',
        'select': '#4c9f70', 'select_hover': '#66bb8a', 'select_fg': '#0c1712',
        'canvas_bg': '#0e1512', 'tree_bg': '#18221d', 'tree_heading_bg': '#243029',
        'tab_bg': '#1f2b25', 'notebook_bg': '#18221d'},
    'amethyst': {  # 紫晶
        'bg': '#1a1625', 'panel': '#221d30', 'card': '#2b2540', 'field': '#1a1628',
        'fg': '#e2dcf0', 'sub_fg': '#9a90b8', 'border': '#3a3355',
        'select': '#a78bfa', 'select_hover': '#c0a8ff', 'select_fg': '#160f29',
        'canvas_bg': '#14101e', 'tree_bg': '#221d30', 'tree_heading_bg': '#2e2844',
        'tab_bg': '#2b2540', 'notebook_bg': '#221d30'},
    'mocha': {  # 暖棕摩卡
        'bg': '#1e1a17', 'panel': '#27221d', 'card': '#312b24', 'field': '#201b17',
        'fg': '#e8ddd0', 'sub_fg': '#a89884', 'border': '#40382e',
        'select': '#d4a373', 'select_hover': '#e2b98c', 'select_fg': '#241a10',
        'canvas_bg': '#171310', 'tree_bg': '#27221d', 'tree_heading_bg': '#332c25',
        'tab_bg': '#312b24', 'notebook_bg': '#27221d'},
    'paper': {  # 亮白
        'bg': '#eef1f5', 'panel': '#ffffff', 'card': '#ffffff', 'field': '#ffffff',
        'fg': '#1f2430', 'sub_fg': '#6b7280', 'border': '#d4d9e2',
        'select': '#2563eb', 'select_hover': '#1d4ed8', 'select_fg': '#ffffff',
        'canvas_bg': '#e2e6ec', 'tree_bg': '#ffffff', 'tree_heading_bg': '#eef1f5',
        'tab_bg': '#e7ecf3', 'notebook_bg': '#ffffff'},
    'cream': {  # 暖米白
        'bg': '#f4efe6', 'panel': '#fdfbf6', 'card': '#ffffff', 'field': '#fffdf8',
        'fg': '#3a3128', 'sub_fg': '#8a7d6b', 'border': '#e3dac8',
        'select': '#b45309', 'select_hover': '#92400e', 'select_fg': '#fffaf2',
        'canvas_bg': '#ece4d6', 'tree_bg': '#fdfbf6', 'tree_heading_bg': '#f0e9da',
        'tab_bg': '#f6f0e4', 'notebook_bg': '#fdfbf6'},
}

ORDER = ['auto', 'tokyo', 'oled', 'graphite', 'forest', 'amethyst', 'mocha', 'paper', 'cream']
LABELS = {
    'auto': '跟随系统', 'tokyo': '深夜蓝', 'oled': '纯黑 OLED', 'graphite': '石墨灰',
    'forest': '深林墨绿', 'amethyst': '紫晶', 'mocha': '暖棕摩卡',
    'paper': '亮白', 'cream': '暖米白',
}
_LABEL_REV = {v: k for k, v in LABELS.items()}

_PALETTE = THEMES['tokyo']  # 当前生效调色板


# ==================== 配置 ====================
def _load_cfg():
    cfg = {'theme': 'auto', 'animate': True}
    try:
        with open(_CONFIG_FILE, 'r', encoding='utf-8') as f:
            d = json.load(f)
        if d.get('theme') in ORDER:
            cfg['theme'] = d['theme']
        if 'animate' in d:
            cfg['animate'] = bool(d['animate'])
    except Exception:
        pass
    return cfg


def _save_cfg(cfg):
    try:
        with open(_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _detect_os_theme():
    """Windows 深/浅色：1=浅, 0=深；失败按浅色。"""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        val, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        winreg.CloseKey(key)
        return 'light' if val else 'dark'
    except Exception:
        return 'light'


def _resolve_key(theme_key):
    """auto 按系统解析为具体主题 key；非法值回落到 tokyo。"""
    if theme_key == 'auto':
        return 'paper' if _detect_os_theme() == 'light' else 'tokyo'
    return theme_key if theme_key in THEMES else 'tokyo'


def _resolve(theme_key):
    """auto 按系统解析为具体调色板。"""
    return THEMES[_resolve_key(theme_key)]


# ==================== ttk 样式 ====================
def _apply_ttk_styles(t, style):
    style.theme_use('clam')
    style.configure('.', background=t['bg'], foreground=t['fg'])
    style.configure('TFrame', background=t['bg'])
    style.configure('Panel.TFrame', background=t['panel'])      # 三栏/工具栏面板
    style.configure('TLabel', background=t['bg'], foreground=t['fg'])
    style.configure('Panel.TLabel', background=t['panel'], foreground=t['fg'])
    style.configure('Sub.TLabel', background=t['bg'], foreground=t['sub_fg'])

    style.configure('TButton', background=t['field'], foreground=t['fg'],
                    borderwidth=1, padding=(10, 4), focusthickness=0)
    style.map('TButton',
              background=[('pressed', t['select']), ('active', t['select_hover']),
                          ('disabled', t['border'])],
              foreground=[('active', t['select_fg']), ('pressed', t['select_fg']),
                          ('disabled', t['sub_fg'])])

    style.configure('Accent.TButton', background=t['select'], foreground=t['select_fg'],
                    borderwidth=0, padding=(12, 5))
    style.map('Accent.TButton',
              background=[('active', t['select_hover']), ('pressed', t['select'])])

    style.configure('TEntry', fieldbackground=t['field'], foreground=t['fg'],
                    insertcolor=t['fg'], bordercolor=t['border'],
                    lightcolor=t['border'], darkcolor=t['border'])
    style.configure('TCombobox', fieldbackground=t['field'], background=t['field'],
                    foreground=t['fg'], arrowcolor=t['fg'], bordercolor=t['border'],
                    lightcolor=t['border'], darkcolor=t['border'])
    style.map('TCombobox', fieldbackground=[('readonly', t['field'])],
              foreground=[('readonly', t['fg'])],
              selectbackground=[('focus', t['select'])],
              selectforeground=[('focus', t['select_fg'])])

    style.configure('TCheckbutton', background=t['bg'], foreground=t['fg'])
    style.map('TCheckbutton', background=[('active', t['bg'])])
    style.configure('TRadiobutton', background=t['bg'], foreground=t['fg'])
    style.map('TRadiobutton', background=[('active', t['bg'])])

    # 横向 Notebook
    style.configure('TNotebook', background=t['notebook_bg'], borderwidth=0)
    style.configure('TNotebook.Tab', background=t['bg'], foreground=t['sub_fg'],
                    padding=(12, 5), borderwidth=0)
    style.map('TNotebook.Tab',
              background=[('selected', t['tab_bg']), ('active', t['card'])],
              foreground=[('selected', t['fg']), ('active', t['fg'])])
    # 竖排 Notebook（右栏）：tab 在左侧、文字正向
    try:
        style.configure('Vertical.TNotebook', tabposition='wn',
                        background=t['notebook_bg'], borderwidth=0)
        style.configure('Vertical.TNotebook.Tab', padding=(10, 16),
                        background=t['bg'], foreground=t['sub_fg'], borderwidth=0)
        style.map('Vertical.TNotebook.Tab',
                  background=[('selected', t['tab_bg']), ('active', t['card'])],
                  foreground=[('selected', t['fg']), ('active', t['fg'])])
    except Exception:
        pass

    style.configure('Treeview', background=t['tree_bg'], fieldbackground=t['tree_bg'],
                    foreground=t['fg'], borderwidth=0, rowheight=24)
    style.map('Treeview',
              background=[('selected', t['select'])],
              foreground=[('selected', t['select_fg'])])
    style.configure('Treeview.Heading', background=t['tree_heading_bg'],
                    foreground=t['fg'], borderwidth=1, relief='flat')
    style.map('Treeview.Heading', background=[('active', t['card'])])

    style.configure('TScale', background=t['bg'], troughcolor=t['field'])
    style.map('TScale', background=[('active', t['bg'])])
    style.configure('Horizontal.TScale', background=t['bg'], troughcolor=t['field'])
    style.configure('TProgressbar', background=t['select'], troughcolor=t['field'],
                    borderwidth=0)
    # 卡片式分组
    style.configure('Card.TLabelframe', background=t['card'], bordercolor=t['border'],
                    lightcolor=t['border'], darkcolor=t['border'])
    style.configure('Card.TLabelframe.Label', background=t['card'], foreground=t['fg'])
    # Menubutton（插件设置下拉）
    style.configure('TMenubutton', background=t['field'], foreground=t['fg'],
                    borderwidth=1, padding=(10, 4), arrowcolor=t['fg'])
    style.map('TMenubutton', background=[('active', t['select_hover'])],
              foreground=[('active', t['select_fg'])])


# ==================== tk 控件递归上色 ====================
def _walk_apply(widget, t):
    try:
        if getattr(widget, '_wm_keep_bg', False):
            pass  # 保留手动背景，但仍遍历子控件
        else:
            cls = widget.winfo_class()
            if cls == 'Canvas':
                # 预览主画布用 canvas_bg；其余小色板 Canvas 用 _wm_keep_bg 自保
                if not getattr(widget, '_wm_keep_bg', False):
                    widget.configure(bg=t['canvas_bg'], highlightthickness=0)
            elif cls == 'Text':
                widget.configure(bg=t['field'], fg=t['fg'], insertbackground=t['fg'])
            elif cls == 'Entry':
                widget.configure(bg=t['field'], fg=t['fg'], insertbackground=t['fg'])
            elif cls == 'Label':
                widget.configure(bg=t['bg'], fg=t['fg'])
            elif cls == 'Listbox':
                widget.configure(bg=t['field'], fg=t['fg'])
            elif cls == 'Checkbutton':
                widget.configure(bg=t['bg'], fg=t['fg'], activebackground=t['bg'],
                                 activeforeground=t['fg'], selectcolor=t['field'])
            elif cls == 'Radiobutton':
                widget.configure(bg=t['bg'], fg=t['fg'], activebackground=t['bg'],
                                 activeforeground=t['fg'], selectcolor=t['field'])
    except Exception:
        pass
    for child in widget.winfo_children():
        _walk_apply(child, t)


def _color_menu(menu, t, menubar=False):
    """递归给 tk.Menu 及其 cascade 子菜单上色（修复黑夜菜单栏白底 P1）。"""
    try:
        menu.configure(
            bg=(t['bg'] if menubar else t['panel']), fg=t['fg'],
            activebackground=t['select'], activeforeground=t['select_fg'],
            borderwidth=0, relief='flat', tearoff=0)
        end = menu.index('end')
        if end is None:
            return
        for idx in range(int(end) + 1):
            try:
                if menu.type(idx) == 'cascade':
                    sub = menu.nametowidget(menu.entrycget(idx, 'menu'))
                    _color_menu(sub, t, menubar=False)
            except Exception:
                continue
    except Exception:
        pass


# ==================== 轻动效（一次性、只改 toplevel 透明度）====================
def _fade_in(win, cfg, start=0.90, end=1.0, steps=5, interval=16):
    """开窗淡入：仅操作 -alpha，5 帧共约 80ms，不触发控件重绘。"""
    if not cfg.get('animate', True):
        return
    try:
        step = (end - start) / steps
        state = {'v': start, 'n': 0}

        def tick():
            state['n'] += 1
            state['v'] += step
            try:
                win.attributes('-alpha', min(end, state['v']))
            except Exception:
                return
            if state['n'] < steps:
                win.after(interval, tick)
        win.attributes('-alpha', start)
        win.after(10, tick)
    except Exception:
        try:
            win.attributes('-alpha', 1.0)
        except Exception:
            pass


# ==================== 应用主题 ====================
def _apply_theme(theme_key, app, style, cfg):
    global _PALETTE
    t = _resolve(theme_key)
    _PALETTE = t
    _apply_ttk_styles(t, style)
    try:
        app.root.configure(bg=t['bg'])
    except Exception:
        pass
    _walk_apply(app.root, t)
    mb = getattr(app, 'menubar', None)   # 主程序保存的菜单栏引用
    if mb is not None:
        _color_menu(mb, t, menubar=True)
    # 切主题时主窗口极短淡入（3 帧）
    _fade_in(app.root, cfg, start=0.96, end=1.0, steps=3, interval=14)
    return t


def _theme_window(win, cfg):
    """动态 Toplevel 上色 + 淡入。"""
    t = _PALETTE
    try:
        win.configure(bg=t['bg'])
    except Exception:
        pass
    _walk_apply(win, t)
    # Toplevel 内若有菜单也上色
    try:
        for child in win.winfo_children():
            if child.winfo_class() == 'Menu':
                _color_menu(child, t, menubar=True)
    except Exception:
        pass
    _fade_in(win, cfg)


def register(api):
    def init_ui(app):
        import tkinter as tk
        from tkinter import ttk
        style = ttk.Style()
        cfg = _load_cfg()
        state = {'theme': cfg.get('theme', 'auto'), 'applied': None}

        def apply_now():
            try:
                _apply_theme(state['theme'], app, style, cfg)
                state['applied_key'] = _resolve_key(state['theme'])
            except Exception as e:
                print('[theme-switcher] apply:', e)

        # 主题下拉：优先挂到底部预留槽 self.theme_slot，没有则降级自建 bar
        try:
            slot = getattr(app, 'theme_slot', None)
            parent = slot if slot is not None else app.root
            ttk.Label(parent, text='🌓 ').pack(side='left', padx=(4, 1))
            combo = ttk.Combobox(parent, values=list(LABELS[k] for k in ORDER),
                                 state='readonly', width=11)
            combo.set(LABELS.get(state['theme'], '跟随系统'))
            combo.pack(side='left')

            def on_change(_evt=None):
                key = _LABEL_REV.get(combo.get(), 'auto')
                state['theme'] = key
                cfg['theme'] = key
                _save_cfg(cfg)
                apply_now()

            combo.bind('<<ComboboxSelected>>', on_change)
        except Exception as e:
            print('[theme-switcher] selector:', e)

        apply_now()

        # 跟随系统：每 5 秒轻量检测，仅 auto 模式且实际深/浅变化时才重绘
        def poll():
            try:
                if state['theme'] == 'auto':
                    want = _resolve_key('auto')
                    if want != state.get('applied_key'):
                        apply_now()
            except Exception:
                pass
            try:
                app.root.after(5000, poll)
            except Exception:
                pass

        app.root.after(5000, poll)

    def on_window(win):
        cfg = _load_cfg()
        _theme_window(win, cfg)

    api.on_ui_ready(init_ui)
    api.on_window_created(on_window)
