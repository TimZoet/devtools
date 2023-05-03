Setup
=====

[**<<- Back**](readme.md)

After going through all steps listed in this document, it should be possible to invoke any further commands just by
calling `devtools <cmd> <options>` from the development environment.

The default settings will result in the following directory structure:

```sh
~/dev
├── .conan
├── devtools
├── projects
│   ├── alexandria
│   ├── bettertest
│   ├── cmake-modules
│   ├── common
│   └── etc...
├── pyenv
├── tools
|   └── Python311
├── devtools.ini
└── startup[.bat]
```

**Note:** The generated files are not relocatable, as they contain absolute paths.

Retrieve devtools
-----------------

First retrieve this repository:

**Windows:**

```sh
cd %USERPROFILE%
mkdir dev && cd dev
git clone git@github.com:TimZoet/devtools.git devtools
```

**Linux:**

```sh
cd ~
mkdir dev && cd dev
git clone git@github.com:TimZoet/devtools.git devtools
```

Python Environment
------------------

Install a recent Python version. You can install it to any directory depending on your preferences, though placing it
somewhere inside of the development folder (as shown in the directory structure above) might be a good idea.

After installation, setup a virtual environment as follows:

**Windows:**

Run the following commands:

```sh
cd %USERPROFILE%/dev
python -m venv pyenv
```

**Linux:**

Run the following commands:

```sh
cd ~/dev
python3 -m venv pyenv
```

Startup Script
--------------

All subsequent commands must be done with this virtual environment enabled. To automate setting up this environment, you
can do the following:

**Windows:**

Run the following commands:

```sh
python %USERPROFILE%/dev/devtools/devtools.py setup
```

Create a new profile in the Terminal with the following command line (replace the path to the Visual Studio installation
to your desired version):

```sh
%USERPROFILE%/dev/startup.bat && cmd.exe /k "C:/Program Files/Microsoft Visual Studio/2022/Preview/Common7/Tools/VsDevCmd.bat" -arch=x64 -host_arch=x64
```

Optionally, set a starting directory: `%USERPROFILE%/dev`. From here on out, do all your work through this profile.

**Linux:**

Run the following commands:

```sh
python3 ~/dev/devtools/devtools.py setup
chmod +x ~/dev/devtools/linux/devtools
```

From here on out, source the startup script before doing any work:

```sh
. ~/dev/startup
```

**Note:** Query the help of the setup command for more options.
