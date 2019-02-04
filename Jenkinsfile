
def unique_id = UUID.randomUUID().toString()
def persisters = [
    '{"engine_name": "redis", "parameters": {"host": "db", "port": 6379, "db": 0}}',
    '{"engine_name": "mongodb", "parameters": {"host": "db", "port": 27017, "db": "cowbull"}}'
]

def systest_persister = readJSON text: '{"engine_name": "redis", "parameters": {"host": "db", "port": 6379, "db": 0, "password": ""}}'
def engine1 = readJSON text: '{"persister":"redis", "image":"redis:5.0.3-alpine", "name":"redis"}'
def engine2 = readJSON text: '{"persister":"mongodb", "image":"mongo:4.0.5", "name":"mongo"}'
def test_engines = [
    engine1,
    engine2
]

def python_engine='dsanderscan/jenkins-py:3-0.2'

def image_name = ''
def logging_level = ''
def major = '2'
def minor = '0'

pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'systest_persister', variable: 'SECRET')]) {
                        systest_persister['parameters']['password'] = SECRET
                    }
                    systest_persister['parameters']['host'] = params.RedisHost.toString()
                    systest_persister.parameters.port = params.RedisPort.toString()
                    image_name = "dsanderscan/cowbull:${unique_id}"
                    logging_level = params.LoggingLevel
                    echo "Pulling required sidecars"
                    for (int i = 0; i < persisters.size(); i++) {
                        echo "Pulling test sidecar ${test_engines[i]['name']}: ${test_engines[i]['image']}"
                        sh """
                            docker pull ${test_engines[i]['image']}
                        """
                    }
                }
            }
        }

        stage('Unit Test') {
            steps {
                script {
                    echo "Testing with image: ${test_engines[0]['name']}"
                    docker.image(test_engines[0]['image']).withRun("--name ${unique_id}-${test_engines[0]['name']}") { container ->
                        docker.image(python_engine).inside("--link ${unique_id}-${test_engines[0]['name']}:db") {
                            withEnv(["PERSISTER=${persisters[0]}","HOME=${env.WORKSPACE}","LOGGING_LEVEL=${logging_level}"]) {
                                // checkout scm
                                sh """
                                    python3 -m venv /tmp/env
                                    source /tmp/env/bin/activate 
                                    export PYTHONPATH="\$(pwd)/:\$(pwd)/unittests"
                                    python3 -m pip install -q -r requirements.txt
                                    coverage run -m unittest unittests
                                    coverage xml -i
                                """
                            }
                        }
                    }
                }
            }
        }

        stage('Code Analysis') {
            // agent {
            //     docker {
            //         image python_engine
            //     }
            // }
            steps {
                echo "Code analysis"
                script {
                    def scannerHome = tool 'SonarQube Scanner 2.8';
                    withSonarQubeEnv('sonarqube') {
                        sh """
                            rm -rf *.pyc
                            rm -f /var/jenkins_home/workspace/cowbull-server/.scannerwork/report-task.txt
                            rm -f /var/jenkins_home/workspace/cowbull-server/.sonar/report-task.txt
                            echo "Run sonar scanner"
                            ${scannerHome}/bin/sonar-scanner -Dproject.settings=./sonar-project.properties -Dsonar.python.coverage.reportPath=./coverage.xml -Dsonar.projectVersion="${major}"."${minor}"."${env.BUILD_NUMBER}"
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            environment {
                scannerHome = tool 'SonarQube Scanner 2.8'
            }
            steps {
                echo "Quality validation"
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo "Building image ${image_name}"
                    withEnv(["image_tag=${image_name}"]) {
                        sh """
                            docker build -t ${image_tag} -f vendor/docker/Dockerfile .
                        """
                    }
                }
            }
        }

        stage('Security Scan') {
            steps {
                echo "Starting security scan"
                aquaMicroscanner imageName: image_name, notCompliesCmd: '', onDisallowed: 'fail', outputFormat: 'html'
            }
        }

        stage('Image Test') {
            steps {
                script {
                    for (int i = 0; i < persisters.size(); i++) {
                        echo "Testing with image: ${test_engines[i]['name']}"
                        docker.image(test_engines[i]['image']).withRun("--name ${unique_id}-${test_engines[i]['name']}") { container ->
                            docker.image(image_name).inside("--link ${unique_id}-${test_engines[i]['name']}:db") {
                                withEnv(["PERSISTER=${persisters[i]}","LOGGING_LEVEL=${logging_level}"]) {
                                    sh """
                                        export PYTHONPATH="\$(pwd)/:\$(pwd)/systests"
                                        python -m unittest systests
                                    """
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('System Test') {
            steps {
                script {
                    withEnv(["PERSISTER=${systest_persister.toString()}","LOGGING_LEVEL=${logging_level}"]) {
                        docker.image(image_name).inside() {
                            sh """
                                export PYTHONPATH="\$(pwd)/:\$(pwd)/systests"
                                python -m unittest systests
                            """
                        }
                    }
                }
            }
        }

        stage('Push') {
            steps {
                echo "Pushing ${image_name}"
                withCredentials([
                    [$class: 'UsernamePasswordMultiBinding', 
                    credentialsId: 'dockerhub',
                    usernameVariable: 'USERNAME', 
                    passwordVariable: 'PASSWORD']
                ]) {
                    sh """
                    docker login -u "${USERNAME}" -p "${PASSWORD}"
                    docker tag "${image_name}" dsanderscan/cowbull:"${major}"."${minor}"."${env.BUILD_NUMBER}"
                    docker push dsanderscan/cowbull:"${major}"."${minor}"."${env.BUILD_NUMBER}"
                    docker rmi "${image_name}"
                    docker rmi dsanderscan/cowbull:"${major}"."${minor}"."${env.BUILD_NUMBER}"
                    rm -f /var/jenkins_home/.docker/config.json
                    #
                    # TODO
                    #
                    # 1. ADD docker rmi of build and prod image
                    # 2. Clear up /var/jenkins_home/.docker/config.json
                    """
                }
            }
        }
    }
}