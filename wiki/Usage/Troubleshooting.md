## General
- The first troubleshooting step you should always try is to run `linuxmuster-linuxclient7 setup` this will help in many cases.
- A wrong system time also causes many problems!
- You can always check if the domain join is working using the command `linuxmuster-linuxclient7 status`

## Logging
- All logs are written to /var/log/syslog
- All linuxmuster-linuxclient7 relevant logs can be printed using `linuxmuster-linuxclient7 print-logs`
- If you want a compact output, use `linuxmuster-linuxclient7 print-logs -c`

## Error popups on login
There are some common error popups that might occur on login:
- `lpadmin: Unable to query printer: Der Drucker oder die Klasse existiert nicht.` This usually means that some printer, which is assigned to this machine, does not exist or has the wrong name in CUPS