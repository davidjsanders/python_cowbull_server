pipeline {
    agent any
    environment {
        REDIS_PERSISTER='{"engine_name": "redis", "parameters": {"host": "redis", "port": 6379, "db": 0}}'
        MONGO_PERSISTER='{"engine_name": "mongodb", "parameters": {"host": "mongo", "port": 27017, "db": "cowbull"}}'
    }

    stages {
        stage('Clone') {
            steps {
                /* Let's make sure we have the repository cloned to our workspace */
                checkout scm
            }
        }

        stage('Test') {
            steps {
                script {
                    def persisters=[]
                    def sidecars=[]
                    sidecars[0] = 'redis:5.0.3-alpine'
                    sidecars[1] = 'mongo:4.0.5'
                    persisters[0] = '{"engine_name": "redis", "parameters": {"host": "db", "port": 6379, "db": 0}}'
                    persisters[1] = '{"engine_name": "mongodb", "parameters": {"host": "db", "port": 27017, "db": "cowbull"}}'
                    for (int i = 0; i < persisters.size; i++) {
                        docker.image('${sidecars[0]}').withRun('--name db') { container ->
                            docker.image('dsanderscan/jenkins-py3-0.1').inside('--link db:db') {
                                withEnv(["HOME=${env.WORKSPACE}"]) {
                                    checkout scm
                                    sh """
                                        #export PATH="\$(pwd)/.local/bin:\$PATH"
                                        python3 -m venv env
                                        source ./env/bin/activate 
                                        export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                                        export PERSISTER='${persisters[i]}'
                                        printf "\n** Validation Loop ${i}\n\n"
                                        echo "*** PYTHONPATH=\${PYTHONPATH}"
                                        python3 -m pip install -r requirements.txt --no-cache --user
                                        python3 -m unittest tests
                                    """
                                }
                            }
                        }
                    }
                    // docker.image('redis:5.0.3-alpine').withRun('--name redis') { container ->
                    //     docker.image('dsanderscan/jenkins-py3-0.1').inside('--link redis:redis') {
                    //         withEnv(["HOME=${env.WORKSPACE}"]) {
                    //             checkout scm
                    //             sh """
                    //                 #export PATH="\$(pwd)/.local/bin:\$PATH"
                    //                 python3 -m venv env
                    //                 source ./env/bin/activate 
                    //                 export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                    //                 export PERSISTER='\${REDIS_PERSISTER}'
                    //                 printf "\n** Validating build with Redis\n\n"
                    //                 echo "*** PYTHONPATH=\${PYTHONPATH}"
                    //                 python3 -m pip install -r requirements.txt --no-cache --user
                    //                 python3 -m unittest tests
                    //             """
                    //         }
                    //     }
                    // }
                    // docker.image('mongo:4.0.5').withRun('--name mongo') { container ->
                    //     docker.image('dsanderscan/jenkins-py3-0.1').inside('--link mongo:mongo') {
                    //         withEnv(["HOME=${env.WORKSPACE}"]) {
                    //             checkout scm
                    //             sh """
                    //                 python3 -m venv env
                    //                 source ./env/bin/activate 
                    //                 export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                    //                 export PERSISTER='{"engine_name": "mongodb", "parameters": {"host": "mongo", "port": 27017, "db": "cowbull"}}'
                    //                 echo "*** PYTHONPATH=\${PYTHONPATH}"
                    //                 python3 -m pip install -r requirements.txt --no-cache --user
                    //                 python3 -m unittest tests
                    //             """
                    //         }
                    //     }
                    // }
                }
            }
        }

        stage('Build') {
            steps {
                sh """
                    docker build -t not_sustainable_image -f vendor/docker/Dockerfile .
                """
            }
        }

        // stage{'SysTest'} {
        //     docker.image('redis:5.0.3-alpine').withRun('--name redis') { container ->
        //         docker.image('not_sustainable_image').inside('--link redis:redis') {
        //             sh """
        //                 python3 -m unittest tests
        //             """
        //         }
        //     }
        // }

        // stage('Validate') {
        //     steps {
        //         docker.image('redis:5.0.3-alpine').withRun('--name redis') { c ->
        //             docker.image('not_sustainable_image').inside('--link redis:redis') {
        //                 sh """
        //                     export PERSISTER='{"engine_name": "redis", "parameters": {"host": "redis", "port": 6379, "db": 0}}'
        //                     python3 -m unittest tests
        //                 """
        //             }
        //         }
        //     }
        // }

        // stage('Push') {
        //     steps {
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
        //     }
        // }
    }
}