#!/bin/bash
IF=`ip route | awk '$1 ~ "172.30.0.0/24" {print $3}'`
if test $IF ; then
    : all well
else
    echo Interface not found
fi
CLOUDINIT=/etc/cloud/cloud.cfg.d/50-curtin-networking.cfg

cp -p "$CLOUDINIT" "$CLOUDINIT".`date +%s`
cat << EOF >> "$CLOUDINIT"
  vlans:
    vlan.18:
      id: 18
      mtu: 1500
      link: $IF
EOF
cat "$CLOUDINIT" | sed -e 's/^\( *\)/\1\1/g' > /etc/netplan/50-cloud-init.yaml
netplan generate
netplan apply
exit 0
