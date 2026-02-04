// Copyright (c) 2026 Canonical Ltd
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"syscall"

	"github.com/grpc-ecosystem/grpc-gateway/v2/runtime"
	openfgav1 "github.com/openfga/api/proto/openfga/v1"
	"github.com/openfga/openfga/pkg/logger"
	openfgaServer "github.com/openfga/openfga/pkg/server"
	"github.com/openfga/openfga/pkg/storage/postgres"
	"github.com/openfga/openfga/pkg/storage/sqlcommon"
	"gopkg.in/yaml.v3"
)

const (
	maxOpenConns = 3
	maxIdleConns = 1
)

type regionConfig struct {
	DatabaseHost string `yaml:"database_host"`
	DatabaseName string `yaml:"database_name"`
	DatabasePass string `yaml:"database_pass"`
	DatabaseUser string `yaml:"database_user"`
}

func readRegionConfig() *regionConfig {
	configDir := os.Getenv("SNAP_DATA")
	if configDir == "" {
		// Deb installation
		configDir = "/etc/maas"
	}

	configPath := configDir + "/regiond.conf"
	fmt.Println(configPath)
	cfg, err := os.ReadFile(configPath)
	if err != nil {
		log.Fatalf("failed to read region config file: %v", err)
	}

	var regionCfg regionConfig
	err = yaml.Unmarshal(cfg, &regionCfg)
	if err != nil {
		log.Fatalf("failed to parse region config file: %v", err)
	}

	return &regionCfg
}

func getPostgresDSN(cfg *regionConfig) string {
	socketPath := url.QueryEscape(cfg.DatabaseHost)

	return fmt.Sprintf(
		"postgres://%s:%s@/%s?host=%s&search_path=openfga",
		cfg.DatabaseUser,
		cfg.DatabasePass,
		cfg.DatabaseName,
		socketPath,
	)
}

func main() {
	socketPath := os.Getenv("MAAS_OPENFGA_HTTP_SOCKET_PATH")

	if socketPath == "" {
		// Deb installation
		socketPath = "/var/lib/maas/openfga-http.sock"
	}

	_ = os.Remove(socketPath)

	lis, err := net.Listen("unix", socketPath)
	if err != nil {
		log.Fatal(err)
	}

	psqlDataStore, err := postgres.New(
		getPostgresDSN(readRegionConfig()),
		sqlcommon.NewConfig(
			// We might want to tune these values later. For now, keep them low
			sqlcommon.WithMaxOpenConns(maxOpenConns),
			sqlcommon.WithMaxOpenConns(maxIdleConns),
		),
	)
	if err != nil {
		log.Fatalf("failed to create postgres datastore: %v", err)
	}

	openfgaLogger, err := logger.NewLogger(logger.WithFormat("json"))
	if err != nil {
		panic(err)
	}

	opts := []openfgaServer.OpenFGAServiceV1Option{
		// TODO: investigate if we need to set some specific options
		openfgaServer.WithDatastore(psqlDataStore),
		openfgaServer.WithLogger(openfgaLogger),
	}

	fgaSvc, err := openfgaServer.NewServerWithOpts(opts...)
	if err != nil {
		log.Fatal(err)
	}

	ctx := context.Background()
	mux := runtime.NewServeMux()

	if err := openfgav1.RegisterOpenFGAServiceHandlerServer(
		ctx,
		mux,
		fgaSvc,
	); err != nil {
		log.Fatal(err)
	}

	httpServer := &http.Server{
		Handler: mux,
	}

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-sig
		log.Println("shutting down")
		httpServer.Close()
		_ = os.Remove(socketPath)
	}()

	log.Printf("OpenFGA HTTP listening on unix://%s", socketPath)
	if err := httpServer.Serve(lis); err != nil && err != http.ErrServerClosed {
		log.Fatal(err)
	}
}
