import subprocess
import time
import os
import json
import argparse
import shutil
import sys
import logging as log


def init():
    module_dir = os.path.dirname(os.path.abspath(__file__))
    libs_dir = os.path.split(module_dir)[0]
    libs_path = os.path.join(libs_dir, 'libs')
    sys.path.insert(0, libs_path)
    
def initParser():
    curDir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()

    parser.add_argument('-binary', required=True)
    parser.add_argument('-workDir', default=os.path.join(curDir, 'data'))

    parser.add_argument('-dbHost', default='0.0.0.0')
    parser.add_argument('-dbPort', default='5432')
    parser.add_argument('-dbUser', default='postgres')
    parser.add_argument('-dbPassword', default='password')

    parser.add_argument('-tcpPort1', default='7048')
    parser.add_argument('-httpPort1', default='7049')
    parser.add_argument('-dbName1', default='apla1')

    parser.add_argument('-tcpPort2', default='7058')
    parser.add_argument('-httpPort2', default='7059')
    parser.add_argument('-dbName2', default='apla2')

    parser.add_argument('-tcpPort3', default='7068')
    parser.add_argument('-httpPort3', default='7069')
    parser.add_argument('-dbName3', default='apla3')

    parser.add_argument('-tcpPort4', default='7078')
    parser.add_argument('-httpPort4', default='7079')
    parser.add_argument('-dbName4', default='apla4')

    parser.add_argument('-tcpPort5', default='7088')
    parser.add_argument('-httpPort5', default='7089')
    parser.add_argument('-dbName5', default='apla5')

    parser.add_argument('-gapBetweenBlocks', default='2')
    parser.add_argument('-centrifugo', required=False)
    parser.add_argument('-test', default='true')
    parser.add_argument('-wait', default='3')

    parser.add_argument("-onlyStartNodes", default='false')

    args = parser.parse_args()
    return vars(args)

def initDirectoryStructure(workDirArgValue):
    workDir = os.path.abspath(workDirArgValue)
    workDirs = dict()
    workDirs['1'] = os.path.join(workDir, 'node1')
    workDirs['2'] = os.path.join(workDir, 'node2')
    workDirs['3'] = os.path.join(workDir, 'node3')
    workDirs['4'] = os.path.join(workDir, 'node4')
    workDirs['5'] = os.path.join(workDir, 'node5')
    firstBlockPath = os.path.join(workDir, 'node1', '1block')

    if os.path.exists(workDir):
        shutil.rmtree(workDir)
    os.makedirs(workDirs['1'])
    os.makedirs(workDirs['2'])
    os.makedirs(workDirs['3'])
    os.makedirs(workDirs['4'])
    os.makedirs(workDirs['5'])
    log.info('Work dirs created')

    return workDirs, firstBlockPath

def initCentrifugoAndRun(centrifugoArgValue):
    # Set centrifugo variables
    global centrifugo_url
    global centrifugo_secret
    cenConfig = os.path.join(centrifugoArgValue, 'config.json')
    cenPath = os.path.join(centrifugoArgValue, 'centrifugo')
    log.info('Setted centrifugo variables')

    # Create config for centrifugo
    cen_config_string = {
        'secret': centrifugo_secret,
        'admin_secret': 'admin'
    }
    with open(cenConfig, 'w') as cen_conf_file:
        json.dump(cen_config_string, cen_conf_file, indent=4)

    # Run centrifugo
    if sys.platform == 'win32':
        centrifugo = subprocess.Popen([
            cenPath,
            '--config='+cenConfig,
            '--admin',
            '--insecure_admin',
            '--web'
        ])
    else:
        centrifugo = subprocess.Popen([
            cenPath,
            '--config='+cenConfig,
            '--admin',
            '--insecure_admin'
        ])

