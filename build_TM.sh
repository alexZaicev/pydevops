#!/bin/bash

function build {
	cd $1
	svn cleanup;
	svn update;
	mvn clean install -DskipTests;

	if [[ $? -ne 0 ]]; then
		exit 1;
	fi
}

function deploy {
	cd $DIR;
	./pydevops.sh --deploy
}

clear;

DIR=$(pwd)
LOGDIR="${DIR}/.log"
LOGFILE="${LOGDIR}/build.log"

if [ ! -d ${LOGDIR} ]; then
	mkdir ${LOGDIR}
fi

rm -rf $LOGFILE;

{
####################################################
#	Build TM-Core

build "$DIR/tools.tomcat.libs"
build "$DIR/tools.solr.lib"
build "$DIR/tools.jboss.modules"

build "$DIR/resources.labels"

build "$DIR/fwk.base.lib"
build "$DIR/fwk.base.util"

build "$DIR/fwk.core.security"
build "$DIR/fwk.core.directory"
build "$DIR/fwk.core.docpersistency"

build "$DIR/fwk.msg.util"
build "$DIR/fwk.msg.swift"
build "$DIR/fwk.msg.core"
build "$DIR/fwk.msg.payments"

build "$DIR/fwk.report"

build "$DIR/fwk.web"

build "$DIR/fwk.web.swift"
build "$DIR/fwk.web.payments"
build "$DIR/fwk.web.six"
build "$DIR/fwk.web.secom"

###################################################
#	Build KeyCloak Libraries

#build "$DIR/keycloak.lib"
#build "$DIR/keycloak.authenticator.lib"
#build "$DIR/keycloak.audit.listener"
#build "$DIR/keycloak.auth.provider"
#build "$DIR/keycloak.crux.theme"
#build "$DIR/keycloak.email.authenticator"
#build "$DIR/keycloak.post.saml.authenticator"
#build "$DIR/keycloak.portal.theme"
#build "$DIR/keycloak.radius.authenticator"
#build "$DIR/keycloak.saml.authenticator"
#build "$DIR/keycloak.tm.theme"
#build "$DIR/keycloak.tomcat.adapter"
#build "$DIR/keycloak.tomcat.root"
#build "$DIR/keycloak.unique.authenticator"
#build "$DIR/keycloak.x509.authenticator"

###################################################
#	Build Applications

build "$DIR/app.admin"
build "$DIR/app.audit"
build "$DIR/app.authentication"
build "$DIR/app.cockpit"
build "$DIR/app.directory"
build "$DIR/app.fin"
build "$DIR/app.funds"
build "$DIR/app.help"
build "$DIR/app.report"
build "$DIR/app.rma"
build "$DIR/app.six"

###################################################
#	Build Non-Core Applications

#build "$DIR/app.accountStatement"
#build "$DIR/app.cbp"
#build "$DIR/app.cdvalidation"
#build "$DIR/app.cofi"
#build "$DIR/app.fileflow"
#build "$DIR/app.filesDistribution"
#build "$DIR/app.integrator_cc"
#build "$DIR/app.manualpayment"
#build "$DIR/app.mastercard"
#build "$DIR/app.ripple"
#build "$DIR/app.secom.areg"
#build "$DIR/app.secom.banking"
#build "$DIR/app.secom.ca"
#build "$DIR/app.secom.cashplan"
#build "$DIR/app.secom.clearing"
#build "$DIR/app.secom.depository"
#build "$DIR/app.secom.migration"
#build "$DIR/app.secom.repo"
#build "$DIR/app.secom.reports"
#build "$DIR/app.secom.seclend"
#build "$DIR/app.secom.secplan"
#build "$DIR/app.secom.slb"
#build "$DIR/app.secom.tcm"
#build "$DIR/app.secom.xclr"
#build "$DIR/app.thunes"

##################################################
#	Deploy to VM

deploy

} | tee -a $LOGFILE

