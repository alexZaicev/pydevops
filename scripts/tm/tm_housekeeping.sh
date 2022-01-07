#!/bin/bash

# remove workbench tarballs and backed up workbench directories
find ~ -maxdepth 1 -type f -mtime +3 -name 'wbGMP_*.tar.gz' -exec rm {} \;
find ~ -maxdepth 1 -type f -mtime +3 -name 'workbench.tm-*.tar.gz' -exec rm {} \;
find ~ -maxdepth 1 -type d -mtime +3 -name 'install-*' -exec rm -r {} \;
find ~ -maxdepth 1 -type d -mtime +3 -name 'install_*' -exec rm -r {} \;

# remove artifacts left in the repo directory
find -L ~/repo -maxdepth 1 -type f -mtime +3 -name '*.tar.gz' -exec rm {} \;

# remove backed up log files from the log directory
find -L ~/log -maxdepth 1 -type d -mtime +5 -name 'bak_*' -exec rm -r {} \;

# remove miscellaneous log files left by the applications
find -L ~ -type f -mtime +2 -name derby.log -exec rm {} \;
find -L ~ -type f -mtime +2 -name log4j.log -exec rm {} \;

find ~ -maxdepth 1 -type f -mtime +2 -name 'hs_err_pid[0-9]*.log' -exec rm {} \;

# remove temporary files left by the workbench scripts
find -L ~ -type f -mtime +1 -name 'db_update.sh[0-9]*' -exec rm {} \;
find -L ~ -type f -mtime +1 -name 'fmp_cas.sh[0-9]*' -exec rm {} \;
find -L ~ -type f -mtime +1 -name 'fmp_db.sh[0-9]*' -exec rm {} \;
find -L ~ -type f -mtime +1 -name 'fmp_jboss_deploy.sh[0-9]*' -exec rm {} \;
find -L ~ -type f -mtime +1 -name 'fmp_solrc.sh[0-9]*' -exec rm {} \;
find -L ~ -type f -mtime +1 -name 'fmp_tomcat.sh[0-9]*' -exec rm {} \;
find -L ~ -type f -mtime +1 -name 'sanity_check.sh[0-9]*' -exec rm {} \;
find -L ~ -type f -mtime +1 -name 'sanity_check.sh-solr-[0-9]*' -exec rm {} \;
find -L ~ -type f -mtime +1 -name '0_check.sh[0-9]*' -exec rm {} \;

# remove other miscellaneous files
find ~ -maxdepth 1 -type f -mtime +1 -name '.aesh_aliases' -exec rm {} \;
find ~ -maxdepth 1 -type f -mtime +1 -name '.lesshst' -exec rm {} \;
find ~ -maxdepth 1 -type f -mtime +1 -name '.rnd' -exec rm {} \;

