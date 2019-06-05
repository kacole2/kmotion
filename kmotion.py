#!/usr/bin/python3

# Hackathon Lucky Team13

from kubernetes import client
from kubernetes import config
from pick import pick
import subprocess
import time

def main():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return

    # Create Python List of all contexts for use by PICK Module
    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])

    # PICK to select SOURCE Cluster for KMOTION
    cluster1, first_index = pick(contexts, title="Pick the source Cluster Context for the POD to kmotioned",
                                 default_index=active_index)
    client1 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster1))

    # Create Python List of all PODs in SRC Namespace for PICK Module
    source_pods = [i.metadata.name for i in client1.list_pod_for_all_namespaces().items]
    selected_pod = pick(source_pods, title="Pick the POD to be backed up")

    # PICK to select Destination Cluster for KMOTION
    cluster2, _ = pick(contexts, title="Pick the target Cluster Context for the POD to be kmotioned to",
                       default_index=first_index)
    client2 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster2))

    start_time = time.time()
    for i in client1.list_pod_for_all_namespaces().items:
        if selected_pod[0] == i.metadata.name: # Return the Kubernetes API POD object
            #DEBUG print("--Found the POD Object for Selected POD")
            source_pod_object = i

    #DEBUG print ('This is the POD you selected {0}'.format(source_pod_object.metadata.name))

    # Create a LIST from the Labels Dict
    labels_list = [[k, v] for k, v in source_pod_object.metadata.labels.items()]

    # Will need to work on this in future - Currently takes first label for the pod
    # usually app=xyz so this works. Can easily make a label selector for user to choose.
    akey = labels_list[0][0]
    avalue = labels_list[0][1]
    selector = '{0}={1}'.format(akey, avalue)
    backup_name = '{0}-{1}-{2}'.format(akey, avalue,timestr)
    #DEBUG print("\nsource_pod_object selected lables(","akey =", akey," avalue =", avalue,")\nselector string is", selector)
    print("\n|-|-|-|-|-| Temporary backup_name is", backup_name)

    ######## VELERO WORK ########
    # VELERO BACKUP Create
    backup_create_cmd = ['velero', 'backup', 'create', backup_name, '--selector', selector, '-w', '--kubecontext', cluster1]
    subprocess.check_call(backup_create_cmd)

    # Work to interpret results of velero backup get
    while True:
        output = subprocess.check_output(['velero', 'backup', 'get', '--kubecontext', cluster2]).decode()
        print("\n|-|-|-|-|-| Waiting for backup ", backup_name, " to be synchronized with Recovery Cluster ", cluster2)
        # DEBUG print("backup_name.encode=", backup_name, "output velero get =", output, "Find result=", output.find(backup_name))
        time.sleep(3)
        if (output.find(backup_name) != -1):
            print("\n|-|-|-|-|-| Velero backup ", backup_name, " exists on Recovery Cluster ", cluster2, ". Moving to next step.")
            break
    print('\n|-|-|-|-|-| KMotioning POD {0} from {1} cluster to {2} cluster... '.format(source_pod_object.metadata.name,cluster1,cluster2))

    # VELERO Backup Restore
    restore_create_cmd = ['velero', 'restore', 'create', backup_name, '--from-backup', backup_name, '-w','--kubecontext',cluster2]
    subprocess.check_call(restore_create_cmd)

    ### Check POD Status of Restored PODs in Recovery Cluster

    for i in client2.list_pod_for_all_namespaces().items:
        if i.metadata.labels:       # Verify dict exists and is not empty to prevent errors
            if akey in i.metadata.labels.keys():
                if i.metadata.labels[akey] == avalue:
                    #print("\nFound a POD with the SRC POD Label and Key ", akey, avalue)
                    print("%s\t%s\t%s" % (i.metadata.name, i.metadata.namespace, i.status.phase))
                    while True:
                        if i.status.phase == 'Running':
                            print("\n|-|-|-|-|-| Restored PODs ", i.metadata.name, " is running on Recovery Cluster ", cluster2)
                            break
                        else:
                            print("Waiting..\n Restored PODs ", i.metadata.name, " status is ", i.status.phase)
                            time.sleep(3)

    end_time = time.time()
    print('\n|-|-|-|-|-| KMotion complete for POD {0} !!!!'.format(source_pod_object.metadata.name))
    print('\n|-|-|-|-|-| KMotion time was {0} Seconds.'.format(end_time-start_time))
    print('|-|-|-|-|-| Cleaning up temporary backup on SRC Cluster')
    # VELERO BACKUP Delete from Source Context
    backup_delete_cmd = ['velero', 'backup', 'delete', backup_name, '--kubecontext', cluster2, '--confirm']
    subprocess.check_call(backup_delete_cmd)



if __name__ == '__main__':
    main()