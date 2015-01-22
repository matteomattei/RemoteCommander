import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
	base = "Win32GUI"

executableOptions = [
	Executable(
		"remotecommander.py",
		appendScriptToExe=True,
		appendScriptToLibrary=False,
		targetName="remotecommander.exe",
		base = base # <-- this is needed to hide Windows console
	)
]

buildOptions = dict(
	compressed=True,
	create_shared_zip = False,
	excludes = [],
	packages = [],
	include_files = [],
)

setup(
	name = "RemoteCommander",
	version = '1.0',
	description = "A simple tool to issue remote commands via SSH",
	author = 'Matteo Mattei',
	author_email = 'matteo.mattei@gmail.com',
	options = dict(build_exe = buildOptions),
	executables = executableOptions
)