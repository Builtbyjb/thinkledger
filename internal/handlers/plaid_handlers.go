package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/labstack/echo/v4"
	"github.com/plaid/plaid-go/plaid"
)

func (h *Handler) PlaidLinkToken(c echo.Context) error {
	ctx := context.Background()

	cookie, _ := c.Request().Cookie("session_id")
	sessionID := cookie.Value

	// Get userID
	userID, err := h.RedisClient.Get(ctx, sessionID).Result()
	if err != nil {
		log.Println(err)
		return c.String(500, "Internal server error")
	}

	user := plaid.LinkTokenCreateRequestUser{
		ClientUserId: userID,
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

	cookie, err := c.Request().Cookie("session_id")
	if err != nil || cookie.Value == "" {
		log.Println(err)
		return c.JSON(500, map[string]string{
			"error": "Internal server error",
		})
	}

	sessionID := cookie.Value
	userID, err := h.RedisClient.Get(ctx, sessionID).Result()
	if err != nil {
		log.Println(err.Error())
		return c.JSON(400, map[string]string{
			"error": "Internal server error",
		})

	}

	plaidAccessToken := "plaidAccessToken:" + userID
	if err := h.RedisClient.Set(ctx, plaidAccessToken, accessToken, 0).Err(); err != nil {
		log.Println(err.Error())
		return c.JSON(400, map[string]string{
			"error": "Internal server error",
		})
	}

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
