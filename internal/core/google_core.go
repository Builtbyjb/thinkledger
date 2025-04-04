package core

import (
	"fmt"
	"server/internal/utils"

	"github.com/redis/go-redis/v9"
)

func UpdateTransactionSheet(
	r *redis.Client,
	transactions []utils.PlaidTransaction,
	userID string,
) error {
	fmt.Println("Called google update transaction function")
	return nil
}
