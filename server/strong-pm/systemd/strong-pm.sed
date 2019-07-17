#!/bin/bash
# StrongLoop Process Manager 

# Source function library.
. /etc/rc.d/init.d/functions

# Path to the apachectl script, server binary, and short-form for messages.
prog="StrongLoop PM"
pidfile=${PIDFILE-/var/run/slp.pid}
lockfile=${LOCKFILE-/var/lock/subsys/slp}
RETVAL=0

root_path="REPLACE_TO_REAL_PATH"
node_path=$root_path/node-v12.6.0-linux-x64

slpm=$node_path/bin/slpmnodesvc

start() {
        echo -n $"Starting $prog: "
        HOME=$root_path/strong-pm/pm $slpm $node_path/lib/node_modules/strongloop/node_modules/strong-pm/bin/sl-pm.js --listen 8701 --base /var/lib/strong-pm --base-port
 3000 --driver direct
        RETVAL=$?
        echo
        [ $RETVAL = 0 ] && touch ${lockfile}
        return $RETVAL
}

stop() {
  echo -n $"Stopping $prog: "
  killproc -p ${pidfile} -d 10 $slpm
  RETVAL=$?
  echo
  [ $RETVAL = 0 ] && rm -f ${lockfile} ${pidfile}
}

reload() {
    echo -n $"Reloading $prog: "
    killproc -p ${pidfile} $slpm -HUP
    RETVAL=$?
}

case "$1" in
  start)
  start
  ;;
  stop)
  stop
  ;;
  status)
        status -p ${pidfile} $slpm
  RETVAL=$?
  ;;
  restart)
  stop
  start
  ;;
  condrestart)
  if [ -f ${pidfile} ] ; then
    stop
    start
  fi
  ;;
  reload)
        reload
  ;;
  help)
  ;;
  *)
  echo $"Usage: $prog {start|stop|restart|condrestart|reload|status|help}"
  exit 1
esac

exit $RETVAL
