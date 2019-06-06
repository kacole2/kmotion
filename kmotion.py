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
    selected_pod = pick(source_pods, title="Pick the POD to be kMotioned")

    # PICK to select Destination Cluster for KMOTION
    cluster2, _ = pick(contexts, title="Pick the target Cluster Context for the POD to be kMotioned to",
                       default_index=first_index)
    client2 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster2))

    start_time = time.time()
    for i in client1.list_pod_for_all_namespaces().items:
        if selected_pod[0] == i.metadata.name: # Return the Kubernetes API POD object
            # DEBUG print ('This is the POD you selected {0}'.format(source_pod_object.metadata.name))
            source_pod_object = i

    # Create a LIST from the Labels Dict
    labels_list = [[k, v] for k, v in source_pod_object.metadata.labels.items()]

    # Will need to work on this in future - Currently takes first label for the pod
    # usually app=xyz so this works. Can easily make a label selector for user to choose.
    akey = labels_list[0][0]
    avalue = labels_list[0][1]
    selector = '{0}={1}'.format(akey, avalue)
    backup_name = '{0}-{1}-{2}'.format(akey, avalue,timestr)
    print('\n|-|-|-|-|-| Selected Pod object: {0}. Pod label key: {1}. Pod label value: {2}'.format(source_pod_object.metadata.name,akey,avalue))
    print('\n|-|-|-|-|-| Temporary backup_name is: {0}. and label selector is: {1}\n'.format(backup_name,selector))

    ######## VELERO WORK ########
    # VELERO BACKUP Create
    backup_create_cmd = ['velero', 'backup', 'create', backup_name, '--selector', selector, '-w', '--kubecontext', cluster1]
    subprocess.check_call(backup_create_cmd)
    print("")

    # Work to interpret results of velero backup get
    while True:
        output = subprocess.check_output(['velero', 'backup', 'get', '--kubecontext', cluster2]).decode()
        print("|-|-|-|-|-| Waiting for Recovery Cluster", cluster2, " to recognize backup ", backup_name," on S3.")
        # DEBUG print("output velero get =", output, "Find result=", output.find(backup_name))
        time.sleep(3)
        if (output.find(backup_name) != -1):
            print("\n|-|-|-|-|-| Velero backup ", backup_name, " exists on Recovery Cluster ", cluster2, ". Moving to next step.")
            break
    print('\n|-|-|-|-|-| kMotioning POD {0} from {1} cluster to {2} cluster... \n'.format(source_pod_object.metadata.name,cluster1,cluster2))

    # VELERO Backup Restore
    restore_create_cmd = ['velero', 'restore', 'create', backup_name, '--from-backup', backup_name, '-w','--kubecontext',cluster2]
    subprocess.check_call(restore_create_cmd)

    ### Check POD Status of Restored PODs in Recovery Cluster

    while True:
        pod = client1.read_namespaced_pod(name=source_pod_object.metadata.name,
                                          namespace=source_pod_object.metadata.namespace)

        if pod.status.phase == 'Running':
            print("\n|-|-|-|-|-| kMotioned POD", pod.metadata.name, " is Running on Recovery Cluster ", cluster1)
            break
        else:
            print('Waiting for POD {0} status to be Running. \nCurrent status is {1}'.format(pod.metadata.name, pod.status.phase))
            time.sleep(3)

    end_time = time.time()
    print('|-|-|-|-|-| kMotion complete for POD {0} !!!!'.format(source_pod_object.metadata.name))
    print('|-|-|-|-|-| kMotion time was {0} Seconds.'.format(end_time-start_time))
    print('|-|-|-|-|-| Cleaning up temporary backup on SRC Cluster\n')

    # VELERO BACKUP Delete from Source Context
    backup_delete_cmd = ['velero', 'backup', 'delete', backup_name, '--kubecontext', cluster2, '--confirm']
    subprocess.check_call(backup_delete_cmd)

if __name__ == '__main__':
    main()