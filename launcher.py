#!/usr/bin/python3
"""Native Qt Widgets interface for the offline Kavach dashboard."""
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

from PySide6.QtCore import QRectF, QSettings, Qt, QUrl
from PySide6.QtGui import (
    QColor, QDesktopServices, QFontMetrics, QIcon, QPainter, QPainterPath, QPalette, QPen, QPixmap,
)
from PySide6.QtWidgets import (
    QApplication, QBoxLayout, QCheckBox, QComboBox, QDialog, QFrame, QGridLayout,
    QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QLineEdit, QListView, QMainWindow, QMenu, QPlainTextEdit, QProgressBar, QPushButton,
    QScrollArea, QSizePolicy, QStackedWidget, QToolButton, QVBoxLayout,
)

ROOT = Path(__file__).resolve().parent
ICON = ROOT / 'kavach.png'
VERSION = (ROOT / 'version.txt').read_text(encoding='utf-8').strip()
CREATOR = 'Anup Kumar Yadav'
CONTENT = json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
LANGUAGE_LABELS = json.loads((ROOT / 'languages.json').read_text(encoding='utf-8'))
LANGUAGES = tuple(LANGUAGE_LABELS)
TABS = ('dashboard', 'scams', 'learnTab', 'tips', 'checklist', 'report')
TOPICS = {
    'payments': 'learnPayments', 'messages': 'learnMessages', 'identity': 'learnIdentity',
    'offers': 'learnOffers', 'devices': 'learnDevices', 'response': 'learnResponse',
}
PORTAL = 'https://cybercrime.gov.in/'
WEBSITE = 'https://jatayuos.in/'
RBI = 'https://rbi.org.in/'
DOT = 'https://www.sancharsaathi.gov.in/'
OFFICIAL_WEBSITES = frozenset((PORTAL, WEBSITE, RBI, DOT))
ACTIONS = {
    'firewall': ('/usr/bin/systemsettings', 'kcm_firewall'),
    'updates': ('/usr/bin/plasma-discover', '--mode', 'Update'),
    'backup': ('/usr/bin/jatayu', 'backup'),
}
STYLE = """
QMainWindow, QScrollArea, QFrame#page { background: #f5f7f9; color: #1a1a2e; }
QScrollArea { border: none; }
QLabel, QCheckBox { color: #1a1a2e; font-size: 16px; }
QLineEdit, QComboBox { font-size: 16px; }
QFrame#header { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #172554, stop:1 #1e3a8a); }
QFrame#header QLabel { color: white; }
QFrame#navigation { background: rgba(0, 0, 0, 51); }
QLabel#brand { font-family: "Noto Sans Devanagari"; font-size: 35px; font-weight: bold; }
QLabel#title { font-size: 29px; font-weight: bold; color: #1a1a2e; }
QLabel#cardTitle { font-size: 19px; font-weight: bold; color: #1a1a2e; }
QLabel#muted { color: #40536c; }
QDialog#readingDialog { background: #f5f7fb; }
QFrame#readingHeader { background: #172554; border-radius: 12px; }
QFrame#readingHeader QLabel { color: #ffffff; }
QLabel#readingTitle { font-size: 25px; font-weight: bold; }
QLabel#readingBody { font-size: 17px; color: #202840; }
QFrame#readingSection { background: white; border: 1px solid #dce5ef; border-radius: 9px; }
QLabel#readingHeading { font-size: 15px; color: #263f76; font-weight: bold; }
QLabel#creatorName { font-size: 24px; color: #172554; font-weight: bold; }
QPushButton[role="dialogClose"] { background: #1e3a8a; border-color: #1e3a8a; color: white; font-weight: bold; padding: 8px 24px; }
QPushButton[role="dialogClose"]:hover { background: #172554; }
QLabel#lesson { background: #fff1cb; color: #5e360b; padding: 10px; border-radius: 7px; }
QLabel#sample { background: #eaf0fa; color: #17243d; padding: 10px; border-radius: 7px; }
QLabel#right { background: #def6e7; color: #135b35; padding: 10px; border-radius: 7px; }
QLabel#retry { background: #fff1cb; color: #63390c; padding: 10px; border-radius: 7px; }
QFrame#card, QFrame#dialog { background: white; border-radius: 15px; }
QFrame#card[accent="green"] { border-left: 5px solid #16a34a; }
QFrame#card[accent="amber"] { border-left: 5px solid #f59e0b; }
QFrame#card[accent="red"] { border-left: 5px solid #dc2626; }
QFrame#card[accent="green"][rtl="true"] { border-left: 0; border-right: 5px solid #16a34a; }
QFrame#card[accent="amber"][rtl="true"] { border-left: 0; border-right: 5px solid #f59e0b; }
QFrame#card[accent="red"][rtl="true"] { border-left: 0; border-right: 5px solid #dc2626; }
QFrame#card[accent="top-green"] { border-top: 4px solid #16a34a; }
QFrame#card[accent="top-red"] { border-top: 4px solid #dc2626; }
QFrame#card[accent="top-amber"] { border-top: 4px solid #f59e0b; }
QFrame#card[accent="top-blue"] { border-top: 4px solid #1e3a8a; }
QFrame#urgent, QFrame#scamHeader {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #dc2626, stop:1 #991b1b);
}
QFrame#urgent { border-radius: 15px; }
QFrame#scamHeader { border-top-left-radius: 15px; border-top-right-radius: 15px; }
QFrame#urgent QLabel, QFrame#scamHeader QLabel { color: white; }
QLabel#urgentTitle { font-size: 24px; font-weight: bold; }
QLabel#scamTitle { font-size: 19px; font-weight: bold; }
QLabel#sectionLabel { font-size: 15px; font-weight: bold; color: #a51b1b; }
QLabel#iconTile { font-size: 25px; border-radius: 11px; background: #dcfce7; }
QLabel#iconTile[tone="amber"] { background: #fef3c7; }
QLabel#iconTile[tone="red"] { background: #fee2e2; }
QLabel#iconTile[tone="scam"] { background: rgba(255, 255, 255, 51); }
QLabel#statusPill { padding: 5px 9px; border-radius: 12px; font-size: 14px; font-weight: bold; }
QLabel#statusPill[tone="green"] { background:#dcfce7; color:#146534; }
QLabel#statusPill[tone="amber"] { background:#fef3c7; color:#8a4900; }
QLabel#statusPill[tone="red"] { background:#fee2e2; color:#991b1b; }
QPushButton { background: #eaf0fb; color: #17356e; border: 1px solid #9eafc9; border-radius: 8px; }
QPushButton:hover, QPushButton:checked { background: #d7e5fd; border-color: #234994; }
QPushButton:focus, QLineEdit:focus, QComboBox:focus { border: 2px solid #9e5a00; }
QPushButton QLabel { background: transparent; color: #17356e; }
QPushButton[role="nav"] { background: transparent; border: none; border-bottom: 3px solid transparent; border-radius: 0; }
QPushButton[role="nav"]:hover, QPushButton[role="nav"]:focus { background: rgba(255,255,255,25); }
QPushButton[role="nav"]:checked { border-bottom: 3px solid #ffc451; }
QPushButton[role="nav"] QLabel { color: white; }
QPushButton[role="nav"]:checked QLabel { font-weight: bold; }
QPushButton[role="urgent"] { background: #dc2024; border-radius: 25px; border: none; }
QPushButton[role="urgent"] QLabel { color: white; font-weight: bold; }
QPushButton[role="urgent"]:hover { background: #bd1b23; }
QPushButton[role="emergencyTile"] { background: white; border: none; border-radius: 10px; }
QPushButton[role="reportPhone"] { background: white; border: 1px solid #e3a7ad; border-radius: 9px; }
QPushButton[role="reportPhone"]:hover { background: #fef0f1; border-color: #b72431; }
QPushButton[role="reportPhone"]:focus { border: 2px solid #a96808; }
QPushButton[role="reportPhone"] QLabel { color: #9c2030; font-weight: bold; }
QFrame#urgent QPushButton[role="emergencyTile"] QLabel { color: #bb202a; font-weight: bold; }
QPushButton[role="primary"] { background: #1e3a8a; border: 1px solid #1e3a8a; }
QPushButton[role="primary"]:hover { background: #172554; }
QPushButton[role="primary"] QLabel { color: white; font-weight: bold; }
QPushButton[role="risk"] { background: #fee2e2; border: 1px solid #fee2e2; border-radius: 13px; }
QPushButton[role="risk"]:hover { border-color: #c4212a; }
QPushButton[role="risk"] QLabel { color: #991b1b; font-size: 14px; font-weight: bold; }
QPushButton[role="urgent"]:focus, QPushButton[role="primary"]:focus,
QPushButton[role="risk"]:focus, QPushButton[role="emergencyTile"]:focus { border: 2px solid #a96808; }
QLineEdit, QComboBox { color: #18213e; background: white; padding: 8px; border-radius: 6px; border: 1px solid #9eafc9; }
QFrame#footer { background: #172554; }
QFrame#footer QLabel { color: #f0f4fc; }
QFrame#footer QLabel#copyright { color: #d3d9e6; }
QFrame#websiteBar { background: #f5f7f9; }
QPushButton[role="footerLink"], QPushButton[role="websiteLink"] {
    border: 1px solid transparent; background: transparent; padding: 6px 8px; font-size: 16px;
}
QPushButton[role="footerLink"] { color: #fbbf24; font-weight: bold; }
QPushButton[role="footerLink"]:hover, QPushButton[role="websiteLink"]:hover { text-decoration: underline; }
QPushButton[role="footerLink"]:focus, QPushButton[role="websiteLink"]:focus { border-color: #d89017; }
QPushButton[role="websiteLink"] { color: #1644a4; text-decoration: underline; }
QProgressBar { background: #e2e8f0; border: 0; border-radius: 5px; }
QProgressBar::chunk { background: #16a34a; border-radius: 5px; }
QLabel#checkProgress { font-weight: bold; color: #1a1a2e; }
QFrame#checkRow:hover { background: #f4f7fb; }
QFrame#checkDivider { background: #e2e8f0; }
QToolButton#aboutMenu {
    background: #142657; color: white; font-size: 16px;
    border: 1px solid #7489af; border-radius: 6px; padding: 8px 18px 8px 10px;
}
QToolButton#aboutMenu:focus, QToolButton#aboutMenu:hover { border-color: #ffc451; }
QToolButton#aboutMenu::menu-indicator { subcontrol-position: right center; right: 4px; }
QMenu#aboutPopup { background: white; color: #18213e; border: 1px solid #9eafc9; }
QMenu#aboutPopup::item { padding: 8px 18px; }
QMenu#aboutPopup::item:selected { color: white; background: #254b96; }
QPlainTextEdit#licenceText { font-size: 16px; padding: 10px; color: #18213e; background: white; border: 1px solid #dce5ef; }

"""


