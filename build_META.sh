#!/bin/bash

clear;

DIR="C:/Users/u722245/REPOS/SVN/META"
LOGFILE="C:/Users/u722245/REPOS/SVN/META/.log/build.log"

function build {
	cd $1;
	svn cleanup;
	svn update;
	mvn clean install;

	if [[ $? -ne 0 ]]; then
		exit 1;
	fi
}

rm -rf $LOGFILE;

{

#build "$DIR/pb"
build "$DIR/meta"
#build "$DIR/meta-rt"
#build "$DIR/meta-tools"

} | tee -a $LOGFILE
