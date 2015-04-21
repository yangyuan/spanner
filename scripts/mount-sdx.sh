# format mount opt
parted -s -a optimal /dev/sdb mklabel gpt -- mkpart primary ext4 1 -1
mkfs.ext4 /dev/sdb1
echo "UUID=$(blkid -o value -s UUID /dev/sdb1) /opt            ext4    defaults        0       2" >> /etc/fstab