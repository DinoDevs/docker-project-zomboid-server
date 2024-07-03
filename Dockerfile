# BUILD STAGE

FROM cm2network/steamcmd:root as build_stage

ENV STEAMAPPID 380870
ENV STEAMAPP pz
ENV STEAMAPPDIR "${HOMEDIR}/${STEAMAPP}-dedicated"
# ENV STEAMAPPVALIDATE 0

COPY scripts/entry.sh "${HOMEDIR}/entry.sh"
COPY scripts/search_folder.sh "${HOMEDIR}/search_folder.sh"

RUN set -x \
	# Install, update & upgrade packages
	&& apt-get update \
	&& apt-get install -y --no-install-recommends --no-install-suggests \
		            wget \
		            ca-certificates \
		            lib32z1 \
                simpleproxy \
                libicu-dev \
                unzip \
		            jq \
                dos2unix \
	&& mkdir -p "${STEAMAPPDIR}" \
	# Add entry script
	&& chmod +x "${HOMEDIR}/entry.sh" \
	&& chmod +x "${HOMEDIR}/search_folder.sh" \
	&& chown -R "${USER}:${USER}" "${HOMEDIR}/entry.sh" "${STEAMAPPDIR}" \
	&& chown -R "${USER}:${USER}" "${HOMEDIR}/search_folder.sh" "${STEAMAPPDIR}" \
	# Clean up
        && apt-get clean \
        && find /var/lib/apt/lists/ -type f -delete

# BASE

FROM build_stage AS bullseye-base

# Set permissions on STEAMAPPDIR
#   Permissions may need to be reset if persistent volume mounted
RUN set -x \
        && chown -R "${USER}:${USER}" "${STEAMAPPDIR}" \
        && chmod 0777 "${STEAMAPPDIR}" \
        && bash "${STEAMCMDDIR}/steamcmd.sh" +force_install_dir "${STEAMAPPDIR}" \
        +login anonymous \
        +app_update "${STEAMAPPID}" validate \
        +quit

# Switch to user
USER ${USER}

RUN mkdir -p "${HOMEDIR}/Zomboid"

WORKDIR ${HOMEDIR}

CMD ["bash", "entry.sh"]

# Expose ports
EXPOSE 16261-16262/udp \
       27015/tcp
