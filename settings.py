
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

# custer details
cluster_name = 'My_MariaDB_Cluster'
cluster_hosts = ['root@node1', 'root@node2', 'root@node3', 'root@node4']
hosts_mapping = {
    'node1': ('192.168.0.101', '?pc.boostrap=1'),  # this one is the bootstrap
    'node2': ('192.168.0.102', 'node1,node3,node4?pc.wait_prim=no'),
    'node3': ('192.168.0.103', 'node1,node2,node3?pc.wait_prim=no'),
    'node4': ('192.168.0.104', 'node1,node2,node3?pc.wait_prim=no')
}
hosts_plain_list = 'node1,node2,node3,node4'

# MariaDB
mariadb_root_password = 'my-ultra-secret-password'

# repository server
# look at: https://downloads.mariadb.org/mariadb/repositories/
repo_server = \
    'http://ftp.heanet.ie/mirrors/mariadb/repo/5.5/ubuntu precise main'