def text(value, role=''):
    label = QLabel(value)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setWordWrap(True)
    label.setObjectName(role)
    return label


def button(value, action, role=''):
    control = QPushButton()
    control.setAccessibleName(value)
    control.setProperty('role', role)
    control.setCursor(Qt.CursorShape.PointingHandCursor)
    layout = QVBoxLayout(control)
    margins = {'nav': (14, 14, 14, 14), 'urgent': (18, 13, 18, 13),
               'primary': (12, 10, 12, 10), 'emergencyTile': (12, 12, 12, 12),
               'risk': (10, 5, 10, 5)}
    layout.setContentsMargins(*margins.get(role, (9, 7, 9, 7)))
    label = text(value)
    label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    if role in ('nav', 'urgent', 'primary', 'emergencyTile', 'reportPhone', 'risk'):
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    control.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    control.clicked.connect(action)
    return control


def panel(role='', *, horizontal=False, padding=0, gap=10):
    box = QFrame()
    box.setObjectName(role)
    layout = QHBoxLayout(box) if horizontal else QVBoxLayout(box)
    layout.setContentsMargins(padding, padding, padding, padding)
    layout.setSpacing(gap)
    return box, layout


class ChecklistCheckbox(QCheckBox):
    def __init__(self, title):
        super().__init__()
        self.setAccessibleName(title)
        self.setFixedSize(26, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def hitButton(self, position):
        return self.rect().contains(position)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        checked = self.isChecked()
        painter.setPen(QPen(QColor('#14743a' if checked else '#718299'), 1.5))
        painter.setBrush(QColor('#16a34a' if checked else '#ffffff'))
        painter.drawRoundedRect(QRectF(3, 3, 20, 20), 4, 4)
        if checked:
            painter.setPen(QPen(QColor('#ffffff'), 2.2))
            painter.drawLine(8, 13, 12, 17)
            painter.drawLine(12, 17, 19, 9)
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor('#a96808'), 1.5))
            painter.drawRoundedRect(QRectF(1, 1, 24, 24), 5, 5)
        painter.end()


