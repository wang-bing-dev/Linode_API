# pip install paramiko

import paramiko

USERNAME = 'dan'
USERPASSWORD = 'cf664bz2'


class RUN_SCRIPT():
    """
    Run Bahs script when boot instance.
    """

    def __init__(self):
        """
        initialize.
        """

        self.bash_script = "nohup sh /home/dan/wrf-scripts/"

    def connect(self, IP):
        """
        Connect to instance via ssh and return connect instance.
        """

        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        ssh.connect(IP, username=USERNAME, password=USERPASSWORD)
        return ssh

    def run_shell(self, cmd, ssh):
        """
        send single command via ssh.
        """
        try:
            stdin, stdout, stderr = ssh.exec_command(cmd)

            print('stdout: {}\n'.format(stdout.readlines()))
            print('stderr: {}\n'.format(stderr.readlines()))
            stdin.close()
        except Exception as e:
            print('Exception: {}'.format(e))

    def run_shells(self, linode_index, ssh):
        """
        send multiple commands via ssh.
        """
        cmd = self.bash_script + "gefsp0" + str(linode_index) + ".sh"
        print('cmd: {}'.format(cmd))
        self.run_shell(cmd, ssh)

    def run_main(self, IP, linode_index):
        """
        Main Function.
        """

        ssh = run_script.connect(IP)
        print("connected to {}\n".format(IP))
        run_script.run_shells(linode_index + 1, ssh)
        print("{} is completed to run bash script successfully\n".format(IP))

run_script = RUN_SCRIPT()

