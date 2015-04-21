#!/usr/bin/env python

import os
import sys
import time
import subprocess
import threading
import argparse
import csv
import Queue
import ConfigParser

class SpannerConfigParser (type):
    config = ConfigParser.ConfigParser()
    config.read('spanner.cfg')
    def __getattr__(self, name):
        return self.config.get('DEFAULT', name.lower())

class CFG (object):
    __metaclass__ = SpannerConfigParser

def ipmi_reboot_pxe(address, username, password):
    if address == '' or address == '0.0.0.0' or address == '255.255.255.255' or address == '127.0.0.1':
        return True
    p1 = subprocess.Popen('ipmitool -I ' + CFG.ipmi_interface + ' -H ' + address + ' -U ' + username + ' -P ' + password + ' chassis bootdev pxe 2>&1', shell=True, stdout=subprocess.PIPE)
    out, err = p1.communicate()
    if out.strip() != 'Set Boot Device to pxe':
        return False
    p2 = subprocess.Popen('ipmitool -I ' + CFG.ipmi_interface + ' -H ' + address + ' -U ' + username + ' -P ' + password + ' chassis power reset 2>&1', shell=True, stdout=subprocess.PIPE)
    out, err = p2.communicate()
    if out.strip() != 'Chassis Power Control: Reset':
        return False
    return True
    
