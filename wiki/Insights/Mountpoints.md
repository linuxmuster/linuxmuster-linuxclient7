The Samba shares are mounted in user context using the [sudo tools](Sudo-tools). There are two locations a share can be mounted to:
1. Hidden: `/srv/samba/$USER`. This is used for shares the user should not see, e.g. sysvol.
2. Visible: `/home/$USER/media`. This is used for all shares the user should see in the nautilus sidebar, e.g. their home.
The root folder of the shares is automatically hidden form nautilus by creating a `.hidden` file containing its name in its parent directory.  
As all shares are mounted in a user-specific subfolder, it is also possible to switch users.