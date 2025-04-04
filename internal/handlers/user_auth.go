package handlers

import (
	"context"
	"log"
	"net/http"
	"server/internal/utils"
	"time"

	"github.com/labstack/echo/v4"
)

// Signin user
func (h *Handler) SignInAuth(c echo.Context) error {
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
	return c.Redirect(307, h.SignInAuthConfig.AuthCodeURL(state))
}

// Sign out user
func (h *Handler) Signout(c echo.Context) error {
	ctx := context.Background()

	cookie, err := c.Request().Cookie("session_id")
	if err != nil {
		log.Println(err)
	}

	if cookie.Value == "" {
		log.Println("session id cookie is empty")
	}

	sessionID := cookie.Value

	// TODO: Delete sign in token

	// Delete the user id from the redis cache
	_, rErr := h.RedisClient.Del(ctx, sessionID).Result()
	if rErr != nil {
		log.Println(rErr)
	}

	utils.ClearSessionIDCookie(c)

	return c.Redirect(307, "/")
}
