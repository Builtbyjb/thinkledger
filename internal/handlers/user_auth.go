package handlers

import (
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

// Logout user
func (h *Handler) HandleLogout(c echo.Context) error {
	ctx := c.Request().Context()

	cookie, err := c.Request().Cookie("authId")
	if err != nil {
		log.Println(err)
		return c.Redirect(307, "/")
	}

	if cookie.Value == "" {
		log.Println("authId cookie is empty")
		return c.Redirect(307, "/")
	}

	authId := cookie.Value

	// Delete the user id from the redis cache
	_, rErr := h.RedisClient.Del(ctx, authId).Result()
	if rErr != nil {
		log.Println(rErr)
		return c.Redirect(307, "/")
	}

	utils.ClearAuthIdCookie(c)

	return c.Redirect(307, "/")
}
