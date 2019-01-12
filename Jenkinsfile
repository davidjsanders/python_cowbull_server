pipeline {
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
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh """
                      pwd
                      ls -als
                      python3 -m venv env
                      source ./env/bin/activate 
                      export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                      echo "*** PYTHONPATH=\${PYTHONPATH}"
                      python3 -m pip install -r requirements.txt
                      python3 -m unittest tests
                    """
                }
            }
        }
    }
}