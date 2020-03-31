import yaml
import paramiko


def get_server_login_pasword_from_yaml(logger):
    try:
        with open ('./../data/lpt.yaml') as f:
            lpt = yaml.safe_load((f.read()))
            server_address = str(lpt['server_address'])
            server_login = str(lpt['server_login'])
            server_password = str(lpt['server_password'])
        return server_address, server_login, server_password
    except FileNotFoundError as e:
        error_message = ('moduls/get_server_login_pasword_from_yaml - ' + str(e) + 'no server_address-file')
        print(error_message)


def get_create_time_of_data_file(logger, server_address, server_login, server_password)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=server_address, username=server_login, password=server_password)
    stdin, stdout, stderr = client.exec_command('ls -l')
    data = stdout.read() + stderr.read()
    client.close()


logger = 'logger'

server_address, server_login, server_password = get_server_login_pasword_from_yaml(logger)
