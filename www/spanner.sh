#!/bin/sh

echo "blacklist ipv6" >> /etc/modprobe.d/blacklist.conf
echo "UseDNS no" >> /etc/ssh/sshd_config

apt-get update
apt-get -y --force-yes install bridge-utils
apt-get -y --force-yes install git
apt-get -y --force-yes install vlan
