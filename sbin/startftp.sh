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
pidfile="$wkdir/plugins/ftpd/ftpd.pid"
binIpath=$(which pure-config.py)
#binIIpath=$(which pure-uploadscript)


case "$1" in
  start)
        echo -en "Starting FTPServer:\t\t"
        #$binIIpath -B -r $wkdir/sbin/pureftpd_uploadscript.sh >/dev/null 2>&1 
        $wkdir/sbin/start-stop-daemon --start --background -m --pidfile $pidfile --exec $wkdir/venv/bin/python -- $binIpath $confdir/ftp.conf
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
        #$wkdir/sbin/start-stop-daemon --stop  --name pure-ftpd >/dev/null 2>&1
        for pid in  $( ps ax|grep pure-ftpd |grep -v 'grep'|awk '{print $1}');do
            kill -9 $pid >/dev/null 2>&1 
        done
        RETVAL=$?
        #echo
        if [ $RETVAL -eq 0 ] ;then
           rm -f $pidfile >/dev/null 2>&1
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
