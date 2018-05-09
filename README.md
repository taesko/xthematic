xthematic
=========
modify, save and load terminal colors in a convenient manner.

### Quick Demo
A demo youtube video is available below that showcases the following:
* set colors from the terminal through hex codes:
* save the current colors as a theme with some name
* activate a theme in the terminal

[![xthematic demo gif](https://img.youtube.com/vi/w0SPD3lVWHE/0.jpg)](https://www.youtube.com/watch?v=w0SPD3lVWHE)


### Installation
python 3.6+ and pip are required.

```bash
    pip install xthematic
```

##### Development version
```bash
    git clone https://github.com/taesko/xthematic.git && cd xthematic
    pip install --user .
```

##### Logging setup (optional)
Logs are written to /var/log/xthematic.log if this file doesn't exist or can't be created because of permissions
a warning is printed when the app is invoked. Backups logs are written to $XDG_CONFIG_HOME/xthematic/logs.
You need to create the /var/log/xthematic.log file with r/w permissions if you want to avoid this.

```bash
    sudo touch /var/log/xthematic.log
    sudo chown username: /var/log/xthematic.log
```


### Basic Usage
Complete help can be found at `xthematic --help`.

The single executable `xthematic` is split into 3 subcommands - `view`, `color` and `theme`

#### xthematic view
View colors in various formats through the terminal.

Takes a variable number of arguments in a colorview format and
prints a line with specific text, foreground and background colors.

the colorview format is made out of 3 fields seperated by ':' and
fields can be left empty to specify default values.

`{foreground_hex}:{background_hex}:{string}`

Note - '#' can be omitted at the start of hex codes.

e.g.
`FF0000:00FF00:"Hello World"` - print "Hello World" with red text and green background.
`FF0000::"Hello World"' - print "Hello World" with red text and default background.

#### xthematic color
View or set terminal colors.

Takes two arguments - `color_id` and `color`(optional). The first must be 
an integer between 0 and 16 while the second a valid hex code (the '#' can be omitted)

If only color_id is supplied the respectful terminal color is printed.
If both arguments are supplied that terminal color is set to the hex value until the terminal session is closed.

#### xthematic theme
Activate, save and deactivate themes.

Takes a single argument - a name of a theme. Without any other optional arguments prints the colors of the
theme to the terminal. If a theme name is not given it prints the current terminal colors.

Use the -a, -s, -d feature switches to activate, save or deactivate themes.

### Documentation
Man or info pages are not written the most complete
documentation is: `xthematic --help`

### License
This project is licensed under the MIT License - see the 
[LICENSE](https://github.com/taesko/xthematic/blob/master/LICENSE.txt) file for details.

### Authors
* Antonio Todorov

### Acknowledgements
* the [pywal](https://github.com/dylanaraps/pywal) project for inspiration and example of code printing 
escape sequences which was part of the earliest version.
