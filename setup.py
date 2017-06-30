import sys
from cx_Freeze import setup, Executable


build_exe_options = {
    "packages": ["os", "sys", "datetime", "urllib.request", "base64", "getpass"],
    "includes": ["urllib", "configparser", "lxml", "gzip", "requests", "re", "smtplib", "bs4", "email.mime.multipart", "email.mime.text", "twilio.rest", "pushbullet"]
}
setup(
    name="CP CSGOLD Web Scrape",
    version="1.0",
    description="Web scraping tool for Cal Poly CS Gold",
    options={"build_exe": build_exe_options},
    executables=[Executable("PlusDollarsScraper.py", base="Win32GUI")])
