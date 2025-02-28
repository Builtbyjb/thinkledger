package gemini

import (
	"strings"
)

// Sanitize AI Response
func CleanString(jsonString string) string {
	// Remove the backticks
	cleanedString := strings.TrimPrefix(jsonString, "\"```json\\n")
	cleanedString = strings.TrimSuffix(cleanedString, "\\n```\\n\"")
	cleanedString = strings.TrimSuffix(cleanedString, "```\"")

	// Remove JSON formatting indicators
	cleanedString = strings.ReplaceAll(cleanedString, "\\n", "\n")
	cleanedString = strings.ReplaceAll(cleanedString, "\\t", "\t")
	cleanedString = strings.ReplaceAll(cleanedString, "\\\"", "\"")
	cleanedString = strings.ReplaceAll(cleanedString, "\\", "")

	// fmt.Println(cleanedString)

	return cleanedString
}