class ChecklistRow(QFrame):
    def __init__(self, item, checked):
        super().__init__()
        self.setObjectName('checkRow')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        row = QHBoxLayout(self)
        row.setContentsMargins(15, 13, 15, 13)
        row.setSpacing(14)
        self.checkbox = ChecklistCheckbox(item['title'])
        self.checkbox.setAccessibleDescription(item['desc'])
        self.checkbox.setChecked(checked)
        row.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignTop)
        body, column = panel(gap=4)
        self.title = text(item['title'], 'cardTitle')
        description = text(item['desc'], 'muted')
        body.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        column.addWidget(self.title)
        column.addWidget(description)
        row.addWidget(body, 1)
        self.checkbox.toggled.connect(self.apply_completed_style)
        self.apply_completed_style(checked)

    def apply_completed_style(self, checked):
        font = self.title.font()
        font.setStrikeOut(checked)
        self.title.setFont(font)
        self.title.setStyleSheet('color: #506681;' if checked else '')

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.checkbox.setFocus()
            self.checkbox.click()
            event.accept()
        else:
            super().mouseReleaseEvent(event)


def light_combo():
    combo = QComboBox()
    combo.setStyleSheet("QComboBox { combobox-popup: 0; }")
    view = QListView(combo)
    palette = QPalette(view.palette())
    for role, color in (
        (QPalette.ColorRole.Base, '#ffffff'),
        (QPalette.ColorRole.Text, '#18213e'),
        (QPalette.ColorRole.Highlight, '#254b96'),
        (QPalette.ColorRole.HighlightedText, '#ffffff'),
    ):
        palette.setColor(role, QColor(color))
    view.setPalette(palette)
    view.setSpacing(3)
    view.setStyleSheet("""
        QListView { background-color: white; color: #18213e; border: 1px solid #9eafc9; }
        QListView::item { color: #18213e; }
        QListView::item:selected { color: white; background-color: #254b96; }
    """)
    combo.setView(view)
    return combo


def classic_logo():
    pixmap = QPixmap(66, 66)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor('#ffb612'))
    painter.drawEllipse(QRectF(0, 0, 66, 66))
    shield = QPainterPath()
    shield.moveTo(33, 14)
    shield.quadTo(41, 21, 50, 21)
    shield.quadTo(48, 44, 33, 54)
    shield.quadTo(18, 44, 16, 21)
    shield.quadTo(25, 21, 33, 14)
    painter.setPen(QPen(QColor('#5086a4'), 2))
    painter.setBrush(QColor('#adcbd7'))
    painter.drawPath(shield)
    painter.setPen(QPen(QColor('#e7f5fc'), 2))
    painter.drawLine(33, 18, 33, 48)
    painter.end()
    return pixmap


def icon_tile(symbol, tone='green'):
    label = text(symbol, 'iconTile')
    label.setFixedSize(50, 50)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setProperty('tone', tone)
    return label


def pill(value, tone):
    label = text(value, 'statusPill')
    label.setProperty('tone', tone)
    return label


def shadow(widget, color='#210d1e38'):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(18)
    effect.setOffset(0, 4)
    effect.setColor(QColor(color))
    widget.setGraphicsEffect(effect)

def scroll_view(content):
    view = QScrollArea()
    view.setWidgetResizable(True)
    view.setWidget(content)
    return view


