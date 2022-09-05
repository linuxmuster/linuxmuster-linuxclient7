# Using Conky
- install conky: `apt install conky`
- add some lines to your sessionstart script:
```
# start conky
killall /usr/bin/conky &
sleep 1
/usr/bin/conky &
```  