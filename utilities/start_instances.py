import subprocess
import sys
import time

from get_info_instances import get_info_instances

def create_instances(nmachines):

    instance_list = ' '.join(['instance-{}'.format(i) for i in range(nmachines)])
    
    query = 'gcloud compute instances create ' + instance_list + \
            ' --zone=us-central1-c' + \
            ' --metadata-from-file=startup-script=base_script.sh'

    print(query)
    subprocess.call(query, shell=True)

def create_hosts_file(instances_list):
    for instance in instances_list:
        subprocess.call('echo {} >> hosts'.format(instance['INTERNAL_IP']), shell=True)


def copy_files(instances_list):
    for instance in instances_list:
        ext_ip = instance['EXTERNAL_IP']
        subprocess.call('scp -i ~/.ssh/google-cloud-cs123 -o StrictHostKeyChecking=no ~/.ssh/google-cloud-cs123 {}:~/.ssh/id_rsa'.format(ext_ip), shell=True)
        subprocess.call('scp -i ~/.ssh/google-cloud-cs123 hosts {}:~/hosts'.format(ext_ip), shell=True)
        #subprocess.call('gcloud compute copy-files ~/LOCAL-FILE-1 ~/LOCAL-FILE-2 \
        #example-instance:~/REMOTE-DIR --zone us-central1-a')

def ssh_into_others(instances_list):
    '''
    Function to log into the first VM and SSH into the other VMs (to get MPI working)
    '''
    #if there is just 1 VM, there's no point in ssh into others
    if len(instances_list) == 1:
        return None

    #First VM is master, others are child
    master_instance = instances_list[0]

    for instance in instances_list[1:]:
        #send a ssh command to master, for each child
        subprocess.call("gcloud compute ssh {master_name} --command='ssh -o StrictHostKeyChecking=no {internal_ip}'".format(master_name=master_instance['NAME'], internal_ip=instance['INTERNAL_IP']), shell=True)



    pass

if __name__ == '__main__':
    try:
        N_MACHINES = int(sys.argv[1])
    except:
        N_MACHINES = 2

    create_instances(N_MACHINES)

    time.sleep(5)

    instances = get_info_instances()

    create_hosts_file(instances)

    time.sleep(5)

    copy_files(instances)

    ssh_into_others(instances)