def generateConfig(binary, workDir, dbName, dbPassword, tcpPort, httpPort,
             firstBlockPath = None, nodesAddr = None):
    global centrifugo_url
    global centrifugo_secret

    params = [
        'config',
        '--dataDir=' + workDir,
        '--dbHost=' + "127.0.0.1",
        '--dbPort=' + "5432",
        '--dbUser=' + "postgres",
        '--dbName=' + dbName,
        '--dbPassword=' + dbPassword,
        '--centUrl=' + centrifugo_url,
        '--centSecret=' + centrifugo_secret,
        '--tcpPort=' + tcpPort,
        '--httpPort=' + httpPort
    ]
    if firstBlockPath:
        params.append('--firstBlock=' + firstBlockPath)
    if nodesAddr:
        params.append('--nodesAddr=' + nodesAddr)
    config1 = subprocess.Popen([
        binary,
        *params
    ])
    
def generateKeys(binary, workDir):
    return subprocess.Popen([
        binary,
        'generateKeys',
        '--config=' + workDir+ '/config.toml'
    ])

def generateFirstBlock(binary, workDir, isTest):
    # Generate first block
    return subprocess.Popen([
        binary,
        'generateFirstBlock',
        '--config=' + workDir + '/config.toml',
        '--test=' + isTest,
        '--private=true'
    ])

def initDatabase(binary, workDir):
    subprocess.Popen([
        binary,
        'initDatabase',
        '--config=' + workDir + '/config.toml'
    ])

def startNode(binary, workDir):
    return subprocess.Popen([
        binary,
        'start',
        '--config='+workDir+'/config.toml'
    ])

def initAndStartNode(binary, workDir, dbName, dbPassword, 
        firstBlockPath=None, tcpPort=None, httpPort=None, nodesAddr=None, isFirstNode=False, isTest='true', onlyStartNodes=False):
    
    global wait 

    if not onlyStartNodes:
        generateConfig(
            binary=binary,
            workDir=workDir,
            dbName=dbName,
            dbPassword=dbPassword,
            firstBlockPath=firstBlockPath,
            tcpPort=tcpPort,
            httpPort=httpPort,
            nodesAddr=nodesAddr
        )
        time.sleep(wait)
        
        generateKeys(
            binary=binary,
            workDir=workDir
        )
        time.sleep(wait)

        if isFirstNode:
            generateFirstBlock(
                binary=binary,
                workDir=workDir,
                isTest=isTest
            )
            time.sleep(wait)
        
        initDatabase(binary, workDir)
        time.sleep(wait)

    startNode(binary, workDir)
    time.sleep(wait)
    
def saveNodesConfig(workDirs, args):
    config =[]
    full_nodes_config = []

    for key, workDir in workDirs.items():
        with open(os.path.join(workDir, 'PrivateKey'), 'r') as f:
            priv_key = f.read()
        with open(os.path.join(workDir, 'PublicKey'), 'r') as f:
            pub_key =  f.read()
        with open(os.path.join(workDir, 'KeyID'), 'r') as f:
            key_id = f.read()
        with open(os.path.join(workDir, 'NodePublicKey'), 'r') as f:
            node_public_key = f.read()

        nodeConfig = {
            'url': 'http://localhost:' + args['httpPort' + key] + '/api/v2',
            'private_key': priv_key,
            'keyID': key_id,
            'pubKey': node_public_key,
            'tcp_address': 'localhost:' + args['tcpPort' + key],
            'api_address': 'http://localhost:' + args['httpPort' + key],
            'db':
            {
                'dbHost': args['dbHost'],
                'dbName': args['dbName' + key],
                'login': args['dbUser'],
                'pass': args['dbPassword']
            }
        }
        config.append(nodeConfig)
        full_nodes_config.append({
            "tcp_address": '127.0.0.1:' + args['tcpPort' + key],
            "api_address": "127.0.0.1:" + args['httpPort' + key],
            "key_id": key_id,
            "public_key": node_public_key
        })


    curDir = os.path.dirname(os.path.abspath(__file__))
    confPath = os.path.join(curDir, './../', 'nodesConfig.json')
    confPath = os.path.normpath(confPath)
    with open(confPath, 'w') as fconf:
        fconf.write(json.dumps(config, indent=4))
    
    fullNodePath = os.path.join(curDir, './../', 'full_nodes.json')
    fullNodePath = os.path.normpath(fullNodePath)
    with open(fullNodePath, 'w') as fconf:
        fconf.write(json.dumps(full_nodes_config, indent=4))
    
    

