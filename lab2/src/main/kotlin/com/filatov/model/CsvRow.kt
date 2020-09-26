package com.filatov.model

class CsvRow (type: String, val content: String) {
    val category: MessageCategory = MessageCategory.valueOf(type.toUpperCase())
}
