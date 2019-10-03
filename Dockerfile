ARG VERSION=0.8.1

FROM anirishduck/petrify:$VERSION

RUN cd /tmp && mkdir x && cd x \
    && git clone https://github.com/AnIrishDuck/petrify.git \
    && cd petrify && git checkout $VERSION \
    && rm -r ${HOME}/examples && mkdir -p ${HOME}/examples \
    && cp ./examples/*.ipynb ${HOME}/examples \
    && cp ./examples/*.svg ${HOME}/examples \
    && cp ./examples/*.stl ${HOME}/examples
