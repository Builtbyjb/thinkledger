package core

import (
	"context"
	"encoding/json"
	"fmt"
	"server/internal/utils"

	"github.com/plaid/plaid-go/plaid"
	"github.com/redis/go-redis/v9"
)

func GetPlaidTransaction(
	r *redis.Client,
	p *plaid.APIClient,
	userID string,
) ([]utils.PlaidTransaction, error) {
	ctx := context.Background()
	getAccessToken := "plaidAccessToken:" + userID
	accessToken, err := r.Get(ctx, getAccessToken).Result()
	if err != nil {
		return nil, err
	}

	request := plaid.NewTransactionsSyncRequest(accessToken)

	// // Number of initial transactions to get.
	// // request.Count = plaid.PtrInt32(100)

	transactionsResp, _, err := p.PlaidApi.TransactionsSync(ctx).
		TransactionsSyncRequest(*request).
		Execute()
	if err != nil {
		return nil, err
	}

	transactionJsonBytes, err := json.MarshalIndent(transactionsResp, "", "  ")
	if err != nil {
		return nil, err
	}

	// fmt.Println(string(transactionJsonBytes))

	var transactionJsonData utils.PlaidTransactionResponse
	if err := json.Unmarshal(transactionJsonBytes, &transactionJsonData); err != nil {
		return nil, err
	}

	fmt.Println(transactionJsonData.Added)
	return transactionJsonData.Added, nil
}
