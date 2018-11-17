#!/bin/sh
# +-----------------------------------------------------------------------+
# |       Author: Cheng Wenfeng   <277546922@qq.com>                      |
# +-----------------------------------------------------------------------+
#
wkdir=$(cd $(dirname $0); pwd)
if [ ! -f $wkdir/main.py ] ;then
   wkdir=$(cd $(dirname $0)/../; pwd)
fi
PATH=$PATH:$wkdir/sbin
confdir="$wkdir/plugins/ftpd"
piddir="$wkdir/plugins/ftpd/run"

case "$1" in
  start)
        echo -en "Starting FTPServer:\t\t"
        $wkdir/sbin/start-stop-daemon --start --background --exec $wkdir/sbin/pure-config.py -- $confdir/ftp.conf
        RETVAL=$?
        #echo
        if [ $RETVAL -eq 0 ] ;then
	   echo "Done..."
	else
	   echo "Failed"
	fi
        ;;
  stop)
	echo -en "Stoping FTPServer:\t\t"
	$wkdir/sbin/start-stop-daemon --stop  --name pure-ftpd >/dev/null 2>&1
	RETVAL=$?
        #echo
        if [ $RETVAL -eq 0 ] ;then
	   echo "Done..."
	else
	   echo "Failed"
	fi
        ;;
  status)
        for pid in  $( ps ax|grep pure-ftpd |grep -v 'grep'|awk '{print $1}');do
	   echo $pid
	done
        ;;
  restart)
        $0 stop
        $0 start
        RETVAL=$?
        ;;
  *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 2
esac
