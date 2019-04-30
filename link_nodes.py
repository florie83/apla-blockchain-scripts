import time
import json

from libs import actions, tools, loger


log = loger.create_loger(__name__)


def is_in_block(call, url, token):
    status = actions.tx_status(url, 30, call, token)
    if 'blockid' not in status or int(status['blockid']) < 0:
        return False
    return True


def roles_install(url, pr_key, token):
    data = {}
    log.info('RolesInstall started')
    call = actions.call_contract(url, pr_key, 'RolesInstall',
                                 data, token)
    if not is_in_block(call, url, token):
        log.error('RolesInstall is failed')
        exit(1)


def voting_templates_install(url, pr_key, token):
    data = {}
    log.info('VotingTemplatesInstall started')
    call = actions.call_contract(url, pr_key, 'VotingTemplatesInstall',
                                 data, token)
    if not is_in_block(call, url, token):
        log.error('VotingTemplatesInstall is failed')
        exit(1)


def edit_app_param(name, val, url, pr_key, token):
    log.info('EditAppParam started')
    id = actions.get_object_id(url, name, 'app_params', token)
    data = {'Id': id, 'Value': val, 'Conditions': 'true'}
    call = actions.call_contract(url, pr_key, 'EditAppParam',
                                 data, token)
    if not is_in_block(call, url, token):
        log.error('EditAppParam ' + name + ' is failed')
        exit(1)


def update_profile(name, url, pr_key, token):
    log.info('UpdateProfile started')
    time.sleep(5)
    data = {'member_name': name}
    resp = actions.call_contract(url, pr_key, 'ProfileEdit',
                                 data, token)
    if not is_in_block(resp, url, token):
        log.error('UpdateProfile ' + name + ' is failed')
        exit(1)


def set_apla_consensus(id, url, pr_key, token):
    log.info('setAplaconsensus started')
    data = {'member_id': id, 'rid': 3}
    call = actions.call_contract(url, pr_key, 'RolesAssign',
                                 data, token)
    if not is_in_block(call, url, token):
        log.error('RolesAssign ' + id + ' is failed')
        exit(1)


if __name__ == '__main__':
    log.info('Start ' + __name__)
    wait = tools.read_config('test')['wait_tx_status']
    conf = tools.read_config('nodes')
    url = conf[0]['url']
    pr_key1 = conf[0]['private_key']
    data = actions.login(url, pr_key1, 0)
    token1 = data['jwtToken']

    print("Importing init_qs.json")
    actions.imp_app('init_qs', url, pr_key1, token1)

    
    full_nodes = []
    for c in conf:
        full_nodes.append({
            'tcp_address': c['tcp_address'],
            'api_address': c['api_address'],
            'key_id': c['keyID'],
            'public_key': c['pubKey']
        })

    print("Setting full_nodes param")               
    actions.edit_platform_param('full_nodes', json.dumps(full_nodes), url, pr_key1, token1, wait)
    



    print("Import system.json")               
    actions.imp_app('system', url, pr_key1, token1)

    print("Import conditions.json")               
    actions.imp_app('conditions', url, pr_key1, token1)
    
    print("Import basic.json")               
    actions.imp_app('basic', url, pr_key1, token1)
    
    print("Import lang_res.json")               
    actions.imp_app('lang_res', url, pr_key1, token1)

    node1 = json.dumps({'tcp_address': conf[0]['tcp_address'],
                        'api_address': conf[0]['api_address'],
                        'key_id': conf[0]['keyID'],
                        'public_key': conf[0]['pubKey']})
    print("Setting first_node param")              
    actions.edit_app_param('first_node', node1, url, pr_key1, token1, wait)
   


    print("Installing default roles")
    actions.roles_install(url, pr_key1, token1, wait)

    print("Installing voting templates")
    actions.voting_templates_install(url, pr_key1, token1, wait)

    # print("Setting voting template for sys params")
    # actions.edit_app_param('voting_sysparams_template_id', 2, url, pr_key1, token1, wait)
    
    print("Setting roles")
    #actions.set_apla_consensus(conf[0]['keyID'], url, pr_key1, token1, wait)
    #actions.set_apla_consensus(conf[1]['keyID'], url, pr_key1, token1, wait)
    #actions.set_apla_consensus(conf[2]['keyID'], url, pr_key1, token1, wait)
    #actions.set_apla_consensus(conf[3]['keyID'], url, pr_key1, token1, wait)
    #actions.set_apla_consensus(conf[4]['keyID'], url, pr_key1, token1, wait)

    print("Done...")
    