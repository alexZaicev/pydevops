STOP_TM = '$FMP_HOME/utility/fmp_all.sh kill'
STOP_SOLR = '$SOLR_HOME/wb/stop_all.sh'
STOP_INGRES = 'source setIngres.env; cd $II_SYSTEM/ingres; ingstop; ingstop -f; ingstatus'
STOP_POSTGRES = 'sudo systemctl stop postgresql-11'
STOP_KEYCLOAK = 'sudo systemctl stop {}'

START_TM = '$FMP_HOME/utility/fmp_all.sh start'
START_SOLR = '$SOLR_HOME/wb/start_all.sh'
START_INGRES = 'source setIngres.env; cd $II_SYSTEM/ingres; ingstart; ingstatus'
START_POSTGRES = 'sudo systemctl start postgresql-11'
START_KEYCLOAK = 'sudo systemctl stop {}'

MAKE_CFG_TM = '$FMP_HOME/install/1_config/1_make_configuration.sh'
MAKE_CFG_SOLR = '$SOLR_HOME/wb/1_make_configuration.sh'
MAKE_CFG_INGRES = '$II_SYSTEM/ingres/wb/1_make_apply_config.sh'
MAKE_CFG_POSTGRES = '$HOME/wb/1_make_apply_config.sh'

DEPLOY_CFG_TM = '$FMP_HOME/install/1_config/2_deploy_configuration.sh'
DEPLOY_CFG_SOLR = '$SOLR_HOME/wb/2_deploy_configuration.sh'

BACKUP_OLD_WB_TM = 'mv $FMP_HOME/install $FMP_HOME/install-old'
BACKUP_OLD_WB_SOLR = 'mv $SOLR_HOME/wb $SOLR_HOME/wb-old'
BACKUP_OLD_WB_INGRES = 'mv $II_SYSTEM/ingres/wb $II_SYSTEM/ingres/wb-old'
BACKUP_OLD_WB_POSTGRES = 'mv $HOME/wb $HOME/wb-old'
BACKUP_OLD_TOMCAT = 'mv $FMP_HOME/$(basename $(readlink -f tomcat)) $FMP_HOME/$(basename $(readlink -f tomcat))-old'
BACKUP_OLD_JBOSS = 'mv $FMP_HOME/$(basename $(readlink -f jboss)) $FMP_HOME/$(basename $(readlink -f jboss))-old'

EXTRACT_TM_COMPONENT = 'tar -xzvf $FMP_HOME/repo/{} -C $FMP_HOME'
EXTRACT_WB_SOLR = 'tar -xzvf $SOLR_HOME/repo/{} -C $SOLR_HOME'
EXTRACT_WB_INGRES = 'tar -xzvf $II_SYSTEM/ingres/repo/{} -C $II_SYSTEM/ingres'
EXTRACT_WB_POSTGRES = 'tar -xzvf $HOME/repo/{} -C $HOME'

DELETE_BACKED_UP_WB_TM = 'rm -rf $FMP_HOME/install-old'
DELETE_BACKED_UP_WB_SOLR = 'rm -rf $SOLR_HOME/wb-old'
DELETE_BACKED_UP_WB_INGRES = 'rm -rf $II_SYSTEM/ingres/wb-old'
DELETE_BACKED_UP_WB_POSTGRES = 'rm -rf $HOME/wb-old'
DELETE_BACKED_UP_TOMCAT = 'rm -rf $FMP_HOME/apache-tomcat-*-old'
DELETE_BACKED_UP_JBOSS = 'rm -rf $FMP_HOME/wildfly*.Final-old'

CREATE_REPO = '[ ! -d $HOME/repo ] && mkdir $HOME/repo'

REMOVE_TOMCAT_SYMLINK = 'rm -f $FMP_HOME/tomcat'
REMOVE_JBOSS_SYMLINK = 'rm -f $FMP_HOME/jboss'

CREATE_TOMCAT_SYMLINK = 'ln -s $FMP_HOME/{} tomcat'
CREATE_JBOSS_SYMLINK = 'ln -s $FMP_HOME/{} jboss'

COPY_OLD_TOMCAT_WEBAPPS = 'cp -r $FMP_HOME/apache-tomcat-*-old/webapps/* $FMP_HOME/tomcat/webapps/'
COPY_OLD_TOMCAT_LIBS = 'cp -r $FMP_HOME/apache-tomcat-*-old/lib/* $FMP_HOME/tomcat/lib/'

COPY_OLD_JBOSS_MODULES = 'cp -r $FMP_HOME/wildfly-*.Final-old/modules/ch $FMP_HOME/jboss/modules'
COPY_OLD_JBOSS_DEPLOYMENTS = 'cp -r $FMP_HOME/wildfly-*.Final-old/standalone/deployments/* $FMP_HOME/jboss/standalone/deployments/'
COPY_OLD_JBOSS_VAULT = 'cp -r $FMP_HOME/wildfly-*.Final-old/vault $FMP_HOME/jboss/vault'

CHANGE_PERM_PYDEVOPS = 'chmod -R 755 $HOME/pydevops'

REMOVE_SCRIPTS = 'rm -rf $HOME/pydevops/scripts'
CREATE_SCRIPTS = 'mkdir -p $HOME/pydevops/scripts'

REMOVE_TOOLS = 'rm -rf $HOME/pydevops/tools'
CREATE_TOOLS = 'mkdir -p $HOME/pydevops/tools'

TOOLS_SET_PASSWORD = 'cd {}/pydevops/tools; ./pydevopsUtils.sh -o {} -setPassword -p {} -dbHost {} -dbPort {} -dbUser {} -dbPwd {} -d {}'

ECHO_AUTH_TYPE = 'echo $AUTHENTICATION_TYPE'
