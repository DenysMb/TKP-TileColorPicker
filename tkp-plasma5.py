import subprocess
from utils import lighten, selectColor, setColorScheme, kwinrules, kcolorschemes, transformName, windowListToDictionary

prefix = "TKP-"

subprocess.Popen(f'touch {kwinrules}'.split(), stdout=subprocess.PIPE)

createDirectoryCommand = f'mkdir -p {kcolorschemes}'
subprocess.Popen(createDirectoryCommand.split(), stdout=subprocess.PIPE)

wmctrlCommand = ['wmctrl', '-l', '-x']
awkCommand = ['awk', '{print $3}']

wmctrlProcess = subprocess.Popen(wmctrlCommand, stdout=subprocess.PIPE)
awkProcess = subprocess.Popen(awkCommand, stdin=wmctrlProcess.stdout, universal_newlines=True, stdout=subprocess.PIPE)
wmctrlProcess.wait()

windowList = awkProcess.stdout.read().splitlines()
windowDictionary = windowListToDictionary(windowList)
windowNameList = []

for i in windowList:
    windowNameList.append(i.split('.')[1].strip())

kdialogCommand = ['kdialog', '--title', 'TKP - Tile Color Picker', '--combobox', 'Select window to change title bar color', 'No application'] + windowNameList + ['--default', 'No application']

selectedWindow = subprocess.check_output(kdialogCommand, universal_newlines=True).strip()

noAppSelected = selectedWindow == 'No application'

if (noAppSelected):
    kdialogNoAppCommand = ['kdialog', '--title', 'TKP - Tile Color Picker', '--inputbox', 'Type application name']
    selectedWindowName = subprocess.check_output(kdialogNoAppCommand, universal_newlines=True).strip()
    selectedWindowClass = "(?i).*" + selectedWindowName + ".*"
else:
    selectedWindowClass = windowDictionary[selectedWindow]
    selectedWindowName = selectedWindow.strip()

appName = transformName(selectedWindowName)
ruleName = f'{prefix}{appName}'

hexColor, rgbTuple = selectColor()

rgbColor = lighten(rgbTuple, 1)

newColorScheme = f'{kcolorschemes}/{ruleName}.colors'

colorScheme = setColorScheme(rgbTuple)

subprocess.Popen(f'cp {colorScheme} {newColorScheme}'.split(),
                 stdout=subprocess.PIPE).wait()

colorSchemeFile = open(newColorScheme, "r")
lines = colorSchemeFile.readlines()
colorSchemeFile.close()

newColorSchemeFile = open(newColorScheme, "w")

for line in lines:
    if "{BACKGROUND_1}" in line:
        line = line.replace("{BACKGROUND_1}", rgbColor)
    if "{BACKGROUND_2}" in line:
        line = line.replace("{BACKGROUND_2}", rgbColor)
    if "{BACKGROUND_3}" in line:
        line = line.replace("{BACKGROUND_3}", rgbColor)
    if "{BACKGROUND_4}" in line:
        line = line.replace("{BACKGROUND_4}", rgbColor)
    if "{BACKGROUND_5}" in line:
        line = line.replace("{BACKGROUND_5}", rgbColor)
    if "{BACKGROUND_6}" in line:
        line = line.replace("{BACKGROUND_6}", rgbColor)
    if "{HEADER_1}" in line:
        line = line.replace("{HEADER_1}", rgbColor)
    if "{HEADER_2}" in line:
        line = line.replace("{HEADER_2}", rgbColor)
    if "{NAME}" in line:
        line = line.replace("{NAME}", ruleName)
    newColorSchemeFile.write(line)

newColorSchemeFile.close()

kwinRulesFile = open(kwinrules, "r")

isInGeneral = False
isAlreadyInKwinrules = False
groupIndex = 0
kgroupnum = 0
kgroupstr = ""

for line in kwinRulesFile:
    if "Description" in line and not isAlreadyInKwinrules:
        groupIndex += 1
        isAlreadyInKwinrules = ruleName in line
    if "[General]" in line:
        isInGeneral = True
    if not isInGeneral:
        continue
    if not len(line.split()):
        continue
    if "count" in line.split()[0]:
        kgroupnum = line.split('=')[1].strip()
    if "rules" in line.split()[0]:
        kgroupstr = line.split('=')[1].strip()

kwinRulesFile.close()

groupIndex = groupIndex + 1 if not isAlreadyInKwinrules else groupIndex

def writeConfig(key, value):
    command = ['kwriteconfig5', '--file', kwinrules, '--group', str(groupIndex), '--key', key, value]
    subprocess.Popen(command, stdout=subprocess.PIPE).wait()

if not isAlreadyInKwinrules:
    wmClassComplete = "false" if noAppSelected else "true"
    wmClassMatch = "3" if noAppSelected else "1"

    writeConfig("Description", ruleName)
    writeConfig("decocolor", ruleName)
    writeConfig("decocolorrule", "2")
    writeConfig("wmclass", selectedWindowClass)
    writeConfig("wmclasscomplete", wmClassComplete)
    writeConfig("wmclassmatch", wmClassMatch)

    newCount = f'kwriteconfig5 --file {kwinrules} --group General --key count {int(kgroupnum) + 1}'
    subprocess.Popen(newCount.split(), stdout=subprocess.PIPE).wait()

    newRulesStr = f'{kgroupstr},{groupIndex}'
    newRules = f'kwriteconfig5 --file {kwinrules} --group General --key rules {newRulesStr if kgroupstr else groupIndex}'
    subprocess.Popen(newRules.split(), stdout=subprocess.PIPE).wait()

    qdbusCommand = f'qdbus-qt5 org.kde.KWin /KWin reconfigure'
    subprocess.Popen(qdbusCommand.split(), stdout=subprocess.PIPE).wait()
else:
    qdbusCommand = f'qdbus-qt5 org.kde.KWin /KWin reconfigure'

    writeConfig("decocolor", "BreezeDark")

    subprocess.Popen(qdbusCommand.split(), stdout=subprocess.PIPE).wait()

    subprocess.Popen('sleep 1'.split(), stdout=subprocess.PIPE).wait()

    writeConfig("decocolor", ruleName)

    subprocess.Popen(qdbusCommand.split(), stdout=subprocess.PIPE).wait()
