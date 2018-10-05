FROM debian:stable-slim

RUN useradd -r litecoin

RUN apt-get update -y \
  && apt-get install -y wget curl \
  && apt-get clean 

RUN wget https://download.litecoin.org/litecoin-0.16.3/linux/litecoin-0.16.3-x86_64-linux-gnu.tar.gz \
  && tar --strip=2 -xzf *.tar.gz -C /usr/local/bin \
  && rm *.tar.gz

USER litecoin

VOLUME ["/home/litecoin/.litecoin"]

COPY --chown=litecoin ./../../config/litecoin.conf /home/litecoin/.litecoin/

CMD ["litecoind", "--conf=/home/litecoin/.litecoin/litecoin.conf"]