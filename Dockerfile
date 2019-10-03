FROM anirishduck/petrify:0.7
RUN rm -r ${HOME}/examples && mkdir -p ${HOME}/examples \
    && cp ./examples/*.ipynb ${HOME}/examples \
    && cp ./examples/*.svg ${HOME}/examples \
    && cp ./examples/*.stl ${HOME}/examples
