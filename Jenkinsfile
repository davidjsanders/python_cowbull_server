podTemplate(containers: [
    containerTemplate(name: 'redis', image: 'k8s-master:32080/redis:5.0.3-alpine', ttyEnabled: true, command: 'redis-server'),
    containerTemplate(name: 'python', image: 'k8s-master:32080/python:3.7.4-alpine3.10', ttyEnabled: true, command: 'cat'),
  ]) {
  node(POD_LABEL) {
    stage('Verify Redis is running') {
        container('redis') {
            sh 'redis-cli ping'
        }
    }
    stage('Setup environment') {
        git 'https://github.com/dsandersAzure/python_cowbull_server'
        container('python') {
            sh """
                python --version
                python3 -m pip install -q -r requirements.txt
            """
        }
    }
    stage('Execute Python unit tests') {
        container('python') {
            sh """
                export PYTHONPATH="\$(pwd)/:\$(pwd)/unittests"
                python -m unittest unittests
            """
        }
    }
    stage('Execute Python system tests') {
        container('python') {
            sh """
                export PYTHONPATH="\$(pwd)/:\$(pwd)/systests"
                export PERSISTER='{"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0, "password": ""}}'
                export LOGGING_LEVEL=10
                python -m unittest systests
            """
        }
    }
  }
}