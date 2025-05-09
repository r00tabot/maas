SHELL := /bin/bash

BIN_DIR := bin
BUILD_DIR := build

# override to use alternative Go binary
GO := go
VENDOR_DIR := vendor

LDFLAGS := -ldflags '-linkmode=external -extldflags "-fPIC -static -luv -llz4 -ldqlite"'

# Explicitly set cache dirs to avoid situations where we can't mkdir under $HOME (e.g. Launchpad builds)
export GOCACHE := $(shell [ -d $(HOME)/.cache ] && echo $(HOME)/.cache/go-cache || mktemp --tmpdir -d tmp.go-cacheXXX)
export GOMODCACHE := $(shell [ -d $(HOME)/go ] && echo $(HOME)/go/pkg/mod || mktemp --tmpdir -d tmp.go-mod-cacheXXX)
export GOFLAGS := -mod=vendor

default: build

$(BIN_DIR): ; mkdir -p $@

ARTIFACTS := $(subst /,,$(subst cmd/,,$(wildcard cmd/*/)))

.PHONY: build
build: vendor
	$(MAKE) $(addprefix $(BUILD_DIR)/,$(ARTIFACTS))

$(BUILD_DIR)/%:
	CGO_ENABLED=1 $(GO) build -o $(BUILD_DIR)/$* $(LDFLAGS) cmd/$*/*.go

.PHONY: install
install: build
	install -t $(DESTDIR)/bin -D $(BUILD_DIR)/*

.PHONY: test
test: vendor
	CGO_ENABLED=1 $(GO) test ./...

.PHONY: test-race
test-race: vendor
	CGO_ENABLED=1 $(GO) test -race ./...

.PHONY: test-cover
test-cover: vendor
	CGO_ENABLED=1 $(GO) test -coverprofile=cover.out ./...

.PHONY: generate
generate:
	$(GO) generate ./...

.PHONY: vendor
vendor: $(VENDOR_DIR)/modules.txt

$(VENDOR_DIR)/modules.txt: go.mod
	$(GO) mod vendor

.PHONY: clean
clean:
	rm -rf $(VENDOR_DIR) $(BIN_DIR) $(BUILD_DIR)

format:
	@go fmt maas.io/core/src/maasagent/...
.PHONY: format
