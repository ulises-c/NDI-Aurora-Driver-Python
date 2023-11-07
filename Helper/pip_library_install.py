import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Add the libraries you want to install to this list
libraries = ["pyserial"]

for library in libraries:
    install(library)
