# Installs Jupyter Notebook and IPython kernel from the current branch
# Another Docker container should inherit with `FROM jupyter/notebook`
# to run actual services.
#
# For opinionated stacks of ready-to-run Jupyter applications in Docker,
# check out docker-stacks <https://github.com/jupyter/docker-stacks>

FROM vsiri/voxel_globe:common
#based off of Debian:jessie instead of Ubuntu

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends locales && \
    echo "en_US UTF-8" > /etc/locale.gen && \
    DEBIAN_FRONTEND=noninteractive locale-gen && \
    DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales && \
    rm -rf /var/lib/apt/lists/*

# Not essential, but wise to set the lang
# Note: Users with other languages should set this in their derivative image
ENV LANGUAGE=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONIOENCODING=UTF-8

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential ca-certificates curl libcurl4-openssl-dev libffi-dev \
        libsqlite3-dev libzmq3-dev pandoc python3 python-dev \
        python3-dev sqlite3 texlive-fonts-recommended texlive-latex-base \
        texlive-latex-extra zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Install the recent pip release
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libssl-dev && \
    curl -O https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py && \
    pip2 --no-cache-dir install requests[security] && \
    pip3 --no-cache-dir install requests[security] && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        libssl-dev && \
    rm -rf /var/lib/apt/lists/* /root/.cache

# Install some dependencies.
RUN pip2 --no-cache-dir install ipykernel && \
    pip3 --no-cache-dir install ipykernel && \
    python2 -m ipykernel.kernelspec && \
    python3 -m ipykernel.kernelspec && \
    rm -rf /root/.cache

# Install dependencies and run tests.
RUN BUILD_DEPS="nodejs-legacy npm" && \
    apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq $BUILD_DEPS && \
    pip3 install notebook==4.2.0 && \
    pip3 install ipywidgets && \
    npm cache clean && \
    apt-get clean && \
    rm -rf /root/.npm && \
    rm -rf /root/.cache && \
    rm -rf /root/.config && \
    rm -rf /root/.local && \
    rm -rf /root/tmp && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get purge -y --auto-remove \
        -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false $BUILD_DEPS

# Run tests.
RUN pip3 install --no-cache-dir notebook[test] && nosetests notebook

VOLUME /notebooks
WORKDIR /notebooks

EXPOSE 8888

ENV JUPYTER_CONFIG_DIR=/profile
RUN mkdir -p ${JUPYTER_CONFIG_DIR}/custom && \
    echo "c.MultiKernelManager.default_kernel_name = 'python2'" > ${JUPYTER_CONFIG_DIR}/jupyter_notebook_config.py && \
    echo "c.NotebookApp.ip = '*'" >> ${JUPYTER_CONFIG_DIR}/jupyter_notebook_config.py && \
    JUPYTER_DATA_DIR=/usr/local/share/jupyter pip2 install https://github.com/ipython-contrib/IPython-notebook-extensions/archive/f7ad9bd853e685ecb096053a5571ecf0e6fbe95a.zip && \
    rm -r /root/.cache

ENV USER_ID=1 GROUP_ID=1 \
    PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl

CMD groupadd user -g ${GROUP_ID} -o && \
    useradd -u ${USER_ID} -o --create-home --home-dir /home/user -g user user && \
    chown user:user ${JUPYTER_CONFIG_DIR} ${JUPYTER_CONFIG_DIR}/*.* && \
    gosu user bash -c "/opt/vip/wrap.bat jupyter notebook --no-browser --ip='*'"