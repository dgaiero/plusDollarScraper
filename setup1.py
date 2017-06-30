from cx_Freeze import setup, Executable

exe = Executable(
    script="PlusDollarsScraper.py",
    base="Win32Gui"
    #icon="Icon.ico"
)
includefiles = []
includes = ["lxml._elementpath"]
excludes = []
packages = ["urllib", "configparser", "lxml","gzip", "requests", "re", "smtplib", "bs4", "email.mime.multipart", "email.mime.text", "twilio.rest", "pushbullet"]
setup(

    version="0.0",
    description="No Description",
    author="Name",
    name="App name",
    options={'build_exe': {'excludes': excludes,
                           'packages': packages, 'include_files': includefiles}},
    executables=[exe]
)
