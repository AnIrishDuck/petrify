FROM python:3.6
WORKDIR /root/

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    cmake \
    libgmp-dev \
    libmpfr-dev \
    libgmpxx4ldbl \
    libboost-dev \
    libcgal-dev \
    libboost-thread-dev \
    swig && \
    apt-get clean
RUN pip install numpy
RUN pip install pymesh2
RUN pip install --no-cache notebook pythreejs

RUN cd /tmp \
  && git clone https://github.com/AnIrishDuck/petrify.git \
  && cd petrify \
  && pip install -r requirements.txt \
  && python setup.py install

# ARG NB_USER=notebook
# ARG NB_UID=1000
# ENV USER ${NB_USER}
# ENV HOME /home/${NB_USER}

# RUN adduser --disabled-password \
#     --gecos "Default user" \
#     --uid ${NB_UID} \
#     ${NB_USER}
# WORKDIR ${HOME}
# USER ${NB_USER}
