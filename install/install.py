#!/usr/bin/env python

import os
import re
import subprocess
import ConfigParser

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class SpannerConfigParser (type):
    config = ConfigParser.ConfigParser()
    config.read('../spanner.cfg')
    def __getattr__(self, name):
        return self.config.get('DEFAULT', name.lower())

class CFG (object):
    __metaclass__ = SpannerConfigParser

def execute(commands):
    p = subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    return out

def accessible(path):
    if not os.path.isfile(path):
        print path + ' not exists!\n'
        return False
    if not os.access(path, os.R_OK|os.W_OK):
        print path + ' not accessible!\n'
        return False
    return True

def configure_apache():
    version = execute("apache2 -V | grep -i 'server\sversion' | awk -F ':' '{print $2}' | awk '{print $1}' | awk -F '/' '{print $2}'")
    if version.startswith('2.4'):
        text = open(PATH + '/install/apache/spanner.conf').read()
        text = re.sub(r'\$', CFG.spanner_home, text)
        out = open(PATH + '/tmp/spanner.conf', 'w')
        out.write(text)
        out.close
        os.rename(PATH + '/tmp/spanner.conf', '/etc/apache2/conf-enabled/spanner.conf')
    elif version.startswith('2.2'):
        text = open(PATH + '/install/apache/spanner_22.conf').read()
        text = re.sub(r'\$', CFG.spanner_home, text)
        out = open(PATH + '/tmp/spanner.conf', 'w')
        out.write(text)
        out.close
        os.rename(PATH + '/tmp/spanner.conf', '/etc/apache2/conf.d/spanner.conf')

def configure_cobbler():
    if not accessible('/etc/cobbler/settings'): return
    if not accessible('/etc/cobbler/dhcp.template'): return
    
    text = open('/etc/cobbler/settings').read()
    text = re.sub(r'^manage_dhcp\s*:.*$', 'manage_dhcp: 1', text, 0, re.M)
    text = re.sub(r'^server\s*:.*$', 'server: 0.0.0.0', text, 0, re.M)
    text = re.sub(r'^next_server\s*:.*$', 'next_server: 0.0.0.0', text, 0, re.M)
    out = open('/etc/cobbler/settings', 'w')
    out.write(text)
    out.close
    
    
    text = open('/etc/cobbler/dhcp.template').read()
    text = re.sub(r'subnet[0-9\.\s]*netmask[0-9\.\s]*{[^}]*}',
'subnet ' + CFG.network_gateway + ' netmask ' + CFG.network_netmask + ' {\n' \
'     option routers             ' + CFG.network_gateway + ';\n' \
'     option domain-name-servers ' + CFG.network_nameservers + ';\n' \
'     option subnet-mask         ' + CFG.network_netmask + ';\n' \
'     range dynamic-bootp        ' + CFG.network_openrange + ';\n' \
'     filename                   "/pxelinux.0";\n' \
'     default-lease-time         21600;\n' \
'     max-lease-time             43200;\n' \
'     next-server                $next_server;\n' \
'}', text, 0, re.M|re.S)
    out = open('/etc/cobbler/dhcp.template', 'w')
    out.write(text)
    out.close
    

if __name__ == "__main__":
    configure_apache()
    print execute('service apache2 restart')
    configure_cobbler()
    print execute('service cobbler restart')
    print execute('cobbler sync')