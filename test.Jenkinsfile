/**
 * This pipeline will build and deploy a Docker image with Kaniko
 * https://github.com/GoogleContainerTools/kaniko
 * without needing a Docker host
 *
 * You need to create a jenkins-docker-cfg secret with your docker config
 * as described in
 * https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-secret-in-the-cluster-that-holds-your-authorization-token
 *
 * ie.
 * kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=csanchez --docker-password=mypassword --docker-email=john@doe.com
 */

pipeline {
  agent {
    kubernetes {
      //cloud 'kubernetes'
      defaultContainer 'kaniko'
      yaml '''
        kind: Pod
        spec:
          containers:
          - name: kaniko
            image: gcr.io/kaniko-project/executor:v1.7.0-debug
            imagePullPolicy: Always
            command:
            - sleep
            args:
            - 99d
            env:
            - name: PYPI_USER
              valueFrom:
                secretKeyRef:
                  name: jenkins-docker-secret
                  key: username
            - name: PYPI_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: jenkins-docker-secret
                  key: password
            volumeMounts:
              - name: jenkins-docker-cfg
                mountPath: /kaniko/.docker
          volumes:
          - name: jenkins-docker-cfg
            projected:
              sources:
              - secret:
                  name: regcred-push
                  items:
                    - key: .dockerconfigjson
                      path: config.json
'''
    }
  }
  environment {
    BRANCH_NAME_ESC = env.BRANCH_NAME.replace("/", "_")
  }
  stages {
    stage('Build with Kaniko') {
      steps {
        checkout scm
        sh "/kaniko/executor -f \"`pwd`/test.Dockerfile\" -c \"`pwd`\" --tarPath=\"`pwd`\"/testresult.tar --no-push --single-snapshot --build-arg pypiuser=\"\${PYPI_USER}\" --build-arg pypipass=\"\${PYPI_PASSWORD}\" --destination=dilcher-configuration-test:${BRANCH_NAME_ESC}-${env.BUILD_NUMBER}"
        sh "tar -xvf \"`pwd`/testresult.tar\" manifest.json"
        sh "cat \"./manifest.json\" | grep -e '[^\"]*.tar.gz' -o | tail -n 1 | head -n 1"
        sh "mkdir -p \"`pwd`/test_layer\""
        sh "TARFILE=`cat \"./manifest.json\" | grep -e '[^\"]*.tar.gz' -o | tail -n 1 | head -n 1` && tar -xvf \"`pwd`/testresult.tar\" \"\${TARFILE}\" && mv \"\${TARFILE}\" \"`pwd`/test_layer/test_layer.tar.gz\""
        sh "rm -f \"`pwd`/testresult.tar\""
        sh "cd \"`pwd`/test_layer\" && tar -xzvf \"`pwd`/test_layer.tar.gz\""
        sh "mv \"`pwd`/test_layer/tmp/test/test-reports\" \"`pwd`/test_reports\""
        sh "sed -i -e \"s%/tmp/test%`pwd`%g\" \"`pwd`/test_reports/coverage/coverage.xml\""
        sh "head -n 10 \"`pwd`/test_reports/coverage/coverage.xml\""
        sh "rm -rf \"`pwd`/test_layer\""
      }
    }
    stage('Publishing test & coverage results') {
      steps {
        recordCoverage(
            tools: [[parser: 'COBERTURA', pattern: '**/test_reports/coverage/coverage.xml']],
            sourceDirectories: [[path: "."]],
            qualityGates: [[threshold: 80, metric: 'LINE', baseline: 'PROJECT', unstable: true], [threshold: 80, metric: 'METHOD', baseline: 'PROJECT', unstable: true], [threshold: 80, metric: 'BRANCH', baseline: 'PROJECT', unstable: true], [threshold: 70, metric: 'FILE', baseline: 'PROJECT', unstable: true]]
        )
//         cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: '**/test_reports/coverage/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
        junit allowEmptyResults: true, testResults: '**/test_reports/unittest/unittest.xml'
        recordIssues(tools: [flake8(pattern: '**/test_reports/flake8/flake8.txt')])
      }
    }
  }
}
