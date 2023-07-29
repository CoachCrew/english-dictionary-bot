#!/bin/sh

# ============================================================================= #
# Version  v1.1.0                                                               #
# Date     2023.06.08                                                           #
# CoachCrew.tech                                                                #
# admin@CoachCrew.tech                                                          #
# ============================================================================= #

# Add a new non-root user
groupadd --gid ${USER_GID} ${USERNAME}
useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME}
echo ${USERNAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USERNAME}
chmod 0440 /etc/sudoers.d/${USERNAME}

# setup proxy settings
echo "source /opt/python/.venv/bin/activate" >> /home/${USERNAME}/.bashrc

# Change ownership and group of files in home and app directory of user
chown -R ${USERNAME} /home/${USERNAME} 2>&1 > /dev/null
chgrp -R ${USERNAME} /home/${USERNAME} 2>&1 > /dev/null

cd ${WORK_DIR}
sudo -u ${USERNAME} /bin/bash
