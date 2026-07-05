Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Convert path to 8.3 short path representation to bypass VBScript ANSI and space limitations
shortDir = fso.GetFolder(currentDir).ShortPath
WshShell.CurrentDirectory = shortDir

WshShell.Run "cmd.exe /c start.bat", 0

Set WshShell = Nothing
Set fso = Nothing
