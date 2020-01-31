#!groovy​

def label = "mypod-${UUID.randomUUID().toString()}"
podTemplate(label: label, imagePullSecrets: ["regsecret"], containers: [
    containerTemplate(name: 'docker', image: 'docker', ttyEnabled: true, command: 'cat',
        envVars: [containerEnvVar(key: 'DOCKER_CONFIG', value: '/tmp/'),])],
        volumes: [secretVolume(secretName: 'jenkins-docker-secret', mountPath: '/var/run/secrets/registry-account/'),
        hostPathVolume(hostPath: '/var/run/docker.sock', mountPath: '/var/run/docker.sock'),
        persistentVolumeClaim(claimName: 'jenkins-slave-docker-10gi', mountPath: '/var/lib/docker')
  ]) {
    node(label) {

        def app
        def BRANCH_NAME_ESC = env.BRANCH_NAME.replace("/", "_")

        stage('Clone repository') {
            /* Let's make sure we have the repository cloned to our workspace */
            checkout scm
        }

        container('docker') {
                stage('Docker Build & Push Current & Latest Versions') {
                    sh ("""
                    #!/bin/bash
                    set +x
                    PYPI_USER=`cat /var/run/secrets/registry-account/username`
                    PYPI_PASSWORD=`cat /var/run/secrets/registry-account/password`
                    docker build -t dilcher-configuration:${BRANCH_NAME_ESC}-${env.BUILD_NUMBER} --build-arg pypiuser="\${PYPI_USER}" --build-arg pypipass="\${PYPI_PASSWORD}" -f ./test.Dockerfile .
                    container_id=\$(docker create dilcher-configuration:${BRANCH_NAME_ESC}-${env.BUILD_NUMBER})
                    rm -rf ./test-reports
                    docker cp \$container_id:/tmp/test/test-reports ./test-reports
                    pwd
                    find *
                    docker rm -v \$container_id
                    docker image rm -f dilcher-configuration:${BRANCH_NAME_ESC}-${env.BUILD_NUMBER}
                    """)
                    cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: '**/test-reports/coverage/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
                }
        }
    }
}
