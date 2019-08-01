def major = '2'
def minor = '2'

podTemplate(yaml:
"""
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins: slave
  name: cowbull-server-cicd
  namespace: jenkins
spec:
  containers:
  - command:
    - cat
    env:
    - name: JENKINS_SECRET
      value: daa4d5dbd2d1a7aa3f10a7c96ba39b1baa3465fefdc5bd95410e460496110bd1
    - name: JENKINS_AGENT_NAME
      value: cowbull-server-43-bj3tl-fmx4l-d9zsm
    - name: JENKINS_NAME
      value: cowbull-server-43-bj3tl-fmx4l-d9zsm
    - name: JENKINS_URL
      value: http://jenkins-service/
    image: k8s-master:32080/python:3.7.4-alpine3.10
    imagePullPolicy: IfNotPresent
    name: python
    resources: {}
    securityContext:
      privileged: false
      procMount: Default
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    tty: true
    volumeMounts:
    - mountPath: /home/jenkins
      name: workspace-volume
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-hbsp9
      readOnly: true
    workingDir: /home/jenkins
  - command:
    - cat
    env:
    - name: JENKINS_SECRET
      value: daa4d5dbd2d1a7aa3f10a7c96ba39b1baa3465fefdc5bd95410e460496110bd1
    - name: JENKINS_AGENT_NAME
      value: cowbull-server-43-bj3tl-fmx4l-d9zsm
    - name: dns
      value: 8.8.8.8
    - name: JENKINS_NAME
      value: cowbull-server-43-bj3tl-fmx4l-d9zsm
    - name: JENKINS_URL
      value: http://jenkins-service/
    image: k8s-master:32080/openjdk:11-jre
    imagePullPolicy: IfNotPresent
    name: jre
    resources: {}
    securityContext:
      privileged: false
      procMount: Default
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    tty: true
    volumeMounts:
    - mountPath: /home/jenkins
      name: workspace-volume
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-hbsp9
      readOnly: true
    workingDir: /home/jenkins
  - command:
    - redis-server
    env:
    - name: JENKINS_SECRET
      value: daa4d5dbd2d1a7aa3f10a7c96ba39b1baa3465fefdc5bd95410e460496110bd1
    - name: JENKINS_AGENT_NAME
      value: cowbull-server-43-bj3tl-fmx4l-d9zsm
    - name: JENKINS_NAME
      value: cowbull-server-43-bj3tl-fmx4l-d9zsm
    - name: JENKINS_URL
      value: http://jenkins-service/
    image: k8s-master:32080/redis:5.0.3-alpine
    imagePullPolicy: IfNotPresent
    name: redis
    resources: {}
    securityContext:
      privileged: false
      procMount: Default
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    tty: true
    volumeMounts:
    - mountPath: /home/jenkins
      name: workspace-volume
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-hbsp9
      readOnly: true
    workingDir: /home/jenkins
  - env:
    - name: JENKINS_SECRET
      value: daa4d5dbd2d1a7aa3f10a7c96ba39b1baa3465fefdc5bd95410e460496110bd1
    - name: JENKINS_AGENT_NAME
      value: cowbull-server-43-bj3tl-fmx4l-d9zsm
    - name: JENKINS_NAME
      value: cowbull-server-43-bj3tl-fmx4l-d9zsm
    - name: JENKINS_URL
      value: http://jenkins-service/
    image: jenkins/jnlp-slave:alpine
    imagePullPolicy: IfNotPresent
    name: jnlp
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /home/jenkins
      name: workspace-volume
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-hbsp9
      readOnly: true
  dnsPolicy: ClusterFirstWithHost
  hostNetwork
  enableServiceLinks: true
  nodeName: vm-djs-k8s-worker-1-eus-5724
  priority: 0
  restartPolicy: Never
  schedulerName: default-scheduler
  securityContext: {}
  serviceAccount: default
  serviceAccountName: default
  terminationGracePeriodSeconds: 30
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  volumes:
  - emptyDir: {}
    name: workspace-volume
  - name: default-token-hbsp9
    secret:
      defaultMode: 420
      secretName: default-token-hbsp9
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
                python3 -m pip install -r requirements.txt
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