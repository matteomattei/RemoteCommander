!define exe             'RemoteCommander.exe'

!define compressor      'lzma'  ;one of 'zlib', 'bzip2', 'lzma'

; - - - - do not edit below this line, normaly - - - -
!ifdef compressor
    SetCompressor ${compressor}
!else
    SetCompress Off
!endif
Name ${exe}
OutFile ${exe}
SilentInstall silent
!ifdef icon
    Icon ${icon}
!endif

Section
	SetOutPath '$EXEDIR\REMOTECOMMANDER-Portable'
	SetOverwrite on
	File /r build\exe.win32-3.4\*.*
	SetOutPath '$EXEDIR\'
	ExecWait "$EXEDIR\REMOTECOMMANDER-Portable\remotecommander.exe"
	RMDir /r '$EXEDIR\REMOTECOMMANDER-Portable'
SectionEnd