xthematic
=========
modify, save and load terminal colors in a convenient manner.

### Quick Demo
* set colors from the terminal through hex codes:
* save the current colors as a theme with some name
* activate a theme in the terminal

![xthematic demo gif](https://thumbs.gfycat.com/FabulousLimitedKittiwake-size_restricted.gif)


### Installation
python 3.6+ and pip are required.

```bash
    git clone https://github.com/taesko/xthematic.git && cd xthematic
    pip install --user .
```

Logs are written to /var/log/xthematic.log if this file doesn't exist or can't be created because of permissions
a warning is printed when the app is invoked. Backups logs are written to $XDG_CONFIG_HOME/xthematic/logs.
You need to create the /var/log/xthematic.log file with r/w permissions if you want to avoid this.

```bash
    sudo touch /var/log/xthematic.log
    sudo chown username: /var/log/xthematic.log
```


### Documentation
The most up to date documentation is always:

```bash
    xthematic --help
```

Man/info pages or online docs are not written.

### License
This project is licensed under the MIT License - see the 
[LICENSE](https://github.com/taesko/xthematic/blob/master/LICENSE.txt) file for details.

### Authors
* Antonio Todorov

### Acknowledgements
* the [pywal](https://github.com/dylanaraps/pywal) project for inspiration and example of code printing 
escape sequences which was part of the earliest version.
