# strong-pm

[Unit]
Description=StrongLoop Process Manager

# To start/stop strong-pm service manually, run:
#
# systemctl start strong-pm
# systemctl stop strong-pm

[Service]
Type=simple
ExecStart=/home/sota/sota/server/node-v12.6.0-linux-x64/bin/node /home/sota/sota/server/node-v12.6.0-linux-x64/lib/node_modules/strongloop/node_modules/strong-pm/bin/sl-pm.js --listen 8701 --base /var/lib/strong-pm --base-port 3000 --driver direct
WorkingDirectory=/

Restart=on-failure
Environment="HOME=REPLACE_TO_REAL_PATH"

User=strong-pm
Group=strong-pm

LimitNOFILE=50000
LimitCORE=infinity

StandardInput=null
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target
