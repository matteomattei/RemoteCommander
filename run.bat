rmdir build /s /q
rmdir REMOTECOMMANDER-Portable /s /q
del /s /q RemoteCommander.exe
python setup.py build
"C:\Program Files (x86)\NSIS\makensis.exe" compile.nsi
