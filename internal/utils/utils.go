package utils

import (
	"crypto/rand"
	"encoding/base64"
)

func Sum(amounts []int) int {
	var totalAmount int
	for i := range amounts {
		totalAmount += amounts[i]
	}
	return totalAmount
}

// Create session state string
func GenerateRandomstring() (string, error) {
	b := make([]byte, 32)
	_, err := rand.Read(b)
	if err != nil {
		return "", err
	}

	return base64.StdEncoding.EncodeToString(b), nil
}
