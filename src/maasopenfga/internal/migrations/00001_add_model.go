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

package migrations

import (
	"context"
	"database/sql"
	"fmt"

	sq "github.com/Masterminds/squirrel"
	parser "github.com/openfga/language/pkg/go/transformer"
	"github.com/pressly/goose/v3"
	"google.golang.org/protobuf/proto"
)

const (
	storeID = "00000000000000000000000000"
)

func init() {
	goose.AddMigrationContext(Up00001, Down00001)
}

func createStore(ctx context.Context, tx *sql.Tx) error {
	stmt, args, err := sq.StatementBuilder.PlaceholderFormat(sq.Dollar).
		Insert("openfga.store").
		Columns("id", "name", "created_at", "updated_at").
		Values(storeID, "MAAS", sq.Expr("NOW()"), sq.Expr("NOW()")).
		Suffix("returning id, name, created_at, updated_at").ToSql()

	if err != nil {
		return err
	}

	_, err = tx.ExecContext(
		ctx,
		stmt,
		args...,
	)
	return err
}

func createAuthorizationModel(ctx context.Context, tx *sql.Tx) error {
	modelDSL := `
model
  schema 1.1

type user

type group
  relations
    define member: [user]

type system
  relations
    define admin: [user, group#member]
    define pools.create: admin

type pool
  relations
    define system: [system]
    define user: [user, group#member]
    define auditor: [user, group#member]
    define operator: [user, group#member]
    define pool.delete: admin from system
    define pool.edit: admin from system
    define pool.machines.add: admin from system
    define pool.machines.remove: admin from system
    define pool.machines.view: auditor or user or operator or admin from system
    define pool.machines.deploy: user or operator
    define pool.machines.manage: operator
`

	model, err := parser.TransformDSLToProto(modelDSL)

	if err != nil {
		return err
	}

	// The ID in the protobuf and in the database must be set and match, otherwise openfga will not work properly with this model.
	model.Id = storeID

	pbdata, err := proto.Marshal(model)
	if err != nil {
		return err
	}

	stmt, args, err := sq.StatementBuilder.PlaceholderFormat(sq.Dollar).
		Insert("openfga.authorization_model").
		Columns("store", "authorization_model_id", "schema_version", "type", "type_definition", "serialized_protobuf").
		Values(storeID, model.GetId(), model.GetSchemaVersion(), "", nil, pbdata).
		ToSql()

	if err != nil {
		return err
	}

	_, err = tx.ExecContext(
		ctx,
		stmt,
		args...,
	)
	return err
}

func Up00001(ctx context.Context, tx *sql.Tx) error {
	if err := createStore(ctx, tx); err != nil {
		return fmt.Errorf("failed to create store: %w", err)
	}

	if err := createAuthorizationModel(ctx, tx); err != nil {
		return fmt.Errorf("failed to create authorization model: %w", err)
	}

	return nil
}

func Down00001(ctx context.Context, tx *sql.Tx) error {
	return fmt.Errorf("Downgrade not supported")
}
