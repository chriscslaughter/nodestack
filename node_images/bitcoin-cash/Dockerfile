FROM debian:stable-slim

RUN useradd -r bitcoin

RUN apt-get update -y \
  && apt-get install -y wget curl \
  && apt-get clean 

RUN wget https://download.bitcoinabc.org/0.18.2/linux/bitcoin-abc-0.18.2-linux.tar.gz \
  && tar --strip=2 -xzf *.tar.gz -C /usr/local/bin \
  && rm *.tar.gz

USER bitcoin

VOLUME ["/home/bitcoin/.bitcoin"]

COPY --chown=bitcoin ./bitcoin-cash.conf /home/bitcoin/.bitcoin/

EXPOSE 8332

CMD ["bitcoind", "--conf=/home/bitcoin/.bitcoin/bitcoin.conf"]
