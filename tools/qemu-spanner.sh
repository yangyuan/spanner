qemu-system-x86_64 --enable-kvm -m 8096 -smp 4 -net nic,model=virtio,macaddr=0A-1B-2C-3D-4E-5F -net tap,script=qemu-ifup,downscript=qemu-ifdown --drive file=spanner.qcow2,if=virtio -vnc :0 -daemonize
