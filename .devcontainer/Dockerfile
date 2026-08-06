FROM rockylinux:8

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG USERNAME=pokerth
ARG USER_UID=1000
ARG USER_GID=${USER_UID}
ARG GCC_TOOLSET=gcc-toolset-14
ARG USE_EMSDK=1

# toolchain + requirements for vcpkg built libraries only.
RUN dnf -y install --enablerepo=devel autoconf-archive libtool && \
    dnf -y install dnf-plugins-core epel-release && \
    dnf config-manager --set-enabled powertools && \
    dnf -y update
RUN dnf -y install \
        libX11-devel \
        libxcb-devel \
        xcb-util-devel \
        xcb-util-image-devel \
        xcb-util-keysyms-devel \
        xcb-util-renderutil-devel \
        xcb-util-wm-devel \
        xcb-util-cursor-devel \
        libxkbcommon-devel \
        libxkbcommon-x11-devel \
        libXext-devel \
        libXrandr-devel \
        libglvnd-glx \
        libglvnd-devel \
        mesa-libGL-devel \
        libSM \
        libICE
RUN dnf -y install \
        "${GCC_TOOLSET}" \
        mold \
        ninja-build \
        nasm \
        git \
        aria2 \
        curl \
        ca-certificates \
        sudo \
        zip \
        unzip \
        tar \
        pkgconf-pkg-config \
        automake \
        bison \
        flex \
        cmake \
        make \
        perl \
        python39 \
        shadow-utils \
        bzip2 \
        xz && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN mkdir -p /bootstrap
COPY autoconf-mirrors.txt /bootstrap/
WORKDIR /bootstrap
RUN aria2c --input-file=autoconf-mirrors.txt --checksum=sha-256=afb181a76e1ee72832f6581c0eddf8df032b83e2e0239ef79ebedc4467d92d6e
RUN tar -xzf autoconf-2.72.tar.gz
WORKDIR /bootstrap/autoconf-2.72
RUN ./configure --prefix=/usr/local && make && make install
WORKDIR /
RUN rm -rf /bootstrap

# Create a non-root user for devcontainer sessions.
RUN groupadd --gid "${USER_GID}" "${USERNAME}" && \
    useradd --uid "${USER_UID}" --gid "${USER_GID}" -m "${USERNAME}"

RUN printf '%s\n' "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${USERNAME}" && \
    chmod 0440 "/etc/sudoers.d/${USERNAME}"

# Install vcpkg
ENV VCPKG_DISABLE_METRICS="1"
ENV VCPKG_ROOT="/opt/vcpkg"
RUN git clone https://github.com/microsoft/vcpkg.git "${VCPKG_ROOT}" && \
    "${VCPKG_ROOT}/bootstrap-vcpkg.sh" -disableMetrics
RUN chown -R "${USERNAME}:${USERNAME}" "${VCPKG_ROOT}"

# Optionally install emscripten ( which requires at least Python 3.10, so we also use micromamba to get it... )
ENV EMSDK="/opt/emsdk"
ENV MAMBA_ROOT_PREFIX="/opt/micromamba"
ENV EMSDK_PYTHON="/opt/micromamba/envs/emsdk-py/bin/python"
RUN if [ "${USE_EMSDK}" = "1" ]; then \
      curl -fsSL https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C /tmp bin/micromamba && \
      install -Dm755 /tmp/bin/micromamba /usr/local/bin/micromamba && \
      rm -rf /tmp/bin && \
      micromamba create -y -n emsdk-py -c conda-forge python=3.11 && \
      micromamba clean --all --yes; \
    fi
RUN if [ "${USE_EMSDK}" = "1" ]; then \
      git clone --depth 1 https://github.com/emscripten-core/emsdk.git "${EMSDK}" && \
      EMSDK_PYTHON="${EMSDK_PYTHON}" "${EMSDK}/emsdk" install latest && \
      EMSDK_PYTHON="${EMSDK_PYTHON}" "${EMSDK}/emsdk" activate latest --embedded; \
    fi
RUN printf '%s\n' \
    "if [ -f /opt/rh/${GCC_TOOLSET}/enable ]; then" \
    "  source /opt/rh/${GCC_TOOLSET}/enable" \
    "fi" \
    "if [ -f ${EMSDK}/emsdk_env.sh ]; then" \
    "  if [ -x ${EMSDK_PYTHON} ]; then" \
    "    export EMSDK_PYTHON=${EMSDK_PYTHON}" \
    "  fi" \
    "  source ${EMSDK}/emsdk_env.sh >/dev/null 2>&1" \
    "  if [ -x ${EMSDK_PYTHON} ]; then" \
    "    export EMSDK_PYTHON=${EMSDK_PYTHON}" \
    "  fi" \
    "fi" \
    > /etc/profile.d/toolchain.sh && \
    chmod 0644 /etc/profile.d/toolchain.sh

# Keep toolchain available even for commands that do not source shell profiles.
ENV PATH="/opt/rh/${GCC_TOOLSET}/root/usr/bin:${PATH}"
ENV BASH_ENV="/etc/profile.d/toolchain.sh"
ENV ENV="/etc/profile.d/toolchain.sh"
ENV CC="gcc"
ENV CXX="g++"

WORKDIR /workspaces/pokerth
