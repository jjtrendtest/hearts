IMG=trend-hearts
TAG=latest
PLAYER=kaija
NUM=1
TOKEN=123
URL=ws://10.1.201.189:8080/

.PHONY: build run

all: build

build:
	docker build -t ${IMG}:${TAG} .

run:
	docker run ${IMG} ${PLAYER} ${NUM} ${TOKEN} ${URL}
