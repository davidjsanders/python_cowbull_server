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

pipeline {
    agent any
    environment {
        REDIS_PERSISTER='{"engine_name": "redis", "parameters": {"host": "redis", "port": 6379, "db": 0}}'
        MONGO_PERSISTER='{"engine_name": "mongodb", "parameters": {"host": "mongo", "port": 27017, "db": "cowbull"}}'
    }

    stages {
        stage('Setup') {
            steps {
                // /* Let's make sure we have the repository cloned to our workspace */
                // checkout scm
                script {
                    systest_persister['parameters']['host'] = '${params.RedisHost.toString()}'
                    systest_persister.parameters.port = "${params.RedisPort.toString()}"
                    image_name = "${params.imageName}:test-${params.Version}.${env.BUILD_NUMBER}"
                    echo "Set image_name        -> ${image_name}"
                    echo "Set systest_persister -> ${systest_persister}"
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    for (int i = 0; i < persisters.size(); i++) {
                        echo "Testing ${test_engines[i]['image']}"
                        docker.image(test_engines[i]['image']).withRun("--name ${test_engines[i]['name']}") { container ->
                            docker.image(python_engine).inside("--link ${test_engines[i]['name']}:db") {
                                withEnv(["HOME=${env.WORKSPACE}"]) {
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

        stage('Build') {
            steps {
                script {
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
                    for (int i = 0; i < persisters.size(); i++) {
                        docker.image(test_engines[i]['image']).withRun("--name ${test_engines[i]['name']}") { container ->
                            docker.image(image_name).inside("--link ${test_engines[i]['name']}:db") {
                                withEnv(["HOME=${env.WORKSPACE}"]) {
                                    // checkout scm
                                    sh """
                                        export PERSISTER='${persisters[i]}'
                                        python3 -m unittest tests
                                    """
                                }
                            }
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
        //         withCredentials([
        //             [$class: 'UsernamePasswordMultiBinding', 
        //             credentialsId: 'dockerhub',
        //             usernameVariable: 'USERNAME', 
        //             passwordVariable: 'PASSWORD']
        //         ]) {
        //             sh """
        //             docker login -u "${USERNAME}" -p "${PASSWORD}"
        //             docker tag not_sustainable_image "${params.imageName}":"${params.Environment}"-"${params.Version}"."${env.BUILD_NUMBER}"
        //             docker push "${params.imageName}":"${params.Environment}"-"${params.Version}"."${env.BUILD_NUMBER}"
        //             """
        //         }
            }
        }
    }
}