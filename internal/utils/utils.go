package utils

func Sum(amounts []int) int {
	var totalAmount int
	for i := range amounts {
		totalAmount += amounts[i]
	}
	return totalAmount
}
