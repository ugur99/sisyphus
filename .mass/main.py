import logging
import sys, getopt, subprocess, new


def usage():
    print("help: parameters required are --username, --groupname, --clustername")


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["username=", "groupname=", "clustername="])
    except getopt.GetoptError:
        usage()
        sys.exit()

    username = None
    groupname = None
    clustername = None

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-g", "--groupname"):
            groupname = arg
        elif opt in ("-c", "--clustername"):
            clustername = arg

    if username == None or groupname == None or clustername == None:
        usage()
        sys.exit()
    else:
        logging.info("UserName is: " + username + " , GroupName is: " + groupname + " ,ClusterName is: " + clustername )

        new_object = new.KubeConfigGen(username, clustername, groupname)

        if new_object.path_control():
            new_object.generate_kubeconfig(new_object.k8s(new_object.generate_csr_yaml()))

    print("Done")


if __name__ == "__main__":
    main(sys.argv[1:])
