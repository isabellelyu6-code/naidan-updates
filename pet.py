"""Milk Egg (奶蛋) Desktop Assistant v2 for Windows."""
from __future__ import annotations
import json, math, os, random, shutil, subprocess, sys, tempfile, threading, time, urllib.parse, urllib.request, webbrowser
from datetime import datetime
from pathlib import Path
import numpy as np
from PySide6.QtCore import QObject, QPoint, QRect, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QImage, QPainter, QPen, QPixmap, QTransform
from PySide6.QtWidgets import QAbstractItemView, QApplication, QCheckBox, QColorDialog, QComboBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, QLabel, QListWidget, QMenu, QMessageBox, QPlainTextEdit, QPushButton, QSlider, QSpinBox, QSystemTrayIcon, QVBoxLayout, QWidget

SCRIPT_ROOT=Path(__file__).resolve().parent; ROOT=Path(getattr(sys,"_MEIPASS",SCRIPT_ROOT)); ASSETS=ROOT/"assets"
APP_VERSION="2.5.0"
# A GitHub Releases API endpoint will be inserted after the user's publishing
# repository is connected. pet_data.json can override it with update_api_url.
UPDATE_API_URL="https://api.github.com/repos/isabellelyu6-code/naidan-updates/releases/latest"
if getattr(sys,"frozen",False):
    DATA_DIR=Path(os.environ.get("APPDATA",Path.home()))/"奶蛋"; DATA_DIR.mkdir(parents=True,exist_ok=True); DATA=DATA_DIR/"pet_data.json"
else: DATA=SCRIPT_ROOT/"pet_data.json"
DEFAULT={"city":"London","quiet":False,"speak":False,"voice":"","voice_rate":0,"voice_language":"zh","notes":[],"pet_scale":70,"width_scale":100,"height_scale":100,"opacity":100,"layer_mode":"top","position_locked":False,"click_through":False,"click_action":"all","chatter":"low","screen_mode":"current","settings_v2_2":True,"saved_timers":[],"stopwatch_started":None,"auto_update":True,"update_api_url":"","skin_mode":"default","skin_color":"#f6c94f","costume_mode":"none","costume":"none","costume_interval":300,"deleted_links":[],"link_modes":{"GO":"desktop","Moodle":"desktop"},"links":{"ChatGPT":"https://chatgpt.com/","小红书":"https://www.xiaohongshu.com/","Portico":"https://evision.ucl.ac.uk/urd/sits.urd/run/siw_lgn","Gmail":"https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox","timetable":"https://timetable.ucl.ac.uk/my-timetable","GO":"https://ucl.ombiel.co.uk/campusm/home#menu","Moodle":"https://moodle.ucl.ac.uk/my/"}}
LEGACY_LINKS={"Imperial Blackboard","My Imperial","Imperial Outlook","YouTube","Spotify","Portical"}

COSTUMES={
    "none":"原味奶蛋","angel":"天使奶蛋","demon":"恶魔奶蛋",
    "aries":"白羊座","taurus":"金牛座","gemini":"双子座","cancer":"巨蟹座","leo":"狮子座","virgo":"处女座","libra":"天秤座","scorpio":"天蝎座","sagittarius":"射手座","capricorn":"摩羯座","aquarius":"水瓶座","pisces":"双鱼座",
    "rat":"生肖鼠","ox":"生肖牛","tiger":"生肖虎","rabbit":"生肖兔","dragon":"生肖龙","snake":"生肖蛇","horse":"生肖马","goat":"生肖羊","monkey":"生肖猴","rooster":"生肖鸡","dog":"生肖狗","pig":"生肖猪",
}
COSTUME_CATEGORIES={
    "原始与特殊":["none","angel","demon"],
    "十二生肖":["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"],
    "十二星座":["aries","taurus","gemini","cancer","leo","virgo","libra","scorpio","sagittarius","capricorn","aquarius","pisces"],
}
COSTUME_LINES={
    "none":["今天不换衣服，我就是最经典的原味奶蛋！","原味奶蛋也超级可爱呀。"],
    "angel":["我是天使奶蛋，给你送来一点好运！","天使奶蛋来守护你啦。"],
    "demon":["我是恶魔奶蛋，正在策划一个可爱的坏主意！","小恶魔登场，不许被我萌到哦。"],
    "aries":["我是白羊座奶蛋，今天也要勇敢向前冲！"],"taurus":["我是金牛座奶蛋，稳稳地陪着你。"],"gemini":["我是双子座奶蛋，猜猜现在是哪一个我？"],"cancer":["我是巨蟹座奶蛋，把温柔都留给你。"],"leo":["我是狮子座奶蛋，今天也闪闪发光！"],"virgo":["我是处女座奶蛋，把今天整理得漂漂亮亮。"],"libra":["我是天秤座奶蛋，可爱当然要刚刚好。"],"scorpio":["我是天蝎座奶蛋，神秘一下也很可爱。"],"sagittarius":["我是射手座奶蛋，向快乐出发！"],"capricorn":["我是摩羯座奶蛋，认真陪你完成今天。"],"aquarius":["我是水瓶座奶蛋，给你倒一杯好心情。"],"pisces":["我是双鱼座奶蛋，送你一颗软绵绵的梦。"],
    "rat":["我是生肖鼠奶蛋，机灵的小好运来啦！"],"ox":["我是生肖牛奶蛋，今天也稳稳加油。"],"tiger":["我是生肖虎奶蛋，嗷呜——但一点也不凶。"],"rabbit":["我是生肖兔奶蛋，送你一根好运胡萝卜！"],"dragon":["我是生肖龙奶蛋，今天一定龙运当头！"],"snake":["我是生肖蛇奶蛋，悄悄把好运绕给你。"],"horse":["我是生肖马奶蛋，马上就有好事发生！"],"goat":["我是生肖羊奶蛋，软绵绵地陪你。"],"monkey":["我是生肖猴奶蛋，今天也要机灵又开心。"],"rooster":["我是生肖鸡奶蛋，咕咕咕，起床啦！"],"dog":["我是生肖狗奶蛋，会一直忠实地陪着你。"],"pig":["我是生肖猪奶蛋，圆滚滚的福气来啦！"],
}
JAPANESE_LINES={
    "今天也要照顾好自己呀。":"今日も自分を大切にしてね。","你现在在忙什么呢？":"今、何をしているの？","要记得喝水哦。":"お水を飲むのを忘れないでね。","累了就休息一下吧。":"疲れたら少し休もうね。","奶蛋在这里陪你。":"ナイダンはここでそばにいるよ。",
    "今天也辛苦啦，摸摸你。":"今日もお疲れさま。よしよし。","我偷偷给你存了一点好运。":"君のために幸運を少し貯めておいたよ。","先伸个懒腰，再继续努力吧。":"ちょっと伸びをしてから、また頑張ろう。","奶蛋刚刚是不是又可爱了一点？":"ナイダン、さっきよりもっと可愛くなったかな？","别担心，慢慢来就好。":"心配しないで、ゆっくりでいいよ。","完成一件事就很了不起啦！":"一つできただけでもすごいよ！","给你一个软乎乎的抱抱。":"ふわふわのハグをあげるね。",
    "换装完成！请欣赏全新的奶蛋！":"お着替え完了！新しいナイダンを見てね。","不许眨眼，我又变得更可爱啦。":"まばたきしないで、もっと可愛くなったよ。","你好呀，我是奶蛋。":"こんにちは、ナイダンだよ。",
}

def load_data():
    data=json.loads(json.dumps(DEFAULT))
    try:
        saved=json.loads(DATA.read_text(encoding="utf-8")); data.update({k:v for k,v in saved.items() if k!="links"})
        if not saved.get("settings_v2_2"):
            if int(saved.get("pet_scale",100))==100:data["pet_scale"]=70
            data["settings_v2_2"]=True
        deleted={str(name) for name in saved.get("deleted_links",[]) if str(name)}
        data["links"]={k:v for k,v in data["links"].items() if k not in deleted}
        data["links"].update({k:v for k,v in saved.get("links",{}).items() if k not in LEGACY_LINKS and k not in deleted})
    except (OSError,ValueError,TypeError): pass
    return data

class NotesWindow(QWidget):
    def __init__(self,pet):
        super().__init__(); self.pet=pet; self.setWindowTitle("奶蛋的小本本"); self.resize(420,330); layout=QVBoxLayout(self)
        self.editor=QPlainTextEdit("\n\n".join(pet.data["notes"])); self.editor.setPlaceholderText("在这里写点什么……不同笔记请空一行。")
        save=QPushButton("保存"); save.clicked.connect(self.save); layout.addWidget(self.editor); layout.addWidget(save)
    def save(self):
        self.pet.data["notes"]=[x.strip() for x in self.editor.toPlainText().split("\n\n") if x.strip()]; self.pet.save_data(); self.pet.say("记好啦！"); self.close()

