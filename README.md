MariaDB Cluster Fabric install for Ubuntu 12.04 LTS
===================================================
Copyright (C) 2013 Oscar Campos
Licensed under the terms of hte GPL Public License

HOWTO
-----
Install fabric with `pip` or `easy_install`:

	pip install fabric

Get this repo content:

	git clone git://github.com/DamnWidget/fabric_mariadb_cluster

Edit the settings file and use the fab commadn line to install and configure it:

	fab INSTALL_FULL

You can then `start` or `stop` your cluster with:

	fab mysql:<command>

Where command is one of: `status`, `start`, `stop`, `restart`. The Cluster log is saved in `/var/log/mariadb_cluster.log`

That's all!
