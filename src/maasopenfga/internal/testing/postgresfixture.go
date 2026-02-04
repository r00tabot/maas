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

// Inspired by https://salsa.debian.org/python-team/packages/postgresfixture/-/blob/debian/master/postgresfixture/cluster.py
package postgresfixture

import (
	"bytes"
	"database/sql"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"

	_ "github.com/lib/pq"
)

const PGBase = "/usr/lib/postgresql"

var (
	LatestPGVersionPath string
)

// Find the latest installed PostgreSQL version
func init() {
	var latestPGVersion int = -1

	entries, err := os.ReadDir(PGBase)
	if err != nil {
		return
	}

	for _, e := range entries {
		if !e.IsDir() {
			continue
		}
		pgCtl := filepath.Join(PGBase, e.Name(), "bin", "pg_ctl")
		if _, err := os.Stat(pgCtl); err == nil {
			version, err := strconv.Atoi(e.Name())
			if err != nil || version > latestPGVersion {
				latestPGVersion = version
				LatestPGVersionPath = filepath.Join(PGBase, e.Name(), "bin")
			}
		}
	}

	if latestPGVersion == -1 {
		panic("No PostgreSQL installation found")
	}
}

type Cluster struct {
	DataDir string
}

func NewCluster(datadir string) *Cluster {
	abs, _ := filepath.Abs(datadir)
	return &Cluster{
		DataDir: abs,
	}
}

func (c *Cluster) execute(cmd []string, stdout, stderr io.Writer) error {

	var newEnv []string

	newEnv = append(newEnv,
		"PGDATA="+c.DataDir,
		"PGHOST="+c.DataDir,
	)

	cmd[0] = filepath.Join(LatestPGVersionPath, cmd[0])

	command := exec.Command(cmd[0], cmd[1:]...)
	command.Env = newEnv
	command.Stdout = stdout
	command.Stderr = stderr

	return command.Run()
}

func (c *Cluster) Exists() bool {
	_, err := os.Stat(filepath.Join(c.DataDir, "PG_VERSION"))
	return err == nil
}

func (c *Cluster) LogFile() string {
	return filepath.Join(c.DataDir, "db.log")
}

func (c *Cluster) Running() bool {
	var stderr bytes.Buffer

	err := c.execute(
		[]string{"pg_ctl", "status"},
		io.Discard,
		&stderr,
	)

	if err == nil {
		return true
	}

	exitErr, ok := err.(*exec.ExitError)
	if !ok {
		panic(err)
	}

	code := exitErr.ExitCode()

	if code == 3 {
		return false
	}
	if code == 4 && !c.Exists() {
		return false
	}

	panic(err)
}

func (c *Cluster) Create() error {
	if c.Exists() {
		return nil
	}

	if err := os.MkdirAll(c.DataDir, 0755); err != nil {
		return err
	}

	return c.execute(
		[]string{"pg_ctl", "init", "-s", "-o", "-E utf8 -A trust"},
		io.Discard,
		io.Discard,
	)
}

func (c *Cluster) Start() error {
	if c.Running() {
		return nil
	}

	if err := c.Create(); err != nil {
		return err
	}

	opts := fmt.Sprintf("-h '' -F -k %s", c.DataDir)
	return c.execute(
		[]string{
			"pg_ctl", "start",
			"-l", c.LogFile(),
			"-s", "-w",
			"-o", opts,
		},
		io.Discard,
		io.Discard,
	)
}

func (c *Cluster) Stop() error {
	if !c.Running() {
		return nil
	}

	return c.execute(
		[]string{"pg_ctl", "stop", "-s", "-w", "-m", "fast"},
		io.Discard,
		io.Discard,
	)
}

func (c *Cluster) Destroy() error {
	if !c.Exists() {
		return nil
	}

	_ = c.Stop()
	return os.RemoveAll(c.DataDir)
}

func (c *Cluster) Connect(database string) (*sql.DB, error) {
	dsn := fmt.Sprintf(
		"host=%s dbname=%s sslmode=disable",
		c.DataDir,
		database,
	)

	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, err
	}

	return db, nil
}

func (c *Cluster) CreateDB(name string) error {
	db, err := c.Connect("template1")
	if err != nil {
		return err
	}
	defer db.Close()

	_, err = db.Exec("CREATE DATABASE " + name)
	return err
}
