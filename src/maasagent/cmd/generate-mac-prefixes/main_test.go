// Copyright (c) 2025 Canonical Ltd
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
	"bytes"
	"encoding/csv"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestParseEntries(t *testing.T) {
	testcases := map[string]struct {
		in  *bytes.Buffer
		out []macEntry
		err error
	}{
		"empty file": {
			in:  &bytes.Buffer{},
			out: []macEntry{}, // explicitly not nil
		},
		"one entry": {
			in: bytes.NewBufferString(strings.ReplaceAll(strings.TrimSpace(`
			Registry,Assignment,Organization Name,Organization Address
			MA-L,112233,company,company address
			`), "\t", "")),
			out: []macEntry{
				{
					Registry:     "MA-L",
					Assignment:   "112233",
					Organization: "company",
					Address:      "company address",
				},
			},
		},
		"multiple entries": {
			in: bytes.NewBufferString(strings.ReplaceAll(strings.TrimSpace(`
			Registry,Assignment,Organization Name,Organization Address
			MA-L,112233,company,company address
			MA-M,741AE09,Private,
			`), "\t", "")),
			out: []macEntry{
				{
					Registry:     "MA-L",
					Assignment:   "112233",
					Organization: "company",
					Address:      "company address",
				},
				{
					Registry:     "MA-M",
					Assignment:   "741AE09",
					Organization: "Private",
				},
			},
		},
		"malformed": {
			in:  bytes.NewBufferString("{\"this_is_not_a_csv\": \"\"}"),
			err: &csv.ParseError{},
		},
	}

	for tname, tc := range testcases {
		t.Run(tname, func(t *testing.T) {
			out, err := parseEntries(tc.in)
			if err != nil {
				if tc.err != nil {
					assert.IsType(t, tc.err, err)
					return
				}

				t.Fatal(err)
			}

			assert.Equal(t, out, tc.out)
		})
	}
}
