# Build Server Base
FROM cm2network/steamcmd:root AS steamcmd-pz-server-base

ENV STEAMAPPID 380870
ENV STEAMAPP pz
ENV STEAMAPPDIR "${HOMEDIR}/${STEAMAPP}-dedicated"
ENV SERVERDIR "/server"
ENV SERVERSCRIPTSDIR "${SERVERDIR}/scripts"
# ENV STEAMAPPVALIDATE 0

# Update packages, install packages, clean cache, prepare folders
RUN apt-get update && \
	apt-get install -y --no-install-recommends --no-install-suggests wget ca-certificates lib32z1 simpleproxy libicu-dev unzip jq  dos2unix && \
	apt-get clean && \
	find /var/lib/apt/lists/ -type f -delete && \
	mkdir -p "${STEAMAPPDIR}" && \
	mkdir -p "${SERVERSCRIPTSDIR}" && \
	chmod -R 775 "${STEAMAPPDIR}" "${SERVERDIR}" && \
	chown -R "${USER}:${USER}" "${STEAMAPPDIR}" "${SERVERDIR}"

# Install python dependencies for modcheck
RUN apt-get update && \
	apt-get install -y python3 python3.pip && \
	apt-get clean && \
	find /var/lib/apt/lists/ -type f -delete && \
	python3 -m pip install --no-cache-dir requests psutil zomboid-rcon

# Switch to user
USER ${USER}

RUN mkdir -p "${HOMEDIR}/Zomboid" && \
	bash "${STEAMCMDDIR}/steamcmd.sh" +force_install_dir "${STEAMAPPDIR}" +login anonymous +app_update "${STEAMAPPID}" validate +quit



# Build Server Runner
FROM steamcmd-pz-server-base AS steamcmd-pz-server

# Copy scripts
COPY --chown=${USER}:${USER} scripts/entry.sh "${SERVERSCRIPTSDIR}/entry.sh"
COPY --chown=${USER}:${USER} scripts/search_folder.sh "${SERVERSCRIPTSDIR}/search_folder.sh"
COPY --chown=${USER}:${USER} scripts/search_folder.sh "${SERVERSCRIPTSDIR}/modchecker.sh"

# Prepare scripts permissions
RUN chmod 550 "${SERVERSCRIPTSDIR}/entry.sh" && \
	chmod 550 "${SERVERSCRIPTSDIR}/search_folder.sh" && \
	chmod 550 "${SERVERSCRIPTSDIR}/modchecker.py"

WORKDIR ${HOMEDIR}

# Expose ports
EXPOSE 16261-16262/udp 27015/tcp

CMD ["bash", "/server/scripts/entry.sh"]
