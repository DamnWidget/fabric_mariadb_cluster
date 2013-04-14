daemon_script = """#!/bin/bash

mysqld --wsrep_cluster_address=gcomm://{} > /var/log/mariadb_cluster.log 2>&1 &
"""
