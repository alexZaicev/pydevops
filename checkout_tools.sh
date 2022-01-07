#!/bin/bash

# CHECKOUT TOOLS
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/tools/jboss-modules/trunk tools.jboss.modules
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/tools/tm-tomcat-libs/trunk tools.tomcat.libs
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/tools/solr-lib/trunk tools.solr.lib

svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/tools/security-filters/CSRF tools.security.filters.csrf