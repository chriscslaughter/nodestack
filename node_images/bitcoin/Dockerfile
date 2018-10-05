FROM debian:stable-slim

RUN useradd -r bitcoin

RUN apt-get update -y \
  && apt-get install -y wget curl \
  && apt-get clean 

RUN wget https://bitcoin.org/bin/bitcoin-core-0.17.0/bitcoin-0.17.0-x86_64-linux-gnu.tar.gz \
  && tar --strip=2 -xzf *.tar.gz -C /usr/local/bin \
  && rm *.tar.gz

USER bitcoin

VOLUME ["/home/bitcoin/.bitcoin"]

COPY --chown=bitcoin ./bitcoin.conf /home/bitcoin/.bitcoin/

EXPOSE 8332

CMD ["bitcoind", "--conf=/home/bitcoin/.bitcoin/bitcoin.conf"]