if __name__ == '__main__':
    global wait
    wait = 2
    global centrifugo_url
    centrifugo_url = 'http://127.0.0.1:8000'
    global centrifugo_secret
    centrifugo_secret = '4597e75c-4376-42a6-8c1f-7e3fc7eb2114'

    init()
    args = initParser()
    print(args)
    
    binary = os.path.abspath(args['binary'])
    wait = int(args['wait'])
    onlyStartNodes = args['onlyStartNodes'] == 'true'

    if not onlyStartNodes:
        workDirs, firstBlockPath = initDirectoryStructure(args['workDir'])

    
    #log.info("Starting centrifugo...")
    #initCentrifugoAndRun(args.centrifugo)
    #time.sleep(wait)
    #log.info("Centrifugo started")

    # workDir, dbName, dbPassword, firstBlockPath=None, tcpPort=None, httpPort=None, nodesAddr=None, isFirstNode=False
    log.info("Starting node 1...")
    initAndStartNode(
        binary=binary,
        workDir=workDirs['1'],
        dbName=args['dbName1'],
        dbPassword=args['dbPassword'],
        tcpPort=args['tcpPort1'],
        httpPort=args['httpPort1'],
        isFirstNode=True,
        isTest=args['test'],
        onlyStartNodes=onlyStartNodes
    )
    time.sleep(wait)
    firstNodeAddress = '127.0.0.1:' + args['tcpPort1']
    log.info("Node 1 started...")

    log.info("Starting node 2...")
    initAndStartNode(
        binary=binary,
        workDir=workDirs['2'],
        dbName=args['dbName2'],
        dbPassword=args['dbPassword'],
        tcpPort=args['tcpPort2'],
        httpPort=args['httpPort2'],
        nodesAddr=firstNodeAddress,
        firstBlockPath=firstBlockPath,
        isFirstNode=False,
        onlyStartNodes=onlyStartNodes
    )
    time.sleep(wait)
    log.info("Node 2 started...")

    log.info("Starting node 3...")
    initAndStartNode(
        binary=binary,
        workDir=workDirs['3'],
        dbName=args['dbName3'],
        dbPassword=args['dbPassword'],
        tcpPort=args['tcpPort3'],
        httpPort=args['httpPort3'],
        nodesAddr=firstNodeAddress,
        firstBlockPath=firstBlockPath,
        isFirstNode=False,
        onlyStartNodes=onlyStartNodes
    )
    time.sleep(wait)
    log.info("Node 3 started...")

    log.info("Starting node 4...")
    initAndStartNode(
        binary=binary,
        workDir=workDirs['4'],
        dbName=args['dbName4'],
        dbPassword=args['dbPassword'],
        tcpPort=args['tcpPort4'],
        httpPort=args['httpPort4'],
        nodesAddr=firstNodeAddress,
        firstBlockPath=firstBlockPath,
        isFirstNode=False,
        onlyStartNodes=onlyStartNodes
    )
    time.sleep(wait)
    log.info("Node 4 started...")

    log.info("Starting node 5...")
    initAndStartNode(
        binary=binary,
        workDir=workDirs['5'],
        dbName=args['dbName5'],
        dbPassword=args['dbPassword'],
        tcpPort=args['tcpPort5'],
        httpPort=args['httpPort5'],
        nodesAddr=firstNodeAddress,
        firstBlockPath=firstBlockPath,
        isFirstNode=False,
        onlyStartNodes=onlyStartNodes
    )
    time.sleep(wait)
    log.info("Node 5 started...")

    log.info("Creating nodesConfig.json")
    saveNodesConfig(workDirs, args)
    log.info("nodesConfig.json created")

    log.info("5 nodes were successfully started")










