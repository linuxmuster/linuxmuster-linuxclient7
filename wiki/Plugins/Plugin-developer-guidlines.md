These guidelines are meant to make sure that plugins have a consistent format and are properly maintained.

#### Maintainer

The maintainer of a plugin has to make sure to consider these things before publishing it:

- The maintainer has to offer support and updates for their plugins. 
- The maintainer has to test their plugin and ensure that it will not break anything in a users system
- The linuxmuster team **will not offer support, updates or tests**
- Should the maintainer not respond to a support request within 30 days, the plugin will be marked `unmaintained`
- Your code will be published under the [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html)

#### Plugin page

The page of the plugin in this wiki as to stick to the template to make it machine-readable! The linuxmuster team may make changes to your plugin page when the template is changed.

#### Functional

These are some functional guidelines you should stick to:

- User-specific settings should be stored in `$SERVERHOME/.linux-settings`
- More complex plugins should be written in python
- The [`linuxmusterLinuxclient7` api](https://linuxmuster.github.io/linuxmuster-linuxclient7/index.html) should be used where possible