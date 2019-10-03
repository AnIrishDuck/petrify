ENV VERSION 0.7

FROM anirishduck/petrify:$VERSION

RUN git clone https://github.com/AnIrishDuck/petrify.git \
    && git checkout $VERSION \
    && rm -r ${HOME}/examples && mkdir -p ${HOME}/examples \
    && cp ./examples/*.ipynb ${HOME}/examples \
    && cp ./examples/*.svg ${HOME}/examples \
    && cp ./examples/*.stl ${HOME}/examples
