# ============================================================================= #
# Version  v1.1.1                                                               #
# Date     2023.06.08                                                           #
# CoachCrew.tech                                                                #
# admin@CoachCrew.tech                                                          #
# ============================================================================= #

# ============================================================================= #
# TARGET: develop
# ============================================================================= #
FROM ubuntu:22.04 as develop

ARG DOCKER_ENTRYPOINT

# Install build essentials ---------------------------------------------------- #
RUN apt-get update                             && \
    apt-get install -y --no-install-recommends    \
        build-essential                           \
        curl                                      \
        gnupg                                     \
        python3                                   \
        python3-pip                               \
        python3-venv                              \
        sudo                                   && \
    apt-get clean all                          && \
    rm -rf /var/lib/apt/lists/*

# Install OpenAI -------------------------------------------------------------- #
WORKDIR /opt/python
RUN python3 -m venv .venv                               && \
    /bin/bash -c                                           \
    "source .venv/bin/activate;                            \
    python3 -m pip install --no-cache-dir openai;"

# Install Telegram-bot -------------------------------------------------------- #
WORKDIR /opt/python
RUN python3 -m venv .venv                               && \
    /bin/bash -c                                           \
    "source .venv/bin/activate;                            \
    python3 -m pip install --no-cache-dir python-telegram-bot;"

# Install Google Cloud Text to speech api ------------------------------------- #
WORKDIR /opt/python
RUN python3 -m venv .venv                               && \
    /bin/bash -c                                           \
    "source .venv/bin/activate;                            \
    python3 -m pip install --no-cache-dir ipython google-cloud-texttospeech;"

# Install mysql python -------------------------------------------------------- #
WORKDIR /opt/telegram-bot
RUN python3 -m venv .venv                               && \
    /bin/bash -c                                           \
    "source .venv/bin/activate;                            \
    python3 -m pip install --no-cache-dir mysql-connector-python;"

# Install gcloud -------------------------------------------------------------- #
WORKDIR /opt/gcloud
RUN curl -LO https://dl.google.com/dl/cloudsdk/\
release/google-cloud-sdk.tar.gz                       && \
    tar -xvf google-cloud-sdk.tar.gz                  && \
    ./google-cloud-sdk/install.sh --quiet

COPY ${DOCKER_ENTRYPOINT} /root/
RUN chmod +x /root/develop-entrypoint.sh

ENTRYPOINT ["/root/develop-entrypoint.sh"]
