package app

import (
	"fmt"
	"log"
	"server/internal/core"
	"server/internal/database/postgres"
	"server/internal/handlers"
	"time"
)

func Core(h *handlers.Handler) {
	for {
		// Query the database every minute
		time.Sleep(1 * time.Minute)
		fmt.Println("Running database query...")

		var users []postgres.User
		result := h.DB.Find(&users)
		if result.Error != nil {
			log.Fatal("Database error")
		}

		if result.RowsAffected == 0 {
			continue
		}

		for _, u := range users {
			isVerified := core.CheckStatus(h.RedisClient, u.ID)
			if isVerified {
				plaidTransactions, err := core.GetPlaidTransaction(
					h.RedisClient,
					h.PlaidClient,
					u.ID,
				)
				// Handle errors gracefully
				if err != nil {
					log.Println(err)
					continue
				} else {
					if err := core.UpdateTransactionSheet(
						h.RedisClient,
						plaidTransactions,
						u.ID,
					); err != nil {
						log.Println(err)
						continue
					}
				}
			}
		}
	}
}
