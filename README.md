A lot of the codes come from https://github.com/jon1012/mihome

1. Turn on developer mode on aqara(xiaomi) gateway. (from android app)

2. modified the ini file. 

3. run it.  it will publish info to mqtt server on xiaomi/# by default

4. to issue on/off command, send ON or OFF to the mqtt channel the script subscribes to (xiaomi/blah..blah /command)
