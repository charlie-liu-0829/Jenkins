pipeline {
    agent any

    environment {
        DB_HOST = '127.0.0.1'
        DB_PORT = '3306'
        DB_USER = 'root'
        DB_PASSWORD = 'Lym030829'
        DB_NAME = 'ecommerce_demo'
    }

    stages {
        stage('运行自动化测试') {
            steps {
                sh '''
                    set -eu

                    export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
                    export PATH="/Users/charlieliu/miniforge3/envs/pytest/bin:$JAVA_HOME/bin:/opt/homebrew/bin:/usr/bin:/bin"

                    python --version
                    python -m pip install -r requirements.txt

                    mkdir -p report
                    rm -f report/junit.xml

                    python main.py --junitxml=report/junit.xml
                '''
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('report/junit.xml')) {
                    junit testResults: 'report/junit.xml'
                }
            }

            emailext(
                mimeType: 'text/html',
                subject: "${env.JOB_NAME} #${env.BUILD_NUMBER}：${currentBuild.currentResult}",
                to: '18600988847@163.com',
                body: '''
                    <html>
                    <body>
                        <h2>自动化测试结果</h2>
                        <p>任务：${PROJECT_NAME}</p>
                        <p>构建：#${BUILD_NUMBER}</p>
                        <p>总数：${TEST_COUNTS,var="total"}</p>
                        <p>通过：${TEST_COUNTS,var="pass"}</p>
                        <p>失败：${TEST_COUNTS,var="fail"}</p>
                        <p>跳过：${TEST_COUNTS,var="skip"}</p>
                        <p><a href="${BUILD_URL}">查看构建详情</a></p>
                    </body>
                    </html>
                '''
            )
        }
    }
}