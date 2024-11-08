import unicodedata
import subprocess
import colorsys
import os

dir = os.path.dirname(__file__)
darkColorScheme = f"{dir}/TemplateDark.colors"
lightColorScheme = f"{dir}/TemplateLight.colors"
kwinrules = os.path.expanduser("~/.config/kwinrulesrc")
kcolorschemes = os.path.expanduser("~/.local/share/color-schemes")


def lighten(color, amount=0.5):
    r = color[0]
    g = color[1]
    b = color[2]

    hslColor = colorsys.rgb_to_hls(r, g, b)

    newR = hslColor[0] if hslColor[0] <= 255 else 255
    newG = 1 - amount * (1 - hslColor[1])
    newB = hslColor[2]

    colorTuple = colorsys.hls_to_rgb(newR, newG, newB)

    colorList = list(colorTuple)
    colorList[:] = [x if x <= 255 else 255 for x in colorList]
    colorTuple = tuple(colorList)

    return f'{",".join(map(str, tuple(map(int, colorTuple))))}'


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

    rgbTuple = tuple(int(hexColor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    # Sum all values in the tuple +1 to fix the problem of the
    # wrong color being selected in Wayland (darker than the actual color)
    rgbTuple = tuple(x + 1 for x in rgbTuple)

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
