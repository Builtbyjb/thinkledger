package handlers

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"server/internal/utils"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

func (h *Handler) HandleCallbackAuth(c echo.Context) error {
	ctx := c.Request().Context()

	// Verify state to prevent CSRF
	cookie, err := c.Cookie("state")
	if err != nil || cookie.Value != c.QueryParam("state") {
		log.Println(err)
		return c.String(400, "Invalid state parameter")
	}

	// Get google oauth2 token
	token, err := h.OAuthConfig.Exchange(ctx, c.QueryParam("code"))
	if err != nil {
		log.Println(err)
		return c.String(500, "Token exchange failed: "+err.Error())
	}

	// Convert token to jsonBytes for easy type conversion later
	tokenBytes, err := json.Marshal(token)
	if err != nil {
		log.Println(err)
		return c.String(500, "Failed to Marshal token")
	}

	// Generate authentication id
	authId := uuid.New().String()

	// Set cookie and redis expiration date
	expiration := time.Duration(24 * time.Hour)

	userInfo, err := utils.GetUserInfo(token.AccessToken, h.OAuthConfig)
	if err != nil {
		log.Print(err)
		c.String(500, "Failed to ger user info")
	}

	// Save the user token
	if err := h.RedisClient.Set(ctx, authId, tokenBytes, expiration).Err(); err != nil {
		log.Println(err)
		return c.String(500, "Failed to save token: "+err.Error())
	}

	// Save user name
	name := fmt.Sprintf("name:%s", authId)
	if err := h.RedisClient.Set(ctx, name, userInfo.Name, expiration).Err(); err != nil {
		log.Println(err)
		return c.String(500, "Failed to save user name: "+err.Error())
	}

	// Set user authentication cookie
	c.SetCookie(&http.Cookie{
		Name:     "authId",
		Value:    authId,
		HttpOnly: true,
		Path:     "/",
		Secure:   true,
		SameSite: http.SameSiteLaxMode,
		Expires:  time.Now().Add(24 * time.Hour),
	})

	return c.Redirect(307, "/home")
}
