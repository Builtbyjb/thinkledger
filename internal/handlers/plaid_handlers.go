package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"server/internal/utils"

	"github.com/labstack/echo/v4"
	"github.com/plaid/plaid-go/plaid"
)

func (h *Handler) PlaidLinkToken(c echo.Context) error {
	ctx := context.Background()
	var userInfo utils.UserInfo

	cookie, _ := c.Request().Cookie("session_id")
	sessionID := cookie.Value

	sessionUser := "user:" + sessionID

	// Get user info from redis
	userInfoStr, err := h.RedisClient.Get(ctx, sessionUser).Result()
	if err != nil {
		log.Println(err)
		return c.String(500, "Internal server error")
	}

	if err := json.Unmarshal([]byte(userInfoStr), &userInfo); err != nil {
		log.Println(err)
		return c.String(500, "Internal server error")
	}

	user := plaid.LinkTokenCreateRequestUser{
		ClientUserId: userInfo.Sub,
	}
	request := plaid.NewLinkTokenCreateRequest(
		"ThinkLedger",
		"en",
		[]plaid.CountryCode{plaid.COUNTRYCODE_US, plaid.COUNTRYCODE_CA},
		user,
	)
	request.SetProducts([]plaid.Products{plaid.PRODUCTS_TRANSACTIONS})
	request.SetLinkCustomizationName("default")
	request.SetWebhook(os.Getenv("SERVER_URL") + "/plaid-webhooks")
	// request.SetRedirectUri(fmt.Sprintf("%s/auth/plaid/callback", os.Getenv("SERVER_URL")))
	request.SetAccountFilters(plaid.LinkTokenAccountFilters{
		Depository: &plaid.DepositoryFilter{
			AccountSubtypes: []plaid.AccountSubtype{
				plaid.ACCOUNTSUBTYPE_CHECKING,
				plaid.ACCOUNTSUBTYPE_SAVINGS,
			},
		},
	})
	resp, _, err := h.PlaidClient.PlaidApi.LinkTokenCreate(ctx).
		LinkTokenCreateRequest(*request).
		Execute()
	if err != nil {
		log.Println(err)
		return c.JSON(400, map[string]string{
			"error": "Failed to create plaid link token",
		})
	}

	linkToken := resp.GetLinkToken()
	return c.JSON(200, map[string]string{
		"linkToken": linkToken,
	})
}

func (h *Handler) PlaidAccessToken(c echo.Context) error {
	ctx := context.Background()

	jsonData := make(map[string]any)
	if err := json.NewDecoder(c.Request().Body).Decode(&jsonData); err != nil {
		log.Println(err)
		return c.JSON(400, map[string]string{
			"error": "Error decoding json",
		})
	}

	// TODO: store metadata in a database

	publicToken := jsonData["public_token"].(string)
	if len(publicToken) == 0 {
		log.Println("No public token")
		return c.JSON(400, map[string]string{
			"error": "No public token",
		})
	}

	exchangePublicTokenReq := plaid.NewItemPublicTokenExchangeRequest(publicToken)
	exchangePublicTokenResp, _, err := h.PlaidClient.PlaidApi.
		ItemPublicTokenExchange(ctx).
		ItemPublicTokenExchangeRequest(
			*exchangePublicTokenReq,
		).Execute()
	if err != nil {
		log.Println(err)
		return c.JSON(400, map[string]string{
			"error": "Failed to exchange public token for access token",
		})
	}

	accessToken := exchangePublicTokenResp.GetAccessToken()
	fmt.Printf("Plaid access token: %s\n", accessToken)

	// TODO: store access token in a postgres database

	request := plaid.NewTransactionsSyncRequest(accessToken)

	// Number of initial transactions to get.
	// request.Count = plaid.PtrInt32(100)

	transactionsResp, _, err := h.PlaidClient.PlaidApi.TransactionsSync(ctx).
		TransactionsSyncRequest(*request).
		Execute()
	if err != nil {
		log.Println(err)
		return c.JSON(400, map[string]string{
			"error": "Failed to get transactions data from plaid",
		})
	}

	transactionJsonBytes, err := json.MarshalIndent(transactionsResp, "", "  ")
	if err != nil {
		log.Println(err)
		c.JSON(500, map[string]string{
			"error": "Internal server error",
		})
	}

	// fmt.Println(string(transactionJsonBytes))

	var transactionJsonData utils.PlaidTransactionResponse
	if err := json.Unmarshal(transactionJsonBytes, &transactionJsonData); err != nil {
		log.Println(err)
		return c.JSON(500, map[string]string{
			"error": "Internal server error",
		})
	}

	// fmt.Println(transactionJsonData)

	return c.JSON(200, map[string]string{
		"success": "access token gotten",
	})
}

func (h *Handler) PlaidWebhooks(c echo.Context) error {
	return c.NoContent(200)
}

func (h *Handler) PlaidCallback(c echo.Context) error {
	return c.NoContent(200)
}
