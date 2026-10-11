package com.aidataanalyst.service;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class CsvParserTest {

    @Test
    void parsesQuotedCommasEscapedQuotesAndMultilineFields() {
        String csv = "name,description\r\n"
                + "\"North, Region\",\"She said \"\"hello\"\"\"\r\n"
                + "Multi,\"first line\nsecond line\"\r\n";

        assertEquals(List.of(
                List.of("name", "description"),
                List.of("North, Region", "She said \"hello\""),
                List.of("Multi", "first line\nsecond line")
        ), CsvParser.parseRows(csv));
    }

    @Test
    void rejectsAnUnterminatedQuotedField() {
        assertThrows(IllegalArgumentException.class, () -> CsvParser.parseRows("name,value\nitem,\"unfinished"));
    }
}
