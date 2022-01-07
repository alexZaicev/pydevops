#!/bin/bash

cd ~/utility/admin-tools/bin 

FILENAME=$1
ORG=$2

./excelTool -instance remote://deivos:25113 -organization ${ORG} -filename ${FILENAME} -import -type users

./excelTool -instance remote://deivos:25113 -organization ${ORG} -filename ${FILENAME} -release -type users -activete

./excelTool -instance remote://deivos:25113 -organization ${ORG} -filename ${FILENAME} -import -type roles

./excelTool -instance remote://deivos:25113 -organization ${ORG} -filename ${FILENAME} -release -type roles

./excelTool -instance remote://deivos:25113 -organization ${ORG} -filename ${FILENAME} -import -type rolegroups

./excelTool -instance remote://deivos:25113 -organization ${ORG} -filename ${FILENAME} -release -type rolegroups

./excelTool -instance remote://deivos:25113 -organization ${ORG} -filename ${FILENAME} -import -type provisioning

./excelTool -instance remote://deivos:25113 -organization ${ORG} -filename ${FILENAME} -release -type users -activate
