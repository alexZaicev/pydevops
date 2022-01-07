#!/bin/bash

HOME_PATH=$(pwd);
if [ -z ${PYDEVOPS_HOME} ]; then
	echo PYDEVOPS_HOME variable is not set. Using default...
else
	HOME_PATH=${PYDEVOPS_HOME}
fi

while test $# -gt 0; do
  case "$1" in
  -h | --help)
    echo "PyDevOps - Python based automation for TM"
    echo " "
    echo "pydevops.sh [options]"
    echo " "
    echo "Options:"
    echo "-h, --help        show brief help"
    echo "--switch          TM/Solr/Ingres/PostgreSQL/KeyCloak service switch (additional options:"
    echo "                      -s, --start - start"
    echo "                      -ss, --stop - stop"
    echo "                      -r, --restart - restart )"
    echo " "
    echo "--deploy          deploy TM/KeyCloak artifacts (includes service stop & start)"
    echo "                      -v, --version - deploy specific version of TM/TS/TM4C release."
    echo "                            TM/TS/TM4C releases are specified in 'release-management.yml' file."
    echo "                            Example: pydevops.sh --deploy -v=6.0.0"
    echo "                      -h, --hotfix - deploy specific hotfix version of TM/TS/TM4C release."
    echo "                            Hotfix option must be accompanied with version option."
    echo "                            Example: pydevops.sh --deploy -v=6.0.2 -h=4"
    echo " "
    echo "--upgrade         upgrade TM components"
    echo "                      -wtm, --workbench-tm - upgrade TM workbench"
    echo "                      -ws, --workbench-solr - upgrade Solr workbench"
    echo "                      -wi, --workbench-ingres - upgrade Ingres workbench"
    echo "                      -wpg, --workbench-postgres - upgrade Postgres workbench"
    echo "                      -t, --tomcat - upgrade Apache Tomcat"
    echo "                      -j, --jboss - upgrade RedHat Jboss (WildFly)"
    echo "                      -r, --release - upgrade component with release version (if "
    echo "                            not specified, fetching snapshot)"
    echo "                      -v, --version - upgrade component to specified veriosn (if version"
    echo "                            not specified, fetching latest version)"
    echo " "
    echo "--tools           run PyDevOps tools"
    echo "                      --set-password - set password for TM users in organization"
    echo "                      -p, --password - password to be set"
    echo "                      -o, --organization - TM organization name"
    echo " "
    echo "--xsd2xml         run XSD to XML generation tools"
    echo "                      -xsd - Path to XSD directory"
    echo "                      -xml - Generated XML output directory"
    echo "                      -o, --optional - Generate optional attributes"
    echo "                      -v, --validate - Validate generated XML document"
    echo " "
    echo " "
    exit 0
    ;;
  --switch)
    shift
    python "${HOME_PATH}"/switch.py "$@";
    exit $?;
    shift
    ;;
  --deploy)
    shift
    python "${HOME_PATH}"/deployer.py;
    exit $?;
    shift
    ;;
  --upgrade)
    shift
    python "${HOME_PATH}"/upgrade.py "$@";
    exit $?;
    shift
    ;;
  --tools)
    shift
    python "${HOME_PATH}"/tools.py "$@";
    exit $?;
    shift
    ;;
  --xsd2xml)
    shift
    python "${HOME_PATH}"/xsd2xml.py "$@";
    exit $?;
    shift
    ;;
  esac
done
