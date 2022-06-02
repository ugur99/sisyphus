import subprocess,sys, os, shutil, base64
import env

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

    def generate_csr_yaml(self):
        # GENERATE USER.KEY AND USER.CSR FILES ON THE INVENTORY PATH
        inventory = workspacePath + "clusters/" + self.clusterName + "/" + self.groupName + "/" + self.userName + "/"
        os.chdir(inventory)
        subprocess.call(['openssl req -newkey rsa:2048 -nodes -out ' + self.userName + '.csr' + ' -keyout ' + self.userName + '.key' + ' -subj ' + '"/CN=' + self.userName + '/O=' + self.groupName + '"'],shell=True)

        # COPY CSR TEMPLATE FILE TO TMP DIRECTORY
        os.chdir(tmpFolder)
        user_csr = tmpFolder + self.userName + "-csr.yaml"
        shutil.copyfile(templateDir + 'csr-template.yaml',user_csr)

        csrdata = open(inventory + self.userName + ".csr","r").read()
        csrdata_bytes = csrdata.encode("ascii")
        base64_bytes = base64.b64encode(csrdata_bytes)
        base64_string = base64_bytes.decode("ascii")

        fin = open(user_csr, "rt")
        data = fin.read()
        data = data.replace('$USERNAME', self.userName)
        data = data.replace('$DATA', base64_string)
        fin.close()
        fin = open(user_csr, "wt")
        fin.write(data)
        fin.close()

        return True

#    def k8s(self,csr):
#        subprocess.call(['export KUBECONFIG=' + kubeConfig + '/config-' + self.clusterName], shell=True)
#        subprocess.call(['kubectl apply -f ' + csr], shell=True)
        # OR WE CAN USE KUBESWITCH LIKE TOOL TO PULL KUBE_CONFIG TO CONNECT CLUSTER WITH AN AUTHORIZED USER TO APPLY CSR!

#        inventory = workspacePath + "clusters/" + self.clusterName + "/" + self.groupName + "/" + self.userName + "/"
#        os.chdir(inventory)
#        subprocess.call(['kubectl get csr ' + self.userName + ' -o jsonpath=\'{.status.certificate}\' |base64 -d > ' + self.userName + '.crt'], shell=True)

#        user_cert = inventory + self.userName + '.crt'

#        return user_cert

    def generate_kubeconfig(self):

        subprocess.call(['chmod +x /app/helper.sh'], shell=True)
        subprocess.call(['/app/helper.sh ' + self.userName + " " + self.groupName + " " + self.clusterName ], shell=True)
