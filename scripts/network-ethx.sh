echo "" >> /etc/network/interfaces
echo "auto eth1" >> /etc/network/interfaces
echo "iface eth1 inet static" >> /etc/network/interfaces
echo "$(cat /etc/network/interfaces | grep address | sed 's/192.168.0./192.168.1./g')" >> /etc/network/interfaces
echo "    netmask 255.255.255.0" >> /etc/network/interfaces

/etc/init.d/networking restart