FROM ghcr.io/hdl/sim/osvb

# ----------------------------------------
# - Install dependencies
# ----------------------------------------

# Harbor adaptation: copy the converted task workspace into /code.
WORKDIR /code
COPY . /code
RUN chmod +x /code/cvdp_harness_env.sh
RUN mkdir -p /code/rundir
RUN [ -e /src ] || ln -s /code/src /src
RUN [ -e /rundir ] || ln -s /code/rundir /rundir
ENV HOME=/code/rundir
RUN printf '. /code/cvdp_harness_env.sh\n' >> /root/.bashrc
