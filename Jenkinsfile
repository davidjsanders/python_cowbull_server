def persisters = [
    '{"engine_name": "redis", "parameters": {"host": "db", "port": 6379, "db": 0}}',
    '{"engine_name": "mongodb", "parameters": {"host": "db", "port": 27017, "db": "cowbull"}}'
]

def systest_persister = readJSON text: '{"engine_name": "SecureRedis", "parameters": {"host": "db", "port": 6379, "db": 0, "password": "fCFlVIE7nUD2unwYYn8agYYWXzAz1GvK"}}'
def engine1 = readJSON text: '{"persister":"redis", "image":"redis:5.0.3-alpine", "name":"redis"}'
def engine2 = readJSON text: '{"persister":"mongodb", "image":"mongo:4.0.5", "name":"mongo"}'
def test_engines = [
    engine1,
    engine2
]

def python_engine='dsanderscan/jenkins-py:3-0.1'

def image_name = ''
def logging_level = ''
def major = '1'
def minor = '2'

pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                script {
                    systest_persister['parameters']['host'] = params.RedisHost.toString()
                    systest_persister.parameters.port = params.RedisPort.toString()
                    image_name = "${params.imageName}:build-${major}.${minor}.${env.BUILD_NUMBER}"
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

        stage('Test') {
            steps {
                script {
                    for (int i = 0; i < persisters.size(); i++) {
                        echo "Testing with image: ${test_engines[i]['name']}"
                        docker.image(test_engines[i]['image']).withRun("--name ${test_engines[i]['name']}") { container ->
                            docker.image(python_engine).inside("--link ${test_engines[i]['name']}:db") {
                                withEnv(["HOME=${env.WORKSPACE}","LOGGING_LEVEL=${logging_level}"]) {
                                    // checkout scm
                                    sh """
                                        python3 -m venv env
                                        source ./env/bin/activate 
                                        export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                                        export PERSISTER='${persisters[i]}'
                                        python3 -m pip install --quiet -r requirements.txt --no-cache --user
                                        python3 -m unittest tests
                                    """
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Code Analysis') {
            steps {
                echo "Code analysis"
                script {
                    def scannerHome = tool 'SonarQube Scanner 2.8';
                    withSonarQubeEnv('sonarqube') {
                        sh "${scannerHome}/bin/sonar-scanner -Dproject.settings=./sonar-project.properties"
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    // Parameter indicates whether to set pipeline to UNSTABLE if Quality Gate fails
                    // true = set pipeline to UNSTABLE, false = don't
                    // Requires SonarQube Scanner for Jenkins 2.7+
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

        stage('System Test') {
            steps {
                script {
                    withEnv(["PERSISTER=${systest_persister.toString()}","LOGGING_LEVEL=${logging_level}"]) {
                        docker.image(image_name).inside() {
                            sh """
                                python3 -m unittest tests
                            """
                        }
                    }
                }
            }
        }

        stage('Security Scan') {
            steps {
                echo "Starting security scan"
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
                    docker tag "${image_name}" "${params.imageName}":"${major}"."${minor}"."${env.BUILD_NUMBER}"
                    docker push "${params.imageName}":"${major}"."${minor}"."${env.BUILD_NUMBER}"
                    docker rmi "${image_name}"
                    """
                }
            }
        }
    }
}