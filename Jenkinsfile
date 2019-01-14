pipeline {
    environment {
        HOME="${env.WORKSPACE}"
    }
    agent none
    stages {
        stage('Test') {
            agent {
                docker {
                    image 'dsanderscan/jenkins-py3-0.1' 
                }
            }
            steps {
                checkout scm
                script {
                    docker.image('redis:5.0.3-alpine').withRun('-p 6379:6379') { c ->
                    }
                }
                sh """
                    pwd
                    ls -als
                    python3 -m venv env
                    source ./env/bin/activate 
                    export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                    export PERSISTER='PERSISTER={"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0}}'
                    echo "*** PYTHONPATH=\${PYTHONPATH}"
                    python3 -m pip install -r requirements.txt
                    python3 -m unittest tests
                """
            }
        }
    }
}