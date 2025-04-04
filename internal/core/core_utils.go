package core

import (
	"context"

	"github.com/redis/go-redis/v9"
)

func CheckStatus(r *redis.Client, userID string) bool {
	ctx := context.Background()

	getServiceToken := "serviceToken:" + userID
	_, err := r.Get(ctx, getServiceToken).Result()
	if err != nil {
		return false
	}
	// TODO: Verify service token

	getPlaidAccessToken := "plaidAccessToken:" + userID
	_, err = r.Get(ctx, getPlaidAccessToken).Result()
	if err != nil {
		return false
	}

	return true
}
