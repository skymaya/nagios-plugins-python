# Python plugins for Nagios Core

## Synopsis

A collection of plugins written in python for Nagios Core.

## Installation

Upload the plugins to your Nagios plugins directory; in most cases it will be /usr/local/nagios/libexec.

They will most likely need to be executable so run the following for each .py file, replacing "plugin" with the plugin name:

`chmod 700 plugin.py`

They will also need to be owned by the nagios user:

`chown nagios:nagios plugin.py`

## Usage

Each plugin needs, at minimum, a check command defined for it. The location where these commands are stored may vary. Each plugin contains a commented section at the top with a sample check command and an example service check that would be added to the host's configuration file.

## Uninstalling

Remove the plugin file from the plugins directory, remove the check command, and remove the service check from any host configuration files.
