// -------------------------------------------------------------------
//
// Module:         python_cowbull_server
// Submodule:      Jenkinsfile
// Environments:   all
// Purpose:        Jenkins scripted pipeline to perform the CI and CD
//                 build of the python cowbull server image.
//                 NOTE: Scripted pipeline
//
// Created on:     30 July 2019
// Created by:     David Sanders
// Creator email:  dsanderscanada@nospam-gmail.com
//
// -------------------------------------------------------------------
// Modifed On   | Modified By                 | Release Notes
// -------------------------------------------------------------------
// 30 Jul 2019  | David Sanders               | First release.
// -------------------------------------------------------------------
// 06 Aug 2019  | David Sanders               | Change python3 to use
//              |                             | default python rather
//              |                             | than specific version.
// -------------------------------------------------------------------
// 06 Aug 2019  | David Sanders               | Add multi-branch
//              |                             | support and push non-
//              |                             | master branches as dev
//              |                             | and promote major/minor
//              |                             | to year month format.
// -------------------------------------------------------------------

def major = '19'
def minor = '08'
def imageName = ''

podTemplate(containers: [
    containerTemplate(name: 'redis', image: 'k8s-master:32080/redis:5.0.3-alpine', ttyEnabled: true, command: 'redis-server'),
    containerTemplate(name: 'python', image: 'k8s-master:32080/python:3.7.4-alpine3.10', ttyEnabled: true, command: 'cat'),
    containerTemplate(name: 'maven', image: 'k8s-master:32080/maven:3.6.1-jdk-11-slim', ttyEnabled: true, command: 'cat'),
    containerTemplate(name: 'docker', image: 'k8s-master:32080/docker:19.03.1-dind', ttyEnabled: true, privileged: true),
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
                python -m pip install -r requirements.txt
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
        container('maven') {
            def scannerHome = tool 'SonarQube Scanner';
            withSonarQubeEnv('Sonarqube') {
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
    stage('Quality Gate') {
        container('maven') {
            def scannerHome = tool 'SonarQube Scanner';
            timeout(time: 10, unit: 'MINUTES') {
                waitForQualityGate abortPipeline: true
            }
        }
    }
    stage('Docker Build') {
        def imageName = ""
        container('docker') {
            withCredentials([
                [$class: 'UsernamePasswordMultiBinding', 
                credentialsId: 'dockerhub',
                usernameVariable: 'USERNAME', 
                passwordVariable: 'PASSWORD']
            ]) {
                sh """
                    docker login -u "${USERNAME}" -p "${PASSWORD}"
                    if [ "${env.BRANCH_NAME}" == "master" ]
                    then
                        imageName = "dsanderscan/cowbull:${major}.${minor}.${env.BUILD_NUMBER}"
                    else
                        imageName = "dsanderscan/cowbull:${env.BRANCH_NAME}"
                    fi
                    echo "Building "${imageName}
                    docker build -t ${imageName} -f vendor/docker/Dockerfile .
                    docker push ${imageName}
                    docker image rm ${imageName}
                """
            }
        }
    }
    // stage('Docker Build') {
    //     container('docker') {
    //         when {
    //             not {branch 'master'}
    //         }
    //         withCredentials([
    //             [$class: 'UsernamePasswordMultiBinding', 
    //             credentialsId: 'dockerhub',
    //             usernameVariable: 'USERNAME', 
    //             passwordVariable: 'PASSWORD']
    //         ]) {
    //             sh """
    //                 docker login -u "${USERNAME}" -p "${PASSWORD}"
    //                 docker build -t dsanderscan/${imageName}:dev.${major}.${minor}.${env.BUILD_NUMBER} -f vendor/docker/Dockerfile .
    //                 docker push dsanderscan/${imageName}:dev."${major}"."${minor}"."${env.BUILD_NUMBER}"
    //                 docker image rm dsanderscan/${imageName}:dev."${major}"."${minor}"."${env.BUILD_NUMBER}"
    //             """
    //         }
    //     }
    // }
  }
}