class ShortcutsWindow(QWidget):
    def __init__(self,pet):
        super().__init__();self.pet=pet;self.setWindowTitle("管理快捷入口");self.resize(430,390)
        layout=QVBoxLayout(self);hint=QLabel("选中入口后可以编辑或删除；拖动条目可以调整右键菜单中的顺序。")
        hint.setWordWrap(True);layout.addWidget(hint)
        self.items=QListWidget();self.items.setDragDropMode(QAbstractItemView.InternalMove);self.items.setDefaultDropAction(Qt.MoveAction)
        self.items.model().rowsMoved.connect(self.save_order);self.items.itemDoubleClicked.connect(lambda item:self.edit_selected());layout.addWidget(self.items,1)
        row=QHBoxLayout();add=QPushButton("添加");edit_button=QPushButton("编辑");delete=QPushButton("删除");close=QPushButton("完成")
        add.clicked.connect(self.add);edit_button.clicked.connect(self.edit_selected);delete.clicked.connect(self.delete_selected);close.clicked.connect(self.close)
        row.addWidget(add);row.addWidget(edit_button);row.addWidget(delete);row.addStretch();row.addWidget(close);layout.addLayout(row);self.refresh()
    def refresh(self,select_name=None):
        self.items.blockSignals(True);self.items.clear()
        for name,url in self.pet.data["links"].items():
            mode="优先打开桌面快捷方式" if self.pet.data.get("link_modes",{}).get(name)=="desktop" else "打开网页"
            self.items.addItem(f"{name}\n{url}\n{mode}")
        self.items.blockSignals(False)
        if select_name:
            for index in range(self.items.count()):
                if self.item_name(index)==select_name:self.items.setCurrentRow(index);break
    def item_name(self,index):return self.items.item(index).text().split("\n",1)[0] if self.items.item(index) else ""
    def selected_name(self):return self.item_name(self.items.currentRow()) if self.items.currentRow()>=0 else ""
    def add(self):
        before=set(self.pet.data["links"]);self.pet.add_link();created=next((x for x in self.pet.data["links"] if x not in before),None);self.refresh(created)
    def edit_selected(self):
        name=self.selected_name()
        if not name:QMessageBox.information(self,"管理快捷入口","请先选择一个入口。");return
        self.pet.edit_link(name);self.refresh()
    def delete_selected(self):
        name=self.selected_name()
        if not name:QMessageBox.information(self,"管理快捷入口","请先选择一个入口。");return
        self.pet.delete_link(name);self.refresh()
    def save_order(self,*args):
        ordered={}
        for index in range(self.items.count()):
            name=self.item_name(index)
            if name in self.pet.data["links"]:ordered[name]=self.pet.data["links"][name]
        if len(ordered)==len(self.pet.data["links"]):self.pet.data["links"]=ordered;self.pet.save_data()

class SizeWindow(QWidget):
    def __init__(self,pet):
        super().__init__(); self.pet=pet; self.setWindowTitle("奶蛋外观尺寸"); self.setFixedWidth(360); layout=QVBoxLayout(self)
        layout.addWidget(QLabel("拖动时会实时预览；横向和纵向可以独立压缩。"))
        self.sliders={}
        for text,key,low,high in (("整体大小","pet_scale",50,160),("横向宽度","width_scale",50,150),("纵向高度","height_scale",50,150)):
            row=QHBoxLayout(); label=QLabel(text); value=QLabel(); value.setFixedWidth(45)
            slider=QSlider(Qt.Horizontal); slider.setRange(low,high); slider.setValue(int(pet.data.get(key,100))); slider.setTickInterval(10)
            slider.valueChanged.connect(lambda v,k=key,l=value:self.changed(k,v,l)); value.setText(f"{slider.value()}%")
            row.addWidget(label); row.addWidget(slider,1); row.addWidget(value); layout.addLayout(row); self.sliders[key]=slider
        reset=QPushButton("恢复默认比例"); reset.clicked.connect(self.reset); layout.addWidget(reset)
    def changed(self,key,value,label):
        label.setText(f"{value}%"); self.pet.data[key]=value; self.pet.update_window_size(); self.pet.update(); self.pet.save_data()
    def reset(self):
        self.sliders["pet_scale"].setValue(70); self.sliders["width_scale"].setValue(100); self.sliders["height_scale"].setValue(100)

class SettingsWindow(QWidget):
    def __init__(self,pet):
        super().__init__(); self.pet=pet; self.setWindowTitle("奶蛋设置中心"); self.setMinimumWidth(430); layout=QVBoxLayout(self)
        appearance=QGroupBox("外观"); form=QFormLayout(appearance); self.sliders={}
        for text,key,low,high in (("整体大小","pet_scale",50,160),("横向宽度","width_scale",50,150),("纵向高度","height_scale",50,150),("透明度","opacity",40,100)):
            row=QHBoxLayout(); slider=QSlider(Qt.Horizontal); slider.setRange(low,high); slider.setValue(int(pet.data.get(key,70 if key=="pet_scale" else 100))); value=QLabel(f"{slider.value()}%"); value.setFixedWidth(45)
            slider.valueChanged.connect(lambda v,k=key,l=value:self.slider_changed(k,v,l)); row.addWidget(slider);row.addWidget(value);form.addRow(text,row);self.sliders[key]=slider
        self.layer=QComboBox();self.layer.addItems(["始终置顶","普通窗口层级","置于其他窗口下方"]);self.layer.setCurrentIndex({"top":0,"normal":1,"bottom":2}.get(pet.data.get("layer_mode"),0));self.layer.currentIndexChanged.connect(self.layer_changed);form.addRow("奶蛋图层",self.layer)
        color_row=QHBoxLayout();self.color_mode=QComboBox();self.color_mode.addItems(["默认黄色","自选肤色","彩虹平滑轮换"]);self.color_mode.setCurrentIndex({"default":0,"custom":1,"rainbow":2}.get(pet.data.get("skin_mode"),0));self.color_mode.currentIndexChanged.connect(self.color_mode_changed);pick=QPushButton("选择颜色…");pick.clicked.connect(self.pick_color);color_row.addWidget(self.color_mode);color_row.addWidget(pick);form.addRow("身体颜色",color_row)
        layout.addWidget(appearance)
        behaviour=QGroupBox("活动方式"); bform=QFormLayout(behaviour)
        self.quiet=QCheckBox("固定在原地，但仍会做表情和说话");self.quiet.setChecked(bool(pet.data.get("quiet")));self.quiet.toggled.connect(pet.set_quiet);bform.addRow("安静奶蛋",self.quiet)
        self.locked=QCheckBox("禁止拖动奶蛋");self.locked.setChecked(bool(pet.data.get("position_locked")));self.locked.toggled.connect(lambda v:self.set_value("position_locked",v));bform.addRow("位置锁定",self.locked)
        self.clickthrough=QCheckBox("鼠标点击穿过奶蛋（从托盘关闭）");self.clickthrough.setChecked(bool(pet.data.get("click_through")));self.clickthrough.toggled.connect(pet.set_click_through);bform.addRow("点击穿透",self.clickthrough)
        self.click_action=QComboBox();self.click_action.addItems(["不触发新动作","只随机表情","随机表情和动作","表情、动作和装扮全部随机"]);self.click_action.setCurrentIndex({"none":0,"expression":1,"expression_action":2,"all":3}.get(pet.data.get("click_action","all"),3));self.click_action.currentIndexChanged.connect(lambda i:self.set_value("click_action",("none","expression","expression_action","all")[i]));bform.addRow("单击奶蛋",self.click_action)
        self.chatter=QComboBox();self.chatter.addItems(["关闭","低","中","高"]);self.chatter.setCurrentIndex({"off":0,"low":1,"medium":2,"high":3}.get(pet.data.get("chatter"),1));self.chatter.currentIndexChanged.connect(self.chatter_changed);bform.addRow("主动说话频率",self.chatter)
        self.screen=QComboBox();self.screen.addItems(["只在当前显示器","允许跨显示器"]);self.screen.setCurrentIndex(0 if pet.data.get("screen_mode","current")=="current" else 1);self.screen.currentIndexChanged.connect(lambda i:self.set_value("screen_mode","current" if i==0 else "all"));bform.addRow("活动范围",self.screen)
        layout.addWidget(behaviour)
        costume=QGroupBox("装扮");cform=QFormLayout(costume)
        self.costume_mode=QComboBox();self.costume_mode.addItems(["保持原味","永远保持原始奶蛋","固定装扮","随机轮换"]);self.costume_mode.setCurrentIndex({"none":0,"locked_original":1,"fixed":2,"random":3}.get(pet.data.get("costume_mode"),0));self.costume_mode.currentIndexChanged.connect(self.costume_mode_changed);cform.addRow("换装方式",self.costume_mode)
        self.costume_category=QComboBox();self.costume_category.addItems(list(COSTUME_CATEGORIES));self.costume_category.currentTextChanged.connect(self.costume_category_changed);cform.addRow("装扮类别",self.costume_category)
        self.costume=QComboBox();self.costume.currentTextChanged.connect(self.costume_changed);cform.addRow("当前装扮",self.costume)
        current_key=pet.data.get("costume","none");category=next((c for c,keys in COSTUME_CATEGORIES.items() if current_key in keys),"原始与特殊");self.costume_category.setCurrentText(category);self.costume_category_changed(category);self.costume.setCurrentText(COSTUMES.get(current_key,COSTUMES["none"]))
        layout.addWidget(costume)
        voice=QGroupBox("语音");vform=QFormLayout(voice)
        self.speech=QCheckBox("开启语音播报");self.speech.setChecked(bool(pet.data.get("speak")));self.speech.toggled.connect(lambda v:self.set_value("speak",v));vform.addRow(self.speech)
        self.voice=QComboBox(); voices=pet.available_voices();self.voice.addItems(["系统默认"]+voices);saved=pet.data.get("voice","");self.voice.setCurrentText(saved if saved in voices else "系统默认");self.voice.currentTextChanged.connect(lambda v:self.set_value("voice","" if v=="系统默认" else v));vform.addRow("声音",self.voice)
        self.voice_language=QComboBox();self.voice_language.addItems(["中文","日语（气泡仍为中文）"]);self.voice_language.setCurrentIndex(1 if pet.data.get("voice_language")=="ja" else 0);self.voice_language.currentIndexChanged.connect(lambda i:self.set_value("voice_language","ja" if i else "zh"));vform.addRow("播报语言",self.voice_language)
        self.rate=QSpinBox();self.rate.setRange(-5,5);self.rate.setValue(int(pet.data.get("voice_rate",0)));self.rate.valueChanged.connect(lambda v:self.set_value("voice_rate",v));vform.addRow("语速",self.rate)
        preview=QPushButton("试听声音");preview.clicked.connect(lambda:pet.speak_text("你好呀，我是奶蛋。"));vform.addRow(preview);layout.addWidget(voice)
        row=QHBoxLayout();reset=QPushButton("恢复默认外观");reset.clicked.connect(self.reset_appearance);close=QPushButton("完成");close.clicked.connect(self.close);row.addWidget(reset);row.addStretch();row.addWidget(close);layout.addLayout(row)
    def set_value(self,key,value):self.pet.data[key]=value;self.pet.save_data()
    def slider_changed(self,key,value,label):
        label.setText(f"{value}%");self.pet.data[key]=value
        if key=="opacity":self.pet.setWindowOpacity(value/100)
        else:self.pet.update_window_size();self.pet.update()
        self.pet.save_data()
    def layer_changed(self,index):self.pet.set_layer_mode(("top","normal","bottom")[index])
    def color_mode_changed(self,index):self.pet.set_skin_mode(("default","custom","rainbow")[index])
    def pick_color(self):
        color=QColorDialog.getColor(QColor(self.pet.data.get("skin_color","#f6c94f")),self,"选择奶蛋肤色")
        if color.isValid():self.pet.data["skin_color"]=color.name();self.pet.set_skin_mode("custom");self.color_mode.setCurrentIndex(1)
    def costume_mode_changed(self,index):self.pet.set_costume_mode(("none","locked_original","fixed","random")[index])
    def costume_category_changed(self,category):
        current=self.costume.currentText();self.costume.blockSignals(True);self.costume.clear();self.costume.addItems([COSTUMES[k] for k in COSTUME_CATEGORIES.get(category,[])]);self.costume.blockSignals(False)
        if current in [self.costume.itemText(i) for i in range(self.costume.count())]:self.costume.setCurrentText(current)
    def costume_changed(self,label):
        key=next((k for k,v in COSTUMES.items() if v==label),"none");self.pet.set_costume(key,announce=False)
    def chatter_changed(self,index):self.pet.data["chatter"]=("off","low","medium","high")[index];self.pet.schedule_chatter();self.pet.save_data()
    def reset_appearance(self):
        self.sliders["pet_scale"].setValue(70);self.sliders["width_scale"].setValue(100);self.sliders["height_scale"].setValue(100);self.sliders["opacity"].setValue(100);self.layer.setCurrentIndex(0)

