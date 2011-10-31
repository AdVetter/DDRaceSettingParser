'''
Created on 13.05.2011

@author: XXLTomate
'''
import urllib, os, datetime
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-b", "--html", dest="useHtml", help="Html output (table)", default=False, action="store_true")
parser.add_option("-s", "--cfg", dest="useDefault", help="Generate config file with default values (default)", default=True, action="store_true")
parser.add_option("-c", "--commands", dest="useCommands", help="Parse commands, not settings", default=False, action="store_true")
parser.add_option("-n", "--noformat", dest="noFormat", help="Does not format HTML output", default=False, action="store_true")
parser.add_option("-v", "--verbose", dest="useVerbose", help="Shows much output", default=False, action="store_true")
parser.add_option("-m", "--maxclients", dest="maxClients", help="maximal clients in your DDRace mod (default: %default)", default=16)
(options, args) = parser.parse_args()

#Config:
github = "https://github.com/XXLTomate/XXLDDRace" #no / at the end
branch = "master"
#for path conf look in _init_

class GetSettings():
    def __init__(self, github, branch, options):
        githubPrefix = github + "/raw/" + branch
        self.variables_h = githubPrefix + "/src/game/variables.h" 
        self.config_variables_h = githubPrefix + "/src/engine/shared/config_variables.h"
        self.ddracecommands_h = githubPrefix + "/src/game/ddracecommands.h"
        self.chatcommands_h = githubPrefix + "/src/game/server/ddracechat.h"
        self.gamecontext_cpp = githubPrefix + "/src/game/server/gamecontext.cpp"
        self.server_cpp = githubPrefix + "/src/engine/server/server.cpp"
        
        self.useHtml = options.useHtml
        self.useVerbose = options.useVerbose
        self.maxClients = options.maxClients
        self.noFormat = options.noFormat
        self.useCommands = options.useCommands
        
        if self.useHtml and self.useCommands:
            self.storeFile = "DDRaceCommands.html"
        elif self.useHtml:
            self.storeFile = "DDRaceSettings.html"
        elif self.useCommands:
            self.storeFile = "commands.txt"
        else:
            self.storeFile = "default.cfg"
        self.dateTime = str(datetime.datetime.now())
                
    def run(self):
        if os.path.exists(self.storeFile):
            print "Deleting \""+ self.storeFile + "\""
            os.remove(self.storeFile)
        if self.useHtml:
            print "Saving header";
            self.printHeader()
        if self.useCommands:
            print "Parsing server.cpp"
            self.getConsoleCommands(self.server_cpp)
            print "Parsing gamecontext.cpp"
            self.getConsoleCommands(self.gamecontext_cpp)
            print "Parsing ddracecommands.h"
            self.getMacoCommands(self.ddracecommands_h)
            print "Parsing ddracechat.h"
            self.getMacoCommands(self.chatcommands_h)
        else:
            print "Parsing variables.h"
            self.getMacroSettings(self.variables_h)
            print "Parsing config_variables.h"
            self.getMacroSettings(self.config_variables_h)
        if self.useHtml:
            print "Saving footer";
            self.printFooter()
        print "Finished! (saved to \""+ self.storeFile + "\")"
        
    def getMacroSettings(self, url):
        tmp = urllib.urlopen(url)
        for line in tmp.readlines():
            self.parseLine(line);
            
    def getMacoCommands(self, url):
        tmp = urllib.urlopen(url)
        for line in tmp.readlines():
            if line[0] == "/" or line[0] == "#" or line == "\n" or line == "":
                continue
            
            #macro lenght
            offset = len(line.split("(")[0]) + 1
            
            settingLine = line[offset:-2].replace(", ",",").replace("\"","").replace(";","")
            commandSplit = settingLine.split(",")
                   
            if self.useHtml:
                self.printHtml(commandSplit)
            else:
                self.printDefault(commandSplit)

    def getConsoleCommands(self, url):
        tmp = urllib.urlopen(url)
        for line in tmp.readlines():
            if line.find("Console()->Register(") != -1:
                 
                settingLine = line.strip()[:-2].replace(", ",",").replace("\"","").replace(";","").replace("Console()->Register(","")
                commandSplit = settingLine.split(",")

                if self.useHtml:
                    self.printHtml(commandSplit)
                else:
                    self.printDefault(commandSplit)
    
    def parseLine(self,line):
        if line[0] == "/" or line[0] == "#" or line == "\n" or line == "":
            return

        dataType = line[13:16]
        settingLine = line[17:-2].replace(", ",",")
        settingSplit = settingLine.split(',')
        settingSplit.append(dataType)
        
        if self.useHtml:
            self.printHtml(settingSplit)
        else:
            self.printDefault(settingSplit)
    
    def printDefault(self,setting):
        if self.useCommands:
            
            if setting[-1] == ")": #empty description
                setting[-1] = ""
            
            out = setting[0] + " " + setting[1] + " [" + setting[-1].split("_")[-1] +"]"
            
            if self.useVerbose:
                print out;
            
            file = open(self.storeFile, "a")    
            file.write(out + "\n")
            file.close()
            
        else:
            if setting[0][0:2] == "Sv":
                if setting[-1] == "STR":
                    out = setting[1] + " " + setting[3] 
                else:
                    out = setting[1] + " " + setting[2] 
                    
                if self.useVerbose:
                    print out;
                
                file = open(self.storeFile, "a")    
                file.write(out + "\n")
                file.close()
                
    def printHeader(self):
        if self.useCommands:
            if self.noFormat:
                out = """
<html>
<h1>DDRaceCommands</h1>
<table border="2">
<tr><th align="center">Command</th><th align="center">Description</th></tr>"""
            else:
                out = """
<html>
    <h1>DDRaceCommands</h1>
    <table border="2">
        <tr>
            <th align="center">Command</th>
            <th align="center">Description</th>
        </tr>"""
        else:
            if self.noFormat:
                out = """
<html>
<h1>DDRaceSettings</h1>
<table border="2">
<tr><th align="center">Setting</th><th align="center">Description</th><th align="center">Type</th><th align="center">Default</th><th align="center">Min - Max / Max. Length</th></tr>"""
            else:
                out = """
<html>
    <h1>DDRaceSettings</h1>
    <table border="2">
        <tr>
            <th align="center">Setting</th>
            <th align="center">Description</th>
            <th align="center">Type</th>
            <th align="center">Default</th>
            <th align="center">Min - Max / Max. Length</th>
        </tr>"""
        
        file = open(self.storeFile, "a")    
        file.write(out + "\n")
        file.close()
        
    def printFooter(self):
        if self.noFormat:
            out = """
</table>
Generated: """ + self.dateTime + """ with DDRaceSettingParser by XXLTomate
</html>"""
        else:
            out = """
    </table>
    Generated: """ + self.dateTime + """ with DDRaceSettingParser by XXLTomate
</html>"""

        file = open(self.storeFile, "a")    
        file.write(out + "\n")
        file.close()
        
    def printHtml(self, setting):
        if self.useCommands:
            outCommand  = []
            command = setting
            
            #0:Command
            outCommand.append(command[0] + " " + command[1])
            #1:Description
            if command[5] == ")": #empty description
                outCommand.append("")
            else:
                outCommand.append(command[5])
        
            if self.noFormat:
                out = """<tr>"""
                for n in outCommand:
                    style = ""
                    if outCommand.index(n) == 2:
                        style = " align=\"center\""
                    out = out + """<td""" + style + """>""" + n + """</td>"""
                out = out + """</tr>"""
            else:
                out = """        <tr>"""
                for n in outCommand:
                    style = ""
                    if outCommand.index(n) == 2:
                        style = " align=\"center\""
                    out = out + """
            <td""" + style + """>""" + n + """</td>"""
                out = out + """
        </tr>"""

            file = open(self.storeFile, "a")
            file.write(out + "\n")
            file.close()
        else:
            outSetting  = []
            #print setting
            if setting[0][0:2] == "Sv":
                if setting[-1] == "STR":
                    #0:Setting
                    outSetting.append(setting[1])
                    #1:Description
                    outSetting.append(setting[5].replace("\"", ""))
                    #2:Type
                    outSetting.append("text")
                    #3:Default
                    outSetting.append(setting[3])
                    #4:MinMay
                    outSetting.append(setting[2])
                else:
                    #0:Setting
                    outSetting.append(setting[1])
                    #1:Description
                    outSetting.append(setting[6].replace("\"", ""))
                    #2:Type
                    outSetting.append("number")
                    #3:Default
                    outSetting.append(setting[2])
                    #4:MinMay
                    outSetting.append(setting[3] + " - " + setting[4].replace("MAX_CLIENTS", str(self.maxClients)))
                    
                if self.noFormat: 
                    out = """<tr>"""
                    for n in outSetting:
                        style = ""
                        if outSetting.index(n) == 2 or outSetting.index(n) == 3 or outSetting.index(n) == 4 or outSetting.index(n) == 5:
                            style = " align=\"center\""
                        out = out + """<td""" + style + """>""" + n + """</td>"""
                    out = out + """</tr>"""
                else:
                    out = """        <tr>"""
                    for n in outSetting:
                        style = ""
                        if outSetting.index(n) == 2 or outSetting.index(n) == 3 or outSetting.index(n) == 4 or outSetting.index(n) == 5:
                            style = " align=\"center\""
                        out = out + """
            <td""" + style + """>""" + n + """</td>"""
                    out = out + """
        </tr>"""
            else:
                return
                
            file = open(self.storeFile, "a")    
            file.write(out + "\n")
            file.close()
        
if __name__ == '__main__':
    #GO!
    GetSettings(github, branch, options).run()