"""
Functions to configure Basic Settings
"""

language = "C"
windowmanager = None
icon_theme = "highcolor"
icon_size = 48

def setWindowManager(wm):
	global windowmanager
	windowmanager = wm

def setIconTheme(theme):
	global icon_theme
	icon_theme = theme

def setIconSize(size):
	global icon_size
	icon_size = size

def setLocale(lang):
	import locale
	locale.setlocale(locale.LANGUAGE, lang)
	import xdg.Locale
	xdg.Locale.update(lang)
