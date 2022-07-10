#!/bin/bash

USERNAME=$1
GROUPNAME=$2
CLUSTERNAME=$3

# CHANGE THIS PATH WITH /workspace
WORKSPACE_DIR="/workspace/"
TMP_DIR="/workspace/tmp/"
CONFIG_DIR="/workspace/.kube"
USER_KUBE_CONFIG_DIR="/workspace/kubeConfig"
USER_KEY_DIR="$WORKSPACE_DIR/clusters/$CLUSTERNAME/$GROUPNAME/$USERNAME"
TEMPLATE_DIR="/app/k8stemplates"



#CA=$(cat $CONFIG_DIR/config-$CLUSTERNAME |grep -i 'certificate-authority-data' |awk '{print $2}')
CA=$(cat $CONFIG_DIR/config-$CLUSTERNAME |grep -i 'certificate-authority-data' |awk '{print $2}')
IP=$(cat $CONFIG_DIR/config-$CLUSTERNAME |grep -i server |awk '{print $2}')
CERT=$(cat $USER_KEY_DIR/$USERNAME.crt |base64 |tr '\n' '\r' | tr -d "[:space:]")
KEY=$(cat $USER_KEY_DIR/$USERNAME.key |base64 |tr '\n' '\r' | tr -d "[:space:]")

#sed -i 's/CA/'$CA'/g' $USER_KUBE_CONFIG_DIR/$USERNAME-$CLUSTERNAME-kubeconfig
sed -i 's@CA@'$CA'@g' $USER_KUBE_CONFIG_DIR/$USERNAME-$CLUSTERNAME-kubeconfig
sed -i 's@IP@'$IP'@g' $USER_KUBE_CONFIG_DIR/$USERNAME-$CLUSTERNAME-kubeconfig
sed -i 's/CLUSTERNAME/'$CLUSTERNAME'/g' $USER_KUBE_CONFIG_DIR/$USERNAME-$CLUSTERNAME-kubeconfig
sed -i 's/USER/'$USERNAME'/g' $USER_KUBE_CONFIG_DIR/$USERNAME-$CLUSTERNAME-kubeconfig
sed -i 's/CERT/'$CERT'/g' $USER_KUBE_CONFIG_DIR/$USERNAME-$CLUSTERNAME-kubeconfig
sed -i 's/KEY/'$KEY'/g' $USER_KUBE_CONFIG_DIR/$USERNAME-$CLUSTERNAME-kubeconfig