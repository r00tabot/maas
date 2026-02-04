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

package postgresfixture

import (
	"context"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
	"time"
)

// Run a command and wait for it to finish
func runCmd(t *testing.T, bin string, args ...string) *exec.Cmd {
	t.Helper()

	cmd := exec.Command(bin, args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		t.Fatalf("failed to run: %v", err)
	}

	return cmd
}

// Fire and forget command
func startCmd(t *testing.T, bin string, args ...string) *exec.Cmd {
	t.Helper()

	cmd := exec.Command(bin, args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Start(); err != nil {
		t.Fatalf("failed to start: %v", err)
	}

	t.Cleanup(func() {
		_ = cmd.Process.Kill()
		_ = cmd.Wait()
	})

	return cmd
}

func waitForSocket(t *testing.T, path string) {
	t.Helper()

	deadline := time.Now().Add(10 * time.Second)
	for time.Now().Before(deadline) {
		if _, err := os.Stat(path); err == nil {
			return
		}
		time.Sleep(50 * time.Millisecond)
	}
	t.Fatalf("socket %s did not appear", path)
}

// Start a postgres cluster, run migrations, start maas-openfga and perform a simple HTTP request to ensure that the service is running and serving the model.
func TestOpenFGA_E2E(t *testing.T) {
	tmp := t.TempDir()

	// Prepare the database
	pgData := filepath.Join(tmp, "db")
	cluster := NewCluster(pgData)
	if err := cluster.Start(); err != nil {
		t.Fatalf("start postgres: %v", err)
	}
	t.Cleanup(func() { _ = cluster.Destroy() })

	if err := cluster.CreateDB("maas"); err != nil {
		t.Fatalf("create db: %v", err)
	}

	db, err := cluster.Connect("maas")
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	defer db.Close()

	_, err = db.Exec("CREATE SCHEMA IF NOT EXISTS openfga;")
	if err != nil {
		t.Fatalf("create schema: %v", err)
	}

	cfg := `
database_host: ` + pgData + `
database_name: maas
database_user: ubuntu
`
	if err := os.WriteFile(filepath.Join(tmp, "regiond.conf"), []byte(cfg), 0644); err != nil {
		t.Fatal(err)
	}

	// Run migrators and start maas-openfga
	binariesPath := os.Getenv("OPENFGA_BINARIES_PATH")
	runCmd(t, binariesPath+"/maas-openfga-migrator", "postgres://ubuntu@localhost/maas?host="+pgData+"&search_path=openfga")
	runCmd(t, binariesPath+"/maas-openfga-app-migrator", "postgres://ubuntu@localhost/maas?host="+pgData+"&search_path=openfga")

	os.Setenv("SNAP_DATA", tmp)

	socketPath := filepath.Join(tmp, "openfga.sock")
	os.Setenv("MAAS_OPENFGA_HTTP_SOCKET_PATH", socketPath)

	_, cancel := context.WithCancel(context.Background())
	t.Cleanup(cancel)

	go func() {
		startCmd(t, binariesPath+"/maas-openfga")
	}()

	waitForSocket(t, socketPath)

	httpClient := &http.Client{
		Transport: &http.Transport{
			DialContext: func(_ context.Context, _, _ string) (net.Conn, error) {
				return net.Dial("unix", socketPath)
			},
		},
	}

	resp, err := httpClient.Get("http://unix/stores/00000000000000000000000000")
	if err != nil {
		t.Fatalf("http request failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("unexpected status: %s", resp.Status)
	}
}
