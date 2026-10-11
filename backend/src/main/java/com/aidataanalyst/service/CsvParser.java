package com.aidataanalyst.service;

import java.util.ArrayList;
import java.util.List;

public final class CsvParser {

    private CsvParser() {
    }

    public static List<List<String>> parseRows(String csv) {
        List<List<String>> rows = new ArrayList<>();
        List<String> row = new ArrayList<>();
        StringBuilder value = new StringBuilder();
        boolean quoted = false;

        for (int index = 0; index < csv.length(); index++) {
            char character = csv.charAt(index);
            if (quoted) {
                if (character == '"' && index + 1 < csv.length() && csv.charAt(index + 1) == '"') {
                    value.append('"');
                    index++;
                } else if (character == '"') {
                    quoted = false;
                } else {
                    value.append(character);
                }
            } else if (character == '"' && value.isEmpty()) {
                quoted = true;
            } else if (character == ',') {
                row.add(value.toString());
                value.setLength(0);
            } else if (character == '\n' || character == '\r') {
                addRow(rows, row, value);
                if (character == '\r' && index + 1 < csv.length() && csv.charAt(index + 1) == '\n') {
                    index++;
                }
            } else {
                value.append(character);
            }
        }

        if (quoted) {
            throw new IllegalArgumentException("CSV contains an unterminated quoted field.");
        }
        if (!row.isEmpty() || !value.isEmpty()) {
            addRow(rows, row, value);
        }
        if (!rows.isEmpty() && !rows.get(0).isEmpty()) {
            rows.get(0).set(0, rows.get(0).get(0).replaceFirst("^\\uFEFF", ""));
        }
        return rows;
    }

    private static void addRow(List<List<String>> rows, List<String> row, StringBuilder value) {
        row.add(value.toString());
        if (!(row.size() == 1 && row.get(0).isBlank())) {
            rows.add(new ArrayList<>(row));
        }
        row.clear();
        value.setLength(0);
    }
}