class TimerWindow(QWidget):
    def __init__(self,pet):
        super().__init__(); self.pet=pet; self.setWindowTitle("奶蛋计时器"); self.setFixedWidth(360); layout=QVBoxLayout(self)
        self.status=QLabel("没有正在进行的计时"); self.status.setAlignment(Qt.AlignCenter); self.status.setStyleSheet("font-size: 25px; font-weight: 600; padding: 14px; background: #fff7dc; border: 2px solid #efb83f; border-radius: 14px;"); layout.addWidget(self.status)
        grid=QGridLayout()
        for i,(text,mins) in enumerate((("25 分钟专注",25),("50 分钟专注",50),("5 分钟休息",5))):
            button=QPushButton(text); button.clicked.connect(lambda checked=False,m=mins,t=text:self.start_countdown(m,t)); grid.addWidget(button,i//2,i%2)
        custom=QPushButton("自定义倒计时"); custom.clicked.connect(self.custom); grid.addWidget(custom,1,1)
        stopwatch=QPushButton("开始/结束正计时"); stopwatch.clicked.connect(self.toggle_stopwatch); grid.addWidget(stopwatch,2,0)
        stop=QPushButton("停止全部计时"); stop.clicked.connect(self.stop_all); grid.addWidget(stop,2,1); layout.addLayout(grid)
        hint=QLabel("关闭窗口不会停止计时；时间会持续显示在奶蛋头顶。可再次从右键菜单打开。")
        hint.setWordWrap(True); hint.setStyleSheet("color:#666; font-size:11px;"); layout.addWidget(hint)
        self.refresh_timer=QTimer(self); self.refresh_timer.setInterval(250); self.refresh_timer.timeout.connect(self.refresh); self.refresh_timer.start(); self.refresh()
    def start_countdown(self,minutes,label): self.pet.add_timer(minutes,label+"结束啦！"); self.refresh()
    def custom(self): self.pet.custom_timer(False); self.refresh()
    def toggle_stopwatch(self): self.pet.toggle_stopwatch(); self.refresh()
    def stop_all(self):
        self.pet.timers.clear(); self.pet.stopwatch_started=None; self.pet.save_timer_state(); self.pet.say("所有计时都停止啦。","happy"); self.refresh()
    def refresh(self):
        text=self.pet.active_timer_text(multiline=True); self.status.setText(text or "没有正在进行的计时")

class UpdateSignals(QObject):
    checked=Signal(object)
    downloaded=Signal(object)

def version_key(text):
    cleaned=str(text).strip().lower().lstrip("v"); parts=[]
    for item in cleaned.split("."):
        digits="".join(ch for ch in item if ch.isdigit()); parts.append(int(digits or 0))
    return tuple((parts+[0,0,0])[:3])

class FuzzyPet(QWidget):
    def __init__(self):
        super().__init__(); self.data=load_data(); self.setWindowTitle("奶蛋桌面助手 v2")
        self.setWindowFlags(Qt.Window|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint); self.setAttribute(Qt.WA_TranslucentBackground); self.setWindowIcon(QIcon(str(ASSETS/"奶蛋.ico"))); self.setFixedSize(330,350)
        self.frames={}
        for name in ("idle","step","heart","angel","roll","rest"):
            p=QPixmap(str(ASSETS/f"{name}.png"))
            if p.isNull(): raise FileNotFoundError(ASSETS/f"{name}.png")
            self.frames[name]=p
        self.costume_frames={}
        self.costume_body_boxes={}
        self.base_body_box=self.yellow_body_box(self.frames["idle"])
        for name in COSTUMES:
            if name=="none":continue
            p=QPixmap(str(ASSETS/"costumes"/f"{name}.png"))
            if p.isNull() and name=="angel":p=self.frames["angel"]
            if not p.isNull():self.costume_frames[name]=p;self.costume_body_boxes[name]=self.yellow_body_box(p)
        self.tint_cache={};self.current_costume=str(self.data.get("costume","none"));self.next_costume_change=time.monotonic()+10
        self.walking=False; self.paused=bool(self.data.get("quiet")); self.move_dx=random.choice((-2,0,2)); self.move_dy=random.choice((-2,0,2)); self.dragging=False; self.drag_offset=QPoint(); self.press_global=QPoint(); self.press_time=0.0
        self.tiny_mode=False; self.normal_pos=QPoint()
        self.last_interaction=time.monotonic(); self.next_decision=time.monotonic()+2; self.next_chatter=time.monotonic()+60; self.expression="normal"; self.expression_until=0.; self.hop_started=0.; self.roll_speed=0.; self.roll_angle=0.; self.roll_spin_speed=0.; self.rolling_until=0.; self.bubble=""; self.bubble_until=0.
        wall=time.time(); self.timers=[]
        for item in self.data.get("saved_timers",[]):
            try:
                deadline=float(item["deadline"]); label=str(item["label"])
                if deadline>wall:self.timers.append((deadline,label))
            except (KeyError,TypeError,ValueError):pass
        try:self.stopwatch_started=float(self.data["stopwatch_started"]) if self.data.get("stopwatch_started") else None
        except (TypeError,ValueError):self.stopwatch_started=None
        self.notes_window=None; self.update_signals=UpdateSignals(); self.update_signals.checked.connect(self.update_check_finished); self.update_signals.downloaded.connect(self.update_download_finished); self.update_info=None; self.update_busy=False
        self.record_watch_started=0.; self.record_candidate=None; self.record_size=-1; self.record_stable=0; self.size_window=None; self.settings_window=None; self.timer_window=None
        self.apply_window_mode(False);self.setWindowOpacity(float(self.data.get("opacity",100))/100);self.schedule_chatter()
        self.update_window_size(); b=QApplication.primaryScreen().availableGeometry(); self.move(b.right()-self.width()-25,b.bottom()-self.height()+5)
        self.timer=QTimer(self); self.timer.setInterval(40); self.timer.timeout.connect(self.tick); self.timer.start()
        if self.data.get("auto_update",True): QTimer.singleShot(3500,lambda:self.check_for_updates(False))
    def save_data(self):
        try: DATA.write_text(json.dumps(self.data,ensure_ascii=False,indent=2),encoding="utf-8")
        except OSError: pass
    def schedule_chatter(self):
        ranges={"off":(86400,86400),"low":(180,360),"medium":(90,180),"high":(35,80)};lo,hi=ranges.get(self.data.get("chatter","low"),(180,360));self.next_chatter=time.monotonic()+random.uniform(lo,hi)
    def set_skin_mode(self,mode):
        self.data["skin_mode"]=mode;self.tint_cache.clear();self.save_data();self.update()
    def set_costume_mode(self,mode):
        self.data["costume_mode"]=mode
        if mode in ("none","locked_original"):self.set_costume("none",announce=False)
        elif mode=="random":self.random_costume()
        else:self.set_costume(self.data.get("costume","none"),announce=False)
        self.save_data();self.update()
    def set_costume(self,name,announce=True):
        if name not in COSTUMES:name="none"
        self.current_costume=name;self.data["costume"]=name;self.save_data();self.next_costume_change=time.monotonic()+max(60,int(self.data.get("costume_interval",300)))
        if announce:
            line=random.choice(COSTUME_LINES.get(name,[f"我是{COSTUMES[name]}！"]));self.say(line,"happy",6,speech_text=self.japanese_costume_line(name,line))
        self.update()
    def random_costume(self):
        choices=list(COSTUMES);choices.remove(self.current_costume if self.current_costume in choices else "none")
        self.set_costume(random.choice(choices),announce=True)
    def japanese_costume_line(self,name,fallback):
        if self.data.get("voice_language")!="ja":return fallback
        label=COSTUMES.get(name,"ナイダン");translations={"none":"いつものナイダンだよ。","angel":"天使のナイダンだよ。君を守りに来たよ！","demon":"小悪魔ナイダンだよ。かわいいいたずらを考え中！"}
        return translations.get(name,f"今は{label}のナイダンだよ。")
    def colored_frame(self,key,source):
        mode=self.data.get("skin_mode","default")
        if mode=="default":return source
        if mode=="rainbow":target=QColor.fromHsv(int((time.monotonic()*24)%360),185,245)
        else:target=QColor(self.data.get("skin_color","#f6c94f"))
        cache_key=(key,target.hue()//12,target.saturation()//16,target.value()//16)
        if cache_key in self.tint_cache:return self.tint_cache[cache_key]
        image=source.toImage().convertToFormat(QImage.Format_RGBA8888)
        raw=np.frombuffer(image.bits(),dtype=np.uint8).reshape(image.height(),image.bytesPerLine())[:,:image.width()*4].reshape(image.height(),image.width(),4)
        r=raw[:,:,0].astype(np.int16);g=raw[:,:,1].astype(np.int16);b=raw[:,:,2].astype(np.int16);a=raw[:,:,3]
        mask=(a>10)&(r>145)&(g>95)&(b<175)&(r*100>g*102)&(g*100>b*112)&((r-g)<105)
        shade=np.clip(np.maximum(np.maximum(r,g),b)/220.0,.42,1.25)
        for channel,value in enumerate((target.red(),target.green(),target.blue())):
            layer=np.clip(value*shade,0,255).astype(np.uint8);raw[:,:,channel][mask]=layer[mask]
        result=QPixmap.fromImage(image)
        self.tint_cache[cache_key]=result
        return result
    def yellow_body_box(self,pixmap):
        image=pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)
        raw=np.frombuffer(image.bits(),dtype=np.uint8).reshape(image.height(),image.bytesPerLine())[:,:image.width()*4].reshape(image.height(),image.width(),4)
        r=raw[:,:,0].astype(np.int16);g=raw[:,:,1].astype(np.int16);b=raw[:,:,2].astype(np.int16);a=raw[:,:,3]
        mask=(a>30)&(r>145)&(g>90)&(b<180)&((r-b)>30)&((g-b)>8)
        ys,xs=np.where(mask)
        if not len(xs):return QRect(0,0,pixmap.width(),pixmap.height())
        return QRect(int(xs.min()),int(ys.min()),int(xs.max()-xs.min()+1),int(ys.max()-ys.min()+1))
    def available_voices(self):
        if os.name!="nt":return []
        command='[Console]::OutputEncoding=[Text.Encoding]::UTF8; Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices() | ForEach-Object {$_.VoiceInfo.Name}'
        try:
            result=subprocess.run(["powershell","-NoProfile","-Command",command],capture_output=True,text=True,encoding="utf-8",timeout=5,creationflags=0x08000000)
            return [x.strip() for x in result.stdout.splitlines() if x.strip()]
        except (OSError,subprocess.SubprocessError):return []
    def speak_text(self,text):
        if os.name!="nt":return
        safe=text.replace("'","''");voice=str(self.data.get("voice","")).replace("'","''");rate=max(-5,min(5,int(self.data.get("voice_rate",0))))
        select=f"$s.SelectVoice('{voice}');" if voice else ""
        command=f"Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; {select}$s.Rate={rate}; $s.Speak('{safe}')"
        try:subprocess.Popen(["powershell","-NoProfile","-Command",command],creationflags=0x08000000)
        except OSError:pass
    def apply_window_mode(self,show_again=True):
        was_visible=self.isVisible();flags=Qt.Window|Qt.FramelessWindowHint;mode=self.data.get("layer_mode","top")
        if mode=="top":flags|=Qt.WindowStaysOnTopHint
        elif mode=="bottom":flags|=Qt.WindowStaysOnBottomHint
        self.setWindowFlags(flags);self.setAttribute(Qt.WA_TranslucentBackground);self.setAttribute(Qt.WA_TransparentForMouseEvents,bool(self.data.get("click_through")))
        if show_again and was_visible:self.show()
    def set_layer_mode(self,mode):self.data["layer_mode"]=mode;self.save_data();self.apply_window_mode();self.say("图层设置已更新。","happy",4)
    def set_click_through(self,enabled):
        self.data["click_through"]=bool(enabled);self.save_data();self.setAttribute(Qt.WA_TransparentForMouseEvents,bool(enabled))
        if getattr(self,"tray_clickthrough",None):self.tray_clickthrough.setChecked(bool(enabled))
        self.say("已开启点击穿透，可从托盘关闭。" if enabled else "已关闭点击穿透。","happy",5)
    def set_quiet(self,enabled):
        self.paused=bool(enabled);self.data["quiet"]=self.paused;self.walking=False;self.rolling_until=0.;self.roll_speed=0.;self.save_data();self.say("安静奶蛋会留在这里陪你。" if self.paused else "奶蛋又可以四处活动啦。","happy",5)
        if getattr(self,"tray_quiet",None):self.tray_quiet.setChecked(self.paused)
    def save_timer_state(self):
        self.data["saved_timers"]=[{"deadline":deadline,"label":label} for deadline,label in self.timers]
        self.data["stopwatch_started"]=self.stopwatch_started; self.save_data()
    def bounds(self):
        if self.data.get("screen_mode","current")=="all":
            screens=QApplication.screens(); left=min(s.geometry().left() for s in screens);top=min(s.geometry().top() for s in screens);right=max(s.geometry().right() for s in screens);bottom=max(s.geometry().bottom() for s in screens);return QRect(left,top,right-left+1,bottom-top+1)
        s=QApplication.screenAt(self.frameGeometry().center()); return (s or QApplication.primaryScreen()).availableGeometry()
    def render_size(self,key="idle"):
        overall=float(self.data.get("pet_scale",100))/100; wide=float(self.data.get("width_scale",100))/100; tall=float(self.data.get("height_scale",100))/100
        source=self.frames[key]; natural_w=235*source.width()/source.height()
        return max(24,round(natural_w*overall*wide)),max(24,round(235*overall*tall))
    def update_window_size(self):
        if self.tiny_mode:return
        old_bottom=self.y()+self.height(); old_center=self.x()+self.width()//2; w,h=self.render_size()
        self.setFixedSize(max(330,w+50),max(350,h+105)); self.move(old_center-self.width()//2,old_bottom-self.height())
    def tick(self):
        now=time.monotonic(); wall=time.time(); timers_changed=False
        if self.rolling_until and now>=self.rolling_until:
            self.rolling_until=0.;self.roll_speed=0.;self.roll_spin_speed=0.;self.roll_angle=0.
        for deadline,message in self.timers[:]:
            if wall>=deadline:
                self.timers.remove((deadline,message)); timers_changed=True; QApplication.beep(); QTimer.singleShot(350,QApplication.beep); QTimer.singleShot(700,QApplication.beep); self.say(message,"happy",8); QMessageBox.information(None,"奶蛋提醒你",message)
        if timers_changed:self.save_timer_state()
        if now>=self.next_chatter and self.data.get("chatter","low")!="off":
            lines=[("今天也要照顾好自己呀。","happy"),("你现在在忙什么呢？","shock"),("要记得喝水哦。","happy"),("累了就休息一下吧。","shy"),("奶蛋在这里陪你。","heart"),("今天也辛苦啦，摸摸你。","heart"),("我偷偷给你存了一点好运。","shy"),("先伸个懒腰，再继续努力吧。","happy"),("奶蛋刚刚是不是又可爱了一点？","shy"),("别担心，慢慢来就好。","happy"),("完成一件事就很了不起啦！","happy"),("给你一个软乎乎的抱抱。","heart")]
            text,face=random.choice(lines);self.say(text,face,5);self.schedule_chatter()
        if self.data.get("costume_mode")=="random" and now>=self.next_costume_change:self.random_costume()
        if now>=self.expression_until and self.expression!="sleep": self.expression="normal"
        if now>=self.bubble_until: self.bubble=""
        if not self.paused and not self.dragging and now<self.rolling_until:
            b=self.bounds(); x=self.x()+round(self.roll_speed)
            if x<=b.left() or x>=b.right()-self.width()+1: self.roll_speed*=-.92; x=max(b.left(),min(x,b.right()-self.width()+1))
            self.move(x,self.y()); self.roll_angle+=self.roll_spin_speed; self.roll_speed*=.995
        elif not self.paused and not self.dragging:
            if now-self.last_interaction>180: self.walking=False; self.expression="rest"
            elif now>=self.next_decision:
                self.expression="normal"
                if random.random()<.08: self.start_roll(random.choice((-7.,7.)),2.2)
                else:
                    self.walking=random.random()<.58
                    if self.walking:
                        self.move_dx,self.move_dy=random.choice(((-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)))
                    self.next_decision=now+random.uniform(2.5,6)
            if self.walking and now>=self.rolling_until:
                b=self.bounds(); x=self.x()+self.move_dx; y=self.y()+self.move_dy
                if x<=b.left() or x>=b.right()-self.width()+1: self.move_dx*=-1; x=max(b.left(),min(x,b.right()-self.width()+1))
                if y<=b.top() or y>=b.bottom()-self.height()+1: self.move_dy*=-1; y=max(b.top(),min(y,b.bottom()-self.height()+1))
                self.move(x,y)
        self.update()
    def paintEvent(self,event):
        now=time.monotonic(); p=QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
        if self.tiny_mode:
            frame=self.frames["roll"].scaled(64,64,Qt.KeepAspectRatio,Qt.SmoothTransformation)
            p.drawPixmap((self.width()-frame.width())//2,(self.height()-frame.height())//2,frame); return
        rolling=now<self.rolling_until
        costume=self.current_costume if self.data.get("costume_mode")!="none" else "none"
        if not rolling and costume in self.costume_frames and self.expression not in ("heart","angel","rest"):
            key="costume_"+costume;source=self.costume_frames[costume]
        else:
            key="roll" if rolling else (self.expression if self.expression in ("heart","angel","rest") else ("step" if self.walking and not self.dragging and int(now*5)%2 else "idle"));source=self.frames[key]
        source=self.colored_frame(key,source);target_w,target_h=self.render_size("idle" if key.startswith("costume_") or key=="rest" else key)
        costume_box=None
        # The approved 4x3 reference sheets use square cells with deliberate
        # transparent padding. Scale every costume cell by one shared factor;
        # never resize individual outfits according to hats, horns or tails.
        frame=source.scaledToHeight(round(target_h*1.25),Qt.SmoothTransformation) if key.startswith("costume_") else source.scaled(target_w,target_h,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        if not rolling: frame=frame.scaledToHeight(round(frame.height()*(1 if self.dragging else 1+.009*math.sin(now*2.8))),Qt.SmoothTransformation)
        x=(self.width()-frame.width())//2; y=self.height()-frame.height()-4
        hop=now-self.hop_started
        if 0<=hop<.55: y-=round(28*math.sin(math.pi*hop/.55))
        if rolling:
            # Rotate around one fixed centre. The sprite and its bounding box no
            # longer change size from frame to frame, so rolling stays smooth.
            cx=self.width()/2; cy=y+frame.height()/2
            p.save(); p.translate(cx,cy); p.rotate(self.roll_angle)
            p.drawPixmap(round(-frame.width()/2),round(-frame.height()/2),frame); p.restore()
        else: p.drawPixmap(x,y,frame)
        if self.expression not in ("normal","heart","angel","rest") and now>=self.rolling_until:
            p.setFont(QFont("Segoe UI Emoji",28)); p.drawText(QRectF(115,205,110,60),Qt.AlignCenter,{"happy":"✨","angry":"💢","cry":"💧","shock":"❗","shy":"💕","cool":"😎","eat":"🍪","sleep":"💤"}.get(self.expression,""))
        display_text=self.bubble or self.active_timer_text(multiline=False)
        if display_text:
            font=QFont("Microsoft YaHei UI",9); metrics=QFontMetrics(font)
            measured=metrics.boundingRect(QRect(0,0,260,200),Qt.AlignCenter|Qt.TextWordWrap,display_text)
            bubble_w=min(280,max(24,measured.width()+18)); bubble_h=max(24,measured.height()+10)
            bubble_y=max(4,y-bubble_h-5); r=QRectF((self.width()-bubble_w)/2,bubble_y,bubble_w,bubble_h)
            p.setBrush(QColor(255,255,255,238)); p.setPen(QPen(QColor(240,180,55),2)); p.drawRoundedRect(r,10,10); p.setPen(QColor(55,45,35)); p.setFont(font); p.drawText(r.adjusted(8,5,-8,-5),Qt.AlignCenter|Qt.TextWordWrap,display_text)
    def say(self,text,expression="happy",seconds=4,speech_text=None):
        self.bubble=text; self.bubble_until=time.monotonic()+seconds; self.expression=expression; self.expression_until=time.monotonic()+seconds; self.walking=False; self.last_interaction=time.monotonic()
        if self.data.get("speak"):self.speak_text(speech_text or (JAPANESE_LINES.get(text,text) if self.data.get("voice_language")=="ja" else text))
        self.update()
    def start_roll(self,speed=9,seconds=2.6):
        self.walking=False; self.roll_speed=speed; self.roll_spin_speed=(14.0 if abs(speed)<1 else speed*2.4); self.rolling_until=time.monotonic()+seconds; self.last_interaction=time.monotonic()
    def set_expression(self,name):
        text={"happy":"耶！","angry":"哼！再点我就生气啦","cry":"呜呜……","shock":"欸？！","shy":"嘿嘿……","cool":"今天也很酷。","eat":"嚼嚼嚼……","sleep":"晚安啦 Zzz","rest":"抱着枕头休息一下吧。","heart":"送你一颗心！","angel":"今天是天使蛋。"}.get(name,"你好呀"); self.say(text,name,5 if name=="rest" else 3); self.hop_started=time.monotonic()
    def weather(self): self.say("正在看看窗外……","shock",10); QTimer.singleShot(20,self.fetch_weather)
    def fetch_weather(self):
        try:
            city=urllib.parse.quote(self.data["city"]); geo=json.load(urllib.request.urlopen(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=zh&format=json",timeout=8)); place=geo["results"][0]
            url=("https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,apparent_temperature,weather_code&daily=precipitation_probability_max&timezone=auto").format(**place); w=json.load(urllib.request.urlopen(url,timeout=8)); c=w["current"]
            codes={0:"晴",1:"大致晴朗",2:"多云",3:"阴",45:"有雾",51:"毛毛雨",53:"毛毛雨",55:"较强毛毛雨",61:"小雨",63:"中雨",65:"大雨",71:"小雪",73:"中雪",75:"大雪",80:"阵雨",81:"阵雨",82:"强阵雨",95:"雷雨"}; rain=w["daily"]["precipitation_probability_max"][0]
            self.say(f"{self.data['city']}：{codes.get(c['weather_code'],'天气变化')}，{c['temperature_2m']:.0f}°C，体感 {c['apparent_temperature']:.0f}°C。今天最高降雨概率 {rain}% 。","happy",9)
        except Exception: self.say("天气暂时没查到，请检查网络再试试。","cry",6)
    def overview(self):
        n=datetime.now(); self.say(n.strftime("今天是 %Y年%m月%d日，星期")+"一二三四五六日"[n.weekday()]+n.strftime("。现在 %H:%M。"),"happy",7)
    def add_timer(self,mins,label="倒计时结束啦！"): self.timers.append((time.time()+mins*60,label)); self.save_timer_state(); self.say(f"好的，{mins} 分钟后提醒你。")
    def active_timer_text(self,multiline=False):
        now=time.time(); parts=[]
        if self.timers:
            deadline,label=min(self.timers,key=lambda x:x[0]); left=max(0,deadline-now); short=label.replace("结束啦！","").replace("结束啦","")
            parts.append(f"⏳ {short}  {int(left//60):02d}:{int(left%60):02d}")
        if self.stopwatch_started is not None:
            spent=max(0,now-self.stopwatch_started); parts.append(f"⏱ 正计时  {int(spent//60):02d}:{int(spent%60):02d}")
        return ("\n" if multiline else "  ·  ").join(parts)
    def timer_status(self):
        now=time.time(); parts=[]
        if self.timers:
            left=max(0,min(x[0] for x in self.timers)-now); parts.append(f"最近的倒计时还剩 {int(left//60):02d}:{int(left%60):02d}")
        if self.stopwatch_started is not None:
            spent=now-self.stopwatch_started; parts.append(f"正计时已经 {int(spent//60):02d}:{int(spent%60):02d}")
        self.say("；".join(parts) if parts else "现在没有正在进行的计时。","happy",6)
    def toggle_stopwatch(self):
        if self.stopwatch_started is None:self.stopwatch_started=time.time();self.say("正计时开始！","happy")
        else:
            spent=time.time()-self.stopwatch_started;self.stopwatch_started=None;self.say(f"计时结束：{int(spent//60):02d}:{int(spent%60):02d}","happy",7)
        self.save_timer_state()
    def custom_timer(self,reminder=False):
        mins,ok=QInputDialog.getInt(self,"设置提醒" if reminder else "设置倒计时","多少分钟后？",30,1,10080)
        if not ok:return
        msg="倒计时结束啦！"
        if reminder:
            msg,ok=QInputDialog.getText(self,"提醒内容","要提醒什么？")
            if not ok or not msg.strip():return
        self.add_timer(mins,msg.strip())
    def decide(self):
        text,ok=QInputDialog.getText(self,"让奶蛋决定","输入选项，用逗号分隔；留空则抛硬币：")
        if ok:
            choices=[x.strip() for x in text.replace("，",",").split(",") if x.strip()] or ["正面","反面"]; self.say("我选："+random.choice(choices),"shock",6)
    def quick_note(self):
        text,ok=QInputDialog.getMultiLineText(self,"快速记一下","奶蛋帮你记着：")
        if ok and text.strip(): self.data["notes"].append(text.strip()); self.save_data(); self.say("记下来啦！")
    def show_notes(self): self.notes_window=NotesWindow(self); self.notes_window.show()
    def add_link(self):
        name,ok=QInputDialog.getText(self,"添加快捷入口","显示名称：")
        if not ok or not name.strip():return
        url,ok=QInputDialog.getText(self,"添加快捷入口","网址（https://…）：")
        if ok and url.strip():
            name=name.strip();url=self.normalized_link_url(url)
            opening,ok=QInputDialog.getItem(self,"打开方式","选择打开方式：",["打开网页","优先打开桌面快捷方式，找不到时打开网页"],0,False)
            if not ok:return
            self.data["links"][name]=url
            self.data.setdefault("link_modes",{})[name]="desktop" if opening.startswith("优先") else "web"
            self.data["deleted_links"]=[x for x in self.data.get("deleted_links",[]) if x!=name]
            self.save_data(); self.say("快捷入口加好啦！")
    def normalized_link_url(self,url):
        url=url.strip()
        return url if url.startswith(("http://","https://")) else "https://"+url
    def edit_link(self,old_name):
        if old_name not in self.data["links"]:return
        old_url=self.data["links"][old_name]
        new_name,ok=QInputDialog.getText(self,"编辑快捷入口","显示名称：",text=old_name)
        if not ok or not new_name.strip():return
        new_url,ok=QInputDialog.getText(self,"编辑快捷入口","网址（https://…）：",text=old_url)
        if not ok or not new_url.strip():return
        old_mode=self.data.get("link_modes",{}).get(old_name,"desktop" if old_name in ("GO","Moodle") else "web")
        choices=["打开网页","优先打开桌面快捷方式，找不到时打开网页"]
        opening,ok=QInputDialog.getItem(self,"编辑快捷入口","选择打开方式：",choices,1 if old_mode=="desktop" else 0,False)
        if not ok:return
        new_name=new_name.strip();new_url=self.normalized_link_url(new_url)
        if new_name!=old_name and new_name in self.data["links"]:
            if QMessageBox.question(self,"替换快捷入口",f"“{new_name}”已经存在，要替换它吗？",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)!=QMessageBox.Yes:return
        items=list(self.data["links"].items());updated={}
        for name,url in items:
            if name==old_name:updated[new_name]=new_url
            elif name!=new_name:updated[name]=url
        self.data["links"]=updated
        modes=self.data.setdefault("link_modes",{});modes.pop(old_name,None);modes[new_name]="desktop" if opening.startswith("优先") else "web"
        deleted=set(self.data.get("deleted_links",[]));deleted.add(old_name);deleted.discard(new_name)
        self.data["deleted_links"]=sorted(deleted);self.save_data();self.say("快捷入口修改并保存啦！","happy",5)
    def delete_link(self,name):
        if name not in self.data["links"]:return
        if QMessageBox.question(self,"删除快捷入口",f"确定删除“{name}”吗？",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)!=QMessageBox.Yes:return
        self.data["links"].pop(name,None)
        self.data.setdefault("link_modes",{}).pop(name,None)
        deleted=set(self.data.get("deleted_links",[]));deleted.add(name);self.data["deleted_links"]=sorted(deleted)
        self.save_data();self.say("快捷入口已经删除并保存。","happy",5)
    def launch_app(self,protocol,fallback):
        try: os.startfile(protocol)
        except OSError: webbrowser.open(fallback); self.say("没有找到桌面应用，已打开网页版。","shock",5)
    def launch_shortcut_or_url(self,name,url):
        if os.name=="nt":
            roots=[]
            for base in (os.environ.get("USERPROFILE"),os.environ.get("PUBLIC")):
                if base:roots.append(Path(base)/"Desktop")
            if os.environ.get("APPDATA"):roots.append(Path(os.environ["APPDATA"])/"Microsoft"/"Windows"/"Start Menu"/"Programs")
            if os.environ.get("PROGRAMDATA"):roots.append(Path(os.environ["PROGRAMDATA"])/"Microsoft"/"Windows"/"Start Menu"/"Programs")
            aliases={"GO":("ucl go","uclgo","go"),"Moodle":("moodle",)}.get(name,(name.lower(),))
            candidates=[]
            for root in roots:
                if not root.exists():continue
                try:candidates.extend(p for p in root.rglob("*.lnk") if any(a in p.stem.lower() for a in aliases))
                except OSError:pass
            if candidates:
                try:os.startfile(str(sorted(candidates,key=lambda p:len(p.name))[0]));self.say(f"正在打开桌面上的 {name}。","happy",4);return
                except OSError:pass
        webbrowser.open(url);self.say(f"没有找到桌面版 {name}，已打开网页版。","shock",5)
    def open_saved_link(self,name,url):
        if self.data.get("link_modes",{}).get(name,"desktop" if name in ("GO","Moodle") else "web")=="desktop":self.launch_shortcut_or_url(name,url)
        else:webbrowser.open(url)
    def screenshots_folder(self):
        candidates=[]
        if os.environ.get("OneDrive"): candidates.append(Path(os.environ["OneDrive"])/"Desktop")
        if os.environ.get("USERPROFILE"): candidates.append(Path(os.environ["USERPROFILE"])/"Desktop")
        candidates.append(Path.home()/"Desktop")
        desktop=next((p for p in candidates if p.exists()),candidates[-1])
        folder=desktop/"相册"/"screenshots"; folder.mkdir(parents=True,exist_ok=True); return folder
    def screenshot(self):
        folder=self.screenshots_folder()
        path=folder/(datetime.now().strftime("Screenshot_%Y%m%d_%H%M%S")+".png")
        screen=QApplication.primaryScreen(); ok=screen.grabWindow(0).save(str(path),"PNG")
        self.say(("截图已保存到桌面/相册/screenshots。" if ok else "截图失败了。"),"happy" if ok else "cry",6)
    def screen_record(self):
        self.record_watch_started=time.time(); self.record_candidate=None; self.record_size=-1; self.record_stable=0
        try: os.startfile("ms-screenrecorder:"); self.say("已打开录屏工具。完成后会尝试移到 Screenshots 文件夹。","happy",7); QTimer.singleShot(2500,self.watch_recording)
        except OSError:
            try: os.startfile("ms-gamebar:"); self.say("已打开 Xbox Game Bar，请点击录制。","happy",7)
            except OSError: self.say("系统没有找到自带录屏工具。可按 Win+Alt+R 试试。","cry",7)
    def watch_recording(self):
        roots=[Path.home()/"Videos"/"Screen Recordings"]
        if os.environ.get("OneDrive"): roots.append(Path(os.environ["OneDrive"])/"Videos"/"Screen Recordings")
        found=[]
        for root in roots:
            if root.exists(): found.extend(p for p in root.glob("*.mp4") if p.stat().st_mtime>=self.record_watch_started-2)
        if found:
            candidate=max(found,key=lambda p:p.stat().st_mtime); size=candidate.stat().st_size
            if candidate==self.record_candidate and size==self.record_size:self.record_stable+=1
            else:self.record_candidate=candidate;self.record_size=size;self.record_stable=0
            if self.record_stable>=2:
                dest=self.screenshots_folder()/candidate.name
                try: shutil.move(str(candidate),str(dest)); self.say("录屏已移到桌面/相册/screenshots。","happy",7)
                except OSError: self.say("录屏完成，但系统没有允许我移动文件。","shock",7)
                return
        if time.time()-self.record_watch_started<7200:QTimer.singleShot(2500,self.watch_recording)
    def update_api_url(self):
        return str(self.data.get("update_api_url") or UPDATE_API_URL).strip()
    def check_for_updates(self,manual=True):
        if self.update_busy:
            if manual:self.say("已经在检查更新啦。","shock",4)
            return
        url=self.update_api_url()
        if not url:
            if manual:self.say("更新发布地址还没有连接完成。","shock",6)
            return
        self.update_busy=True
        if manual:self.say("正在检查奶蛋的新版本……","shock",8)
        def worker():
            try:
                req=urllib.request.Request(url,headers={"Accept":"application/vnd.github+json","User-Agent":f"Naidan/{APP_VERSION}"})
                with urllib.request.urlopen(req,timeout=12) as response: info=json.load(response)
                tag=str(info.get("tag_name") or "")
                asset=next((a for a in info.get("assets",[]) if str(a.get("name","")).lower() in ("naidan-windows.zip","奶蛋-windows.zip")),None)
                if not tag or not asset: raise ValueError("release is missing naidan-windows.zip")
                self.update_signals.checked.emit({"ok":True,"manual":manual,"version":tag,"notes":str(info.get("body") or ""),"url":str(asset["browser_download_url"])})
            except Exception as exc:self.update_signals.checked.emit({"ok":False,"manual":manual,"error":str(exc)})
        threading.Thread(target=worker,daemon=True).start()
    def update_check_finished(self,result):
        self.update_busy=False
        if not result.get("ok"):
            if result.get("manual"):self.say("暂时无法检查更新，请稍后再试。","cry",6)
            return
        if version_key(result["version"])<=version_key(APP_VERSION):
            if result.get("manual"):self.say(f"已经是最新版 v{APP_VERSION}。","happy",5)
            return
        self.update_info=result; notes=result.get("notes","").strip()[:900] or "修复问题并优化奶蛋。"
        answer=QMessageBox.question(self,"奶蛋发现新版本",f"发现 {result['version']}（当前 v{APP_VERSION}）。\n\n{notes}\n\n现在下载并安装吗？",QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        if answer==QMessageBox.Yes:self.download_update()
    def download_update(self):
        if not self.update_info or self.update_busy:return
        self.update_busy=True; info=dict(self.update_info); self.say("正在下载更新，请稍等……","happy",20)
        def worker():
            try:
                req=urllib.request.Request(info["url"],headers={"User-Agent":f"Naidan/{APP_VERSION}"})
                target=Path(tempfile.gettempdir())/f"naidan-{info['version']}.zip"
                with urllib.request.urlopen(req,timeout=90) as source,target.open("wb") as dest:shutil.copyfileobj(source,dest)
                if target.stat().st_size<1_000_000:raise ValueError("downloaded file is unexpectedly small")
                self.update_signals.downloaded.emit({"ok":True,"path":str(target)})
            except Exception as exc:self.update_signals.downloaded.emit({"ok":False,"error":str(exc)})
        threading.Thread(target=worker,daemon=True).start()
    def update_download_finished(self,result):
        self.update_busy=False
        if not result.get("ok"):
            self.say("更新下载失败，旧版没有受到影响。","cry",7);return
        if not getattr(sys,"frozen",False) or os.name!="nt":
            self.say("新版已下载；自动替换只在奶蛋文件夹版中启用。","shock",8);return
        current=Path(sys.executable);downloaded=Path(result["path"]);script=Path(tempfile.gettempdir())/"naidan_apply_update.ps1";stage=Path(tempfile.gettempdir())/"naidan_update_unpack";backup=Path(str(current.parent)+".update-backup")
        body=f'''$ErrorActionPreference = "Stop"\nStart-Sleep -Seconds 3\n$zip = "{downloaded}"\n$install = "{current.parent}"\n$backup = "{backup}"\n$stage = "{stage}"\ntry {{\n  if (Test-Path $stage) {{ Remove-Item $stage -Recurse -Force }}\n  Expand-Archive -LiteralPath $zip -DestinationPath $stage -Force\n  $source = Join-Path $stage "奶蛋"\n  if (-not (Test-Path (Join-Path $source "奶蛋.exe"))) {{ throw "新版缺少奶蛋.exe" }}\n  if (Test-Path $backup) {{ Remove-Item $backup -Recurse -Force }}\n  Copy-Item -LiteralPath $install -Destination $backup -Recurse -Force\n  Copy-Item (Join-Path $source "*") $install -Recurse -Force\n  $process = Start-Process (Join-Path $install "奶蛋.exe") -PassThru\n  Start-Sleep -Seconds 8\n  if ($process.HasExited) {{ throw "新版未能正常启动" }}\n}} catch {{\n  if (Test-Path $backup) {{\n    Copy-Item (Join-Path $backup "*") $install -Recurse -Force\n    Start-Process (Join-Path $install "奶蛋.exe")\n  }}\n}}\n'''
        script.write_text(body,encoding="utf-8-sig")
        try:subprocess.Popen(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(script)],creationflags=0x08000000);QApplication.quit()
        except OSError:self.say("无法自动替换；旧版仍可正常使用。","cry",7)
    def restore_previous_version(self):
        if not getattr(sys,"frozen",False) or os.name!="nt":self.say("只有安装后的文件夹版可以恢复旧版本。","shock",6);return
        install=Path(sys.executable).parent;backup=Path(str(install)+".update-backup")
        if not backup.exists():self.say("没有找到可以恢复的旧版本。","shock",6);return
        if QMessageBox.question(self,"恢复更新前版本","确定恢复到上次更新前的版本吗？",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)!=QMessageBox.Yes:return
        script=Path(tempfile.gettempdir())/"naidan_restore_previous.ps1"
        body=f'''$ErrorActionPreference = "Stop"\nStart-Sleep -Seconds 3\n$install = "{install}"\n$backup = "{backup}"\nCopy-Item (Join-Path $backup "*") $install -Recurse -Force\nStart-Process (Join-Path $install "奶蛋.exe")\n'''
        script.write_text(body,encoding="utf-8-sig")
        try:subprocess.Popen(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(script)],creationflags=0x08000000);QApplication.quit()
        except OSError:self.say("恢复失败，当前版本没有受到影响。","cry",7)
    def toggle_auto_update(self):
        self.data["auto_update"]=not self.data.get("auto_update",True);self.save_data();self.say("已开启自动检查更新。" if self.data["auto_update"] else "已关闭自动检查更新。","happy",5)
    def toggle_tiny(self):
        if not self.tiny_mode:
            self.normal_pos=self.pos(); self.tiny_mode=True; self.paused=True; self.walking=False; self.setFixedSize(78,78)
            b=self.bounds(); self.move(b.right()-self.width()+1,b.top()+(b.height()-self.height())//2)
        else:
            self.tiny_mode=False; self.setFixedSize(330,350); self.move(self.normal_pos); self.paused=bool(self.data.get("quiet")); self.update_window_size()
        self.update()
    def show_size_settings(self):
        if self.tiny_mode:self.toggle_tiny()
        self.size_window=SizeWindow(self); self.size_window.show(); self.size_window.raise_()
    def show_settings(self):
        if self.tiny_mode:self.toggle_tiny()
        self.settings_window=SettingsWindow(self);self.settings_window.show();self.settings_window.raise_();self.settings_window.activateWindow()
    def show_timer_window(self):
        self.timer_window=TimerWindow(self); self.timer_window.show(); self.timer_window.raise_()
    def show_shortcuts_window(self):
        self.shortcuts_window=ShortcutsWindow(self);self.shortcuts_window.show();self.shortcuts_window.raise_();self.shortcuts_window.activateWindow()
    def restore_pet(self):
        if self.tiny_mode:self.toggle_tiny()
        self.show(); self.raise_(); self.activateWindow()
    def autostart_enabled(self):
        if os.name!="nt":return False
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                winreg.QueryValueEx(key,"奶蛋"); return True
        except OSError:return False
    def toggle_autostart(self):
        if os.name!="nt":self.say("开机启动设置仅支持 Windows。","shock",5);return
        try:
            import winreg
            key=winreg.CreateKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run")
            if self.autostart_enabled():
                try:winreg.DeleteValue(key,"奶蛋")
                except OSError:pass
                enabled=False
            else:
                if getattr(sys,"frozen",False):command=f'"{sys.executable}"'
                else:
                    pythonw=Path(sys.executable).with_name("pythonw.exe"); executable=pythonw if pythonw.exists() else Path(sys.executable)
                    command=f'"{executable}" "{SCRIPT_ROOT/"pet.py"}"'
                winreg.SetValueEx(key,"奶蛋",0,winreg.REG_SZ,command); enabled=True
            winreg.CloseKey(key)
            if getattr(self,"tray_autostart",None):self.tray_autostart.setChecked(enabled)
            self.say("已开启开机自动启动。" if enabled else "已关闭开机自动启动。","happy",5)
        except OSError:self.say("无法修改开机启动设置。","cry",5)
    def setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():return
        self.tray=QSystemTrayIcon(QIcon(str(ASSETS/"idle.png")),self); self.tray.setToolTip("奶蛋桌宠")
        tray_menu=QMenu(); restore=tray_menu.addAction("显示奶蛋"); restore.triggered.connect(self.restore_pet)
        timer=tray_menu.addAction("打开计时面板"); timer.triggered.connect(self.show_timer_window)
        tiny=tray_menu.addAction("隐藏成迷你蛋"); tiny.triggered.connect(self.toggle_tiny)
        tray_menu.addSeparator();settings=tray_menu.addAction("打开设置中心");settings.triggered.connect(self.show_settings)
        quiet=tray_menu.addAction("安静奶蛋");quiet.setCheckable(True);quiet.setChecked(bool(self.data.get("quiet")));quiet.triggered.connect(self.set_quiet);self.tray_quiet=quiet
        clickthrough=tray_menu.addAction("点击穿透");clickthrough.setCheckable(True);clickthrough.setChecked(bool(self.data.get("click_through")));clickthrough.triggered.connect(self.set_click_through);self.tray_clickthrough=clickthrough
        tray_menu.addSeparator(); self.tray_autostart=tray_menu.addAction("🚀 随 Windows 自动启动"); self.tray_autostart.setCheckable(True); self.tray_autostart.setChecked(self.autostart_enabled()); self.tray_autostart.triggered.connect(lambda checked:self.toggle_autostart())
        tray_menu.addSeparator(); quit_action=tray_menu.addAction("退出奶蛋"); quit_action.triggered.connect(QApplication.quit)
        self.tray.setContextMenu(tray_menu); self.tray.activated.connect(lambda reason:self.restore_pet() if reason==QSystemTrayIcon.ActivationReason.Trigger else None); self.tray.show()
    def mouseDoubleClickEvent(self,e):
        if self.tiny_mode and e.button()==Qt.LeftButton:self.toggle_tiny();e.accept()
    def mousePressEvent(self,e):
        self.last_interaction=time.monotonic()
        if e.button()==Qt.LeftButton:
            self.press_global=e.globalPosition().toPoint();self.drag_offset=self.press_global-self.pos();self.press_time=time.monotonic();self.dragging=False;e.accept()
    def mouseMoveEvent(self,e):
        if e.buttons()&Qt.LeftButton and not self.data.get("position_locked"):
            cur=e.globalPosition().toPoint()
            if (cur-self.press_global).manhattanLength()>6:self.dragging=True;self.walking=False;self.move(cur-self.drag_offset)
            e.accept()
    def mouseReleaseEvent(self,e):
        if e.button()!=Qt.LeftButton:return
        if self.dragging:
            self.dragging=False;self.walking=False;self.rolling_until=0.;self.roll_speed=0.;self.next_decision=time.monotonic()+8;self.last_interaction=time.monotonic()
        elif time.monotonic()-self.press_time<1:
            if self.action_active():self.stop_current_action()
            else:self.random_click_interaction()
        e.accept()
    def action_active(self):
        return self.walking or time.monotonic()<self.rolling_until or self.expression!="normal" or 0<=time.monotonic()-self.hop_started<.55
    def stop_current_action(self):
        self.walking=False;self.rolling_until=0.;self.roll_speed=0.;self.roll_spin_speed=0.;self.roll_angle=0.;self.hop_started=0.;self.expression="normal";self.expression_until=0.;self.bubble="";self.bubble_until=0.;self.update()
    def random_click_interaction(self):
        mode=self.data.get("click_action","all")
        if mode=="none":return
        lock_original=self.data.get("costume_mode")=="locked_original"
        if mode=="expression" or lock_original:self.set_expression(random.choice(("heart","happy","shy","shock","cool","eat")));return
        choice=random.random()
        expression_chance=.58 if mode=="expression_action" else .38
        if choice<expression_chance:self.set_expression(random.choice(("heart","happy","shy","shock","cool","eat")))
        elif mode=="all" and choice<.76:
            self.data["costume_mode"]="fixed";self.random_costume()
        elif choice<.9:
            self.hop_started=time.monotonic();self.say(random.choice(("跳一下！","奶蛋弹起来啦！")),"happy",3)
        else:self.start_roll(.01,1.3)
    def contextMenuEvent(self,e):
        menu=QMenu(self); callbacks={}
        act=menu.addMenu("🎭 动作")
        for label,fn in (("滚一圈",lambda:self.start_roll(8,2.6)),("高速滚走",lambda:self.start_roll(random.choice((-15,15)),3.4)),("原地翻滚",lambda:self.start_roll(.01,1.3)),("跳一下",lambda:setattr(self,"hop_started",time.monotonic()))):callbacks[act.addAction(label)]=fn
        expr=menu.addMenu("😊 表情")
        for label,name in (("开心","happy"),("生气","angry"),("哭泣","cry"),("震惊","shock"),("害羞","shy"),("酷酷墨镜","cool"),("吃饼干","eat"),("睡觉","sleep"),("抱枕休息","rest"),("爱心","heart")): callbacks[expr.addAction(label)]=lambda n=name:self.set_expression(n)
        dress=menu.addMenu("👗 装扮")
        callbacks[dress.addAction("原味奶蛋（不换装）")]=lambda:self.set_costume_mode("none")
        callbacks[dress.addAction("锁定原始奶蛋（点击也不换装）")]=lambda:self.set_costume_mode("locked_original")
        callbacks[dress.addAction("随机换装")]=lambda:self.set_costume_mode("random")
        dress.addSeparator()
        for category,keys in COSTUME_CATEGORIES.items():
            submenu=dress.addMenu(category)
            for key in keys:
                if key!="none":callbacks[submenu.addAction(COSTUMES[key])]=lambda k=key:(self.set_costume_mode("fixed"),self.set_costume(k))
        info=menu.addMenu("🌦 信息播报"); callbacks[info.addAction(f"{self.data['city']} 天气")]=self.weather; callbacks[info.addAction("当前时间")]=lambda:self.say(datetime.now().strftime("现在是 %H:%M。")); callbacks[info.addAction("今天日期")]=self.overview; callbacks[info.addAction("今日概览")]=lambda:(self.overview(),QTimer.singleShot(2500,self.weather)); info.addSeparator(); callbacks[info.addAction("修改天气城市…")]=self.change_city
        tools=menu.addMenu("⏱ 小工具"); callbacks[tools.addAction("打开计时面板")]=self.show_timer_window
        callbacks[tools.addAction("快速提醒…")]=lambda:self.custom_timer(True);callbacks[tools.addAction("快速记事…")]=self.quick_note;callbacks[tools.addAction("查看笔记")]=self.show_notes;callbacks[tools.addAction("随机决定…")]=self.decide;callbacks[tools.addAction("掷骰子")]=lambda:self.say(f"掷到了 {random.randint(1,6)}！","shock");callbacks[tools.addAction("查看剪贴板")]=lambda:self.say(QApplication.clipboard().text()[:180] or "剪贴板是空的。","shock",8)
        links=menu.addMenu("🔗 快捷入口")
        for name,url in self.data["links"].items():
            callbacks[links.addAction(name)]=lambda n=name,u=url:self.open_saved_link(n,u)
        links.addSeparator();callbacks[links.addAction("微信")]=lambda:self.launch_app("weixin://","https://weixin.qq.com/");links.addSeparator();callbacks[links.addAction("⚙ 管理快捷入口…")]=self.show_shortcuts_window
        capture=menu.addMenu("📷 截图与录屏");callbacks[capture.addAction("全屏截图")]=self.screenshot;callbacks[capture.addAction("打开录屏工具")]=self.screen_record
        menu.addSeparator();callbacks[menu.addAction("⚙ 奶蛋设置中心")]=self.show_settings
        quiet_action=menu.addAction("🤫 安静奶蛋");quiet_action.setCheckable(True);quiet_action.setChecked(bool(self.data.get("quiet")));callbacks[quiet_action]=lambda:self.set_quiet(not self.data.get("quiet"))
        callbacks[menu.addAction("🥚 恢复正常大小" if self.tiny_mode else "🥚 隐藏成迷你蛋")]=self.toggle_tiny
        autostart=menu.addAction("🚀 开机自动启动");autostart.setCheckable(True);autostart.setChecked(self.autostart_enabled());callbacks[autostart]=self.toggle_autostart
        updates=menu.addMenu("🔄 软件更新");callbacks[updates.addAction("立即检查更新")]=lambda:self.check_for_updates(True);callbacks[updates.addAction("关闭自动检查" if self.data.get("auto_update",True) else "开启自动检查")]=self.toggle_auto_update;updates.addSeparator();callbacks[updates.addAction("恢复到更新前版本…")]=self.restore_previous_version
        callbacks[menu.addAction("🔊 关闭语音播报" if self.data["speak"] else "🔈 开启语音播报")]=self.toggle_speech;callbacks[menu.addAction("退出奶蛋")]=QApplication.quit
        selected=menu.exec(e.globalPos())
        if selected in callbacks:callbacks[selected]()
    def toggle_pause(self):self.set_quiet(not self.data.get("quiet"))
    def toggle_speech(self):self.data["speak"]=not self.data["speak"];self.save_data();self.say("语音播报已"+("开启。" if self.data["speak"] else "关闭。"))
    def change_city(self):
        city,ok=QInputDialog.getText(self,"天气城市","输入城市英文名：",text=self.data["city"])
        if ok and city.strip():self.data["city"]=city.strip();self.save_data();self.say("天气城市改成 "+city.strip()+" 啦！")

def main():
    if os.name=="nt":
        try:
            import ctypes; ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Naidan.DesktopPet.v2")
        except (AttributeError,OSError):pass
    app=QApplication(sys.argv);app.setWindowIcon(QIcon(str(ASSETS/"奶蛋.ico")));app.setQuitOnLastWindowClosed(False);pet=FuzzyPet();pet.setup_tray();pet.show();app.aboutToQuit.connect(pet.save_timer_state);sys.exit(app.exec())
if __name__=="__main__":main()
