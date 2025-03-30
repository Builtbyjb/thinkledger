package handlers

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"server/internal/utils"
	"time"

	"github.com/labstack/echo/v4"
)

// Signin user
func (h *Handler) HandleSignInAuth(c echo.Context) error {
	state, err := utils.GenerateRandomstring()
	if err != nil {
		log.Println(err)
		return c.String(500, "Internal server error")
	}

	// Set state cookie
	c.SetCookie(&http.Cookie{
		Name:     "state",
		Value:    state,
		HttpOnly: true,
		Path:     "/",
		Secure:   true,
		Expires:  time.Now().Add(5 * time.Minute),
	})

	// Add oauth2.AccessTypeOffline to get a refresh token
	return c.Redirect(307, h.OAuthConfig.AuthCodeURL(state))
}

// Sign out user
func (h *Handler) HandleSignout(c echo.Context) error {
	ctx := context.Background()

	cookie, err := c.Request().Cookie("session_id")
	if err != nil {
		log.Println(err)
		return c.Redirect(307, "/")
	}

	if cookie.Value == "" {
		log.Println("session id cookie is empty")
		return c.Redirect(307, "/")
	}

	sessionID := cookie.Value
	sessionUser := fmt.Sprintf("user:%s", sessionID)

	// Delete the user id from the redis cache
	_, rErr := h.RedisClient.Del(ctx, sessionID, sessionUser).Result()
	if rErr != nil {
		log.Println(rErr)
		return c.Redirect(307, "/")
	}

	utils.ClearSessionIDCookie(c)

	return c.Redirect(307, "/")
}
