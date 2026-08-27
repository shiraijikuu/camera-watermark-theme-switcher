# -*- coding: utf-8 -*-
"""theme-switcher —— 主题切换插件（黑夜模式 / 白天模式 / 跟随系统）

主程序需 >= 1.7.0（含 on_ui_ready + on_window_created 扩展点；动态窗口随主题变色；缩略图选中高亮保留）。
功能：
- 三种模式：跟随系统 / 黑夜模式 / 白天模式
- 主窗口顶部提供主题下拉，实时生效并记住选择（存到本插件目录 theme.json）
- 「跟随系统」模式下每 5 秒检测一次 Windows 深/浅色设置，自动切换
"""
import os
import json

PLUGIN_VERSION = '1.0.4'

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'theme.json')

DARK = {
    'bg': '#1e1e1e', 'fg': '#e0e0e0', 'select': '#3b82f6',
    'field': '#2d2d30', 'border': '#3f3f46', 'notebook_bg': '#252526',
    'tree_bg': '#252526', 'tree_heading_bg': '#333337', 'tab_bg': '#2d2d30',
}
LIGHT = {
    'bg': '#f0f0f0', 'fg': '#1f1f1f', 'select': '#2563eb',
    'field': '#ffffff', 'border': '#d4d4d8', 'notebook_bg': '#f0f0f0',
    'tree_bg': '#ffffff', 'tree_heading_bg': '#e4e4e7', 'tab_bg': '#ffffff',
}

LABELS = {'auto': '跟随主题', 'dark': '黑夜模式', 'light': '白天模式'}
_LABEL_REV = {v: k for k, v in LABELS.items()}

_PALETTE = LIGHT  # 当前生效的配色（供动态窗口上色）


def _load_choice():
    try:
        with open(_CONFIG_FILE, 'r', encoding='utf-8') as f:
            d = json.load(f)
        if d.get('theme') in ('auto', 'dark', 'light'):
            return d['theme']
    except Exception:
        pass
    return 'auto'


def _save_choice(theme):
    try:
        with open(_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'theme': theme}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _detect_os_theme():
    """读取 Windows 深/浅色设置（AppsUseLightTheme: 1=浅色, 0=深色）。"""
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


def _apply_ttk_styles(t, style):
    """ttk 全局样式。注意：theme_use('clam') 全局生效，会改变所有窗口及未来创建的控件外观。"""
    style.theme_use('clam')
    style.configure('.', background=t['bg'], foreground=t['fg'])
    style.configure('TFrame', background=t['bg'])
    style.configure('TLabel', background=t['bg'], foreground=t['fg'])
    style.configure('TButton', background=t['field'], foreground=t['fg'], borderwidth=1, padding=(8, 3))
    style.map('TButton',
              background=[('active', t['select']), ('disabled', t['border'])],
              foreground=[('disabled', '#888888')])
    style.configure('TEntry', fieldbackground=t['field'], foreground=t['fg'],
                    insertcolor=t['fg'], bordercolor=t['border'], lightcolor=t['border'], darkcolor=t['border'])
    style.configure('TCombobox', fieldbackground=t['field'], background=t['field'],
                    foreground=t['fg'], arrowcolor=t['fg'], bordercolor=t['border'],
                    lightcolor=t['border'], darkcolor=t['border'])
    style.map('TCombobox',
              fieldbackground=[('readonly', t['field'])],
              foreground=[('readonly', t['fg'])])
    style.configure('TCheckbutton', background=t['bg'], foreground=t['fg'])
    style.map('TCheckbutton', background=[('active', t['bg'])])
    style.configure('TRadiobutton', background=t['bg'], foreground=t['fg'])
    style.map('TRadiobutton', background=[('active', t['bg'])])
    style.configure('TNotebook', background=t['notebook_bg'], borderwidth=0)
    style.configure('TNotebook.Tab', background=t['bg'], foreground=t['fg'], padding=(12, 4))
    style.map('TNotebook.Tab', background=[('selected', t['tab_bg'])], foreground=[('selected', t['fg'])])
    style.configure('Treeview', background=t['tree_bg'], fieldbackground=t['tree_bg'],
                    foreground=t['fg'], borderwidth=0, rowheight=22)
    style.configure('Treeview.Heading', background=t['tree_heading_bg'], foreground=t['fg'],
                    borderwidth=1, relief='flat')
    style.configure('TScale', background=t['bg'], troughcolor=t['field'])
    style.map('TScale', background=[('active', t['bg'])])
    style.configure('TProgressbar', background=t['select'], troughcolor=t['field'], borderwidth=0)
    style.configure('TLabelframe', background=t['bg'], bordercolor=t['border'], lightcolor=t['border'], darkcolor=t['border'])
    style.configure('TLabelframe.Label', background=t['bg'], foreground=t['fg'])
    style.configure('Horizontal.TScale', background=t['bg'], troughcolor=t['field'])


def _walk_apply(widget, t):
    """递归给 tk 控件上色（Canvas/Text/Entry/Label/Listbox/Checkbutton/Radiobutton）。
    被应用标记 _wm_keep_bg 的控件（如缩略图选中态）保留其手动背景，不覆盖。"""
    try:
        if getattr(widget, '_wm_keep_bg', False):
            return  # 跳过该控件本身，但仍会遍历其子控件
        cls = widget.winfo_class()
        if cls == 'Canvas':
            widget.configure(bg=t['bg'], highlightthickness=0)
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


def _apply_theme(mode, root, style):
    """把 clam 主题 + ttk 样式 + tk 控件配色应用到主窗口。"""
    global _PALETTE
    t = DARK if mode == 'dark' else LIGHT
    _PALETTE = t
    _apply_ttk_styles(t, style)
    try:
        root.configure(bg=t['bg'])
    except Exception:
        pass
    _walk_apply(root, t)


def _theme_window(win):
    """给动态 Toplevel（插件设置/管理/商店等）上当前主题色。"""
    t = _PALETTE
    try:
        win.configure(bg=t['bg'])
    except Exception:
        pass
    _walk_apply(win, t)


def register(api):
    def init_ui(app):
        import tkinter as tk
        from tkinter import ttk
        style = ttk.Style()
        state = {'theme': _load_choice(), 'applied': None}

        def apply_now():
            mode = state['theme']
            if mode == 'auto':
                mode = _detect_os_theme()
            try:
                _apply_theme(mode, app.root, style)
            except Exception as e:
                print('[theme-switcher] apply:', e)
            state['applied'] = mode

        # 主窗口顶部主题下拉
        try:
            bar = ttk.Frame(app.root)
            bar.pack(side='top', fill='x')
            ttk.Label(bar, text='主题: ').pack(side='left', padx=(8, 2), pady=2)
            combo = ttk.Combobox(bar, values=list(LABELS.values()), state='readonly', width=10)
            combo.set(LABELS.get(state['theme'], '跟随主题'))
            combo.pack(side='left', pady=2)

            def on_change(_evt=None):
                state['theme'] = _LABEL_REV.get(combo.get(), 'auto')
                _save_choice(state['theme'])
                apply_now()

            combo.bind('<<ComboboxSelected>>', on_change)
        except Exception as e:
            print('[theme-switcher] bar:', e)

        apply_now()

        # 跟随系统：每 5 秒检测一次并自动切换
        def poll():
            try:
                if state['theme'] == 'auto':
                    mode = _detect_os_theme()
                    if mode != state['applied']:
                        apply_now()
            except Exception:
                pass
            try:
                app.root.after(5000, poll)
            except Exception:
                pass

        app.root.after(5000, poll)

    api.on_ui_ready(init_ui)
    api.on_window_created(_theme_window)