def ipmi_reboot_only(address, username, password):
    p = subprocess.Popen('ipmitool -I ' + CFG.ipmi_interface + ' -H ' + address + ' -U ' + username + ' -P ' + password + ' chassis power reset 2>&1', shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    if out.strip() != 'Chassis Power Control: Reset':
        return False
    return True

def ipmi_boot(address, username, password):
    p = subprocess.Popen('ipmitool -I ' + CFG.ipmi_interface + ' -H ' + address + ' -U ' + username + ' -P ' + password + ' chassis power on 2>&1', shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    #if out.strip() != 'Chassis Power Control: Reset':
    #    return False
    return True

def ipmi_shutdown(address, username, password):
    p = subprocess.Popen('ipmitool -I ' + CFG.ipmi_interface + ' -H ' + address + ' -U ' + username + ' -P ' + password + ' chassis power off 2>&1', shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    #if out.strip() != 'Chassis Power Control: Reset':
    #    return False
    return True

def cobbler_import(hostname, address_ipv4, address_mac, password, interface, disk):
    p1 = subprocess.Popen('cobbler system remove --name=' + hostname, shell=True, stdout=subprocess.PIPE)
    out, err = p1.communicate()
    p2 = subprocess.Popen('cobbler system add --name=' + hostname + ' --profile=' + CFG.cobber_profile + ' --mac=' + address_mac + ' --ip-address=' + address_ipv4 + ' --subnet=' + CFG.network_netmask + ' --gateway=' + CFG.network_gateway + ' --interface=ethx --name-servers=' + CFG.network_nameservers + ' --dns-name=' + hostname + '.localdomain --hostname=' + hostname + '.localdomain --kickstart=' + CFG.spanner_home + '/spanner.seed --kopts="netcfg/choose_interface=' + interface + ' partman-auto/disk=' + disk + '" --ksmeta="spanner_eth=' + interface + ' spanner_pwd=' + password + ' spanner_src=' + CFG.cobber_repository + '" 2>&1', shell=True, stdout=subprocess.PIPE)
    out, err = p2.communicate()
    return True

def cobbler_sync(echo=False):
    p = subprocess.Popen('cobbler sync', shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    if echo:
        print out
    return True

'''
def cobbler_hack(hostname):
    hostnames_hack = ['qemu-01']
    for hostname_hack in hostnames_hack:
        if hostname_hack ==  hostname:
            p = subprocess.Popen('cobbler system edit --name=' + hostname + ' --kopts="netcfg/choose_interface=eth0 partman-auto/disk=/dev/vda" 2>&1', shell=True, stdout=subprocess.PIPE)
            out, err = p.communicate()
            return True
    return False

def system_ping(address_ipv4):
    p = subprocess.Popen('ping -c 1 ' + address_ipv4, shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    return True
'''

def system_ssh_test(hostname, address_ipv4):
    p = subprocess.Popen('sshpass -p ' + CFG.default_password + ' ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o ConnectTimeout=1 ' + address_ipv4 + '  "hostname" 2>&1', shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    if out.strip() != hostname:
        return False
    return True

def system_ssh_command(hostname, address_ipv4, command):
    p = subprocess.Popen('sshpass -p ' + CFG.default_password + ' ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o ConnectTimeout=3 ' + address_ipv4 + "  '" + command + "'", shell=True)
    p.communicate()
    return True

def system_ssh_command_async(hostname, address_ipv4, command, queue):
    p = subprocess.Popen('sshpass -p ' + CFG.default_password + ' ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o ConnectTimeout=3 ' + address_ipv4 + "  '" + command + "' 2>&1", shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    queue.put([hostname, out])
    return True

def system_scp(hostname, address_ipv4, source, target):
    p = subprocess.Popen('sshpass -p ' + CFG.default_password + ' scp -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -r ' + source + ' ' + address_ipv4 + ':' + target + '', shell=True)
    p.communicate()
    return True
    
def action_deploy(data):
    print 'cobbler import'
    for row in data:
        print row[0],
        print cobbler_import(row[0], row[1], row[2], row[6], row[4], row[5]),
        print 'done'
    print 'cobbler sync'
    cobbler_sync() 
    print 'pxe reboot'
    for row in data:
        print row[0],
        print ipmi_reboot_pxe(row[3], row[7], row[8]),
        print 'done'
    print 'done'
    
def action_sync(data):
    print 'cobbler import'
    for row in data:
        print row[0],
        print cobbler_import(row[0], row[1], row[2], row[6], row[4], row[5]),
        print 'done'
    print 'cobbler sync'
    cobbler_sync(True)

def action_ping(data):
    for row in data:
        print row[0] + ' ...' ,
        print system_ssh_test(row[0], row[1])
        
def action_reboot(data):
    for row in data:
        print row[0] + ' ...' ,
        print ipmi_reboot_only(row[3], row[7], row[8])
        
def action_boot(data):
    for row in data:
        print row[0] + ' ...' ,
        print ipmi_boot(row[3], row[7], row[8])
        
def action_shutdown(data):
    for row in data:
        print row[0] + ' ...' ,
        print ipmi_shutdown(row[3], row[7], row[8])
        
def action_copy(data, source, target):
    for row in data:
        print row[0] + ' ...' ,
        print system_scp(row[0], row[1], source, target)
    
def action_hosts(target, hosts):
    command = 'sed -i "/SPANNER-MANAGED/d" /etc/hosts'
    for row in hosts:
        command += ' ; echo "' + row[1] + '		' + row[0] + '.localdomain		' + row[0] + '		# SPANNER-MANAGED" >>/etc/hosts'
    print command
    for row in data:
        print row[0] ,
        system_ssh_command(row[0], row[1], command)
        print ' done'
    
def _action_batch_echo_output(output):
    output = output[-384:]
    lines = output.splitlines()
    count_lines = len(lines)
    start = count_lines - 3
    if start < 0:
        start = 0
    for x in range(start, count_lines):
        print lines[x]

def action_batch(data, command, async):
    if not os.path.exists(CFG.spanner_home + '/log/'): os.makedirs(CFG.spanner_home + '/log/')
       
    if async == False:
        for row in data:
            print row[0] + " begin"
            system_ssh_command(row[0], row[1], command)
            print row[0] + " done"
    else:
        threads = []
        queue = Queue.Queue()
        count = 0
        count_done = 0
        
        for row in data:
            print row[0] + ' ... '
            t = threading.Thread(target=system_ssh_command_async, args=(row[0], row[1], command, queue))
            threads.append(t)
            t.start()
            count = count + 1
        
        fl = open(CFG.spanner_home + '/log/_log.log', 'a')
        for x in range(0, count):
            ret = queue.get()
            count_done = count_done + 1
            print ''
            _action_batch_echo_output(ret[1])
            print ret[0] + ' ' + str(count_done) + '/' + str(count) + ' done'
            fsl = open(CFG.spanner_home + '/log/' + ret[0] +'.log', 'w')
            fsl.write(ret[1])
            fsl.close()
            fl.write('\n')
            fl.write(ret[1])
        fl.close()
 
def action_script(data, script, async):
    print 'prepare script'
    for row in data:
        system_ssh_command(row[0], row[1], 'rm -r /tmp/spanner.sh > /dev/null 2>&1')
        system_scp(row[0], row[1], args.copy_source, '/tmp/spanner.sh')
        system_ssh_command(row[0], row[1], 'chmod +x /tmp/spanner.sh')
        print row[0] + " done"
    print 'run script'
    action_batch(data, '/tmp/spanner.sh', async)

    
def spanner_confirm(message='This action might be dangerous.'):
    print message
    sys.stdout.write('Are you sure you want to continue (yes/no)? ')
    yes = set(['yes','y'])
    no = set(['no','n'])

    while True:
        choice = raw_input().lower()
        if choice in yes:
           return True
        elif choice in no:
           return False
        else:
           sys.stdout.write("Please type 'yes' or 'no': ")

def spanner_param_nonone(params):
    for param in params:
        if param == None:
            print 'Param error!'
            return False
    return True

def _spanner_load_item(row):
    for i in range(2, 9):
        value = ''
        if i==2: value = '00:00:00:00:00:00'
        if i==3: value = '127.0.0.1'
        if i==4: value = CFG.default_interface
        if i==5: value = CFG.default_disk
        if i==6: value = CFG.default_password
        if i==7: value = CFG.default_ipmi_username
        if i==8: value = CFG.default_ipmi_password
        if (row[i:] == []): row[i:] = [value]
        if (row[i] == ''): row[i] = value
    return row

def spanner_load(targets):
    with open(CFG.datafile, 'rb') as datafile:
        data = csv.reader(datafile, delimiter=',', quotechar='"')
        data_tar = []
        data_all = []
        for row in data:
            row = _spanner_load_item(row)
            data_all.append(row)
            if len(targets) == 0 or row[0] in targets:
                data_tar.append(row)
        return data_tar,data_all
    return [],[]
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['list','ping','test','shell','copy','script','deploy','sync','reboot','boot','shutdown','hosts'])
    parser.add_argument('-c', dest='command')
    parser.add_argument('-s', dest='copy_source')
    parser.add_argument('-t', dest='copy_target')
    parser.add_argument('-a', dest='async', action='store_true')
    parser.add_argument('target', nargs='*')
    args = parser.parse_args()
    
    data_tar, data_all = spanner_load(args.target)
    
    if args.action == 'list':
        for row in data_tar:
            print ', '.join(row)
    
    if args.action == 'ping' or args.action == 'test':
        action_ping(data_tar)
        
    if args.action == 'shell':
        if spanner_param_nonone([args.command]):
            action_batch(data_tar, command, args.async)

    if args.action == 'copy':
        if spanner_param_nonone([args.copy_source,args.copy_target]):
            action_copy(data_tar, args.copy_source, args.copy_target)
     
    if args.action == 'script':
        if spanner_param_nonone([args.copy_source]):
            action_script(data_tar, args.copy_source, args.async)
    
    if args.action == 'deploy':
        if spanner_confirm():
            action_deploy(data_tar)
    
    if args.action == 'sync':
        action_sync(data_tar)
        
    if args.action == 'reboot':
        if spanner_confirm():
            action_reboot(data_tar)
    
    if args.action == 'boot':
        if spanner_confirm():
            action_boot(data_tar)
    
    if args.action == 'shutdown':
        if spanner_confirm():
            action_shutdown(data_tar)

    if args.action == 'hosts':
        if spanner_confirm():
            action_hosts(data_tar, data_all)