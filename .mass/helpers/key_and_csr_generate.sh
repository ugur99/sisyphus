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

error_exit()
{
  printf "$1" 1>&2
  exit 1
}

export_config()
{
  export KUBECONFIG=$WORKSPACE_DIR/.kube/config-$1
}

create_or_check_dir()
{
  if [ -d "$1" ]; then
    :
  else
    mkdir $1
  fi
}

# CHECK THE NUMBER OF ARGUMENTS --->
if [[ $# -eq 3 ]]; then
  printf "User_Name: $USERNAME\nGroup_Name: $GROUPNAME\nCluster_Name: $CLUSTERNAME\n"
else
  error_exit "************************************************\n** PLEASE RUN THE SCRIPT WITH THREE ARGUMENTS **\n************************************************\n" 1>&2
fi

# MAKE SURE THE EXISTENCE OF SOME PATHS--->
create_or_check_dir $WORKSPACE_DIR
create_or_check_dir $TMP_DIR
create_or_check_dir $CONFIG_DIR
create_or_check_dir $USER_KUBE_CONFIG_DIR

# GENERATE PRIVATE_KEY AND CSR --->
if [ -d "$USER_KEY_DIR" ]; then
  error_exit "************************************************\n** TARGET ROLE HAS BEEN BINDED SAME USER FOR SAME CLUSTER! **\n************************************************\n" 1>&2
elif [ -d "$WORKSPACE_DIR/clusters/$CLUSTERNAME/$GROUPNAME/" ]; then
  mkdir $USER_KEY_DIR
else
  mkdir -p $USER_KEY_DIR
fi




cd $USER_KEY_DIR && openssl genrsa -out $USERNAME.key 2048 && openssl req -new -key $USERNAME.key -out $USERNAME.csr -subj "/CN=$USERNAME/O=$GROUPNAME"
cp $TEMPLATE_DIR/csr-template.yaml $TMP_DIR/$USERNAME-csr.yaml && sed -i 's/$USERNAME/'$USERNAME'/g' $TMP_DIR/$USERNAME-csr.yaml
DATA=$(cat $USER_KEY_DIR/$USERNAME.csr | base64 | tr -d "\n") && sed -i 's/$DATA/'$DATA'/g' $TMP_DIR/$USERNAME-csr.yaml

export_config $CLUSTERNAME

kubectl apply -f $TMP_DIR/$USERNAME-csr.yaml && kubectl certificate approve $USERNAME


kubectl get csr $USERNAME -o jsonpath='{.status.certificate}' |base64 -d > $USER_KEY_DIR/$USERNAME.crt
cp $TEMPLATE_DIR/kubeconf-template.yaml  $USER_KUBE_CONFIG_DIR/$USERNAME-$CLUSTERNAME-kubeconfig

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