def normalized(value):
    return unicodedata.normalize('NFKC', value).casefold()


class KavachWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('JatayuOS', 'Kavach')
        saved = self.settings.value('language', 'en')
        self.locale = saved if saved in LANGUAGES else 'en'
        self.pages = {}
        self.grids = []
        self.banner_layout = None
        self.active_tab = 'dashboard'
        self.query = ''
        self.selected_topic = ''
        self.answers = {}
        self.revealed = set()
        self.completed = self.read_checklist()
        self.english = json.loads((ROOT / 'locales' / 'en.json').read_text(encoding='utf-8'))
        self.setWindowIcon(QIcon(str(ICON)))
        self.resize(1180, 780)
        self.setMinimumSize(760, 520)
        self.setStyleSheet(STYLE)
        self.load_language(self.locale)

    def read_checklist(self):
        try:
            stored = json.loads(self.settings.value('nativeChecklist', '[]', type=str))
        except (ValueError, TypeError):
            return set()
        if not isinstance(stored, list):
            return set()
        return {item for item in stored if type(item) is int and 1 <= item <= 12}

    def t(self, key):
        return self.catalog[key]

    def copy(self, index):
        return self.t(f'copy{index}')

    def native(self, key):
        return self.catalog['_native'][key]

    def load_language(self, locale):
        self.locale = locale
        self.catalog = self.english if locale == 'en' else json.loads(
            (ROOT / 'locales' / f'{locale}.json').read_text(encoding='utf-8'))
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.catalog['_meta']['direction'] == 'rtl'
                                else Qt.LayoutDirection.LeftToRight)
        self.setWindowTitle(self.native('windowTitle'))
        self.settings.setValue('language', locale)
        root, layout = panel(gap=0)
        header, header_layout = panel('header', padding=25, gap=4)
        header_layout.setContentsMargins(30, 25, 30, 25)
        row, bar = panel(horizontal=True)
        row.setMinimumHeight(76)
        emblem = QLabel()
        emblem.setPixmap(classic_logo())
        bar.addWidget(emblem)
        brand, branding = panel(gap=1)
        branding.addWidget(text('कवच', 'brand'))
        branding.addWidget(text(self.copy(0)))
        bar.addWidget(brand, 1)
        languages = light_combo()
        languages.setAccessibleName(self.native('language'))
        languages.setMinimumWidth(122)
        languages.setMaxVisibleItems(12)
        for item, label in LANGUAGE_LABELS.items():
            languages.addItem(label, item)
        languages.setCurrentIndex(LANGUAGES.index(locale))
        languages.currentIndexChanged.connect(lambda index: self.load_language(LANGUAGES[index]))
        bar.addWidget(languages)
        bar.addWidget(self.about_menu())
        emergency = button(self.copy(1), lambda: self.show_phone('1930'), 'urgent')
        emergency.setMinimumSize(208, 49)
        emergency.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        bar.addWidget(emergency)
        header_layout.addWidget(row)
        nav, links = panel('navigation', horizontal=True, gap=4)
        nav.setMinimumHeight(50)
        links.setContentsMargins(16, 0, 16, 0)
        self.nav = {}
        for tab in TABS:
            control = button(self.t(tab), lambda _, key=tab: self.go(key), 'nav')
            control.setCheckable(True)
            self.nav[tab] = control
            links.addWidget(control)
        links.addStretch()
        header_layout.addWidget(nav)
        layout.addWidget(header)
        self.stack = QStackedWidget()
        self.pages = {}
        self.grids = []
        self.banner_layout = None
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)
        self.arrange_navigation()
        self.go(self.active_tab)

    def go(self, tab):
        self.active_tab = tab
        for key, control in self.nav.items():
            control.setChecked(key == tab)
        if tab not in self.pages:
            factory = {'dashboard': self.dashboard, 'scams': self.scams, 'learnTab': self.practice,
                       'tips': self.tips, 'checklist': self.checklist, 'report': self.report}[tab]
            full_page, body = panel('page', gap=0)
            body.addWidget(factory(), 1)
            self.add_footer(body)
            self.pages[tab] = self.stack.addWidget(scroll_view(full_page))
        self.stack.setCurrentIndex(self.pages[tab])

    def about_menu(self):
        terms = self.t('_about')
        trigger = QToolButton()
        trigger.setObjectName('aboutMenu')
        trigger.setText(terms['menu'])
        trigger.setAccessibleName(terms['menu'])
        trigger.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        popup = QMenu(trigger)
        popup.setObjectName('aboutPopup')
        popup.addAction(terms['about'], self.about_dialog)
        popup.addAction(terms['credits'], self.credits_dialog)
        popup.addAction(terms['license'], self.licence_dialog)
        popup.addAction(terms['disclaimer'], self.disclaimer_dialog)
        trigger.setMenu(popup)
        return trigger

    def about_dialog(self):
        terms = self.t('_about')
        self.show_dialog(terms['about'], [
            (terms['creator'], CREATOR),
            (terms['version'], VERSION),
            ('JatayuOS', terms['project']),
            (terms['license'], 'GPL-3.0-or-later'),
        ])

    def credits_dialog(self):
        terms = self.t('_about')
        self.show_dialog(terms['credits'], [
            (terms['creator'], CREATOR),
            ('JatayuOS', terms['project']),
            (terms['desktop'], 'Qt Widgets · PySide6'),
            (terms['translation'], 'AI4Bharat IndicTrans2'),
            (terms['illustration'], 'OpenAI ImageGen'),
        ])

    def licence_dialog(self):
        terms = self.t('_about')
        dialog, outer = self.reading_dialog(terms['license'])
        summary, details = panel('readingSection', padding=14, gap=6)
        details.addWidget(text('GPL-3.0-or-later', 'readingHeading'))
        details.addWidget(text(terms['licenseSummary'], 'readingBody'))
        details.addWidget(text(terms['artwork'], 'muted'))
        outer.addWidget(summary)
        content = QPlainTextEdit()
        content.setObjectName('licenceText')
        content.setReadOnly(True)
        content.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        content.setPlainText((ROOT / 'LICENSE').read_text(encoding='utf-8'))
        outer.addWidget(content, 1)
        self.add_dialog_close(dialog, outer)
        dialog.resize(670, min(650, self.height()))
        dialog.exec()

    def disclaimer_dialog(self):
        terms = self.t('_about')
        self.show_dialog(terms['disclaimer'], [('', terms['disclaimerBody'])])

    def add_footer(self, layout):
        footer, column = panel('footer', gap=13)
        column.setContentsMargins(30, 38, 30, 31)
        heading = text(f'{self.copy(127)} {self.copy(128)}')
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(heading)
        tagline = text(self.copy(129))
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(tagline)
        links, row = panel(horizontal=True, gap=16)
        row.addStretch()
        for key, url in ((130, PORTAL), (131, RBI), (132, DOT)):
            row.addWidget(self.footer_link(key, url, 'footerLink'))
        row.addStretch()
        column.addWidget(links)
        copyright_line = text(self.copy(133), 'copyright')
        copyright_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(copyright_line)
        layout.addWidget(footer)
        website_bar, bar = panel('websiteBar', padding=10)
        bar.addWidget(self.footer_link(134, WEBSITE, 'websiteLink'),
                      alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(website_bar)

    def footer_link(self, key, url, role):
        link = QPushButton(self.copy(key).replace('&', '&&'))
        link.setProperty('role', role)
        link.setCursor(Qt.CursorShape.PointingHandCursor)
        link.clicked.connect(lambda: self.open_url(url))
        return link

    def page(self, title, intro):
        root, layout = panel('page', padding=30, gap=16)
        notice = self.catalog['_meta'].get('notice')
        if notice:
            layout.addWidget(text(notice, 'muted'))
        layout.addWidget(text(title, 'title'))
        layout.addWidget(text(intro, 'muted'))
        return root, layout

    def reading_dialog(self, title, *, reporting=False):
        dialog = QDialog(self)
        dialog.setObjectName('readingDialog')
        dialog.setWindowTitle(title)
        outer = QVBoxLayout(dialog)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)
        header, banner = panel('scamHeader' if reporting else 'readingHeader',
                               horizontal=True, padding=14, gap=14)
        if not reporting:
            emblem = QLabel()
            emblem.setPixmap(QIcon(str(ICON)).pixmap(40, 40))
            banner.addWidget(emblem)
        banner.addWidget(text(title, 'readingTitle'), 1)
        outer.addWidget(header)
        return dialog, outer

    def add_dialog_close(self, dialog, layout):
        close = QPushButton(self.native('ok'))
        close.setProperty('role', 'dialogClose')
        close.setDefault(True)
        close.clicked.connect(dialog.accept)
        layout.addWidget(close, alignment=Qt.AlignmentFlag.AlignTrailing)

    def show_dialog(self, title, sections, *, reporting=False):
        dialog, outer = self.reading_dialog(title, reporting=reporting)
        body, layout = panel(gap=8)
        body.setMinimumWidth(0)
        for heading, value in sections:
            section, column = panel('readingSection', padding=12, gap=5)
            if heading:
                column.addWidget(text(heading, 'sectionLabel' if reporting else 'readingHeading'))
            if value:
                role = 'creatorName' if value == CREATOR else 'readingBody'
                column.addWidget(text(value, role))
            layout.addWidget(section)
        layout.addStretch()
        reader = scroll_view(body)
        outer.addWidget(reader, 1)
        if reporting:
            row, links = panel(horizontal=True)
            for number in ('1930', '112'):
                links.addWidget(button(number, lambda _, value=number: self.show_phone(value)), 1)
            links.addWidget(button('cybercrime.gov.in', lambda: self.open_url(PORTAL)), 1)
            outer.addWidget(row)
        self.add_dialog_close(dialog, outer)
        width = min(670, self.width() - 48)
        height = body.layout().totalHeightForWidth(width - 56)
        if height < 0:
            height = body.sizeHint().height()
        dialog.resize(width, min(600, max(240, height + (165 if reporting else 134)), self.height()))
        dialog.exec()

    def show_phone(self, number):
        if number not in ('1930', '112'):
            return
        title = f"\u2066{number}\u2069 · {self.copy(94 if number == '1930' else 95).lstrip(' -–')}"
        self.show_dialog(title, [('', self.native('dial').format(number=number))])

    def open_url(self, address):
        if address in OFFICIAL_WEBSITES and not QDesktopServices.openUrl(QUrl(address)):
            message = f"{self.native('browser')}\n{address}"
            self.show_dialog(self.native('windowTitle'), [('', message)])

    def launch(self, name):
        try:
            subprocess.Popen(ACTIONS[name], close_fds=True, start_new_session=True)
        except OSError:
            self.show_dialog(self.native('windowTitle'), [('', self.native('shortcut'))])

    def help_dialog(self, key):
        self.show_dialog(self.native('windowTitle'), [('', self.t('_ui')[key])])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.arrange_navigation()
        for entry in self.grids:
            self.arrange_cards(entry)
        if self.banner_layout is not None:
            self.arrange_banner()

    def arrange_navigation(self):
        if not hasattr(self, 'nav'):
            return
        widths = []
        for control in self.nav.values():
            label = control.findChild(QLabel)
            label.ensurePolished()
            font = label.font()
            font.setBold(True)
            widths.append(QFontMetrics(font).horizontalAdvance(label.text()) + 34)
        fits = sum(widths) + 116 <= self.width()
        for control, natural in zip(self.nav.values(), widths):
            label = control.findChild(QLabel)
            label.setWordWrap(not fits)
            control.setMinimumWidth(natural if fits else 0)

    def arrange_banner(self):
        wide = self.width() >= 1320
        self.banner_layout.setDirection(QBoxLayout.Direction.LeftToRight if wide else QBoxLayout.Direction.TopToBottom)
        self.banner_layout.setStretch(0, int(wide))
        self.banner_layout.setStretch(1, int(wide))

    def arrange_cards(self, entry):
        grid, cards, minimum, columns = entry
        available = self.width() - 76
        count = max(1, min(4, (available + 20) // (minimum + 20)))
        if count == columns:
            return
        while grid.count():
            grid.takeAt(0)
        for index in range(4):
            grid.setColumnStretch(index, int(index < count))
        for index, card in enumerate(cards):
            grid.addWidget(card, index // count, index % count)
        entry[3] = count

    def cards(self, layout, entries, minimum=280):
        grid = QGridLayout()
        grid.setSpacing(20)
        layout.addLayout(grid)
        entry = [grid, entries, minimum, 0]
        self.grids.append(entry)
        self.arrange_cards(entry)

    def dashboard(self):
        root, layout = self.page(self.copy(8), self.copy(9))
        warning, banner = panel('urgent', horizontal=self.width() >= 1320, padding=27, gap=18)
        self.banner_layout = banner
        shadow(warning, '#39dc2626')
        lead, heading = panel(gap=8)
        heading.addWidget(text(self.copy(2), 'urgentTitle'))
        heading.addWidget(text(self.copy(3)))
        banner.addWidget(lead, 1)
        bar, links = panel(horizontal=True, gap=12)
        tiles = (
            (f'☎ 1930 · {self.copy(4)}', lambda: self.show_phone('1930'), 150),
            (f'112 · {self.copy(5)}', lambda: self.show_phone('112'), 145),
            (self.copy(6), lambda: self.go('report'), 178),
        )
        for title, action, minimum in tiles:
            tile = button(title, action, 'emergencyTile')
            tile.setMinimumSize(minimum, 54)
            links.addWidget(tile)
        banner.addWidget(bar, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.arrange_banner()
        layout.insertWidget(0, warning)
        cards = []
        actions = (
            (11, '🔥', 'green', 'amber', lambda: self.launch('firewall')),
            (15, '🔄', 'amber', 'amber', lambda: self.launch('updates')),
            (19, '🔐', 'green', 'green', lambda: self.help_dialog('passwordHelp')),
            (23, '💾', 'green', 'amber', lambda: self.launch('backup')),
            (27, '🎣', 'red', 'red', lambda: self.go('scams')),
            (31, '🔒', 'green', 'green', lambda: self.help_dialog('privacyHelp')),
        )
        for index, icon, accent, tone, action in actions:
            card, column = panel('card', padding=24)
            card.setProperty('accent', accent)
            card.setProperty('rtl', self.layoutDirection() == Qt.LayoutDirection.RightToLeft)
            shadow(card)
            row, top = panel(horizontal=True)
            top.addWidget(icon_tile(icon, accent))
            top.addStretch()
            top.addWidget(pill(self.copy(index - 1), tone), alignment=Qt.AlignmentFlag.AlignVCenter)
            column.addWidget(row)
            column.addWidget(text(self.copy(index), 'cardTitle'))
            column.addWidget(text(self.copy(index + 1), 'muted'))
            column.addStretch()
            column.addWidget(button(self.copy(index + 2), action, 'primary'))
            cards.append(card)
        self.cards(layout, cards)
        layout.addSpacing(30)
        layout.addStretch()
        return root

    def scams(self):
        root, layout = self.page(self.copy(34), self.copy(35))
        cards = []
        ui = self.t('_ui')
        for item in CONTENT['scams']:
            scam = self.t('_scams')[item['id']]
            card, column = panel('card', gap=0)
            shadow(card)
            title = scam['name']
            description = scam['howItWorks']
            header, heading = panel('scamHeader', horizontal=True, padding=18, gap=13)
            heading.addWidget(icon_tile(item['emoji'], 'scam'))
            heading.addWidget(text(title, 'scamTitle'), 1)
            column.addWidget(header)
            body, detail = panel(padding=20)
            detail.addWidget(text(ui['howShort'], 'sectionLabel'))
            detail.addWidget(text(description if len(description) <= 150 else description[:150].rstrip() + '…', 'muted'))
            detail.addWidget(text(ui['targets'], 'sectionLabel'))
            detail.addWidget(text(', '.join(scam['targets']), 'muted'))
            detail.addStretch()
            chips, row = panel(horizontal=True)
            row.addWidget(pill(ui[item['severity']], 'red' if item['severity'] == 'high' else 'amber'))
            more = button(ui['details'], lambda _, name=title, guide=scam: self.scam_dialog(name, guide), 'risk')
            more.setMaximumWidth(210)
            more.setMinimumWidth(105)
            row.addWidget(more)
            row.addStretch(1)
            detail.addWidget(chips)
            column.addWidget(body, 1)
            cards.append(card)
        self.cards(layout, cards, minimum=350)
        layout.addStretch()
        return root

    def scam_dialog(self, title, scam):
        ui = self.t('_ui')
        self.show_dialog(title, [
            (ui['howLong'], scam['howItWorks']),
            (ui['targets'], ', '.join(scam['targets'])),
            (ui['flags'], '\n'.join('• ' + piece for piece in scam['redFlags'])),
            (ui['prevention'], '\n'.join('• ' + piece for piece in scam['prevention'])),
            (ui['action'], scam['action']),
            (ui['numbers'], ''),
        ], reporting=True)

    def bullet_card(self, title, items, icon=None, tone='green'):
        card, layout = panel('card', padding=22)
        if icon:
            card.setProperty('accent', 'top-' + tone)
            layout.addWidget(icon_tile(icon, tone))
            shadow(card)
        layout.addWidget(text(title, 'cardTitle'))
        for item in items:
            layout.addWidget(text('✓  ' + item))
        layout.addStretch()
        return card

    def tips(self):
        root, layout = self.page(self.t('safeTitle'), self.t('safeDescription'))
        groups = ((36, 37, 42), (42, 44, 49), (49, 51, 56), (56, 57, 62),
                  (62, 63, 68), (68, 69, 74), (74, 75, 80), (80, 81, 86))
        cards = []
        for (title, start, stop), icon in zip(groups, ('🔐', '📱', '📞', '🌐', '📧', '📲', '🆔', '👪')):
            heading = self.copy(title)
            if title in (42, 49):
                heading += ' · ' + self.copy(title + 1)
            cards.append(self.bullet_card(heading, [self.copy(i) for i in range(start, stop)], icon))
        cards.insert(3, self.bullet_card(self.t('bankTitle'), [self.t(key) for key in
                     ('bankIntro', 'bankExample', 'bankLookalike', 'bankAction')], '🏦'))
        self.cards(layout, cards)
        layout.addStretch()
        return root

    def checklist(self):
        root, layout = self.page(self.copy(86), self.copy(87))
        progress_text = text('', 'checkProgress')
        progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress = QProgressBar()
        progress.setFixedHeight(10)
        progress.setRange(0, len(self.t('_checklist')))
        progress.setTextVisible(False)
        layout.addWidget(progress_text)
        layout.addWidget(progress)
        card, column = panel('card', padding=25, gap=0)
        shadow(card)

        def update():
            size = len(self.t('_checklist'))
            done = len(self.completed)
            progress.setValue(done)
            progress_text.setText(self.t('_ui')['progress'].format(done=done, total=size,
                                                                    percent=round(100 * done / size)))

        def toggle(index, checked):
            if checked:
                self.completed.add(index)
            else:
                self.completed.discard(index)
            self.settings.setValue('nativeChecklist', json.dumps(sorted(self.completed)))
            self.settings.sync()
            update()

        for index, item in enumerate(self.t('_checklist'), 1):
            if index > 1:
                divider = QFrame()
                divider.setObjectName('checkDivider')
                divider.setFixedHeight(1)
                column.addWidget(divider)
            row = ChecklistRow(item, index in self.completed)
            row.checkbox.toggled.connect(lambda checked, key=index: toggle(key, checked))
            column.addWidget(row)
        layout.addWidget(card)
        layout.addStretch()
        update()
        return root

    def report(self):
        root, layout = self.page(self.copy(89), self.copy(90))
        warning, banner = panel('urgent', padding=14)
        banner.addWidget(text(self.copy(91), 'urgentTitle'))
        banner.addWidget(text(self.copy(92)))
        layout.addWidget(warning)
        row, links = panel(horizontal=True, gap=12)
        finance = self.copy(94).lstrip(' -–')
        emergency = self.copy(95).lstrip(' -–')
        actions = (
            (f"\u20661930\u2069 · {finance}", lambda: self.show_phone('1930'), 'reportPhone'),
            (f"\u2066112\u2069 · {emergency}", lambda: self.show_phone('112'), 'reportPhone'),
            ('cybercrime.gov.in', lambda: self.open_url(PORTAL), 'primary'),
        )
        for label, action, role in actions:
            control = button(label, action, role)
            control.setMinimumHeight(54)
            links.addWidget(control, 1)
        layout.addWidget(row)
        first = [f'\u20661930\u2069 {self.copy(94)}', f'\u2066112\u2069 {self.copy(95)}',
                 f'{self.copy(96)} {self.copy(97)}', self.copy(98), self.copy(99)]
        online = [f'{self.copy(107)} \u2066{self.copy(108)}\u2069'] + [self.copy(i) for i in range(109, 113)]
        self.cards(layout, [self.bullet_card(self.copy(93), first, '📞', 'red'),
                            self.bullet_card(self.copy(100), [self.copy(i) for i in range(101, 106)], '🏦', 'amber'),
                            self.bullet_card(self.copy(106), online, '🌐', 'blue'),
                            self.bullet_card(self.copy(113), [self.copy(i) for i in range(114, 119)], '👮')])
        layout.addWidget(self.bullet_card(self.copy(119), [self.copy(i) for i in range(120, 126)]))
        layout.addStretch()
        return root

    def exercises(self):
        for prefix, topic, aliases in (
            ('Qr', 'payments', 'qr upi payment paise kat gaye पैसे कट गए'),
            ('Bank', 'messages', 'bank link bank.in domain बैंक'),
        ):
            yield prefix, topic, aliases, {
                'title': self.t(f'learn{prefix}Title'),
                'sample': self.t('learnQrMessage') if prefix == 'Qr' else 'yourbank.bank.in.example.com',
                'lesson': self.t('learnQrWarning') if prefix == 'Qr' else (
                    f"{self.t('learnBankWarningLead')} \u2066example.com\u2069. {self.t('learnBankWarningTail')}"),
                'question': self.t(f'learn{prefix}Question'),
                'safe': self.t(f'learn{prefix}Safe'),
                'risky': self.t(f'learn{prefix}Risky'),
                'right': self.t(f'learn{prefix}Correct'),
                'retry': self.t(f'learn{prefix}Retry'),
            }
        for key, topic, aliases in CONTENT['practice']:
            data = self.t('_learn')[key]
            english = self.english['_learn'][key]
            yield key, topic, aliases + ' ' + ' '.join(english.values()), {
                **data, 'question': self.t('learnQuestion'),
                'right': self.t('learnRight') + ' ' + data['lesson'],
                'retry': self.t('learnTryAgain') + ' ' + data['lesson'],
            }

    def exercise_card(self, key, item, index, illustration):
        card, layout = panel('card', padding=20)
        card.setProperty('accent', 'top-blue')
        artwork = QLabel()
        artwork.setPixmap(illustration)
        artwork.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(artwork)
        layout.addWidget(text(item['title'], 'cardTitle'))
        layout.addWidget(text(self.t('learnFictionalAddress' if key == 'Bank' else 'learnFictional'), 'muted'))
        sample = text(item['sample'], 'sample')
        if key == 'Bank':
            sample.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(sample)
        lesson = text(item['lesson'], 'lesson')
        lesson.setVisible(key in self.revealed)

        def reveal():
            if key in self.revealed:
                self.revealed.remove(key)
            else:
                self.revealed.add(key)
            lesson.setVisible(key in self.revealed)

        layout.addWidget(button(self.t('learnReveal'), reveal))
        layout.addWidget(lesson)
        layout.addWidget(text(item['question'], 'cardTitle'))
        feedback = text('')
        choices = {}

        def answer(option):
            self.answers[key] = option
            refresh()

        def refresh():
            selected = self.answers.get(key)
            for option, control in choices.items():
                control.setChecked(option == selected)
            feedback.setVisible(selected is not None)
            if selected:
                feedback.setText(item['right' if selected == 'safe' else 'retry'])
                feedback.setObjectName('right' if selected == 'safe' else 'retry')
                feedback.style().unpolish(feedback)
                feedback.style().polish(feedback)

        for option in (('safe', 'risky') if index % 2 == 0 else ('risky', 'safe')):
            control = button(item[option], lambda _, value=option: answer(value))
            control.setCheckable(True)
            choices[option] = control
            layout.addWidget(control)
        layout.addWidget(feedback)
        layout.addStretch()
        layout.addWidget(button(self.t('learnReport'), lambda: self.go('report')))
        refresh()
        return card

    def practice(self):
        root, layout = self.page(self.t('learnTab'), self.t('learnIntro'))
        controls, row = panel(horizontal=True)
        search = QLineEdit(self.query)
        search.setPlaceholderText(self.t('learnSearch'))
        search.setAccessibleName(self.t('learnSearch'))
        search.setClearButtonEnabled(True)
        search.setMaxLength(200)
        row.addWidget(search, 2)
        picker = light_combo()
        picker.setAccessibleName(self.t('learnCategory'))
        picker.addItem(self.t('learnAll'), '')
        for key, name in TOPICS.items():
            picker.addItem(self.t(name), key)
        picker.setCurrentIndex(picker.findData(self.selected_topic))
        row.addWidget(picker, 1)
        layout.addWidget(controls)
        empty = text(self.t('learnNoResults'), 'muted')
        layout.addWidget(empty)
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)
        illustrations = {
            topic: QPixmap(str(ROOT / 'learn-art' / f'{topic}.png')).scaled(
                190, 106, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            for topic in TOPICS
        }
        results = []
        for index, (key, topic, aliases, item) in enumerate(self.exercises()):
            card = self.exercise_card(key, item, index, illustrations[topic])
            card.setParent(root)
            index_text = normalized(aliases + ' ' + ' '.join(item.values()))
            results.append((topic, index_text, card))

        def apply_filter():
            self.query = search.text()
            self.selected_topic = picker.currentData()
            words = normalized(self.query).split()
            while grid.count():
                grid.takeAt(0)
            count = 0
            for topic, index_text, card in results:
                match = (not self.selected_topic or self.selected_topic == topic) and all(
                    word in index_text for word in words)
                if match:
                    grid.addWidget(card, count // 2, count % 2)
                    count += 1
                card.setVisible(match)
            empty.setVisible(count == 0)

        search.textChanged.connect(apply_filter)
        picker.currentIndexChanged.connect(apply_filter)
        layout.addStretch()
        apply_filter()
        return root


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Jatayu Kavach')
    app.setDesktopFileName('org.jatayu.kavach.standalone')
    window = KavachWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
