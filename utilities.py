from PyQt5.QtCore import Qt
from PyQt5 import QtGui


class Format: 
    pass

__format__ = Format()
__format__._default_button_pal = None


def set_default_button_color(pal):
    __format__._default_button_pal = pal

#  def set_button_color(button, color = -999):
    #  if color != -999:
        #  pal = button.palette()
        #  pal.setColor(QtGui.QPalette.Button, QtGui.QColor(color));
        #  button.setAutoFillBackground(True)
        #  button.setPalette(pal)
        #  button.update()
    #  else:
        #  button.setPalette(__format__._default_button_pal)
        #  button.update()
    #  pass


def set_palette_color(obj, role, color):
    pal = obj.palette()
    pal.setColor(role, color);
    obj.setAutoFillBackground(True)
    obj.setPalette(pal)
    obj.update()

def set_button_color(button, color = None):
    if color:
        set_palette_color(button, QtGui.QPalette.Button, QtGui.QColor(color))
    else:
        button.setPalette(__format__._default_button_pal)
        button.update()
    pass
