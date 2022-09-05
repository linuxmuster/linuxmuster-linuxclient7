Plugins can be used to expand the functionality of the linuxmuster-linuxclient7. The intention is to keep special use cases, like conky or static linking of folders like `Documents` and `Pictures`, out of the main codebase to keep it sleek.  
Plugins consist of hook-scripts which are placed inside the respective folders in `/etc/linuxmuster-linuxclient7`.

If you have an issue with a plugin, please contact the maintainer directly.

## Available plugins

- [Conky](Plugin-Conky)

## Adding your own plugin

To add your own plugin to this list, please follow these steps:
- [Fork this repo](https://github.com/linuxmuster/linuxmuster-linuxclient7/fork)
- Add a description and the code of your plugin in `wiki/Plugins` by copying the `_Plugin-Template.md` file
- Create a pull request