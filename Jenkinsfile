pipeline {
    stages {
        agent {
            docker {
                image 'dsanderscan/jenkins-py3-0.1'
            }
        }
        stage('Test') {
            node {
                checkout scm
                docker.image('redis:5.0.3-alpine').withRun('-p 6379:6379') { c ->
                }
                docker.image('dsanderscan/jenkins-py3-0.1').withRun() {
                    sh """
                        pwd
                        ls -als
                        python3 -m venv env
                        source ./env/bin/activate 
                        export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                        export PERSISTER='PERSISTER={"engine_name": "redis", "parameters": {"\${outerHost}": "localhost", "port": 6379, "db": 0}}'
                        echo "*** PYTHONPATH=\${PYTHONPATH}"
                        echo "*** PERSISTER=\${PERSISTER}"
                        python3 -m pip install -r requirements.txt
                        python3 -m unittest tests
                    """
                }
            }
        }
    }
}