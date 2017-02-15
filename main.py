import time
from linode import api
from run_command import *
import threading
"""
Insert the Linode Token.
"""

API_KEY = "Y7UU1JcuKvaxi5kCDkoHgyujhaxyLgXMwPfLSGEnKvUcqSVJutbBfzicwVB6YRL1"


"""
Set the parameters for Linode.
"""

DC_ID = 7  # London, England, UK
PLAN_ID = 2  # Linode 2048
PAYMENT_TERMS = 1  # a month
DISTRIBUTION_ID = 129  # CentOS 6.5
ROOT_PASS="testuser123"

# Disk parameters
SWAP_LABEL = "swap"
SWAP_SIZE_MB = 256
BOOT_LABEL = 'root'
DISK_SIZE_GB = 30
BOOT_SIZE = DISK_SIZE_GB * 1024 - SWAP_SIZE_MB
KERNEL_ID = 138

# Image Name
IMAGE_LABEL = 'wrf-minimal'

# Count time
count_time = 1 * 60

# Script


"""
Functions
"""


class Process_Linode():
    """
    Functions to process Linode
    """

    def __init__(self):
        self.l = api.Api(key=API_KEY)
        self.linodeIds = []
        self.IMAGEID = None

    def get_IMAGEID(self):
        IMAGElist = self.l.image_list()

        for item in IMAGElist:
            if item["LABEL"] == IMAGE_LABEL:
                self.IMAGEID = item["IMAGEID"]
                print('IMAGEID: {}\n'.format(self.IMAGEID))
                return True
        return False

    def init(self):
        """
        Create the instance from image.
        """

        linodeInfo = self.l.linode_create(DatacenterID=DC_ID, PlanID=PLAN_ID, PaymentTerm=PAYMENT_TERMS)
        linodeId = linodeInfo['LinodeID']
        print('Linode ID is {}\n'.format(linodeId))
        rootinfo = self.l.linode_disk_createfromimage(ImageID=self.IMAGEID, LinodeID=linodeId, rootPass=ROOT_PASS)
        print('rootinfo:{}'.format(rootinfo))
        swapinfo = self.l.linode_disk_create(LinodeID=linodeId, Label=SWAP_LABEL, Type="swap", Size=SWAP_SIZE_MB)
        configinfo = self.l.linode_config_create(
            LinodeID=linodeId,
            KernelID=KERNEL_ID,
            Label="CentOS 7",
            DiskList="%s,%s,,,,,," % (rootinfo['DISKID'], swapinfo['DiskID'])
        )
        return linodeId

    def multi_init(self, total):
        """
        Create Multiple instance.
        """
        for current in range(1, total + 1):
            print("Creating Linode %d/%d..." % (current, total))
            linodeId = self.init()
            self.linodeIds.append(linodeId)
            time.sleep(10)
        return self.linodeIds

    def boot(self, linodeId):
        """
        Boot Instance.
        """
        print('booting: {}\n'.format(linodeId))
        self.l.linode_boot(LinodeID=linodeId)
        ipinfo = self.l.linode_ip_list(LinodeID=linodeId)
        print('{} Ip address: {}\n'.format(linodeId, ipinfo))
        time.sleep(10)
        return ipinfo[0]['IPADDRESS']

    def multi_boot(self, linodeIds=[]):
        """
        Boot Multi instance.
        """
        ips = []
        for linodeId in linodeIds:
            print("Booting linode %d/%d..." % (linodeIds.index(linodeId) + 1, len(linodeIds)))
            ipAddress = self.boot(linodeId)
            ips.append(ipAddress)
        return ips

    def reap(self, linodeId):
        """
        Delete Instance.
        """

        self.l.linode_delete(LinodeID=linodeId, skipChecks=True)

    def multi_reap(self, linodeIds=[]):
        """
        Delete multi linode
        """

        for linodeId in linodeIds:
            print("Reaping linode %d/%d..." % (linodeIds.index(linodeId) + 1, len(linodeIds)))
            self.reap(linodeId)


def countdown(t):
    """
    Counting time down
    """
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1
    print('Time is up.\n')


def proceed_script(linode_ips):
    """
    Run the scripts after boot the instance.
    """
    instance_thread_list = []
    for index, linode_ip in enumerate(linode_ips):
        instance_thread = threading.Thread(target=run_script.run_main, args=(linode_ip, index))
        instance_thread.start()
        instance_thread_list.append(instance_thread)
    for p in instance_thread_list:
        p.join()

if __name__ == "__main__":
    process_linode = Process_Linode()
    try:
        linode_lists = []
        if process_linode.get_IMAGEID():
            linode_lists = process_linode.multi_init(10)
            time.sleep(30)
            linode_ips = process_linode.multi_boot(linode_lists)
            time.sleep(20)
            proceed_script(linode_ips)

            countdown(count_time)
            process_linode.multi_reap(linode_lists)
            time.sleep(10)

        else:
            print('No found Image on your account\n')

    except Exception as e:
        print('Exception: {}'.format(e))


