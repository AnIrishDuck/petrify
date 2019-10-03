FROM anirishduck/petrify:0.7
RUN mkdir -p ${HOME}/examples \
    && cp examples/*.ipynb ${HOME}/examples \
    && cp examples/*.svg ${HOME}/examples \
    && cp examples/*.stl ${HOME}/examples
