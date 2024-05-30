#!/bin/bash
IF=`ip route | awk '$1 ~ "172.30.0.0/24" {print $3}'`
if test $IF ; then
    : all well
else
    echo "External interface not found (only error in Kista)"
    exit 0 # do not fail the install
fi
CLOUDINIT=/etc/cloud/cloud.cfg.d/50-curtin-networking.cfg

if grep vlan.18 "$CLOUDINIT" >/dev/null ; then
    : already done
else
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
fi

for SYSCONFFILE in /etc/sysctl.d/10-network-security.conf /usr/lib/sysctl.d/50-default.conf ; do
    if test -f "$SYSCONFFILE" ; then
	# patch boot config
	sed -i 's/rp_filter *= *2/rp_filter=0/g' "$SYSCONFFILE"
	# patch running config
	for f in /proc/sys/net/ipv4/conf/*/rp_filter ; do echo 0 > $f; done
    else
	echo "Warning: $SYSCONNFILE not found"
    fi
done

exit 0
