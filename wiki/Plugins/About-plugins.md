Plugins can be used to expand the functionality of the linuxmuster-linuxclient7. The intention is to keep special use cases, like conky or static linking of folders like `Documents` and `Pictures`, out of the main codebase to keep it sleek.  
Plugins consist of hook-scripts which are placed inside the respective folders in `/etc/linuxmuster-linuxclient7`.

**If you have an issue with a plugin, please contact the maintainer directly.**

## Plugin status

Every plugin has a **status**. There are four types:
- 🧪 experimental - the plugin is highly experimental and may cause damage or data loss
- 🔧 testing - the plugin is not fully tested and may cause damage or data loss 
- ✅ stable - the plugin is fully tested and will not have any unexpected side effects
- 🚧 unmaintained - the maintainer of the plugin does no longer provide updates for it, it may not work as expected

## Available plugins

- [Conky](Plugin-conky): Start Conky when a user logs in

## Adding your own plugin

To add your own plugin to this list, please follow these steps:
- [Fork this repo](https://github.com/linuxmuster/linuxmuster-linuxclient7/fork)
- Copy the file `_Plugin-Template.md` in `wiki/Plugins` to `Plugin-<your plugin name>.md`
- Make sure, you agree to the [developer guidelines](Plugin-developer-guidelines)
- Edit the file and fill in your description and code
- Add your plugin and a short description to this file
- Push the changes to your fork
- Create a pull request