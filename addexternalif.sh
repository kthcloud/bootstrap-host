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
fi

# find IB interface
IBIP=$(ip addr | awk '$1 == "inet" && $2 ~ "^172.30" {sub("\\.0\\.",".1.",$2); print $2}')
if test "$IBIP" ; then
    apt install -y rdma-core
    apt install -y infiniband-diags
    IBIF=$(dmesg | awk '$3 == "mlx5_core" && $6 == "renamed" {print $5 ; exit}')
    if test "$IBIF"; then
	if grep $IBIF "$CLOUDINIT"; then
	    : already done
	else
	    cat <<EOF>/tmp/ibsniplet
    $IBIF
      addresses:
      - $IBIP
      mtu: 4092
EOF
	    awk ' { print } ; $1 == "ethernets:" { while (getline <"/tmp/ibsniplet")  print ; }' < "$CLOUDINIT" > "$CLOUDINIT.new"
	    if diff "$CLOUDINIT" "$CLOUDINIT.new" |egrep '^<' > /dev/null ; then
		: we did screw up the file
	    else
		mv  "$CLOUDINIT.new" "$CLOUDINIT"
	    fi
	fi
    fi
fi
# Generate new netplan
cat "$CLOUDINIT" | sed -e 's/^\( *\)/\1\1/g' > /etc/netplan/50-cloud-init.yaml
netplan generate
netplan apply

# Fix asymeric routing
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
