#!/bin/bash

# CHECKOUT KEYCLOAK 
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-audit-listener/trunk keycloak.audit.listener
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-auth-provider/trunk keycloak.auth.provider
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-authenticator-lib/trunk keycloak.authenticator.lib
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-crux-theme/trunk keycloak.crux.theme
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-email-authenticator/trunk keycloak.email.authenticator
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-lib/trunk keycloak.lib
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-model-infinispan/trunk keycloak.model.infinispan
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-portal-theme/trunk keycloak.portal.theme
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-post-saml-authenticator/trunk keycloak.post.saml.authenticator
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-radius-authenticator/trunk keycloak.radius.authenticator
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-saml-authenticator/trunk keycloak.saml.authenticator
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-tm-theme/trunk keycloak/tm.theme
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-tomcat-adapter/trunk keycloak.tomcat.adapter
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-tomcat-root/trunk keycloak.tomcat.root
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-unique-authenticator/trunk keycloak.unique.authenticator
svn checkout http://svn.bbp.ch:8370/fmscore/gmp2/keycloak/keycloak-x509-authenticator/trunk keycloak.x509.authenticator
