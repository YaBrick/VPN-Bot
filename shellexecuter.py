import os
 
# Using os() method to
# execute shell commands
def create_usual_key():
    print("Generating...")
    os.system('sudo /home/ubuntu/vpnbot/add-vpnbot-client.sh')
    print("newkeywasmade")
