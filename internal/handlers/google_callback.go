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

func (h *Handler) GoogleSignInCallback(c echo.Context) error {
	ctx := c.Request().Context()

	// Verify state to prevent CSRF
	cookie, err := c.Cookie("state")
	if err != nil || cookie.Value != c.QueryParam("state") {
		log.Println(err)
		return c.String(400, "Invalid state parameter")
	}

	fmt.Println(c.QueryParam("scope"))

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
		return c.String(500, "Failed to marshal token")
	}

	// Generate authentication id
	sessionID := uuid.New().String()

	// Set redis expiration date
	expiration := time.Duration(24 * time.Hour)

	// Use the access token to get information about the user trying signing in
	userInfo, err := utils.GetUserInfo(token.AccessToken, h.OAuthConfig)
	if err != nil {
		log.Print(err)
		c.String(500, "Failed to get user info")
	}

	// TODO: check if the user is new the added the postgress database

	// Convert user info to json bytes
	userBytes, err := json.Marshal(userInfo)
	if err != nil {
		log.Println(err)
		return c.String(500, "Failed to marshal user info")
	}

	// use go channels to run these operations of multiple go routines
	// Save user token
	if err := h.RedisClient.Set(ctx, sessionID, tokenBytes, expiration).Err(); err != nil {
		log.Println(err)
		return c.String(500, "Failed to save token: "+err.Error())
	}

	// Save user info
	sessionUser := "user:" + sessionID
	if err := h.RedisClient.Set(ctx, sessionUser, userBytes, expiration).Err(); err != nil {
		log.Println(err)
		return c.String(500, "Failed to save user info: "+err.Error())
	}

	// Set user authentication cookie
	c.SetCookie(&http.Cookie{
		Name:     "session_id",
		Value:    sessionID,
		HttpOnly: true,
		Path:     "/",
		Secure:   true,
		SameSite: http.SameSiteLaxMode,
		Expires:  time.Now().Add(24 * time.Hour),
	})

	return c.Redirect(307, "/home")
}

func (h *Handler) GoogleServiceCallback(c echo.Context) error {
	return c.NoContent(200)
}
