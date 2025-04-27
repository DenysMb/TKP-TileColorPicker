import unicodedata
import subprocess
import colorsys
import os

dir = os.path.dirname(__file__)
darkColorScheme = f"{dir}/TemplateDark.colors"
lightColorScheme = f"{dir}/TemplateLight.colors"
kwinrules = os.path.expanduser("~/.config/kwinrulesrc")
kcolorschemes = os.path.expanduser("~/.local/share/color-schemes")


def colorTupleToString(color):
    colorString = f'{",".join(map(str, tuple(map(int, color))))}'

    print(f'Color tuple: {colorString}')

    return colorString


def setColorScheme(color):
    r = color[0]
    g = color[1]
    b = color[2]

    if (r*0.299 + g*0.587 + b*0.114) > 186:
        return lightColorScheme
    else:
        return darkColorScheme


def selectColor():
    print("Select window color from screen")

    kcolorchooserCommand = 'kcolorchooser --print'

    hexColor = subprocess.check_output(
        kcolorchooserCommand.split(), universal_newlines=True).strip()

    print(f'Window color: {hexColor}')

    rgbTuple = tuple(int(hexColor[i:i+2], 16) for i in range(1, 7, 2))

    print(f'RGB color: {rgbTuple}')
    print(f'Hex color: {hexColor}')

    return hexColor, rgbTuple

def transformName(name):
    name = unicodedata.normalize('NFD', name)
    return name.upper()

def windowListToDictionary(list):
    windowDictionary = {
        'noApplication': 'No application',
    }

    for item in list:
        key = item.split('.')[1].strip()
        value = ' '.join(item.split('.')).strip()
        windowDictionary[key] = value

    return windowDictionary
