FROM bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8

# Fix for Debian Stretch EOL - redirect to archived repositories
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/stretch-updates/d' /etc/apt/sources.list

# Install required tools
RUN apt-get update && apt-get install -y wget nano curl openssh-server && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME (required for Mahout to find the JVM)
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop-3.2.1
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop

# Install Apache Mahout 0.13.0 from locally pre-downloaded tarball (avoids slow network download)
ENV MAHOUT_VERSION=0.13.0
ENV MAHOUT_HOME=/opt/mahout
ENV MAHOUT_LOCAL=false

COPY apache-mahout-distribution-0.13.0.tar.gz /tmp/
RUN tar -xzf /tmp/apache-mahout-distribution-${MAHOUT_VERSION}.tar.gz -C /opt/ && \
    rm /tmp/apache-mahout-distribution-${MAHOUT_VERSION}.tar.gz && \
    mv /opt/apache-mahout-distribution-${MAHOUT_VERSION} $MAHOUT_HOME

# Add Mahout and Hadoop bins to PATH
ENV PATH=$PATH:$MAHOUT_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

WORKDIR /data
