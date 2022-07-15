import subprocess,sys, os, shutil, base64, re, env
import kubernetes.client
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException
from pprint import pprint


# GLOBAL VARIABLES
workspacePath = env.WORKSPACE_DIR
tmpFolder = env.TMP_DIR
templateDir = env.TEMPLATE_DIR
kubeConfig = env.CONFIG_DIR
userKubeConfig = env.USER_KUBE_CONFIG_DIR

class KubeConfigGen():

    def __init__(self,userName,clusterName,groupName="developer"):
        self.userName = userName
        self.clusterName = clusterName
        self.groupName = groupName

    def path_control(self):

        # Check whether the workspace path exists or not
        isExist = os.path.exists(workspacePath)
        if not isExist:
            sys.exit('Workspace path does not exists! Please check your volume mount paths!')

        # Check whether the tmp path exists or not
        isExist = os.path.exists(tmpFolder)
        if not isExist:
            os.makedirs(tmpFolder)
            print("Tmp directory " + tmpFolder + " is created!")

        # Check whether the kubernetes config path exists or not
        isExist = os.path.exists(kubeConfig)
        if not isExist:
            os.makedirs(kubeConfig)
            print("Kubernetes Config directory " + kubeConfig + " is created!")

        # Check whether the workspace path exists or not
        isExist = os.path.exists(userKubeConfig)
        if not isExist:
            os.makedirs(userKubeConfig)
            print("User Kube Config directory " + userKubeConfig + " is created!")

        inventory = workspacePath + "clusters/" + self.clusterName + "/" + self.groupName + "/" + self.userName
        # Check whether the inventory path exists or not
        isExist = os.path.exists(inventory)
        if not isExist:
            os.makedirs(inventory)
            print("Inventory directory " + inventory + " is created!")

        return True

    def generate_csr(self):
        # GENERATE USER.KEY AND USER.CSR FILES ON THE INVENTORY PATH
        inventory = workspacePath + "clusters/" + self.clusterName + "/" + self.groupName + "/" + self.userName + "/"
        os.chdir(inventory)
        subprocess.call(['openssl req -newkey rsa:2048 -nodes -out ' + self.userName + '.csr' + ' -keyout ' + self.userName + '.key' + ' -subj ' + '"/CN=' + self.userName + '/O=' + self.groupName + '"'],shell=True)

        # COPY CSR TEMPLATE FILE TO TMP DIRECTORY
        os.chdir(tmpFolder)
        user_csr = tmpFolder + self.userName + "-csr.yaml"
        shutil.copyfile(templateDir + 'csr-template.yaml',user_csr)

        # B64 ENCODING CSR DATA
        csrdata = open(inventory + self.userName + ".csr","r").read()
        csrdata_bytes = csrdata.encode("ascii")
        base64_bytes = base64.b64encode(csrdata_bytes)
        base64_string = base64_bytes.decode("ascii")

        # SUBSTITUTING THE VARIABLES
        fin = open(user_csr, "rt")
        data = fin.read()
        data = data.replace('$USERNAME', self.userName)
        data = data.replace('$DATA', base64_string)
        fin.close()
        fin = open(user_csr, "wt")
        fin.write(data)
        fin.close()

        return True

    def generate_kubeconfig(self):

        inventory = workspacePath + "clusters/" + self.clusterName + "/" + self.groupName + "/" + self.userName + "/"
        
        # APPLY CSR ,APPROVE IT AND GET THE RELATED CRT DATA USING RIGHT KUBECONFIG
        config.load_kube_config(kubeConfig + '/config-' + self.clusterName)
        k8s_client = client.ApiClient()

        # Apply CSR
        try:
            utils.create_from_yaml(k8s_client, tmpFolder + self.userName + "-csr.yaml", verbose = True)
        except Exception as ex:
            print(ex)
        
        # Approve CSR
        api_instance = kubernetes.client.CertificatesV1Api(k8s_client)
        name = self.userName
        body = {"status":{"conditions":[{"message":"This CSR was approved by Sisyphus.","reason":"KubectlApprove","status":"True","type":"Approved"}]}}
        
        try:
            api_instance.patch_certificate_signing_request_approval(name, body)
            #api_response = api_instance.patch_certificate_signing_request_approval(name, body)
            #pprint(api_response)
        except ApiException as e:
            print("Exception when calling CertificatesV1Api->patch_certificate_signing_request_approval: %s\n" % e)

        # Get the related crt data
        # Currently there is a bug in this code block; I am working on to fix it.
        '''
        api_instancee = kubernetes.client.CertificatesV1Api(k8s_client)
        try:
            api_responsee = base64.b64decode(api_instancee.read_certificate_signing_request_status(name).to_dict()['status']['certificate'].encode('ascii')).decode('ascii')
            #base64_message = api_responsee.to_dict()['status']['certificate']
            #base64_bytes = base64_message.encode('ascii')
            #message_bytes = base64.b64decode(base64_bytes)
            #message = message_bytes.decode('ascii')
            #b = base64.b64decode(api_responsee.to_dict()['status']['certificate']).decode("ascii")
        except ApiException as e:
            print("Exception when calling CertificatesV1Api->read_certificate_signing_request_status: %s\n" % e)

        
        text_file = open(inventory + self.userName + ".crt", "w")
        text_file.write(api_responsee) 
        text_file.close()
        '''

        subprocess.call(['export KUBECONFIG=' + kubeConfig + '/config-' + self.clusterName + ' && ' +' kubectl get csr ' + self.userName + ' -o  jsonpath=\'{.status.certificate}\' |base64 -d > ' + inventory + self.userName + '.crt' ], shell=True)        


        # COPY KUBECONFIG TEMPLATE FILE
        shutil.copyfile(templateDir + 'kubeconf-template.yaml',userKubeConfig + '/' + self.userName + '-' + self.clusterName + '-kubeconfig')

        # ASSIGN VARIABLES
        kubeConfigFile = open(kubeConfig + '/config-' + self.clusterName, "r")
        for line in kubeConfigFile:
            if re.search("certificate-authority-data", line):
                parts = line.split()
                CA=parts[1]
            if re.search("server", line):
                parts = line.split()
                IP=parts[1]
        
        certData = open(inventory + self.userName + ".crt","r").read()
        certData_bytes = certData.encode("ascii")
        certData_base64_bytes = base64.b64encode(certData_bytes)
        certData_base64_string = certData_base64_bytes.decode("ascii")

        keyData = open(inventory + self.userName + ".key","r").read()
        keyData_bytes = keyData.encode("ascii")
        keyData_base64_bytes = base64.b64encode(keyData_bytes)
        keyData_base64_string = keyData_base64_bytes.decode("ascii")

        # SUBSTITUTING THE VARIABLES
        fin = open(userKubeConfig + '/' + self.userName + '-' + self.clusterName + '-kubeconfig', "rt")
        data = fin.read()
        data = data.replace('CLUSTERNAME', self.clusterName)
        data = data.replace('USER', self.userName)
        data = data.replace('CA', CA)
        data = data.replace('IP', IP)
        data = data.replace('CERT', certData_base64_string)
        data = data.replace('KEY', keyData_base64_string)

        fin.close()
        fin = open(userKubeConfig + '/' + self.userName + '-' + self.clusterName + '-kubeconfig', "wt")
        fin.write(data)
        fin.close()

        return True