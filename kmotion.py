# Hackathon Lucky Team13

from kubernetes import client
from kubernetes import config
# install pick using "pip install pick". It is not included
# as a dependency because it only used in examples
from pick import pick
import subprocess
import time

def main():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return
    # Python List of all contexts for use by PICK Module
    contexts = [context['name'] for context in contexts]

    active_index = contexts.index(active_context['name'])
    # PICK to select SOURCE Cluster for KMOTION
    cluster1, first_index = pick(contexts, title="Pick the source Cluster Context for the POD to be backed up",
                                 default_index=active_index)
    client1 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster1))


    # Create Python List of all PODs in SRC Namespace for PICK Module
    source_pods = [i.metadata.name for i in client1.list_pod_for_all_namespaces().items]
    # DEBUGONLY print("\nList of source_pods on %s:" % source_pods)
    selected_pod = pick(source_pods, title="Pick the POD to be backed up")

    # PICK to select Destination Cluster for KMOTION
    cluster2, _ = pick(contexts, title="Pick the target Cluster Context for the POD to be restored to",
                       default_index=first_index)
    client2 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster2))


    for i in client1.list_pod_for_all_namespaces().items:
        if selected_pod[0] == i.metadata.name: # Return the Kubernetes API POD object
            print("Found the POD Object for Selected POD")
            source_pod_object = i

    print ('This is the POD you selected {0}'.format(source_pod_object.metadata.name))

    # Grabbing labels from the POD object we now have.
    #print("Labels for our POD to be backed up" )
    #print("%s" % (source_pod_object.metadata.labels))

    # Create a LIST from the Labels Dict
    labels_list = [[k, v] for k, v in source_pod_object.metadata.labels.items()]
    #print(labels_list[0])
    #print(type(labels_list))

    # Will need to work on this in future - Currently takes first label for the pod
    # usually app=xyz so this works. Can easily make a label selector for user to choose.
    akey = labels_list[0][0]
    avalue = labels_list[0][1]
    print("akey =", akey)
    print("avalue =", avalue)
    selector = '{0}={1}'.format(akey, avalue)
    backup_name = '{0}-{1}-{2}'.format(akey, avalue,timestr)
    print("selector string is", selector)
    print("backup_name string is", backup_name)

    ######## VELERO WORK ########

    # VELERO BACKUP Create
    backup_create_cmd = ['velero', 'backup', 'create', backup_name, '--selector', selector, '-w', '--kubecontext', cluster1]
    subprocess.check_call(backup_create_cmd)

    # CAN PROBABLY GET RID OF THIS EVENTUALLY
    # VELERO BACKUP Status
    #DEBUG backup_query_cmd = ['velero', 'backup', 'describe', backup_name, '--kubecontext',cluster1]
    #DEBUG subprocess.check_call(backup_query_cmd)

    time.sleep(3)

    '''# DEBUG for TESTING - VELERO BACKUP Delete
    backup_delete_cmd = ['velero', 'backup', 'delete', backup_name, '--kubecontext', cluster2, '--confirm']
    subprocess.check_call(backup_delete_cmd)
    print("DEBUG - Sleeping for 25 seconds")
    time.sleep(25)
    

    #DEBUG Check the existence of backup on the DESTINATION side.
    backup_get_cmd = ['velero', 'backup', 'get', '--kubecontext', cluster2]
    subprocess.check_call(backup_get_cmd)
    '''



    '''
    while (output.indexOf(backup_name) < 0):
        print("NEW ouput Waiting for Backup to be synchronized with Recovery Cluster . . . ")
        time.sleep(4)
    else:
        print("NEW output Velero backup exists on Recovery Cluster. Moving to next step.")
        # return
    '''
    '''
    while (output.find(backup_name) == -1):
        print("Waiting for backup ", backup_name, " to be synchronized with Recovery Cluster ", cluster2)
        print("output velero get ", output)
        print("backup_name.encode", backup_name)
        print("Find Integer value", output.find(backup_name))
        time.sleep(4)

    print("Velero backup ", backup_name ," exists on Recovery Cluster ", cluster2, ". Moving to next step.")
    '''
    # Work to interpret results of velero backup get
    while True:
        output = subprocess.check_output(['velero', 'backup', 'get', '--kubecontext', cluster2]).decode()
        print(type(output))
        print(output)
        print("Waiting for backup ", backup_name, " to be synchronized with Recovery Cluster ", cluster2)
        print("output velero get ", output)
        print("backup_name.encode", backup_name)
        print("Find Integer value", output.find(backup_name))
        time.sleep(3)
        if (output.find(backup_name) != -1):
            print("Velero backup ", backup_name, " exists on Recovery Cluster ", cluster2, ". Moving to next step.")
            break

    # VELERO Restore
    restore_create_cmd = ['velero', 'restore', 'create', backup_name, '--from-backup', backup_name, '-w','--kubecontext',cluster2]
    subprocess.check_call(restore_create_cmd)

    # VELERO Restore Describe
    restore_describe_cmd = ['velero', 'restore', 'describe', backup_name, '--kubecontext',cluster2]
    subprocess.check_call(restore_describe_cmd)

    # VELERO BACKUP Delete
    backup_delete_cmd = ['velero', 'backup', 'delete', backup_name, '--kubecontext',cluster2, '--confirm']
    subprocess.check_call(backup_delete_cmd)

    print('KMotioning POD {0} from {1} cluster to {2} cluster... '.format(source_pod_object.metadata.name, cluster1, cluster2))

    '''
    print("\n\nList of pods on %s:" % cluster2)
    for i in client2.list_pod_for_all_namespaces().items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    '''

if __name__ == '__main__':
    main()