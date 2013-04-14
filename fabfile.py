
# Copyright 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Fabfile to install and configure a full functional MariaDB Galera Cluster

This script has been tested in Ubuntu 12.04 TLS only but it shoudl work with
other versions of Debian based distributions

Use the `INSTALL_FULL` command to (wait for it) install it full and configure
the iptables to close the access fro outside the network to the MariaDB
server but allow them to work together.

NOTE: The script automatic allows the SSH 22 port, comment or change it if
this is not your desired behaviour.

When the cluster is installed you DONT need to run any `install` command
anymore.

NOTE: Shoudl be nice if you already have your server configured to allow
login using SSH keys

WARNING: You MUST configure the settings.py file before runing this :)

Copyright (c) 2013 Oscar Campos <oscar.campos@member.fsf.org>
Published under the terms of the GPLv3 License
"""

from fabric.utils import puts, warn
from fabric.api import run, quiet, env
from fabric.decorators import hosts, parallel

import settings


@parallel
@hosts(settings.cluster_hosts)
def INSTALL_FULL():
    """Install/configure MariaDB Cluster in Ubuntu 12.04 (and probably others)
    """

    add_mariadb_repo()
    install_galera()
    configure_firewall()


@parallel
@hosts(settings.cluster_hosts)
def ubuntu_update():
    """Update the ubuntu distributions: use at your own risk
    """

    with quiet():
        run('apt-get update')
        is_upgraded = run('apt-get -y upgrade')

    if is_upgraded.failed is False:
        puts('Distribution up to date')


@parallel
@hosts(settings.cluster_hosts)
def cluster_reboot():
    """Reboot the full cluster
    """

    run('reboot')


@parallel
@hosts(settings.cluster_hosts)
def add_mariadb_repo():
    """Add MariaDB Ubuntu repository from configured server
    """

    with quiet():
        result = run(
            'apt-get -y --no-upgrade install python-software-properties')

    if result.failed is False:
        puts('Python Software Properties installed!')
    else:
        warn('Python Software Properties was not installed!!')

    with quiet():
        result = run(
            'apt-key adv --recv-keys --keyserver keyserver.ubuntu.com '
            '0xcbcb082a1bb943db')

    if result.failed is False:
        puts('Key added to APT Keys!')
    else:
        warn('Key was not added to APT keys!!')

    with quiet():
        result = run(
            'add-apt-repository \'deb {}\''.format(settings.repo_server))

    if result.failed is False:
        puts('Heanet Repository added!')
    else:
        warn('Heanet Repository was not added!!')

    with quiet():
        result = run('apt-get update')

    if result.failed is True:
        warn('I can not update the repositories, manual operation is need')
        return


@parallel
@hosts(settings.cluster_hosts)
def install_galera():
    """Installs MariaDB Galera Cluster
    """

    host_name = env.get('host')
    index = settings.cluster_hosts.index(host_name)
    donor = settings.cluster_hosts[index + 1]

    with quiet():
        run(
            'echo "mariadb-galera-server-5.5 mysql-server/root_password_again '
            'password {}" | debconf-set-selections'.format(
                settings.mariadb_root_password
            )
        )
        run(
            'echo "mariadb-galera-server-5.5 mysql-server/root_password '
            'password {}" | debconf-set-selections'.format(
                settings.mariadb_root_password
            )
        )
        r = run('apt-get -y --no-upgrade install mariadb-galera-server galera')
    if r.failed is False:
        run(
            'mysql -u root -p{} -e "CREATE USER \'root\'@\'%\' "'
            'IDENTIFIED BY \'{}\';"')
        run(
            'mysql -u root -p{} -e "GRANT ALL PRIVILEGES ON *.* TO '
            '\'root\'@\'%\' WITH GRANT OPTION;"')
        run('update-rc.d -f mysql remove')
        run('service mysql stop')
        import my_cnf
        run('echo "{my_cnf}" > /etc/mysql/my.cnf'.format(
            my_cnf=my_cnf.mariadb_conf.format(
                settings=settings, host_name=host_name, donor=donor)))
        puts('MariaDB Galesa Server Installed!')
    else:
        warn('MariaDB Galera Server coul not be installed!!')


@parallel
@hosts(settings.cluster_hosts)
def configure_firewall():
    """Configure the firewall and set the hosts aliases
    """

    for host, ip in settings.hosts_mapping.iteritems():
        if env.get('host') != host:
            run('echo "{}  {}" >> /etc/hosts'.format(ip[0], host))

    run('ufw allow ssh')
    run('ufw allow 80/tcp')
    run('ufw allow 443/tcp')

    for host, ip in settings.hosts_mapping.iteritems():
        if env.get('host') != host:
            run('ufw allow from {}'.format(ip[0]))


@parallel
@hosts(settings.cluster_hosts)
def mysql(command=None):
    """Controls the MySQL cluster: start, stop, status, restart
    """

    host = settings.hosts_mapping[env.get('host')][1]
    start = (
        'mysqld --wsrep_cluster_address="'
        'gcomm://mambalancer,mambaone,mambatwo?{}" '
        '> /tmp/mariadb_cluster.log 2>&1 &'.format(host)
    )
    stop = 'kill $(ps ax | grep -v grep | grep mysqld | awk \'{print $1}\')'

    if command not in ('status', 'stop', 'start', 'restart'):
        warn('Unknown command: {}\n'
             'Available commands: status start, stop restart'.format(command))
    else:
        if command not in ('start', 'restart'):
            if command == 'status':
                result = run('ps aux | grep -v grep | grep mysqld || echo No')
            elif command == 'stop':
                with quiet():
                    result = run(stop)

                if result.failed is False:
                    puts('MariaDB Cluster Node Down')
                else:
                    puts('Seems like there was some error...')
        else:
            if command == 'start':
                with quiet():
                    result = run(start)

                if result.failed is False:
                    puts('MariaDB Cluster Node Started')
                else:
                    warn(
                        'Some error occurred, maybe there '
                        'is a node already running?'
                    )
            elif command == 'restart':
                with quiet():
                    run(stop)
                    result = run(start)

                if result.failed is False:
                    puts('MariaDB Cluster Node Restarted')
                else:
                    warn('Can not restart the node :(')
