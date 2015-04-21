# SPANNER
Cluster Distribution and Management

## Usage

#### Cluster Management Functions (BULK SHH)
* install `ssh` `scp` `sshpass`
* edit `data.csv` and `spanner.cfg`
* run `./spanner.py list/ping/shell/copy/script/hosts`

#### Cluster Power Management Functions (IPMI)
* install `ipmitools`
* edit `data.csv` and `spanner.cfg`
* run `./spanner.py reboot/boot/shutdown`

#### Cluster Distribution Functions (COBBLER: DHCP+PXE)
* install `apache2-utils` `isc-dhcp-server` `bind9` `cobbler`
* import cobbler profile from iso `mount -o loop /opt/ubuntu-12.04.5-server-amd64.iso /mnt && cobbler import --name=ubuntu-12.04.5-server --path=/mnt --breed=ubuntu`
* edit `data.csv` and `spanner.cfg`
* run `./install/install.py`
* run `./spanner.py deploy/sync`

## spanner.py

#### class CFG
read configurations of spanner.cfg

#### def spanner_* ()
functions for spanner itself

#### def action_* ()
functions for handle user commands

#### def _* ()
private functions
