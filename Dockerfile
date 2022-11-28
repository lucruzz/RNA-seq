FROM centos:latest

# specify python version 
ENV PYTHON_VERSION=3.12.0
WORKDIR /rna-seq
COPY teste.py /rna-seq/teste.py

# https://stackoverflow.com/questions/70963985/error-failed-to-download-metadata-for-repo-appstream-cannot-prepare-internal
RUN cd /etc/yum.repos.d/
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*


RUN yum -y update

# https://stackoverflow.com/questions/62554991/how-do-i-install-python-on-alpine-linux
# Setup the environment
RUN yum install gcc openssl-devel bzip2-devel libffi-devel -y

# install wget
RUN yum -y install wget

# intall tar
RUN yum -y install tar

# install make
RUN yum -y install make

# download and extract python sources
RUN cd /opt \
	&& mkdir -p python \
	&& cd python \
	&& wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}a2.tgz \
	&& tar -xzf Python-${PYTHON_VERSION}a2.tgz \
	&& rm Python-${PYTHON_VERSION}a2.tgz \
	&& mv Python-${PYTHON_VERSION}a2 ${PYTHON_VERSION}a2

# build python
RUN cd /opt/python/${PYTHON_VERSION}a2 \
    && ./configure --enable-optimizations \
    && make altinstall


RUN python3 --version
# install htseq
# RUN python3 -m pip install HTSeq

# install parsl
# RUN python3 -m pip install parsl

# install bowtie
#RUN yum install bowtie2-2.3.5-linux-x86_64

# install R
RUN yum install epel-release R

CMD ["echo 'oi'"]
