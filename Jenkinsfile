def major = '2'
def minor = '2'

podTemplate(
    yaml: """
---
apiVersion: "v1"
kind: "Pod"
metadata:
  annotations:
    buildUrl: "http://jenkins-service/job/cowbull-server/38/"
  labels:
    jenkins: "slave"
    jenkins/cowbull-server_38-jqxj3: "true"
  name: "cowbull-server-38-jqxj3-rzr8s-8ckzw"
spec:
  containers:
  - command:
    - "cat"
    env:
    - name: "JENKINS_SECRET"
      value: "********"
    - name: "JENKINS_AGENT_NAME"
      value: "cowbull-server-38-jqxj3-rzr8s-8ckzw"
    - name: "JENKINS_NAME"
      value: "cowbull-server-38-jqxj3-rzr8s-8ckzw"
    - name: "JENKINS_URL"
      value: "http://jenkins-service/"
    image: "k8s-master:32080/python:3.7.4-alpine3.10"
    imagePullPolicy: "IfNotPresent"
    name: "python"
    resources:
      limits: {}
      requests: {}
    securityContext:
      privileged: false
    tty: true
    volumeMounts:
    - mountPath: "/home/jenkins"
      name: "workspace-volume"
      readOnly: false
    workingDir: "/home/jenkins"
  - command:
    - "cat"
    env:
    - name: "JENKINS_SECRET"
      value: "********"
    - name: "JENKINS_AGENT_NAME"
      value: "cowbull-server-38-jqxj3-rzr8s-8ckzw"
    - name: "JENKINS_NAME"
      value: "cowbull-server-38-jqxj3-rzr8s-8ckzw"
    - name: "JENKINS_URL"
      value: "http://jenkins-service/"
    image: "k8s-master:32080/openjdk:11-jre"
    imagePullPolicy: "IfNotPresent"
    name: "jre"
    resources:
      limits: {}
      requests: {}
    securityContext:
      privileged: false
    tty: true
    volumeMounts:
    - mountPath: "/home/jenkins"
      name: "workspace-volume"
      readOnly: false
    workingDir: "/home/jenkins"
  - command:
    - "redis-server"
    env:
    - name: "JENKINS_SECRET"
      value: "********"
    - name: "JENKINS_AGENT_NAME"
      value: "cowbull-server-38-jqxj3-rzr8s-8ckzw"
    - name: "JENKINS_NAME"
      value: "cowbull-server-38-jqxj3-rzr8s-8ckzw"
    - name: "JENKINS_URL"
      value: "http://jenkins-service/"
    image: "k8s-master:32080/redis:5.0.3-alpine"
    imagePullPolicy: "IfNotPresent"
    name: "redis"
    resources:
      limits: {}
      requests: {}
    securityContext:
      privileged: false
    tty: true
    volumeMounts:
    - mountPath: "/home/jenkins"
      name: "workspace-volume"
      readOnly: false
    workingDir: "/home/jenkins"
  - env:
    - name: "JENKINS_SECRET"
      value: "********"
    - name: "JENKINS_AGENT_NAME"
      value: "cowbull-server-38-jqxj3-rzr8s-8ckzw"
    - name: "JENKINS_NAME"
      value: "cowbull-server-38-jqxj3-rzr8s-8ckzw"
    - name: "JENKINS_URL"
      value: "http://jenkins-service/"
    image: "jenkins/jnlp-slave:alpine"
    name: "jnlp"
    volumeMounts:
    - mountPath: "/home/jenkins"
      name: "workspace-volume"
      readOnly: false
  nodeSelector: {}
  restartPolicy: "Never"
  hostNetwork: true
  dnsPolicy: ClusterFirstWithHostNet
  volumes:
  - emptyDir: {}
    name: "workspace-volume"
    """
) {
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
                coverage run -m unittest unittests
                coverage xml -i
            """
        }
    }
    stage('Execute Python system tests') {
        container('python') {
            sh """
                export PYTHONPATH="\$(pwd)/:\$(pwd)/systests"
                export PERSISTER='{"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0, "password": ""}}'
                export LOGGING_LEVEL=30
                python -m unittest systests
            """
        }
    }
    stage('Sonarqube code coverage') {
        container('jre') {
            def scannerHome = tool 'SonarQube Scanner';
            withSonarQubeEnv('Sonarqube') { // If you have configured more than one global server connection, you can specify its name
                sh """
                    rm -rf *.pyc
                    rm -f /var/jenkins_home/workspace/cowbull-server/.scannerwork/report-task.txt
                    rm -f /var/jenkins_home/workspace/cowbull-server/.sonar/report-task.txt
                    echo "Run sonar scanner"
                    chmod +x ${scannerHome}/bin/sonar-scanner
                    ${scannerHome}/bin/sonar-scanner -X -Dproject.settings=./sonar-project.properties -Dsonar.python.coverage.reportPath=./coverage.xml -Dsonar.projectVersion="${major}"."${minor}"."${env.BUILD_NUMBER}"
                """
            }
        }
    }
    stage('Sonarqube quality gate') {
        sh """
          echo "Still a work in progress :) "
        """
    }
  }
}