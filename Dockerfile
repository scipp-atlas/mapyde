ARG BUILDER_IMAGE=matthewfeickert/madgraph5-amc-nlo:mg5_amc2.7.0-python3
FROM ${BUILDER_IMAGE} as builder

USER root
WORKDIR /usr/local

SHELL [ "/bin/bash", "-c" ]

RUN apt-get -qq -y update && \
    apt-get -qq -y install \
      less && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

RUN echo "install pythia8" | mg5_aMC && \
    echo "install mg5amc_py8_interface" | mg5_aMC 


ENTRYPOINT ["/bin/bash", "-l", "-c"]
CMD ["/bin/bash"]
